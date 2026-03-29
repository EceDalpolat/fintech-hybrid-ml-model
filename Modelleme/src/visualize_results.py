import joblib
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
import json
from sklearn.metrics import confusion_matrix
from sklearn.pipeline import Pipeline

# Set global style
sns.set_style("whitegrid")
plt.rcParams['font.size'] = 12

def plot_benchmarks(json_path="reports/benchmark_results.json"):
    """
    Plots benchmark comparison for different mathematical functions.
    """
    if not os.path.exists(json_path):
        print(f"Benchmark results not found at {json_path}")
        return

    with open(json_path, 'r') as f:
        results = json.load(f)

    # Prepare data for plotting
    plot_data = []
    for prob, algos in results.items():
        for algo, metrics in algos.items():
            plot_data.append({
                'Function': prob,
                'Algorithm': algo,
                'Mean Fitness (Log)': np.log10(metrics['mean'] + 1e-30) # Log scale for better visibility
            })

    df = pd.DataFrame(plot_data)
    
    plt.figure(figsize=(14, 8))
    ax = sns.barplot(x='Function', y='Mean Fitness (Log)', hue='Algorithm', data=df, palette='muted')
    
    plt.title('Optimization Algorithm Comparison on Benchmark Functions (Log Scale)', fontsize=16)
    plt.ylabel('Log10(Mean Fitness Error)', fontsize=12)
    plt.xlabel('Benchmark Function', fontsize=12)
    plt.legend(title='Algorithm', bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    
    os.makedirs('reports', exist_ok=True)
    plt.savefig('reports/benchmark_comparison.png', dpi=300)
    print("Benchmark comparison plot saved to reports/benchmark_comparison.png")

def plot_convergence_curves(json_path="reports/benchmark_results.json"):
    """
    Plots convergence curves for each benchmark function.
    """
    if not os.path.exists(json_path):
        print(f"Benchmark results not found at {json_path}")
        return

    with open(json_path, 'r') as f:
        results = json.load(f)

    for prob_name, algos in results.items():
        plt.figure(figsize=(10, 6))
        for algo_name, metrics in algos.items():
            histories = metrics.get('histories', [])
            if not histories:
                continue
            
            # Use the mean history across runs
            max_len = max(len(h) for h in histories)
            padded_histories = []
            for h in histories:
                # Pad with last value if shorter (shouldn't happen with fixed max_iters, but let's be safe)
                padded = h + [h[-1]] * (max_len - len(h))
                padded_histories.append(padded)
            
            mean_history = np.mean(padded_histories, axis=0)
            plt.plot(mean_history, label=algo_name)

        plt.title(f'Convergence Curve: {prob_name}', fontsize=16)
        plt.ylabel('Best Fitness (Lower is Better)', fontsize=12)
        plt.xlabel('Evaluations / Iterations', fontsize=12)
        plt.yscale('log')
        plt.legend()
        plt.tight_layout()
        
        save_path = f'reports/convergence_{prob_name}.png'
        plt.savefig(save_path, dpi=300)
        print(f"Convergence plot saved to {save_path}")

def plot_experiment_results(json_path="reports/experiment_results.json"):
    """
    Plots thesis experiment results (Acc and F1) for different RF versions.
    """
    if not os.path.exists(json_path):
        print(f"Experiment results not found at {json_path}")
        return

    df = pd.read_json(json_path)
    
    # Melt for side-by-side Accuracy and F1
    df_melted = df.melt(id_vars=['method'], value_vars=['accuracy', 'f1_weighted'], 
                        var_name='Metric', value_name='Score')
    
    mapping = {
        'baseline': 'RF (Baseline)',
        'pso': 'RF + PSO',
        'abc': 'RF + ABC',
        'abc-pso': 'RF + ABC-PSO (Hybrid)'
    }
    df_melted['Method Name'] = df_melted['method'].map(mapping)
    
    plt.figure(figsize=(12, 7))
    ax = sns.barplot(x='Method Name', y='Score', hue='Metric', data=df_melted, palette='viridis')
    
    # Add values on bars
    for p in ax.patches:
        if p.get_height() > 0:
            ax.annotate(f'{p.get_height():.4f}', 
                       (p.get_x() + p.get_width() / 2., p.get_height()), 
                       ha='center', va='center', 
                       xytext=(0, 9), 
                       textcoords='offset points',
                       fontsize=10, fontweight='bold')
                       
    plt.title('Thesis Experiments: Hybrid ML Model Performance Comparison', fontsize=16)
    plt.ylabel('Score (Higher is Better)', fontsize=12)
    plt.xlabel('Optimization Strategy', fontsize=12)
    plt.ylim(0, 1.1)
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    
    plt.savefig('reports/thesis_comparison.png', dpi=300)
    print("Thesis comparison plot saved to reports/thesis_comparison.png")

def plot_confusion_matrix_heatmap(model_path, X_test, y_test, class_names):
    """
    Loads model and plots confusion matrix.
    """
    if not os.path.exists(model_path):
        return
        
    model = joblib.load(model_path)
    y_pred = model.predict(X_test)
    cm = confusion_matrix(y_test, y_pred)
    
    plt.figure(figsize=(10, 8))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=class_names, yticklabels=class_names)
    plt.title(f'Hata Matrisi: {os.path.basename(model_path)}', fontsize=16)
    plt.ylabel('Gerçek Sınıf')
    plt.xlabel('Tahmin Edilen Sınıf')
    plt.tight_layout()
    plt.savefig(f'reports/cm_{os.path.basename(model_path)}.png', dpi=300)

if __name__ == "__main__":
    # Run specific plotting tasks if requested
    plot_benchmarks()
    plot_experiment_results()
