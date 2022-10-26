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

In this section, we will use a simple chaos experiment as an example to show how to use Chaos Mesh to inject chaos into the MySQL cluster. Readers can also refer to [Chaos Mesh Documentation](https://chaos-mesh.org/docs/) to learn more about Chaos Mesh.

> **Note:** Please make sure that you have already deployed MySQL in the Kubernetes cluster successfully. If not, please refer to [MySQL Setup](/PerfCE/pages/setup/MySQL.html).

**Step 1:** Click the <u>Experiments</u> button in the side bar and then click the <u>New Experiment</u> button. Then you will see the following page.
<img src="./../assets/images/chaos_mesh_exp.png" />

**Step 2:** Select the experiment type. Here, we take <u>KUBERNETS->IO INJECTION->LATENCY</u> as an example. Then, fill all the required fields then submit. Readers can refer to [the table](https://chaos-mesh.org/docs/simulate-io-chaos-on-kubernetes/#field-description) for the detailed description of each field.

**Step 3:** Fill the <u>Experiment Info</u>. Because we take the MySQL cluster as an example, we need to fill the <u>Namespace</u> field with the namespace where MySQL is deployed and ensure that this chaos will only affect the MySQL pods. Readers can refer to the following image for more details.
<img src="./../assets/images/chaos_mesh_exp_1.png" />

**Step 4:** Click the <u>Submit</u> button to submit and run the experiment. Then, you can see the running experiment. Readers can refer to the following image for more details.
<img src="./../assets/images/chaos_mesh_exp_res.png" />

Besides, you can also find Chaos Mesh automatically creates a yaml file for this experiment as follows.
```yaml
kind: IOChaos
apiVersion: chaos-mesh.org/v1alpha1
metadata:
  namespace: default
  name: io-latency-0
spec:
  selector:
    namespaces:
      - default
    labelSelectors:
      app: mysql
  mode: all
  action: latency
  delay: 100ms
  percent: 100
  volumePath: /var/lib/mysql
  duration: 60s
```
Therefore, there also exists a way to inject chaos by creating a yaml file. For other chaos experiments, the basic steps are the same. Readers can refer to [Chaos Mesh Documentation](https://chaos-mesh.org/docs/) to learn more about how to use Chaos Mesh to inject chaos.

## Use workflow to orchestrate multiple chaos experiments

In our experiments, we use Chaos Mesh workflow to orchestrate multiple chaos experiments. Chaos Mesh workflow is a feature that allows users to create a series of chaos experiments and run them in a certain order. In this section, we will introduce how to use Chaos Mesh workflow to orchestrate multiple chaos experiments. For more details, please refer to [Workflow Documentation](https://chaos-mesh.org/docs/create-chaos-mesh-workflow/).

**Step 1:** Choose the task type as <u>Single</u>. Then create a single chaos experiment as above tutorial. 

**Step 2:** Choose the task type as <u>Suspend</u>. Create a suspend task, i.e., a task that pauses the workflow for a specified duration. Then, fill the <u>Duration</u> field with the duration you want to pause the workflow. For example, if you want to pause the workflow for 10 minutes, then you can fill the <u>Duration</u> field with `10m`.

**Step 3:** Repeat the above steps to create more chaos experiments and suspend tasks. 

We provide the workflow yaml files in our [repo](https://github.com/ZhenlanJi/PerfCE/tree/main/config_files/ce). Readers can refer to them for more details.