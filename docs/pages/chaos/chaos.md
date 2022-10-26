---
layout: page
title: Chaos Engineering
permalink: /chaos/
# has_children: true
nav_order: 3
---

# Chaos Engineering
{: .no_toc}


1. TOC
{:toc}

In out experiments, we use [Chaos Mesh](https://chaos-mesh.org/) to inject chaos into the database clusters. Chaos Mesh is a cloud-native Chaos Engineering platform that orchestrates chaos on Kubernetes environments. In [k8s cluster setup](/PerfCE/pages/setup/k8s.html), we 
have already installed Chaos Mesh. Note that here we suppose that you have already installed Chaos Mesh. In this section, we will introduce how to use Chaos Mesh to inject chaos into the TiDB cluster.

## Login Chaos Mesh Dashboard

Firstly, we need to login Chaos Mesh Dashboard. 

Access the Chaos Mesh dashboard by visiting [http://localhost:2333](http://localhost:2333) in your browser.

You will be prompted to enter a token to login like the following image.
<img src="./../assets/images/chaos_mesh_login.png" style="zoom:33%;" />

Then, click the <u>Click here to generate</u> button.
The prompt will show the guide as follows.
<img src="./../assets/images/chaos_mesh_init.png" style="zoom:33%;" />

> **Note:** Make sure that you select the correct namespace. This value is the 
> namespace where want to conduct chaos experiments. For example, if you deploy
> MySQL in `default` namespace, then you should select `default` namespace.

Follow the guide to generate the token. Then, you can login the Chaos Mesh Dashboard as follows.
<img src="./../assets/images/chaos_mesh_dashboard.png" />

## Start from a simple chaos experiment

## Use workflow to orchestrate multiple chaos experiments