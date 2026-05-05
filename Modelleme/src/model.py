from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier

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
        
        class_weight = params.get('class_weight', 'balanced_subsample')
        max_features = params.get('max_features', 'sqrt')
        
        return RandomForestClassifier(
            n_estimators=n_estimators,
            max_depth=max_depth,
            min_samples_split=min_samples_split,
            max_features=max_features,
            random_state=random_state,
            class_weight=class_weight,
            n_jobs=-1
        )
    
    elif model_type == 'knn':
        n_neighbors = params.get('n_neighbors', 5)
        weights = params.get('weights', 'uniform')
        metric = params.get('metric', 'minkowski')
        
        return KNeighborsClassifier(
            n_neighbors=n_neighbors,
            weights=weights,
            metric=metric,
            n_jobs=-1
        )
        
    else:
        raise ValueError(f"Unsupported model type: {model_type}")
