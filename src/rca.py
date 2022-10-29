from cusum import *

from os.path import (
    abspath,
    dirname,
)
import numpy as np
import pandas as pd
import argparse
import os
import pickle as pkl
from datetime import datetime
from scipy import stats
from tensorflow import keras
import tensorflow as tf
import matplotlib.pyplot as plt
import networkx as nx
from pygraphviz import AGraph
import warnings
from sklearn.exceptions import DataConversionWarning
warnings.filterwarnings(action='ignore', category=DataConversionWarning)
warnings.filterwarnings(action='ignore', category=FutureWarning)

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
tf.get_logger().setLevel('ERROR')
tf.config.set_visible_devices([], 'GPU')
# sess = tf.compat.v1.Session(
#     config=tf.compat.v1.ConfigProto(log_device_placement=True))


def for_estimation(node_name, value, train_df):
    if train_df[node_name].std() == 0:
        return value-value
    else:
        return (value - train_df[node_name].mean()) / train_df[node_name].std()


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


def calc_ate(edge, t0, t1, train_df, model_dir):
    if edge in dml_model_list:
        # read pickle file
        with open(os.path.join(model_dir, "dml", edge+".pkl"), 'rb') as fin:
            dml_model_config = pkl.load(fin)

        X_now = [(current_log.get(c) - train_df.get(c).mean()) / train_df.get(c).std()
                 for c in dml_model_config['confounder']]
        X_now = np.array(X_now).reshape(1, -1)

        ate = dml_model_config['est'].ate(
            X=X_now, T0=t0, T1=t1).mean()

    elif edge in deepiv_model_list:
        deepiv_model = keras.models.load_model(
            os.path.join(model_dir, "deepiv", edge))
        # with open(os.path.join(model_file, "deepiv", edge, "causal.pkl"), 'rb') as fin:
        #     deepiv_model_config = pkl.load(fin)

        ate = deepiv_ate(deepiv_model, X=np.zeros((1, 1)), T0=t0,
                         T1=t1).mean()
    return ate


def counter_factual(DG, sorted_nodes, treat_node_idx, normal_df, train_df, model_dir):
    treat_node = sorted_nodes[treat_node_idx]
    effect_dict = {}

    if treat_node in normal_df.columns:
        t0 = for_estimation(treat_node, normal_df[treat_node].mean(), train_df)
    else:
        t0 = for_estimation(treat_node, 0, train_df)

    t1 = for_estimation(treat_node, current_log[treat_node], train_df)
    for s in DG.successors(treat_node):
        edge = treat_node+'-'+s
        effect_dict[edge] = calc_ate(
            edge, t0, t1,
            train_df, model_dir)

    for i in range(treat_node_idx+1, len(sorted_nodes)-1):
        node = sorted_nodes[i]
        if current_log.get(node) is None:
            for s in DG.successors(node):
                edge = node+'-'+s
                effect_dict[edge] = 0
        else:
            temp_t1 = for_estimation(node, current_log[node], train_df)

            temp_effect = 0
            for p in DG.predecessors(node):
                edge = p+'-'+node
                if effect_dict.get(edge) is not None:
                    temp_effect += effect_dict[edge]
            temp_t0 = temp_t1-temp_effect

            for s in DG.successors(node):
                edge = node+'-'+s
                effect_dict[edge] = calc_ate(
                    edge, temp_t0, temp_t1,
                    train_df, model_dir
                )
    ret_effect = 0
    for p in DG.predecessors(sorted_nodes[-1]):
        edge = p+'-'+sorted_nodes[-1]
        if effect_dict.get(edge) is not None:
            ret_effect += effect_dict[edge]
        else:
            ret_effect += 0
    return ret_effect


def dfs_cause(DG, node, visited, test_df):
    """
    This function reproduce CauseInfer
    """
    visited.add(node)
    isAnomaly = False
    if node in current_log:
        x = test_df[selected_node][(test_df["timestamp"] >= observed_time-180) &
                                   (test_df["timestamp"] <= observed_time+120)]
        x = (x-x.min())/(x.max()-x.min())
        std = x.std()
        for i in range(3, 6):
            res, _, _, _ = detect_cusum(x[0:60], i/10, 0, True, False)
            if res.shape[0] == 0:
                res_1, _, _, _ = detect_cusum(x[120:180], i/10, 0, True, False)
                if res_1.shape[0] != 0:
                    isAnomaly = True
                break
    if isAnomaly:
        for predecessor in DG.predecessors(node):
            if predecessor not in visited:
                visited.union(dfs_cause(DG, predecessor, visited, test_df))
    return visited


