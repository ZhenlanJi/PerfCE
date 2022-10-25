---
layout: page
title: MySQL Setup
parent: Setup
nav_order: 3
---

# MySQL Setup
{: .no_toc}


1. TOC
{:toc}

## Install MySQL

This section aims to provide a step-by-step guide to setting up a MySQL cluster. Readers can also refer to  [k8s documentation](https://kubernetes.io/docs/tasks/run-application/run-single-instance-stateful-application/) for more details.

**Step 1:** Create <u>mysql-pv.yml</u> to build the persistent volume (pv) and persistent volume claim (pvc) for MySQL. You can find the file in the [GitHub repository](https://github.com/ZhenlanJi/PerfCE/tree/main/config_files/setup/mysql).

Then run the following command to create the pv and pvc:

```bash
kubectl apply -f mysql-pv.yml
```

**Step 2:** Create <u>mysql-deployment.yml</u> to build the deployment for MySQL. You can find the file in the [GitHub repository](https://github.com/ZhenlanJi/PerfCE/tree/main/config_files/setup/mysql).

Then run the following command to create the deployment:

```bash
kubectl apply -f mysql-service.yml
```

**Step 3:** Create <u>mysql-service.yml</u> to build the service for MySQL. Similarly, you can find the file in the [GitHub repository](https://github.com/ZhenlanJi/PerfCE/tree/main/config_files/setup/mysql).
    
Then run the following command to create the service:
    
```bash
kubectl apply -f mysql-service.yml
```

**Step 4:** Check the status of the MySQL cluster. Run the following command to respectively check the status of the deployments, pod, and service:

```bash
kubectl get deployments
kubectl get pods
kubectl get services
```

**Step 5:** Port forward the MySQL service to the local machine. Run the following command to port forward the MySQL service to the local machine:

```bash
kubectl port-forward svc/mysql 13306:3306
```
> **Note:** The port 13306 is used to avoid conflicts with the local MySQL service. You can change it to any other port you like.

**Step 6:** Connect to the MySQL cluster. Run the following command to connect to the MySQL cluster:

```bash
mysql -u root -p${password} -h 127.0.0.1 -P 13306
```

> **Note:** The default ${password} is `pass`. You can change it in the <u>mysql-deployment.yml</u> file.

## Install Prometheus and Grafana

**Step 1:** Setup via Prometheus Operator. Since the  [official documentation](https://prometheus-operator.dev/docs/prologue/quick-start/) is very detailed, we skip this procedure and strongly recommend readers to follow it to setup Prometheus and Grafana.

**Step 2:** Check the status of the Prometheus and Grafana. Run the following command to respectively check the status of the pods:

```bash
kubectl get po -n monitoring
```

Pleaser make sure all pods are running.

**Step 3:** Port forward the Prometheus and Grafana service to the local machine. 

**Step 4:** Customize the Prometheus configuration. 

Because the default configuration of Prometheus is not suitable for our experiments, e.g., the default retention time is 24h, which is too short for our experiments. We need to customize the Prometheus configuration to meet our needs.

Run the following command to edit the Prometheus configuration:

```bash
kubectl edit -n monitoring Prometheus k8s
```
Then add the `retention: 15d` under the `spec:` field. 

Readers can also refer to this [GitHub issue](https://github.com/prometheus-operator/prometheus-operator/issues/2666) for more details. To further customize the Prometheus configuration, readers can refer to the [official repo](https://github.com/prometheus/mysqld_exporter).

## Run benchmark on MySQL

We use [TPC-C](https://www.tpc.org/tpcc/) to simulate the workload of a real-world OLTP database.

To be more specific, we use [benchbase](https://github.com/cmu-db/benchbase) to run the benchmark. Readers can refer to the [benchbase documentation](https://github.com/cmu-db/benchbase) for more details.

For the configuration of the benchmark, readers can find it in our [GitHub repository](https://github.com/ZhenlanJi/PerfCE/tree/main/config_files/setup/mysql).

Here are three basic commands to run the benchmark:

1. init: Initialize the database.
   ```bash
   java -jar benchbase.jar -b tpcc -c config/mysql/sample_tpcc_config.xml --create=true --load=true
   ```
2. exec: Run the benchmark.
   ```bash
   java -jar benchbase.jar -b tpcc -c config/mysql/sample_tpcc_config.xml --execute=true
   ```
3. cleanup: Clean up the database.
   ```bash
   java -jar benchbase.jar -b tpcc -c config/mysql/sample_tpcc_config.xml --clear=true
   ```