"""
Thesis Experiment Suite
Compares four Random Forest variants on the payment-preference dataset:
  1. RF – Baseline (default params)
  2. RF + PSO
  3. RF + ABC
  4. RF + ABC-PSO (Hybrid)

Records accuracy, F1-weighted, and optimisation convergence history.
"""
import logging
import pandas as pd
import numpy as np
import os
import copy
import json
import time

from sklearn.metrics import (accuracy_score, f1_score,
                              precision_score, recall_score,
                              classification_report, balanced_accuracy_score)
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import joblib

from src.config import load_config
from src.data_loader import load_and_merge_data
from src.train import build_preprocessor, train_model, evaluate_model, create_pipeline
from src.model import get_model
from src.optimization_niapy import NiapyOptimizer

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
def run_experiment_suite(config_path="config.yaml"):
    # 1. Config
    config = load_config(config_path)

    # 2. Data
    df = load_and_merge_data(config)
    if df is None:
        logger.error("Failed to load data.")
        return

    target_col = config['data'].get('target', 'pi')
    df = df.dropna(subset=[target_col])

    X = df.drop(columns=[target_col])
    y = df[target_col]

    le = LabelEncoder()
    y_encoded = le.fit_transform(y)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded
    )

    preprocessor = build_preprocessor(X)

    bounds = config['optimization']['niapy_params']['bounds']
    prefixed_bounds = {f'classifier__{k}': v for k, v in bounds.items()}

    methods = ['baseline', 'pso', 'abc', 'abc-pso']
    results = []
    # convergence_data: { method: list[float] }  (best CV score per iter)
    convergence_data = {}

    os.makedirs("reports", exist_ok=True)

    for method in methods:
        method_start_time = time.time()
        logger.info(f"\n{'='*20}\nMethod: {method.upper()}\n{'='*20}")

        base_model = get_model(config['model'])
        pipeline   = create_pipeline(preprocessor, base_model)

        iter_history = []

        if method == 'baseline':
            pipeline.fit(X_train, y_train)
            best_model  = pipeline
            best_params = config['model'].get('params', {})

        else:
            opt_config = copy.deepcopy(config)
            opt_config['optimization']['niapy_params']['bounds'] = prefixed_bounds

            optimizer = NiapyOptimizer(pipeline, opt_config)
            # optimizer.optimize now returns (model, params, iter_history)
            best_model, best_params, iter_history = optimizer.optimize(
                X_train, y_train, algorithm=method
            )

        convergence_data[method] = iter_history

        preds = best_model.predict(X_test)
        acc   = accuracy_score(y_test, preds)
        bal_acc = balanced_accuracy_score(y_test, preds)
        f1w   = f1_score(y_test, preds, average='weighted')
        prec  = precision_score(y_test, preds, average='weighted', zero_division=0)
        rec   = recall_score(y_test, preds, average='weighted', zero_division=0)

        method_end_time = time.time()
        duration_sec = method_end_time - method_start_time
        
        logger.info(f"Accuracy     : {acc:.4f}")
        logger.info(f"Balanced Acc : {bal_acc:.4f}")
        logger.info(f"F1 (weighted): {f1w:.4f}")
        logger.info(f"Precision    : {prec:.4f}")
        logger.info(f"Recall       : {rec:.4f}")
        logger.info(f"Time (sec)   : {duration_sec:.2f}")

        results.append({
            'method':               method,
            'duration_sec':         duration_sec,
            'accuracy':             acc,
            'balanced_accuracy':    bal_acc,
            'f1_weighted':          f1w,
            'precision_weighted':   prec,
            'recall_weighted':      rec,
            'best_params':          str(best_params),
        })

        joblib.dump(best_model, f"reports/model_{method}.pkl")
        logger.info(f"Model saved → reports/model_{method}.pkl")

    # Persist results
    results_df = pd.DataFrame(results)
    logger.info("\nFinal Summary:")
    logger.info("\n" + results_df.drop(columns=['best_params']).to_string(index=False))

    results_df.to_json("reports/experiment_results.json", orient='records', indent=4)
    logger.info("Results → reports/experiment_results.json")

    with open("reports/convergence_rf.json", 'w') as f:
        json.dump(convergence_data, f, indent=4)
    logger.info("Convergence data → reports/convergence_rf.json")

    return results_df, convergence_data


# ---------------------------------------------------------------------------
if __name__ == "__main__":
    run_experiment_suite()