def main(args):
    global dml_model_list, deepiv_model_list, current_log, observed_time, selected_node
    observed_time = args.observed_time
    selected_node = args.selected_node

    train_df = pd.read_csv(args.train_data)
    test_df = pd.read_csv(args.test_data)
    nodes_list = train_df.columns.to_list()
    with open(args.causal_graph, 'r') as fin:
        origin_edges = fin.read().splitlines()
    dml_model_list = list(map(lambda x: x.split(
        '.')[0], os.listdir(os.path.join(args.model_dir, "dml"))))
    deepiv_model_list = os.listdir(os.path.join(args.model_dir, "deepiv"))

    # slice normal_df from normal_star to normal_stop
    normal_df = test_df.loc[(test_df['timestamp'] >= args.normal_start) & (
        test_df['timestamp'] < args.normal_end)]
    current_log = test_df[test_df["timestamp"]
                          == args.abnormal_time].to_dict('list')
    current_log = {k: v[0] for k, v in current_log.items()}

    if selected_node not in nodes_list:
        print("Node not found")
        exit(1)

    start_data = train_df[selected_node].to_numpy()
    # start_data = (start_data-start_data.min())/(start_data.max()-start_data.min())
    start_data = for_estimation(selected_node, start_data, train_df)
    # params = stats.norm.fit(start_data)
    # node_distribution = stats.norm(*params)
    node_distribution = stats.gaussian_kde(start_data)
    fact_start = for_estimation(
        selected_node, current_log[selected_node], train_df)
    fact_PDF = node_distribution.pdf(fact_start)

    # generate DiGraph
    node_point = 0
    visit_list = [selected_node, ]
    trace_list = []
    causes = {}

    while(True):
        if node_point >= len(visit_list):
            # print("No more node. Done!")
            break
        # print("Try to find the parent of {}".format(visit_list[node_point]))
        parents = find_parents(visit_list[node_point], origin_edges)
        if len(parents) > 0:
            for parent in parents:
                if parent not in visit_list:
                    visit_list.append(parent)
                trace_list.append((parent, visit_list[node_point]))
        node_point += 1

    DG = nx.DiGraph()
    DG.add_edges_from(trace_list)
    sorted_nodes = list(nx.topological_sort(DG))

    if args.method == "PerfCE":
        for i in range(len(sorted_nodes)-1):
            effect = counter_factual(
                DG, sorted_nodes, i,
                normal_df, train_df,
                args.model_dir
            )
            counter_start = fact_start-effect
            counter_PDF = node_distribution.pdf(counter_start)
            causes[sorted_nodes[i]] = (counter_PDF-fact_PDF, effect)
            if i % 10 == 0:
                # break
                print(f"{i}/{len(sorted_nodes)} has been done")

        sorted_causes = dict(
            sorted(causes.items(), key=lambda item: item[1][0], reverse=True))
        for k, v in sorted_causes.items():
            print(v, k)
    elif args.method == "cause_infer":
        cause_infer = dfs_cause(
            DG, selected_node, set(), test_df
        )
        # print items in sorted_nodes with index
        for i in range(len(sorted_nodes)):
            if sorted_nodes[i] in cause_infer:
                print(sorted_nodes[i])
            if i >= 5:
                break
    else:
        print("Method not found")
        exit(1)


if __name__ == "__main__":
    # Parse arguments
    parser = argparse.ArgumentParser(description='Collect data')
    parser.add_argument("--causal_graph", type=str,
                        help="Path to causal graph file (should be txt file).")
    parser.add_argument("--train_data", type=str,
                        help="Path to training data file (should be csv file).")
    parser.add_argument("--test_data", type=str,
                        help="Path to test data file (should be csv file).")
    parser.add_argument("--model_dir", type=str,
                        help="Path to learned model directory")
    parser.add_argument("--normal_start", type=int,
                        help="Start time for database's normal performance during test (UNIX Timestamp)")
    parser.add_argument("--normal_end", type=int,
                        help="End time for database's normal performance during test (UNIX Timestamp)")
    parser.add_argument("--abnormal_time", type=int,
                        help="Time for database's abnormal performance during test (UNIX Timestamp)")
    parser.add_argument("--selected_node", type=str,
                        help="Node to be explained")
    parser.add_argument("--method", type=str, choices=["PerfCE", "cause_infer"],
                        default='PerfCE', help="Method to be used")
    args = parser.parse_args()

    start_time = datetime.now()

    main(args)

    end_time = datetime.now()
    print('\nDuration: {}'.format(end_time - start_time))
