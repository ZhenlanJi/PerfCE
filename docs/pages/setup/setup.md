---
layout: page
title: Setup
permalink: /setup/
has_children: true
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

> **Note:** Readers need to follow the instructions of [k8s Cluster Setup](https://zhenlanji.github.io/PerfCE/setup/k8s) first, then set up TiDB or MySQL on the cluster according to their needs. We don't recommend deploy MySQL and TiDB at the same cluster.