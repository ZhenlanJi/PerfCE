import yaml
import os
import datetime as dt
import pandas as pd
import pytz
import numpy as np
import argparse


def parse_label(label):
    pods = []
    if label == 'pd':
        pods.append('basic_pd_0')
    elif label == 'tidb':
        pods.append('basic_tidb_0')
    elif label == 'tikv':
        pods.append('basic_tikv_0')
        pods.append('basic_tikv_1')
        pods.append('basic_tikv_2')
    return pods


def parse_selector(selector_data):
    if selector_data.get('pods'):
        pods = selector_data['pods']['tidb-cluster']
        pods = list(map(lambda x: x.replace('-', '_'), pods))
    elif selector_data.get('labelSelectors'):
        label = selector_data['labelSelectors']['app.kubernetes.io/component']
        pods = parse_label(label)
    return pods


def parse_chaos_attr(chaos_attr, chaos_type):
    chaos_attr_dict = {}
    if chaos_type == 'network':
        action = chaos_attr['action']
        if action == 'loss':
            chaos_attr_dict['Network_loss_rate'] = int(
                chaos_attr['loss']['loss'])
        elif action == 'delay':
            chaos_attr_dict['Network_delay_latency'] = int(
                chaos_attr['delay']['latency'].strip('ms'))
        elif action == 'duplicate':
            chaos_attr_dict['Network_duplicate_rate'] = int(
                chaos_attr['duplicate']['duplicate'])
        elif action == 'corrupt':
            chaos_attr_dict['Network_corrupt_rate'] = int(
                chaos_attr['corrupt']['corrupt'])
        elif action == 'bandwidth':
            chaos_attr_dict['Network_bandwidth_limit'] = int(
                chaos_attr['bandwidth']['limit'])
            chaos_attr_dict['Network_bandwidth_buffer'] = int(
                chaos_attr['bandwidth']['buffer'])
        else:
            pass
    elif chaos_type == 'stress':
        action = list(chaos_attr['stressors'].keys())[0]
        if action == 'cpu':
            chaos_attr_dict['Stress_stressors_cpu_load'] = int(
                chaos_attr['stressors']['cpu']['load'])
        elif action == 'memory':
            chaos_attr_dict['Stress_stressors_memory_size'] = int(
                chaos_attr['stressors']['memory']['size'].strip('%'))
        else:
            print('Unknown action: {}'.format(action))
    elif chaos_type == 'time':
        chaos_attr_dict['Time_timeOffset'] = int(
            chaos_attr['timeOffset'].strip('m'))
    elif chaos_type == 'io':
        action = chaos_attr['action']
        if action == 'latency':
            chaos_attr_dict['IO_delay_time'] = int(
                chaos_attr['delay'].strip('ms'))
        elif action == 'fault':
            chaos_attr_dict['IO_error_no'] = int(chaos_attr['errno'])
    else:
        pass
    return chaos_attr_dict


def parse4mysql(workflow_data, chaos_df, chaos_start, chaos_duration, suspend_duration, output_file):
    event_type_list = {'normal': 0}
    current_time = chaos_start

    for event in workflow_data["spec"]["templates"][1:]:
        if event["templateType"] == "Suspend":
            current_time += suspend_duration
        else:
            chaos_type = event["templateType"].split("Chaos")[0]
            chaos_type = chaos_type.lower()

            type_name = '_'.join(event["name"].split("-")[:2]) if event["name"].split("-")[
                0] != 'time' else 'time'
            if event_type_list.get(type_name) is None:
                event_type_list[type_name] = len(event_type_list)
            chaos_df.loc[(chaos_df['timestamp'] >= current_time.timestamp()) & (
                chaos_df['timestamp'] <= (current_time + chaos_duration).timestamp()), 'event_type'] = event_type_list[type_name]

            chaos_attr_dict = parse_chaos_attr(
                event[chaos_type+'Chaos'], chaos_type)
            for c in chaos_attr_dict:
                chaos_df.loc[(chaos_df['timestamp'] >= current_time.timestamp()) & (
                    chaos_df['timestamp'] <= (current_time + chaos_duration).timestamp()), c] = chaos_attr_dict[c]
            current_time += chaos_duration

    chaos_df.to_csv(output_file, index=False)
    for k, v in event_type_list.items():
        print('{}: {}'.format(k, v))
    return


