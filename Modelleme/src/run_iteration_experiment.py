import pandas as pd
import numpy as np
import joblib
import os
import copy
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder, StandardScaler, LabelEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier

from src.config import load_config
from src.data_loader import load_and_merge_data
from src.optimization_niapy import NiapyOptimizer

def evaluate_model(model, X_test, y_test):
    predictions = model.predict(X_test)
    acc = accuracy_score(y_test, predictions)
    f1 = f1_score(y_test, predictions, average='weighted')
    prec = precision_score(y_test, predictions, average='weighted')
    rec = recall_score(y_test, predictions, average='weighted')
    return acc, f1, prec, rec

def run_experiment():
    print("--- Starting Iteration Experiment (50, 100, 150) ---")
    
    # 1. Load Config and Data
    try:
        config = load_config()
        # Enforce Safe & Fast Mode
        config['optimization']['n_jobs'] = 2 
        # Enforce Population 20 (Faster proxy)
        config['optimization']['niapy_params']['population_size'] = 20
        # Enforce CV = 2 (Faster proxy)
        config['optimization']['cv'] = 2
        
        print("Configuration loaded. Enforced n_jobs=2, population_size=20, cv=2.")
    except Exception as e:
        print(f"Error loading config: {e}")
        return

    df = load_and_merge_data(config)
    if df is None:
        print("Data load failed.")
        return

    # 2. Preprocessing (Identical to train.py)
    target_col = config['data'].get('target', 'pi')
    df = df.dropna(subset=[target_col])
    
    X = df.drop(columns=[target_col])
    y = df[target_col]
    
    le = LabelEncoder()
    y_encoded = le.fit_transform(y)
    
    numeric_features = X.select_dtypes(include=['int64', 'float64']).columns
    categorical_features = X.select_dtypes(include=['object', 'category']).columns
    
    numeric_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='median')),
        ('scaler', StandardScaler())
    ])
    
    categorical_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='most_frequent')),
        ('encoder', OneHotEncoder(handle_unknown='ignore'))
    ])
    
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', numeric_transformer, numeric_features),
            ('cat', categorical_transformer, categorical_features)
        ])
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y_encoded, test_size=config['data'].get('test_size', 0.2), 
        random_state=42
    )
    
    print(f"Data prepared. Train shape: {X_train.shape}")
    
    # 3. Experiment Loop
    iterations_to_test = [50, 100, 150,200]
    results = []
    
    base_rf = RandomForestClassifier(random_state=42)
    pipeline_base = Pipeline(steps=[('preprocessor', preprocessor),
                                    ('classifier', base_rf)])
    
    for max_iters in iterations_to_test:
        print(f"\n\n>>> Running Experiment for MAX_ITERS = {max_iters} <<<")
        
        # specific config for this run
        run_config = copy.deepcopy(config)
        run_config['optimization']['niapy_params']['max_iters'] = max_iters
        
        # Ensure deep copy of bounds works for pipeline prefixing
        bounds = run_config['optimization']['niapy_params']['bounds']
        new_bounds = {f'classifier__{k}': v for k, v in bounds.items()}
        run_config['optimization']['niapy_params']['bounds'] = new_bounds
        
        optimizer = NiapyOptimizer(pipeline_base, run_config)
        
        # Optimize
        best_model, best_params = optimizer.optimize(X_train, y_train, algorithm='abc')
        
        # Evaluate
        acc, f1, prec, rec = evaluate_model(best_model, X_test, y_test)
        
        print(f"Result for {max_iters} iters -> Accuracy: {acc:.4f}, F1: {f1:.4f}")
        
        # Save Model
        model_filename = f"reports/best_model_iter{max_iters}.pkl"
        joblib.dump(best_model, model_filename)
        
        results.append({
            'Iterations': max_iters,
            'Accuracy': acc,
            'F1_Score': f1,
            'Precision': prec,
            'Recall': rec,
            'Best_Params': str(best_params)
        })
        
    # 4. Save Results Summary
    results_df = pd.DataFrame(results)
    results_df.to_csv("reports/iteration_experiment_results.csv", index=False)
    
    print("\n\n--- Experiment Completed ---")
    print(results_df[['Iterations', 'Accuracy', 'F1_Score']])

if __name__ == "__main__":
    run_experiment()
