---
layout: page
title: Setup
permalink: /setup/
nav_order: 2
---

# Setup

This section aims to provide a step-by-step guide to setting up a vanilla local k8s cluster. This is not a production-ready setup, but it is a good way to understand the pipeline proposed in **PerfCE**. For readers who have possessed a k8s cluster, they can adjust their cluster to meet the requirements of **PerfCE**. Note that for the sake of convenience, we don't present all config files in this website. You can find them in the [GitHub repository](https://github.com/ZhenlanJi/PerfCE/tree/main/config_files/setup).

## Prerequisites
Our experiments were performed on a server with Ubuntu 18.04 LTS (x86\_64). Although **PerfCE** is not limited to this environment, we recommend using the same environment to avoid potential compatibility issues. 
The following packages are required:
- [docker](https://docs.docker.com/engine/install/ubuntu/)
- [kubectl](https://kubernetes.io/docs/tasks/tools/install-kubectl/)
- [kind](https://kind.sigs.k8s.io/docs/user/quick-start/)


## k8s Cluster Setup 

### 1. Create a k8s cluster with kind

**Step 1:** Configuring the kind Cluster in file kind-config.yaml
```yaml
# three node (two workers) cluster config
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
nodes:
- role: control-plane
- role: worker
- role: worker
```

**Step 2:** Run the following command to create the cluster:
```bash
kind create cluster --name $cluster_name --config kind-config.yaml
```
Note that the creating process may take a few minutes. Please wait patiently. If you encounter any errors, please refer to the kind [documentation](https://kind.sigs.k8s.io/docs/user/quick-start/) for troubleshooting.

### 2. Install k8s Dashboard

### 3. Install Chaos-Mesh

## TiDB Setup


## MySQL Setup Tutorial