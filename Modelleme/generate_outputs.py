import os
import joblib
import logging
from src.config import load_config
from src.data_loader import load_and_merge_data
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from src.visualize_results import plot_confusion_matrix_heatmap, plot_shap_summary

def main():
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    config = load_config()
    df = load_and_merge_data(config)
    
    target_col = config['data'].get('target', 'pi')
    df = df.dropna(subset=[target_col])
    
    X = df.drop(columns=[target_col])
    y = df[target_col]
    
    le = LabelEncoder()
    y_encoded = le.fit_transform(y)
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y_encoded, test_size=config['data'].get('test_size', 0.2), random_state=42
    )
    
    logger.info("Loading model...")
    try:
        pipeline = joblib.load("reports/best_model.pkl")
    except Exception as e:
        logger.error(f"Failed to load model: {e}")
        return
        
    class_names = [str(c) for c in le.classes_]
    
    logger.info("Plotting Confusion Matrix...")
    plot_confusion_matrix_heatmap("reports/best_model.pkl", X_test, y_test, class_names)
    
    logger.info("Plotting SHAP Summary...")
    plot_shap_summary(pipeline, X_train, save_path="reports/shap_random_forest.png")
    
    logger.info("Done generating outputs.")

if __name__ == "__main__":
    main()
