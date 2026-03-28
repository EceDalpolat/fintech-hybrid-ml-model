import logging
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import accuracy_score, classification_report
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder, StandardScaler, LabelEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from src.model import get_model
from src.utils import setup_logging
import pandas as pd
import numpy as np
import joblib
import os
import copy

logger = logging.getLogger(__name__)

def train_model(model, X_train, y_train):
    """
    Train the model.
    """
    logger.info("Training model...")
    model.fit(X_train, y_train)
    logger.info("Training complete.")
    return model

def evaluate_model(model, X_test, y_test, label_encoder=None):
    """
    Evaluate the model.
    """
    logger.info("Evaluating model...")
    predictions = model.predict(X_test)
    accuracy = accuracy_score(y_test, predictions)
    logger.info(f"Model Accuracy: {accuracy:.4f}")
    
    if label_encoder:
        target_names = [str(cls) for cls in label_encoder.classes_]
        report = classification_report(y_test, predictions, target_names=target_names)
    else:
        report = classification_report(y_test, predictions)
    
    logger.info(f"\nClassification Report:\n{report}")
    return accuracy

def build_preprocessor(X):
    """
    Create a preprocessing pipeline based on input data.
    """
    # Identify numerical and categorical columns
    numeric_features = X.select_dtypes(include=['int64', 'float64']).columns
    categorical_features = X.select_dtypes(include=['object', 'category']).columns
    
    logger.info(f"Numerical features: {len(numeric_features)}")
    logger.info(f"Categorical features: {len(categorical_features)}")
    
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
        
    return preprocessor

def train_pipeline(df, config):
    """
    Execute the full training pipeline.
    """
    setup_logging(config.get('logging', {}).get('config_path', 'logging.yaml'))
    
    target_col = config['data'].get('target', df.columns[-1])
    
    if target_col not in df.columns:
        logger.error(f"Target column '{target_col}' not found in dataset.")
        raise ValueError(f"Target column '{target_col}' not found in dataset.")
        
    logger.info(f"Target column: {target_col}")
    
    # Drop rows with missing target
    initial_shape = df.shape
    df = df.dropna(subset=[target_col])
    logger.info(f"Dropped {initial_shape[0] - df.shape[0]} rows with missing target. New shape: {df.shape}")
    
    # Separate Features and Target
    X = df.drop(columns=[target_col])
    y = df[target_col]
    
    # Encode Target
    logger.info("Encoding target variable...")
    le = LabelEncoder()
    y_encoded = le.fit_transform(y)
    logger.info(f"Target classes: {le.classes_}")
    
    # Preprocessor
    preprocessor = build_preprocessor(X)
        
    # Split data
    test_size = config['data'].get('test_size', 0.2)
    random_state = config['data'].get('random_state', 42)
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y_encoded, test_size=test_size, random_state=random_state
    )
    
    logger.info(f"Train set size: {X_train.shape}, Test set size: {X_test.shape}")
    
    # Optimization or Training
    optimization_config = config.get('optimization', {})
    
    if optimization_config.get('enabled', False):
        # Accuracy Push: Using full data for optimization as requested
        return run_optimization(X_train, y_train, X_test, y_test, preprocessor, config, le)
    else:
        return run_single_training(X_train, y_train, X_test, y_test, preprocessor, config, le)

def run_optimization(X_train, y_train, X_test, y_test, preprocessor, config, le):
    method = config['optimization'].get('method', 'grid')
    logger.info(f"--- Starting Optimization using method: {method} ---")
    
    base_model = get_model(config.get('model', {}))
    pipeline_base = Pipeline(steps=[('preprocessor', preprocessor),
                                    ('classifier', base_model)])

    if method in ['pso', 'abc']:
            from src.optimization_niapy import NiapyOptimizer
            
            # Deep copy config to prefix bounds
            config_opt = copy.deepcopy(config)
            if 'niapy_params' in config_opt['optimization'] and 'bounds' in config_opt['optimization']['niapy_params']:
                bounds = config_opt['optimization']['niapy_params']['bounds']
                new_bounds = {f'classifier__{k}': v for k, v in bounds.items()}
                config_opt['optimization']['niapy_params']['bounds'] = new_bounds
            
            optimizer = NiapyOptimizer(pipeline_base, config_opt)
            best_model, best_params = optimizer.optimize(X_train, y_train, algorithm=method)
            
    else:
        # Default Grid Search
        param_grid = config['optimization'].get('param_grid', {})
        grid_search = GridSearchCV(estimator=pipeline_base, param_grid=param_grid, 
                                    cv=config['optimization'].get('cv', 3),
                                    n_jobs=config['optimization'].get('n_jobs', -1),
                                    verbose=config['optimization'].get('verbose', 2),
                                     scoring='f1_weighted')
        
        logger.info("Running Grid Search...")
        grid_search.fit(X_train, y_train)
        best_model = grid_search.best_estimator_
        logger.info(f"Best CV Score: {grid_search.best_score_:.4f}")

    # Evaluate Best Model
    logger.info("--- Evaluating Best Model ---")
    evaluate_model(best_model, X_test, y_test, label_encoder=le)
    
    # Save Model
    save_model(best_model, "reports/best_model.pkl")
    return best_model

def run_single_training(X_train, y_train, X_test, y_test, preprocessor, config, le):
    logger.info("--- Training Single Model ---")
    model = get_model(config.get('model', {}))
    pipeline = Pipeline(steps=[('preprocessor', preprocessor),
                                ('classifier', model)])
    
    train_model(pipeline, X_train, y_train)
    evaluate_model(pipeline, X_test, y_test, label_encoder=le)
    return pipeline

def save_model(model, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    joblib.dump(model, path)
    logger.info(f"Model saved to {path}")
