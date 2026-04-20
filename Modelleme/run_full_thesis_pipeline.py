import yaml
import logging
import os
import pandas as pd
from src.data_loader import load_and_merge_data
from src.train import train_pipeline, evaluate_model
from src.utils import setup_logging
from src.visualize_results import (
    plot_experiment_results, 
    plot_rf_convergence, 
    print_results_table, 
    plot_confusion_matrix_heatmap,
    plot_shap_summary
)
import json

def run_full_pipeline(config_path="config.yaml"):
    # 1. Setup
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    setup_logging(config.get('logging', {}).get('config_path', 'logging.yaml'))
    logger = logging.getLogger(__name__)
    logger.info("Starting Full Thesis Pipeline...")
    
    os.makedirs('reports', exist_ok=True)
    
    # 2. Data Loading
    df = load_and_merge_data(config)
    if df is None:
        logger.error("Data loading failed. Exiting.")
        return

    results = []
    convergence_data = {}

    # 3. Experiment Loop: Compare different methods
    methods = ['baseline', 'abc-pso'] 
    
    # ONLY Random Forest as requested
    model_types = ['random_forest']
    
    current_best_accuracy = 0
    best_overall_pipeline = None
    best_X_train, best_X_test, best_y_test, best_le = None, None, None, None

    for m_type in model_types:
        logger.info(f"=== Testing Model Type: {m_type} ===")
        config['model']['type'] = m_type
        
        # Ensure bounds are set for RF
        config['optimization']['niapy_params']['bounds'] = {
            'n_estimators': [100, 500],
            'max_depth': [5, 50]
        }

        for method in methods:
            logger.info(f"--- Running {method.upper()} for {m_type} ---")
            config['optimization']['enabled'] = (method != 'baseline')
            config['optimization']['method'] = method
            
            try:
                pipeline, metrics, history, le, X_train, X_test, y_train, y_test = train_pipeline(df, config)
                
                # Capture results
                res_entry = metrics.copy()
                res_entry['method'] = method
                res_entry['model_type'] = m_type
                results.append(res_entry)
                
                if history:
                    convergence_data[method] = [float(h) for h in history]
                
                # NEW: SHAP Analysis for the best model of this type
                # (usually we do it for the hybrid one)
                # Keep track of best for visualization
                if method == 'abc-pso':
                    best_overall_pipeline = pipeline
                    best_X_train = X_train
                    best_X_test = X_test
                    best_y_test = y_test
                    best_le = le

            except Exception as e:
                logger.error(f"Error during {method} optimization for {m_type}: {e}")

    # Save results to JSON for the plotting functions
    with open('reports/experiment_results.json', 'w') as f:
        json.dump(results, f, indent=4)
    
    with open('reports/convergence_rf.json', 'w') as f:
        json.dump(convergence_data, f, indent=4)

    # 4. Final Visualization & Reporting
    logger.info("Generating Final Reports...")
    plot_experiment_results()
    plot_rf_convergence()
    print_results_table()
    
    if best_overall_pipeline and best_X_test is not None:
        logger.info("Generating Final Visualizations...")
        
        # 1. Confusion Matrix
        class_names = [str(cls) for cls in best_le.classes_]
        plot_confusion_matrix_heatmap("reports/best_model.pkl", best_X_test, best_y_test, class_names)
        
        # 2. SHAP
        plot_shap_summary(best_overall_pipeline, best_X_train, save_path=f"reports/shap_{config['model']['type']}.png")
    
    logger.info("Pipeline Complete. Check the 'reports/' directory for results.")

if __name__ == "__main__":
    # Ensure we are in the Modellme directory
    if os.path.basename(os.getcwd()) != "Modelleme":
        print("Please run this script from the 'Modelleme' directory.")
    else:
        run_full_pipeline()
