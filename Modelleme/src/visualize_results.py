import joblib
from sklearn.metrics import confusion_matrix
from sklearn.pipeline import Pipeline
from src.config import load_config
from src.data_loader import load_and_merge_data
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
import numpy as np

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import os

def plot_model_comparison(baseline_acc, pso_acc, abc_acc):
    """
    Plots a bar chart comparing model accuracies.
    """
    data = {
        'Model': ['Random Forest (Baseline)', 'RF + PSO', 'RF + ABC'],
        'Accuracy': [baseline_acc, pso_acc, abc_acc]
    }
    df = pd.DataFrame(data)
    
    # Set style
    sns.set_style("whitegrid")
    plt.figure(figsize=(10, 6))
    
    # Create bar plot
    ax = sns.barplot(x='Model', y='Accuracy', data=df, palette='viridis')
    
    # Add values on top of bars
    for p in ax.patches:
        ax.annotate(f'{p.get_height():.4f}', 
                   (p.get_x() + p.get_width() / 2., p.get_height()), 
                   ha = 'center', va = 'center', 
                   xytext = (0, 9), 
                   textcoords = 'offset points',
                   fontsize=12, fontweight='bold')
    
    plt.title('Random Forest Optimizasyon Yöntemleri Karşılaştırması', fontsize=16)
    plt.ylabel('Doğruluk (Accuracy)', fontsize=12)
    plt.ylim(0, 1.0)  # Assuming accuracy is 0-1
    
    # Save plot
    os.makedirs('reports', exist_ok=True)
    plt.savefig('reports/model_comparison.png', dpi=300)
    print("Comparison plot saved to reports/model_comparison.png")

def load_resources():
    config = load_config()
    df = load_and_merge_data(config)
    
    # Re-prepare data (simplified logic from train.py)
    target_col = config['data'].get('target', 'pi')
    df = df.dropna(subset=[target_col])
    X = df.drop(columns=[target_col])
    y = df[target_col]
    
    le = LabelEncoder()
    y_encoded = le.fit_transform(y)
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y_encoded, test_size=config['data'].get('test_size', 0.2), 
        random_state=config['data'].get('random_state', 42)
    )
    
    model = joblib.load('reports/best_model.pkl')
    return model, X_test, y_test, X.columns, le.classes_

def plot_feature_importance(model, feature_names):
    """
    Plots top 20 feature importances.
    """
    # Extract feature importances
    # If pipeline, get classifier steps
    if isinstance(model, Pipeline):
        clf = model.named_steps['classifier']
        # We need transformed feature names if we used OneHotEncoder
        # But grabbing them from typical sklearn pipeline is tricky without fitting
        # For RF, we can just grab raw importance array and try to map to original cols
        # or simplified: just plot top numeric features if extracted?
        
        # Better approach: Get feature names from preprocessor if possible, or just skip names if too hard.
        # Let's try to get feature names from preprocessor
        preprocessor = model.named_steps['preprocessor']
        
        try:
            # This works in newer sklearn versions
            feature_names_out = preprocessor.get_feature_names_out()
        except:
            print("Could not extract feature names directly. Using numeric indices.")
            feature_names_out = [f"Feature {i}" for i in range(len(clf.feature_importances_))]
            
        importances = clf.feature_importances_
    else:
        importances = model.feature_importances_
        feature_names_out = feature_names

    # Create DataFrame
    fi_df = pd.DataFrame({'Feature': feature_names_out, 'Importance': importances})
    fi_df = fi_df.sort_values(by='Importance', ascending=False).head(20)
    
    plt.figure(figsize=(12, 8))
    sns.barplot(x='Importance', y='Feature', data=fi_df, palette='viridis')
    plt.title('En Etkili 20 Özellik (Feature Importance)', fontsize=16)
    plt.xlabel('Önem Derecesi')
    plt.ylabel('Özellikler')
    plt.tight_layout()
    plt.savefig('reports/feature_importance.png', dpi=300)
    print("Feature importance plot saved to reports/feature_importance.png")

def plot_confusion_matrix_heatmap(model, X_test, y_test, class_names):
    """
    Plots confusion matrix heatmap.
    """
    y_pred = model.predict(X_test)
    cm = confusion_matrix(y_test, y_pred)
    
    plt.figure(figsize=(10, 8))
    sns.heatmap(cm, annot=False, fmt='d', cmap='Blues', xticklabels=class_names, yticklabels=class_names)
    plt.title('Hata Matrisi (Confusion Matrix)', fontsize=16)
    plt.ylabel('Gerçek Sınıf')
    plt.xlabel('Tahmin Edilen Sınıf')
    plt.tight_layout()
    plt.savefig('reports/confusion_matrix.png', dpi=300)
    print("Confusion matrix saved to reports/confusion_matrix.png")

if __name__ == "__main__":
    # 1. Model Comparison Plot
    baseline_acc = 0.7582
    pso_acc = 0.7712
    abc_acc = 0.7212
    plot_model_comparison(baseline_acc, pso_acc, abc_acc)
    
    # 2. Advanced Plots (Feature Importance & Confusion Matrix)
    try:
        model, X_test, y_test, feature_cols, class_names = load_resources()
        plot_feature_importance(model, feature_cols)
        plot_confusion_matrix_heatmap(model, X_test, y_test, class_names)
    except Exception as e:
        print(f"Could not generate advanced plots: {e}")
