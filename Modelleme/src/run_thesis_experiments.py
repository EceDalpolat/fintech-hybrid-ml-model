import logging
import pandas as pd
import numpy as np
import os
import copy
import json
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score, classification_report
from src.config import load_config
from src.data_loader import load_and_merge_data
from src.train import build_preprocessor, train_model, evaluate_model
from src.model import get_model
from src.optimization_niapy import NiapyOptimizer
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import joblib

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def run_experiment_suite(config_path="config.yaml"):
    # 1. Load Config
    config = load_config(config_path)
    
    # 2. Load Data
    df = load_and_merge_data(config)
    if df is None:
        logger.error("Failed to load data.")
        return
    
    target_col = config['data'].get('target', 'pi')
    df = df.dropna(subset=[target_col])
    
    X = df.drop(columns=[target_col])
    y = df[target_col]
    
    # Encode target
    le = LabelEncoder()
    y_encoded = le.fit_transform(y)
    
    # Split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y_encoded, test_size=0.2, random_state=42
    )
    
    # Preprocessor
    preprocessor = build_preprocessor(X)
    
    # Define Methods to compare
    methods = ['baseline', 'pso', 'abc', 'abc-pso']
    results = []
    
    # Bounds for optimization (from config)
    bounds = config['optimization']['niapy_params']['bounds']
    prefixed_bounds = {f'classifier__{k}': v for k, v in bounds.items()}
    
    for method in methods:
        logger.info(f"\n{'='*20}\nRunning Method: {method.upper()}\n{'='*20}")
        
        base_model = get_model(config['model'])
        pipeline = Pipeline(steps=[('preprocessor', preprocessor),
                                    ('classifier', base_model)])
        
        if method == 'baseline':
            # Train with default/config params
            pipeline.fit(X_train, y_train)
            best_model = pipeline
            best_params = config['model'].get('params', {})
        else:
            # Run optimization
            opt_config = copy.deepcopy(config)
            opt_config['optimization']['niapy_params']['bounds'] = prefixed_bounds
            
            optimizer = NiapyOptimizer(pipeline, opt_config)
            best_model, best_params = optimizer.optimize(X_train, y_train, algorithm=method)
            
        # Evaluate
        preds = best_model.predict(X_test)
        
        metrics = {
            'method': method,
            'accuracy': accuracy_score(y_test, preds),
            'f1_weighted': f1_score(y_test, preds, average='weighted'),
            'precision_weighted': precision_score(y_test, preds, average='weighted', zero_division=0),
            'recall_weighted': recall_score(y_test, preds, average='weighted', zero_division=0),
            'best_params': str(best_params)
        }
        results.append(metrics)
        
        # Save model for each method
        model_save_path = f"reports/model_{method}.pkl"
        os.makedirs("reports", exist_ok=True)
        joblib.dump(best_model, model_save_path)
        
    # Final Summary Table
    results_df = pd.DataFrame(results)
    logger.info("\nFinal Experiment Results Summary:")
    logger.info("\n" + results_df.drop(columns=['best_params']).to_string(index=False))
    
    # Export to JSON for plotting
    results_df.to_json("reports/experiment_results.json", orient='records', indent=4)
    logger.info("\nResults saved to reports/experiment_results.json")

if __name__ == "__main__":
    run_experiment_suite()
