from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from lightgbm import LGBMClassifier

def get_model(model_config):
    """
    Factory function to get the model based on configuration.
    
    Args:
        model_config (dict): Model configuration dictionary.
        
    Returns:
        model: Instantiated model.
    """
    model_type = model_config.get('type', 'random_forest')
    params = model_config.get('params', {})
    
    print(f"Initializing model: {model_type}")
    
    if model_type == 'random_forest':
        # Default params if not specified
        n_estimators = params.get('n_estimators', 100)
        max_depth = params.get('max_depth', None)
        min_samples_split = params.get('min_samples_split', 2)
        random_state = params.get('random_state', 42)
        
        class_weight = params.get('class_weight', None)
        
        return RandomForestClassifier(
            n_estimators=n_estimators,
            max_depth=max_depth,
            min_samples_split=min_samples_split,
            random_state=random_state,
            class_weight=class_weight,
            n_jobs=-1
        )
        
    elif model_type == 'xgboost':
        # XGBoost requires target 0-N, if target is not continuous.
        # Ensure 'objective' is set correctly in params or default to multi:softprob for multiclass
        n_estimators = params.get('n_estimators', 100)
        max_depth = params.get('max_depth', 6)
        learning_rate = params.get('learning_rate', 0.1)
        random_state = params.get('random_state', 42)
        
        return XGBClassifier(
            n_estimators=n_estimators,
            max_depth=max_depth,
            learning_rate=learning_rate,
            random_state=random_state,
            objective='multi:softprob', # Default assumption for this dataset
            n_jobs=-1,
            subsample=0.8,
            colsample_bytree=0.8
        )
        
    elif model_type == 'lightgbm':
        n_estimators = params.get('n_estimators', 100)
        learning_rate = params.get('learning_rate', 0.1)
        num_leaves = params.get('num_leaves', 31)
        random_state = params.get('random_state', 42)
        
        return LGBMClassifier(
            n_estimators=n_estimators,
            learning_rate=learning_rate,
            num_leaves=num_leaves,
            random_state=random_state,
            n_jobs=-1,
            verbosity=-1
        )
        
    else:
        raise ValueError(f"Unsupported model type: {model_type}")
