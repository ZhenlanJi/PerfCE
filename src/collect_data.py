import os
from os.path import (
    abspath,
    dirname,
)
from prometheus_api_client import (
    PrometheusConnect,
    MetricSnapshotDataFrame,
    MetricRangeDataFrame
)
import argparse
import sys
import datetime as dt
import pandas as pd
import pytz
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler


def collect_raw_data(query_list, query_info_df, start_time, duration, prom, out_dir):
    for i in range(len(query_list)):
        query_df = pd.DataFrame()
        for t in range(duration):
            mstart_time = start_time+dt.timedelta(hours=1)*t
            mend_time = mstart_time + \
                dt.timedelta(hours=1)-dt.timedelta(seconds=1)
            metric_data = prom.custom_query_range(
                query_list[i],
                start_time=mstart_time,
                end_time=mend_time,
                step=1
            )

            metric_df = pd.DataFrame(columns=['timestamp'])
            for m in metric_data:
                if query_info_df.metric[i] == 'None':
                    col_name = "None"
                else:
                    if m['metric'] == {} and len(metric_data) > 1:
                        continue
                    sub_metrics = query_info_df.metric[i].split("+")
                    col_name = "_".join(
                        list(map(lambda x: m['metric'][x], sub_metrics)))
                    col_name = col_name.replace('-', '_')
                temp_df = pd.DataFrame(m['values'], columns=[
                    'timestamp', col_name])
                metric_df = pd.merge(metric_df, temp_df,
                                     on='timestamp', how='outer')

            query_df = pd.concat([query_df, metric_df])

        save_path = os.path.join(out_dir, '_'.join(
            (query_info_df.name[i]).split())+'.csv')
        query_df.to_csv(save_path, index=False)


def combine_data(out_dir, drop_list):
    combined_df = pd.DataFrame(columns=['timestamp'])
    # walk through directory
    for root, dirs, files in os.walk(out_dir):
        for file in files:
            if file.endswith(".csv"):
                if file not in drop_list:
                    temp_df = pd.read_csv(os.path.join(root, file))
                    if temp_df.empty:
                        continue
                    file_name = file.split('.')[0]
                    # rename temp_df columns
                    temp_df.columns = ['timestamp'] + list(
                        map(lambda x: file_name+'__'+x, temp_df.columns[1:]))
                    combined_df = pd.merge(combined_df, temp_df,
                                           on='timestamp', how='outer')
    combined_df.set_index('timestamp')
    # drop columns all nan
    combined_df.dropna(axis=1, how='all', inplace=True)
    combined_df.interpolate(inplace=True, limit=60, method='linear')
    # fill nan by 0
    combined_df.fillna(0, inplace=True)
    combined_df = combined_df.loc[:, (combined_df != 0).any(axis=0)]

    return combined_df



def main(args):
    # Set up the Prometheus connection
    prom = PrometheusConnect(
        url=args.prometheus_url, disable_ssl=True)

    query_info_df = pd.read_csv(args.query_info)
    with open(args.query_list) as f:
        query_list = f.readlines()
    drop_list = []
    if args.drop_list is not None:
        with open(args.drop_list) as f:
            drop_list = f.readlines()

    # replace substring of each line in query_list
    if args.database == 'mysql':
        query_list = list(map(lambda x: x.replace(
            '$host', args.exporter_url), query_list))
        query_list = list(
            map(lambda x: x.replace('$interval', '1m'), query_list))
    elif args.database == 'tidb':
        query_list = list(map(lambda x: x.replace(
            '$tidb_cluster', 'tidb-cluster'), query_list))
        query_list = list(map(lambda x: x.replace(
            '$instance', 'basic-pd-0'), query_list))
    else:
        print('database not supported')
        sys.exit(1)

    start_time = dt.datetime.fromtimestamp(args.start_time)

    collect_raw_data(query_list, query_info_df, start_time,
                     args.duration, prom, args.out_dir)
    combined_df = combine_data(args.out_dir, drop_list)

    temp_df = combined_df.copy()
    temp_df.drop(['timestamp'], axis=1, inplace=True)
    # minus by mean
    temp_df = temp_df - temp_df.mean()
    blip_df = pd.DataFrame()
    # discritize each single column by kmeans cluster
    for col in temp_df.columns:
        kmeans = KMeans(n_clusters=10, random_state=0)
        kmeans.fit(temp_df[col].to_numpy().reshape(-1, 1))
        blip_df[col] = kmeans.labels_

    blip_df.to_csv(args.output_file, index=False)


if __name__ == "__main__":
    # Parse arguments
    parser = argparse.ArgumentParser(description='Collect data')
    parser.add_argument("--database", type=str, choices=['mysql', 'tidb'],
                        default='mysql', help="select the object database")
    parser.add_argument("--start_time", type=int,
                        help="Start time for data collection (UNIX Timestamp)")
    parser.add_argument("--duration", type=int,
                        help="Duration (hours) for data collection")
    parser.add_argument("--prometheus_url", type=str, help="Prometheus URL")
    parser.add_argument("--exporter_url", type=str,
                        help="MySQL exporter host's URL")
    parser.add_argument("--query_list", type=str,
                        help="Path to query list file (should be txt file)")
    parser.add_argument("--query_info", type=str,
                        help="Path to query_csv file (should be csv file)")
    parser.add_argument("--drop_list", type=str, default=None,
                        help="(Optional) Path to dropped table list file (should be txt file)")
    parser.add_argument("--raw_data_output", type=str,
                        help="Path to output directory of raw data")
    parser.add_argument("--output_file", type=str,
                        help="Path of output file (should be csv file)")
    args = parser.parse_args()

    main(args)
