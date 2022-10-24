---
layout: page
title: TiDB Setup
parent: Setup
nav_order: 2
---

# TiDB Setup
{: .no_toc}


1. TOC
{:toc}

## Install TiDB

Since the official TiDB documentation is well organized, we just skip the installation process and focus on the configuration of TiDB. We strongly recommend readers to follow the [official documentation](https://docs.pingcap.com/tidb-in-kubernetes/stable/get-started) to install TiDB.

> **Note:** TiDB has a built-in monitoring service, including Prometheus and Grafana so we don't need to install them here.

## Scale the TiDB cluster

The official documentation also provides a well-written guide on how to scale the TiDB cluster. We just provide a brief summary here.
Readers can refer to [official documentation](https://docs.pingcap.com/tidb-in-kubernetes/stable/scale-a-tidb-cluster) for more details.

The default setting of TiDB only contains one <tt>pd</tt>, one <tt>tidb</tt>, and one <tt>tikv</tt>. In our experiment, we scale out 
the cluster to 3 <tt>tikv</tt> to simulate a more realistic scenario. There are two ways to scale out the cluster:

1. Directly edit the config file of the cluster:
   ```bash
   kubectl edit tc ${tidb_cluster_name{} -n ${tidb_namespace}
   ```
2.In one-line command
    ```bash
    # set the tikv's replicate as 3
    kubectl patch -n ${tidb_namespace} tc ${tidb_cluster_name} --type merge --patch '{"spec":{"tikv":{"replicas":3}}}' 
    ```

## Customize the configuration of monitoring service

Reader can refer to [k8s documentation](https://kubernetes.io/docs/concepts/configuration/configmap/) and [TiDB documentation](https://docs.pingcap.com/tidb-in-kubernetes/dev/monitor-a-tidb-cluster) for more details. Here we just provide a brief guide.

**Step 1:** Create <u>external-configMap.yml</u> according to the official [template](https://github.com/pingcap/tidb-operator/blob/master/examples/monitor-with-externalConfigMap/prometheus/external-configMap.yaml). You can find our example in [here](https://github.com/ZhenlanJi/PerfCE/tree/main/config_files/setup/tidb).

> **Note:** In this config file you can customize the configuration of Prometheus and Grafana. For example, you can change the retention time of Prometheus data, the refresh rate of Grafana dashboard, etc. We set the scrape_interval from 15s to 1s to make the monitoring service more responsive. You can compare the difference between the official template and our configuration.

**Step 2:** Copy the <u>tidb-monitor.yml</u>. You can also find it in our [GitHub repository](https://github.com/ZhenlanJi/PerfCE/tree/main/config_files/setup/tidb)

**Step 3:** Create external configMap by running the following command:
```bash
kubectl apply -f external-configMap.yml -n ${namespace}
```

**Step 4:** Install tidb monitor by running the following command:
```bash
kubectl apply -f tidb-monitor.yaml -n ${namespace}
```

Wait for cluster Pods ready:
```bash
watch kubectl -n ${namespace} get pod
```

**Step 5:** Access the Prometheus dashboard by running the following command:
```bash
kubectl port-forward -n tidb-cluster svc/basic-prometheus 9090 --address 0.0.0.0 
```

Then you can access the Prometheus dashboard by visiting [http://localhost:9090](http://localhost:9090), and check whether the configuration is correct.


## Run benchmark on TiDB

We use [TPC-C](https://www.tpc.org/tpcc/) to simulate the workload of a real-world OLTP database. Readers can refer to [this site](https://docs.pingcap.com/tidb/stable/benchmark-tidb-using-tpcc) for more details.

**Step 1:** Install TiUP
```bash
curl --proto '=https' --tlsv1.2 -sSf https://tiup-mirrors.pingcap.com/install.sh | sh
```

**Step 2:** Install TPC-C
```bash
tiup install bench
```

**Step 3:** Load Data
```bash
tiup bench tpcc -P 14000 -D tpcc --warehouses 4 prepare -T 16
```

**Step 4:** Run benchmark
```bash
while :
do
   tiup bench tpcc -P 14000 -D tpcc --warehouses 4 run -T 16
done
```
