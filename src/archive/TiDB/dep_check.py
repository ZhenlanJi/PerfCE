
import numpy as np
import pandas as pd
import os
from tensorflow import keras
from dowhy import CausalModel
from causallearn.utils.cit import gsq, chisq
from econml.dml import (
    DML, LinearDML,
    SparseLinearDML,
    CausalForestDML
)
from econml.iv.nnet import DeepIV
from sklearn.linear_model import (
    Lasso, LassoCV, LogisticRegression,
    LogisticRegressionCV, LinearRegression,
    MultiTaskElasticNet, MultiTaskElasticNetCV
)
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from pygraphviz import AGraph
import warnings
from sklearn.exceptions import DataConversionWarning
warnings.filterwarnings(action='ignore', category=DataConversionWarning)
warnings.filterwarnings(action='ignore', category=FutureWarning)
import tensorflow as tf
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3' 
tf.get_logger().setLevel('ERROR')
sess = tf.compat.v1.Session(config=tf.compat.v1.ConfigProto(log_device_placement=True))

def IV_dep_check(temp_df):
    # temp_df=data_df[chaos_attr+[treatment, outcome]]
    data=temp_df.to_numpy()
    for i in range(data.shape[1]-2):
        p=gsq(data, X=i, Y=data.shape[1]-1, conditioning_set=[data.shape[1]-2])
        if p<0.05:
            return True
    return False

with open(os.path.join(os.pardir, "inference", 'noChaos_est.txt'), 'r') as fin:
    origin_gfile = fin.read().splitlines()
origin_dgragh = "digraph {"+' '.join(origin_gfile)+"}"

data_df = pd.read_csv(os.path.join(
    os.pardir, "inference", 'Chaos.csv'))
nodes_list = data_df.columns.to_list()

chaos_df = pd.read_csv(os.path.join(
    os.pardir, "output", 'Chaos.csv'))
chaos_attr = list(map(lambda x: "chaos__"+x, chaos_df.columns[1:]))

graph_edges = np.zeros((len(nodes_list), len(nodes_list)))

# dependency check
dep_dict = {}

for edge in origin_gfile:
    treatment, outcome = edge.strip(';').split(' -> ')
    added_edges = list(map(lambda x: x+" -> "+treatment+';', chaos_attr))

    temp_df = data_df[chaos_attr+[treatment, outcome]]
    dep_dict[treatment+' -> '+outcome] = IV_dep_check(temp_df)

    if origin_gfile.index(edge) % 20 == 0:
        print(origin_gfile.index(edge))

print(dep_dict)
# count value =True in dep_dict
count = 0
for key, value in dep_dict.items():
    if value:
        count += 1

print(count/len(dep_dict))