def parse4tidb(workflow_data, chaos_df, chaos_start, chaos_duration, suspend_duration, output_file):
    event_type_list = {'normal': 0}
    current_time = chaos_start

    for event in workflow_data["spec"]["templates"][1:]:
        if event["templateType"] == "Suspend":
            current_time += suspend_duration
        else:
            chaos_type = event["templateType"].split("Chaos")[0]
            chaos_type = chaos_type.lower()

            type_name = '_'.join(event["name"].split("-")[:2]) if event["name"].split("-")[
                0] != 'time' else 'time'
            if event_type_list.get(type_name) is None:
                event_type_list[type_name] = len(event_type_list)
            chaos_df.loc[(chaos_df['timestamp'] >= current_time.timestamp()) & (
                chaos_df['timestamp'] <= (current_time + chaos_duration).timestamp()), 'event_type'] = event_type_list[type_name]

            pods = parse_selector(event[chaos_type+'Chaos']["selector"])
            for pod in pods:
                chaos_df.loc[(chaos_df['timestamp'] >= current_time.timestamp()) & (
                    chaos_df['timestamp'] <= (current_time + chaos_duration).timestamp()), pod] = 1

            chaos_attr_dict = parse_chaos_attr(
                event[chaos_type+'Chaos'], chaos_type)
            for c in chaos_attr_dict:
                chaos_df.loc[(chaos_df['timestamp'] >= current_time.timestamp()) & (
                    chaos_df['timestamp'] <= (current_time + chaos_duration).timestamp()), c] = chaos_attr_dict[c]
            current_time += chaos_duration

    chaos_df.to_csv(output_file, index=False)
    for k, v in event_type_list.items():
        print('{}: {}'.format(k, v))
    return


def main(args):
    start_time = dt.datetime.fromtimestamp(args.collect_start)
    end_time = dt.datetime.fromtimestamp(args.collect_end)
    chaos_start = dt.datetime.fromtimestamp(args.chaos_start)
    chaos_duration = dt.timedelta(seconds=args.chaos_exp_duration)
    suspend_duration = dt.timedelta(minutes=args.chaos_suspend_duration)
    with open(args.chaos_config, "r") as stream:
        try:
            workflow_data = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)

    if args.database == 'tidb':
        chaos_df = pd.DataFrame(
            columns=[
                'timestamp', 'basic_pd_0', 'basic_tidb_0',
                'basic_tikv_0', 'basic_tikv_1', 'basic_tikv_2',
                'event_type', 'Network_loss_rate', 'Network_delay_latency',
                'Network_duplicate_rate', 'Network_corrupt_rate',
                'Network_bandwidth_limit', 'Network_bandwidth_buffer',
                'Stress_stressors_cpu_load', 'Stress_stressors_memory_size',
                'Time_timeOffset'
            ])
        # set chaos_df timestamp
        chaos_df['timestamp'] = pd.date_range(
            start=start_time, end=end_time, freq='1s',)
        chaos_df['timestamp'] = chaos_df['timestamp'].apply(
            lambda x: x.timestamp())
        chaos_df.fillna(0, inplace=True)

        parse4mysql(workflow_data, chaos_df, chaos_start,
                    chaos_duration, suspend_duration, args.output_file)
    elif args.database == 'mysql':
        chaos_df = pd.DataFrame(
            columns=[
                'timestamp', 'event_type', 'IO_delay_time', 'IO_error_no',
                'Network_loss_rate', 'Network_delay_latency',
                'Network_duplicate_rate', 'Network_corrupt_rate',
                'Network_bandwidth_limit', 'Network_bandwidth_buffer',
                'Stress_stressors_cpu_load', 'Stress_stressors_memory_size',
            ])
        # set chaos_df timestamp
        chaos_df['timestamp'] = pd.date_range(
            start=start_time, end=end_time, freq='1s',)
        chaos_df['timestamp'] = chaos_df['timestamp'].apply(
            lambda x: x.timestamp())
        chaos_df.fillna(0, inplace=True)

        parse4tidb(workflow_data, chaos_df, chaos_start,
                   chaos_duration, suspend_duration, args.output_file)

    else:
        print('Unknown database: {}'.format(args.database))
        exit(1)

    return


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Parse chaos mesh workflow')
    parser.add_argument("--database", type=str, choices=['mysql', 'tidb'],
                        default='mysql', help="select the object database")
    parser.add_argument("--collect_start", type=int,
                        help="Start time for data collection (UNIX Timestamp)")
    parser.add_argument("--collect_end", type=int,
                        help="End time for data collection (UNIX Timestamp)")
    parser.add_argument("--chaos_start", type=int,
                        help="Start time for chaos (UNIX Timestamp)")
    parser.add_argument("--chaos_exp_duration", type=int,
                        help="Duration of a single chaos experiment (seconds)")
    parser.add_argument("--chaos_suspend_duration", type=int,
                        help="Duration of interval between experiments (minutes)")
    parser.add_argument("--chaos_config", type=int,
                        help="Path to Chaos Mesh workflow config file (should be yaml file)")
    parser.add_argument("--output_file", type=int,
                        help="Path to output file (should be csv file)")
    args = parser.parse_args()
    main(args)
