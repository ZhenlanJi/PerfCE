import numpy as np
import pandas as pd
import os
import argparse
import pickle as pkl
from scipy import stats
from tensorflow import keras
import tensorflow as tf
import matplotlib.pyplot as plt


import warnings
from sklearn.exceptions import DataConversionWarning
warnings.filterwarnings(action='ignore', category=DataConversionWarning)
warnings.filterwarnings(action='ignore', category=FutureWarning)

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
tf.get_logger().setLevel('ERROR')
tf.config.set_visible_devices([], 'GPU')


def find_parents(node_name, edge_list):
    parents = []
    for edge in edge_list:
        treatment, outcome = edge.strip(';').split(' -> ')
        if node_name == outcome:
            parents.append(treatment)
    return parents


def deepiv_ate(deepiv_model, X=None, T0=0, T1=1):
    if np.ndim(T0) == 0:
        T0 = np.repeat(T0, 1 if X is None else np.shape(X)[0])
    if np.ndim(T1) == 0:
        T1 = np.repeat(T1, 1 if X is None else np.shape(X)[0])
    # if X is None:
    #     print('No data provided. Returning NaN.')
    #     return np.nan
    return (deepiv_model.predict([T1, X]) - deepiv_model.predict([T0, X])).reshape(-1, 1)


def for_estimation(node_name, value):
    return (value - train_df.get(node_name).mean()) / train_df.get(node_name).std()


def one_tailed_pValue(distribution, value):
    if distribution is None:
        return 0.5 if value == 0 else 0
    cdf = distribution.cdf(value)
    if cdf > 0.5:
        return 1 - cdf
    else:
        return cdf


def calc_ate(edge, t0, t1):
    if edge in dml_model_list:
        # read pickle file
        with open(os.path.join(model_file, "dml", edge+".pkl"), 'rb') as fin:
            dml_model_config = pkl.load(fin)

        X_now = [(current_log.get(c) - train_df.get(c).mean()) / train_df.get(c).std()
                 for c in dml_model_config['confounder']]
        X_now = np.array(X_now).reshape(1, -1)

        ate = dml_model_config['est'].ate(
            X=X_now, T0=t0, T1=t1).mean()

    elif edge in deepiv_model_list:
        deepiv_model = keras.models.load_model(
            os.path.join(model_file, "deepiv", edge))
        # with open(os.path.join(model_file, "deepiv", edge, "causal.pkl"), 'rb') as fin:
        #     deepiv_model_config = pkl.load(fin)

        ate = deepiv_ate(deepiv_model, X=np.zeros((1, 1)), T0=t0,
                         T1=t1).mean()
    return ate


def final_effect(trace_list, treat_node, t0, t1):
    alt_effects = []
    for trace in trace_list:
        if trace[0] == treat_node:
            if trace[1] == start_node:
                return calc_ate(trace[0]+'-'+trace[1], t0, t1)
            else:
                effect = calc_ate(trace[0]+'-'+trace[1], t0, t1)
                next_node = trace[1]
                if current_log.get(next_node) is None:
                    alt_effects.append(0)
                else:
                    t1_next = for_estimation(next_node, current_log.get(next_node))
                    t0_next = t1_next-effect
                    alt_effects.append(final_effect(
                        trace_list, next_node, t0_next, t1_next))
    # print(treat_node,alt_effects)
    return sum(alt_effects)


def main():
    pass

if __name__ == '__main__':
    main()
