---
layout: page
title: Collect Data
parent: Utilities
nav_order: 1
---

# Collect Data

In our experiments, we use [Prometheus](https://prometheus.io/) to monitor the performance of the database clusters. Then, we use [prometheus_api_client](https://pypi.org/project/prometheus-api-client/) to collect the data from Prometheus. Please make sure you have finished the [setup](/PerfCE/pages/setup) before you start.

You can find the code for collecting data in [collect_data.py](https://github.com/ZhenlanJi/PerfCE/blob/main/src/collect_data.py). You can directly execute the script to collect and pre-process the data.

**Usage:**
```bash
python test.py [-h] [--database {mysql,tidb}]
               [--start_time START_TIME]
               [--duration DURATION]
               [--prometheus_url PROMETHEUS_URL]
               [--exporter_url EXPORTER_URL]
               [--query_list QUERY_LIST]
               [--query_info QUERY_INFO]
               [--drop_list DROP_LIST]
               [--raw_data_output RAW_DATA_OUTPUT]
               [--output_file OUTPUT_FILE]
``` 


Here is the arguments table for the script:


| Argument        | Description                                                                   | Special Remark                                                                                                                                                           |
| :-------------- | :---------------------------------------------------------------------------- | :----------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| database        | Select which database to be collected.                                        | `str`, only two choice: `mysql` and `tidb`.                                                                                                                              |
| start_time      | Start time for data collection.                                               | `int`, should be Unix timestamp.                                                                                                                                         |
| duration        | Duration (hours) for data collection, i.e., the time range of collected data. | `int`.                                                                                                                                                                   |
| prometheus_url  | The url to access Prometheus service.                                         | `str`, e.g., `http://localhost:9090`.                                                                                                                                    |
| exporter_url    | The url of database exporter service.                                         | `str`, use `kubectl -n ${namespace} svc` to find it, or you can find it in Grafana's dashboard.                                                                          |
| query_list      | Path to query list file (should be txt file).                                 | `str`, we have provided our query list file in our [repo](https://github.com/ZhenlanJi/PerfCE/tree/main/config_files/perfce).                                            |
| query_info      | Path to query_csv file (should be csv file).                                  | `str`, we have provided our query info file in our [repo](https://github.com/ZhenlanJi/PerfCE/tree/main/config_files/perfce).                                            |
| drop_list       | Path to dropped table list file (should be csv file).                         | `str`, we have provided our drop list file in our [repo](https://github.com/ZhenlanJi/PerfCE/tree/main/config_files/perfce). **Note** that only MySQL has the drop list. |
| raw_data_output | Path to output directory of raw data.                                         | `str`.                                                                                                                                                                   |
| output_file_dir | Path to the dir of output file.                                               | `str`, two file, `combined.csv` and `blip.csv` will be outputted in this directory. The latter will be fed to BLIP to learn the causal Graph.                             |
