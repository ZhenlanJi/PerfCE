---
layout: page
title: Parse Chaos
parent: Utilities
nav_order: 2
---

# Parse Chaos Mesh Workflow

Because we use Chaos Mesh workflow to orchestrate multiple chaos experiments, 
we need to parse the workflow config file to get the information of each experiment. 
You can find the code for parsing workflow in [parse_chaos.py](https://github.com/ZhenlanJi/PerfCE/blob/main/src/parse_chaos.py). 
You can directly execute the script to parse the workflow config file.

**Usage:**

```bash
python parse_chaos.py [-h] [--database {mysql,tidb}]
                      [--collect_start COLLECT_START]
                      [--collect_end COLLECT_END]
                      [--chaos_start CHAOS_START]
                      [--chaos_exp_duration CHAOS_EXP_DURATION]
                      [--chaos_suspend_duration CHAOS_SUSPEND_DURATION]
                      [--chaos_config CHAOS_CONFIG]
                      [--output_file OUTPUT_FILE]
```

Here is the arguments table for the script:


| Argument               | Description                                                    | Special Remark                                                                                                                                |
| :--------------------- | :------------------------------------------------------------- | :-------------------------------------------------------------------------------------------------------------------------------------------- |
| database               | Select which database to be collected.                         | `str`, only two choice: `mysql` and `tidb`.                                                                                                   |
| collect_start          | Start time for data collection.                                | `int`, should be Unix timestamp. The time used in `collect_data.py`                                                                           |
| collect_end            | End time for data collection.                                  | `int`, should be Unix timestamp.                                                                                                              |
| chaos_start            | Start time for chaos workflow.                                 | `int`, should be Unix timestamp.                                                                                                              |
| chaos_exp_duration     | Duration (seconds) of a single chaos experiment.               | `int`.                                                                                                                                        |
| chaos_suspend_duration | Duration (minutes) of interval between experiments.            | `int`.                                                                                                                                        |
| chaos_config           | Path to Chaos Mesh workflow config file (should be yaml file). | `str`, i.e., workflow config, find it in our [repo](https://github.com/ZhenlanJi/PerfCE/tree/main/config_files/ce).                           |
| output_file            | Path to output file (should be csv file).                      | `str`, this file and combined.csv outputted by `collect_data.py` will be used in [causal estimation](/PerfCE/pages/utilities/estimation.html) |
