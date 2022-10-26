---
layout: page
title: Collect Data
parent: Utilities
nav_order: 1
---

# Collect Data

In our experiments, we use [Prometheus](https://prometheus.io/) to monitor the performance of the database clusters. Then, we use [prometheus_api_client](https://pypi.org/project/prometheus-api-client/) to collect the data from Prometheus. Please make sure you have finished the [setup](/PerfCE/pages/setup) before you start.

You can find the code for collecting data in [collect_data.py](https://github.com/ZhenlanJi/PerfCE/blob/main/src/collect_data.py). 


