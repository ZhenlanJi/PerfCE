import tensorflow as tf
import numpy as np
import pandas as pd
from datetime import datetime
import os
import argparse
import dill as pkl
from pygraphviz import AGraph
import warnings
from tensorflow import keras
from dowhy import CausalModel
from causallearn.utils.cit import (
    gsq,
    chisq
)
from econml.dml import (
    DML, LinearDML,
    SparseLinearDML,
    CausalForestDML
)
from econml.iv.nnet import DeepIV
from sklearn.linear_model import (
    Lasso, LassoCV,
    LogisticRegression,
    LogisticRegressionCV,
    LinearRegression,
    MultiTaskElasticNet,
    MultiTaskElasticNetCV
)
from sklearn.preprocessing import PolynomialFeatures
from sklearn.ensemble import RandomForestRegressor
from sklearn.exceptions import DataConversionWarning


def main(args):
    keras_fit_options = {
        "verbose": 0,
        "batch_size": 512,
        "epochs": 30,
        "validation_split": 0.1,
        "callbacks": [keras.callbacks.EarlyStopping(patience=2, restore_best_weights=True)]}

    with open(args.causal_graph, 'r') as fin:
        origin_gfile = fin.read().splitlines()
    data_df = pd.read_csv(args.collected_data)

    chaos_df = pd.read_csv(args.workflow_data)
    chaos_attr = list(map(lambda x: "chaos__"+x, chaos_df.columns[1:]))
    chaos_df.columns = ['timestamp']+chaos_attr
    # merge chaos_df into data_df
    data_df = pd.merge(data_df, chaos_df, on='timestamp', how='outer')
    # important!
    data_df = (data_df - data_df.mean()) / (data_df.std())
    data_df.fillna(0, inplace=True)

    for edge in origin_gfile:
        treatment, outcome = edge.strip(';').split(' -> ')
        added_edges = list(map(lambda x: x+" -> "+treatment+';', chaos_attr))
        temp_graph = "digraph {" + \
            ' '.join(origin_gfile) + ''.join(added_edges) + "}"

        model = CausalModel(
            data=data_df,
            treatment=[treatment, ],
            outcome=[outcome, ],
            graph=temp_graph
        )
        identified_estimand = model.identify_effect(
            proceed_when_unidentifiable=True)

        if identified_estimand.get_backdoor_variables():
            # There exist confounders.
            # Assume unobserved confounders' effect can be ignored
            # Use double machine learning to identify the effect
            Y_train = data_df[outcome].to_numpy()
            T_train = data_df[treatment].to_numpy()
            X_train = data_df[identified_estimand.get_backdoor_variables()
                              ].to_numpy()
            if X_train.shape[1] < 5:
                est = LinearDML(model_y=RandomForestRegressor(),
                                model_t=RandomForestRegressor(),
                                random_state=0)
            else:
                est = SparseLinearDML(model_y=RandomForestRegressor(),
                                      model_t=RandomForestRegressor(),
                                      featurizer=PolynomialFeatures(degree=3),
                                      random_state=0)
            est.fit(Y_train, T_train, X=X_train, W=None)

            model_config = {
                "est": est,
                "treatment": treatment,
                "outcome": outcome,
                "confounder": identified_estimand.get_backdoor_variables(),
                "iv": None
            }
            model_file_path = os.path.join(
                args.output_dir, "dml", treatment+'-'+outcome+'.pkl')
            with open(model_file_path, 'wb') as fout:
                pkl.dump(model_config, fout)

        elif identified_estimand.get_instrumental_variables():
            # There is no confounders.
            # Assume unobserved confounders' effect can not be ignored
            # Use DeepIV to identify the effect

            Y_train = data_df[outcome].to_numpy()
            T_train = data_df[treatment].to_numpy()
            Z_train = data_df[identified_estimand.get_instrumental_variables()
                              ].to_numpy()
            X_train = np.zeros((Y_train.shape[0], 1))
            # check X_train contain NaN
            if np.isnan(Z_train).any() or np.isnan(Y_train).any() or np.isnan(T_train).any():
                print(f"There is NaN in edge {edge}!")
            tmodel_width = Z_train.shape[1]+1
            rmodel_width = 2

            treatment_model = keras.Sequential([keras.layers.Dense(128, activation='relu', input_shape=(tmodel_width,)),
                                                keras.layers.Dropout(0.17),
                                                keras.layers.Dense(
                                                    64, activation='relu'),
                                                keras.layers.Dropout(0.17),
                                                keras.layers.Dense(
                                                    32, activation='relu'),
                                                keras.layers.Dropout(0.17)])

            response_model = keras.Sequential([keras.layers.Dense(128, activation='relu', input_shape=(rmodel_width,)),
                                               keras.layers.Dropout(0.17),
                                               keras.layers.Dense(
                                                   64, activation='relu'),
                                               keras.layers.Dropout(0.17),
                                               keras.layers.Dense(
                                                   32, activation='relu'),
                                               keras.layers.Dropout(0.17),
                                               keras.layers.Dense(1)])

            deepIvEst = DeepIV(n_components=10,  # number of gaussians in our mixture density network
                               m=lambda z, x: treatment_model(
                                   keras.layers.concatenate([z, x])),  # treatment model
                               h=lambda t, x: response_model(
                                   keras.layers.concatenate([t, x])),  # response model
                               n_samples=1,  # number of samples to use to estimate the response
                               use_upper_bound_loss=False,  # whether to use an approximation to the true loss
                               # number of samples to use in second estimate of the response (to make loss estimate unbiased)
                               n_gradient_samples=1,
                               optimizer='adam',  # Keras optimizer to use for training - see https://keras.io/optimizers/
                               first_stage_options=keras_fit_options,  # options for training treatment model
                               second_stage_options=keras_fit_options)  # options for training response model
            deepIvEst.fit(Y=Y_train, T=T_train, X=X_train, Z=Z_train)

            deepIvEst._effect_model.save(os.path.join(
                args.output_dir, "deepiv", treatment+'-'+outcome))

            model_config = {
                "est": None,
                "treatment": treatment,
                "outcome": outcome,
                "confounder": None,
                "iv": identified_estimand.get_instrumental_variables()
            }
            model_file_path = os.path.join(
                args.output_dir, "deepiv", treatment+'-'+outcome, 'causal.pkl')
            with open(model_file_path, 'wb') as fout:
                pkl.dump(model_config, fout)

        else:
            print("Exception!")
            print(edge)
            break

        if origin_gfile.index(edge) % 20 == 0:
            print(f"Progress: {origin_gfile.index(edge)}/{len(origin_gfile)}")


if __name__ == "__main__":
    # Parse arguments
    parser = argparse.ArgumentParser(description='Collect data')
    parser.add_argument("--causal_graph", type=str,
                        help="Path to causal graph file (should be txt file).")
    parser.add_argument("--collected_data", type=str,
                        help="Path to collected data file (should be csv file).")
    parser.add_argument("--workflow_data", type=str,
                        help="Path to Chaos Mesh workflow data file (should be csv file).")
    parser.add_argument("--output_dir", type=str,
                        help="Path to output directory")
    args = parser.parse_args()

    start_time = datetime.now()
    warnings.filterwarnings(action='ignore', category=DataConversionWarning)
    warnings.filterwarnings(action='ignore', category=FutureWarning)
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
    tf.get_logger().setLevel('ERROR')
    sess = tf.compat.v1.Session(
        config=tf.compat.v1.ConfigProto(log_device_placement=True))

    main(args)

    end_time = datetime.now()
    print('\nDuration: {}'.format(end_time - start_time))
