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


def main(args):
    # Set up the Prometheus connection
    prom = PrometheusConnect(url=args.prometheus_url, disable_ssl=True)
    
    start_time=dt.datetime.fromtimestamp(args.start_time)



if "__name__" == "__main__":
    # Parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--start_time", type=int, help="Start time for data collection (UNIX Timestamp)")
    parser.add_argument("--duration", type=str, help="Duration (hours) for data collection")

