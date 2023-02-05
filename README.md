# PerfCE

[![Docs](https://badgen.net/badge/color/latest/blue?label=Documentation)](https://zhenlanji.github.io/PerfCE/)

This repository belongs to our submitted manuscript:
> PerfCE: Performance Debugging on Databases with Chaos Engineering-Enhanced Causality Analysis

You can find the code for our paper in this repository.

**Documentation**: Please see this webpage: https://zhenlanji.github.io/PerfCE/

## Introduction

This work identifies novel usage of chaos engineering on helping developers diagnose performance anomalies in databases. Our
presented framework, PerfCE, comprises an offline phase and an
online phase. The offline phase learns the statistical models of the
target database system, whilst the online phase diagnoses the root
cause of monitored performance anomalies on the fly. During the offline phase, PerfCE leverages both passive observations and 
proactive chaos experiments to constitute accurate causal graphs and
structural equation models (SEMs). When observing performance
anomalies during the online phase, causal graphs enable qualitative
root cause identification (e.g., high CPU usage) and SEMs enable
quantitative counterfactual analysis (e.g., determining “when CPU
usage is reduced to 45%, performance returns to normal”). PerfCE
notably outperforms prior works on common synthetic datasets,
and our evaluation on real-world datasets, mySQL and TiDB, shows
that PerfCE is highly accurate and moderately expensive.



## Dependency

```
rstr
numpy
pandas
scipy
sklearn
pygraphviz
networkx
tensorflow
dowhy
causallearn
econml
```


## Human evaluation

We use human evaluation to compare PerfCE and several sota methods. 
<!-- Details of human evaluation is presented in `Root Cause Analysis on MySQL(1-7).xlsx` -->
Questionnaire is presented in `./questionnaire.pdf`.
Participants' answers are presented in `./answers.pdf`.
## Causal graph

We present the causal graph learned by PerfCE in `./causal_graph`.
## Model Structure

### DML
1. If the dimension of confounder is less than 5:
    ```python
    LinearDML(
        model_y=RandomForestRegressor(),
        model_t=RandomForestRegressor(),
        random_state=0)
    ```
2. If the dimension of confounder is equal or more than 5:
    ```py3
    SparseLinearDML(
        model_y=RandomForestRegressor(),
        model_t=RandomForestRegressor(),
        featurizer=PolynomialFeatures(degree=3),
        random_state=0)
    ```

### DeepIV
1. Treatment model
   ```
   _________________________________________________________________
    Layer (type)                Output Shape              Param #   
    =================================================================
    dense (Dense)               (None, 128)               384       
                                                                    
    dropout (Dropout)           (None, 128)               0         
                                                                    
    dense_1 (Dense)             (None, 64)                8256      
                                                                    
    dropout_1 (Dropout)         (None, 64)                0         
                                                                    
    dense_2 (Dense)             (None, 32)                2080      
                                                                    
    dropout_2 (Dropout)         (None, 32)                0         
                                                                    
    =================================================================
    Total params: 10,720
    Trainable params: 10,720
    Non-trainable params: 0
    _________________________________________________________________
   ```
2. Response Model
   ```
    Layer (type)                Output Shape              Param #   
    =================================================================
    dense_4 (Dense)             (None, 128)               384       
                                                                    
    dropout_4 (Dropout)         (None, 128)               0         
                                                                    
    dense_5 (Dense)             (None, 64)                8256      
                                                                    
    dropout_5 (Dropout)         (None, 64)                0         
                                                                    
    dense_6 (Dense)             (None, 32)                2080      
                                                                    
    dropout_6 (Dropout)         (None, 32)                0         
                                                                    
    dense_7 (Dense)             (None, 1)                 33        
                                                                    
    =================================================================
    Total params: 10,753
    Trainable params: 10,753
    Non-trainable params: 0
    _________________________________________________________________
   ```