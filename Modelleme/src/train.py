import logging
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import accuracy_score, classification_report
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder, RobustScaler, LabelEncoder
from sklearn.compose import ColumnTransformer
from sklearn.base import BaseEstimator, TransformerMixin
from imblearn.pipeline import Pipeline
from imblearn.over_sampling import SMOTE
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import TargetEncoder
from src.model import get_model
from src.utils import setup_logging
import pandas as pd
import numpy as np
import joblib
import os
import copy

logger = logging.getLogger(__name__)

class RareEncoder(BaseEstimator, TransformerMixin):
    """
    Groups infrequent categories into an 'Other' category.
    """
    def __init__(self, tol=0.05, replace_with='Rare'):
        self.tol = tol
        self.replace_with = replace_with
        self.rare_labels_ = {}

    def fit(self, X, y=None):
        X = pd.DataFrame(X)
        for col in X.columns:
            # Calculate frequency
            t = X[col].value_counts(normalize=True)
            # Keep labels that are above tolerance
            if not t[t < self.tol].empty:
                self.rare_labels_[col] = [label for label in t[t < self.tol].index]
            else:
                self.rare_labels_[col] = []
        return self

    def transform(self, X):
        X = pd.DataFrame(X).copy()
        for col in X.columns:
            if col in self.rare_labels_ and self.rare_labels_[col]:
                X[col] = X[col].replace(self.rare_labels_[col], self.replace_with)
        return X

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
    Evaluate the model and return metrics.
    """
    logger.info("Evaluating model...")
    predictions = model.predict(X_test)
    
    from sklearn.metrics import accuracy_score, precision_recall_fscore_support
    
    acc = accuracy_score(y_test, predictions)
    prec, rec, f1, _ = precision_recall_fscore_support(y_test, predictions, average='weighted')
    
    metrics = {
        'accuracy': float(acc),
        'f1_weighted': float(f1),
        'precision_weighted': float(prec),
        'recall_weighted': float(rec)
    }
    
    logger.info(f"Model Accuracy: {acc:.4f} | F1: {f1:.4f}")
    
    if label_encoder:
        target_names = [str(cls) for cls in label_encoder.classes_]
        report = classification_report(y_test, predictions, target_names=target_names)
    else:
        report = classification_report(y_test, predictions)
    
    logger.info(f"\nClassification Report:\n{report}")
    return metrics

def build_preprocessor(X, fast_mode=False):
    """
    Create a premium preprocessing pipeline based on input data.
    fast_mode=True uses SimpleImputer for speed (useful during optimization).
    """
    # Identify numerical and categorical columns
    numeric_features = X.select_dtypes(include=['int64', 'float64']).columns
    categorical_features = X.select_dtypes(include=['object', 'category']).columns
    
    # Split categorical features by cardinality
    low_card_features = [col for col in categorical_features if X[col].nunique() < 10]
    high_card_features = [col for col in categorical_features if X[col].nunique() >= 10]
    
    logger.info(f"Numerical features: {len(numeric_features)}")
    logger.info(f"Low-cardinality categorical: {len(low_card_features)}")
    logger.info(f"High-cardinality categorical: {len(high_card_features)}")
    
    # 1. Advanced Numerical Pipeline: KNN Imputation (Slow) or Simple Imputer (Fast)
    # Reverting to SimpleImputer completely because KNNImputer is too slow on 30k+ rows
    imputer = SimpleImputer(strategy='median')
        
    numeric_transformer = Pipeline(steps=[
        ('imputer', imputer),
        ('scaler', RobustScaler())
    ])
    
    # 2. Low-Cardinality Categorical: Simple Imputation + One-Hot Encoding
    low_card_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='most_frequent', fill_value='missing')),
        ('onehot', OneHotEncoder(handle_unknown='ignore', drop='first', sparse_output=False))
    ])
    
    # 3. High-Cardinality Categorical: Rare Encoding + Target Encoding
    high_card_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='most_frequent', fill_value='missing')),
        ('rare_encoder', RareEncoder(tol=0.02)),
        ('target_encoder', TargetEncoder())
    ])
    
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', numeric_transformer, numeric_features),
            ('cat_low', low_card_transformer, low_card_features),
            ('cat_high', high_card_transformer, high_card_features)
        ])
        
    return preprocessor

def create_pipeline(preprocessor, model):
    """
    Create the standardized high-performance pipeline for the accuracy push.
    """
    return Pipeline(steps=[
        ('preprocessor', preprocessor),
        ('smote', SMOTE(random_state=42)),
        ('classifier', model)
    ])

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
    # Use fast_mode during optimization for speed
    is_optimization = config.get('optimization', {}).get('enabled', False)
    preprocessor = build_preprocessor(X, fast_mode=is_optimization)
        
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
    
    # ACCURACY PUSH: Using centralized pipeline builder
    pipeline_base = create_pipeline(preprocessor, base_model)

    if method in ['pso', 'abc', 'abc-pso']:
            from src.optimization_niapy import NiapyOptimizer

            config_opt = copy.deepcopy(config)
            if 'niapy_params' in config_opt['optimization'] and 'bounds' in config_opt['optimization']['niapy_params']:
                bounds = config_opt['optimization']['niapy_params']['bounds']
                new_bounds = {f'classifier__{k}': v for k, v in bounds.items()}
                config_opt['optimization']['niapy_params']['bounds'] = new_bounds

            optimizer = NiapyOptimizer(pipeline_base, config_opt)
            # optimize now returns (model, params, iter_history)
            best_model, best_params, opt_history = optimizer.optimize(X_train, y_train, algorithm=method)
            
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
    
    # Re-train the best model using the SLOW but HIGH QUALITY preprocessor (KNNImputer)
    logger.info("Switching to High-Quality Preprocessor for final fit...")
    final_preprocessor = build_preprocessor(X_train, fast_mode=False)
    best_model.set_params(preprocessor=final_preprocessor)
    best_model.fit(X_train, y_train)
    
    metrics = evaluate_model(best_model, X_test, y_test, label_encoder=le)
    
    # Save Model
    save_model(best_model, "reports/best_model.pkl")
    
    iteration_history = opt_history if method in ['pso', 'abc', 'abc-pso'] else []
    return best_model, metrics, iteration_history, le, X_train, X_test, y_train, y_test

def run_single_training(X_train, y_train, X_test, y_test, preprocessor, config, le):
    logger.info("--- Training Single Model ---")
    model = get_model(config.get('model', {}))
    
    # ACCURACY PUSH: Using centralized pipeline builder
    pipeline = create_pipeline(preprocessor, model)
    
    train_model(pipeline, X_train, y_train)
    metrics = evaluate_model(pipeline, X_test, y_test, label_encoder=le)
    return pipeline, metrics, [], le, X_train, X_test, y_train, y_test

def save_model(model, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    joblib.dump(model, path)
    logger.info(f"Model saved to {path}")
