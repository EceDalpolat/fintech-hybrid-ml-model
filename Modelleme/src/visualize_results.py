"""
Visualisation helpers for thesis plots.

Generates:
  1. benchmark_comparison.png   – grouped bar chart per function (log scale)
  2. benchmark_convergence.png  – 4-panel convergence curves
  3. convergence_<Func>.png     – individual convergence per benchmark function
  4. thesis_comparison.png      – Accuracy / F1 bar chart for 4 RF variants
  5. rf_convergence.png         – best CV score vs. optimiser iteration for
                                   PSO / ABC / ABC-PSO on the RF problem
"""
import os
import json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import joblib
from sklearn.metrics import confusion_matrix
import shap


sns.set_style("whitegrid")
plt.rcParams.update({'font.size': 12})

os.makedirs('reports', exist_ok=True)

# ---------------------------------------------------------------------------
# Shared style helpers
# ---------------------------------------------------------------------------
_METHOD_LABELS = {
    'baseline': 'Baseline',
    'pso':      'PSO Optimized',
    'abc':      'ABC Optimized',
    'abc-pso':  'ABC-PSO Hybrid',
}

_ALGO_STYLES = {
    'PSO':     {'color': '#1f77b4', 'linestyle': '--',  'linewidth': 2.0},
    'ABC':     {'color': '#ff7f0e', 'linestyle': '-.',  'linewidth': 2.0},
    'ABC-PSO': {'color': '#2ca02c', 'linestyle': '-',   'linewidth': 2.5},
    'pso':     {'color': '#1f77b4', 'linestyle': '--',  'linewidth': 2.0},
    'abc':     {'color': '#ff7f0e', 'linestyle': '-.',  'linewidth': 2.0},
    'abc-pso': {'color': '#2ca02c', 'linestyle': '-',   'linewidth': 2.5},
}


# ---------------------------------------------------------------------------
# 1. Benchmark Bar Chart
# ---------------------------------------------------------------------------
def plot_benchmarks(json_path="reports/benchmark_results.json",
                    save_path="reports/benchmark_comparison.png"):
    if not os.path.exists(json_path):
        print(f"[WARN] Not found: {json_path}")
        return

    with open(json_path) as f:
        results = json.load(f)

    problems   = list(results.keys())
    algorithms = [a for a in ['PSO', 'ABC', 'ABC-PSO'] if a in next(iter(results.values()))]
    colors     = [_ALGO_STYLES[a]['color'] for a in algorithms]

    x     = np.arange(len(problems))
    width = 0.25
    fig, ax = plt.subplots(figsize=(12, 6))

    for j, (algo, color) in enumerate(zip(algorithms, colors)):
        means = [results[p][algo]['mean'] for p in problems]
        stds  = [results[p][algo]['std']  for p in problems]
        ax.bar(x + j * width, means, width, label=algo, color=color,
               alpha=0.85, yerr=stds, capsize=4,
               error_kw={'linewidth': 1.2, 'ecolor': 'black'})

    ax.set_xticks(x + width)
    ax.set_xticklabels(problems, fontsize=11)
    ax.set_xlabel('Benchmark Function', fontsize=12)
    ax.set_ylabel('Mean Best Fitness (log scale)', fontsize=12)
    ax.set_yscale('log')
    ax.set_title(
        'Algorithm Comparison on Benchmark Functions (D=30, 25 runs)\n'
        'Lower is Better',
        fontsize=13, fontweight='bold'
    )
    ax.legend(fontsize=11)
    ax.grid(axis='y', alpha=0.3)
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    print(f"Saved: {save_path}")
    plt.close()


# ---------------------------------------------------------------------------
# 2. Benchmark Convergence – 4-panel (like Chen et al. 2020 Fig. 1)
# ---------------------------------------------------------------------------
def plot_convergence_curves(json_path="reports/benchmark_results.json",
                             save_path="reports/benchmark_convergence.png"):
    if not os.path.exists(json_path):
        print(f"[WARN] Not found: {json_path}")
        return

    with open(json_path) as f:
        results = json.load(f)

    problems = list(results.keys())
    rows, cols = 2, 2
    fig, axes = plt.subplots(rows, cols, figsize=(14, 10))
    axes = axes.flatten()

    for idx, pname in enumerate(problems):
        ax = axes[idx]
        for algo, style in _ALGO_STYLES.items():
            if algo not in results[pname]:
                continue
            # support both key names
            hist_key = 'mean_iter_history' if 'mean_iter_history' in results[pname][algo] \
                       else 'mean_history'
            hist = results[pname][algo].get(hist_key, [])
            if not hist:
                continue
            hist_arr = np.clip(hist, 1e-300, None)
            ax.semilogy(hist_arr, label=algo,
                        color=style['color'],
                        linestyle=style['linestyle'],
                        linewidth=style['linewidth'])

        ax.set_title(f'{pname} (D=30)', fontsize=13, fontweight='bold')
        ax.set_xlabel('Iteration', fontsize=11)
        ax.set_ylabel('Best Fitness (log)', fontsize=11)
        ax.legend(fontsize=10)
        ax.grid(True, which='both', alpha=0.3)

    for idx in range(len(problems), len(axes)):
        axes[idx].set_visible(False)

    fig.suptitle(
        'Convergence Curves – PSO vs ABC vs ABC-PSO\n'
        'Benchmark Functions (D=30, Pop=40, 25 runs avg.)',
        fontsize=14, fontweight='bold'
    )
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    print(f"Saved: {save_path}")
    plt.close()

    # Individual function plots
    for pname in problems:
        fig2, ax2 = plt.subplots(figsize=(8, 5))
        for algo, style in _ALGO_STYLES.items():
            if algo not in results[pname]:
                continue
            hist_key = 'mean_iter_history' if 'mean_iter_history' in results[pname][algo] \
                       else 'mean_history'
            hist = results[pname][algo].get(hist_key, [])
            if not hist:
                continue
            ax2.semilogy(np.clip(hist, 1e-300, None), label=algo,
                         color=style['color'],
                         linestyle=style['linestyle'],
                         linewidth=style['linewidth'])
        ax2.set_title(f'{pname} – Convergence (D=30)', fontsize=13, fontweight='bold')
        ax2.set_xlabel('Iteration', fontsize=11)
        ax2.set_ylabel('Best Fitness (log)', fontsize=11)
        ax2.legend(fontsize=11)
        ax2.grid(True, which='both', alpha=0.3)
        plt.tight_layout()
        p = f'reports/convergence_{pname}.png'
        plt.savefig(p, dpi=150, bbox_inches='tight')
        print(f"  Saved: {p}")
        plt.close()


# ---------------------------------------------------------------------------
# 3. RF Experiment Results (Accuracy + F1)
# ---------------------------------------------------------------------------
def plot_experiment_results(json_path="reports/experiment_results.json",
                             save_path="reports/thesis_comparison.png"):
    if not os.path.exists(json_path):
        print(f"[WARN] Not found: {json_path}")
        return

    df = pd.read_json(json_path)
    df['Method'] = df['method'].map(_METHOD_LABELS)

    df_m = df.melt(id_vars=['Method'], value_vars=['accuracy', 'f1_weighted'],
                   var_name='Metric', value_name='Score')
    df_m['Metric'] = df_m['Metric'].map({'accuracy': 'Accuracy', 'f1_weighted': 'F1-Weighted'})

    fig, ax = plt.subplots(figsize=(12, 7))
    method_order = [_METHOD_LABELS[m] for m in ['baseline', 'pso', 'abc', 'abc-pso']
                    if m in df['method'].values]
    sns.barplot(x='Method', y='Score', hue='Metric', data=df_m,
                order=method_order, palette='viridis', ax=ax)

    for patch in ax.patches:
        h = patch.get_height()
        if h > 0.01:
            ax.annotate(f'{h:.4f}',
                        (patch.get_x() + patch.get_width() / 2, h),
                        ha='center', va='bottom',
                        xytext=(0, 4), textcoords='offset points',
                        fontsize=9, fontweight='bold')

    ax.set_ylim(0.5, 1.05)
    ax.set_title(
        'Random Forest Variants – Performance on Payment Preference Dataset\n'
        'Accuracy and F1-Weighted',
        fontsize=13, fontweight='bold'
    )
    ax.set_xlabel('Optimisation Strategy', fontsize=12)
    ax.set_ylabel('Score (Higher is Better)', fontsize=12)
    ax.legend(bbox_inches='tight', fontsize=11)
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    print(f"Saved: {save_path}")
    plt.close()


# ---------------------------------------------------------------------------
# 4. RF Optimiser Convergence (best CV score per iteration)
# ---------------------------------------------------------------------------
def plot_rf_convergence(json_path="reports/convergence_rf.json",
                        save_path="reports/rf_convergence.png"):
    """
    Plot convergence of PSO, ABC, and ABC-PSO optimisers on the RF problem.
    X-axis: iteration; Y-axis: best CV F1 score (higher is better).
    """
    if not os.path.exists(json_path):
        print(f"[WARN] Not found: {json_path}")
        return

    with open(json_path) as f:
        data = json.load(f)

    fig, ax = plt.subplots(figsize=(10, 6))
    plotted = False

    for method in ['pso', 'abc', 'abc-pso']:
        hist = data.get(method, [])
        if not hist:
            continue
        style = _ALGO_STYLES.get(method, {})
        label = _METHOD_LABELS.get(method, method.upper())
        ax.plot(range(1, len(hist) + 1), hist,
                label=label,
                color=style.get('color', None),
                linestyle=style.get('linestyle', '-'),
                linewidth=style.get('linewidth', 2.0),
                marker='o', markersize=4)
        plotted = True

    if not plotted:
        print("[WARN] No optimiser convergence data to plot.")
        plt.close()
        return

    ax.set_xlabel('Optimiser Iteration', fontsize=12)
    ax.set_ylabel('Best CV F1-Weighted Score', fontsize=12)
    ax.set_title(
        'Optimiser Convergence on RF Hyperparameter Tuning\n'
        'Payment Preference Dataset',
        fontsize=13, fontweight='bold'
    )
    ax.legend(fontsize=11)
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    print(f"Saved: {save_path}")
    plt.close()


# ---------------------------------------------------------------------------
# 5. All-in-one summary table (text)
# ---------------------------------------------------------------------------
def print_results_table(json_path="reports/experiment_results.json"):
    if not os.path.exists(json_path):
        return
    df = pd.read_json(json_path)
    df['Method'] = df['method'].map(_METHOD_LABELS).fillna(df['method'])
    cols = ['Method', 'accuracy', 'f1_weighted', 'precision_weighted', 'recall_weighted']
    cols = [c for c in cols if c in df.columns]
    print("\n" + "=" * 70)
    print("  EXPERIMENT RESULTS SUMMARY")
    print("=" * 70)
    print(df[cols].to_string(index=False))
    print("=" * 70)


# ---------------------------------------------------------------------------
# Confusion matrix helper
# ---------------------------------------------------------------------------
def plot_confusion_matrix_heatmap(model_path, X_test, y_test, class_names):
    if not os.path.exists(model_path):
        return
    model  = joblib.load(model_path)
    y_pred = model.predict(X_test)
    cm     = confusion_matrix(y_test, y_pred)
    fig, ax = plt.subplots(figsize=(10, 8))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                xticklabels=class_names, yticklabels=class_names, ax=ax)
    ax.set_title(f'Confusion Matrix – {os.path.basename(model_path)}', fontsize=14)
    ax.set_ylabel('True Label')
    ax.set_xlabel('Predicted Label')
    plt.tight_layout()
    out = f'reports/cm_{os.path.basename(model_path)}.png'
    plt.savefig(out, dpi=150)
    print(f"Saved: {out}")
    plt.close()

# ---------------------------------------------------------------------------
# SHAP Interpretability
# ---------------------------------------------------------------------------
def plot_shap_summary(pipeline, X_train, save_path="reports/shap_summary.png"):
    """
    Generate SHAP summary plot for model transparency.
    """
    try:
        logger.info("Generating SHAP summary plot...")
        # Get the model and preprocessor from pipeline
        model = pipeline.named_steps['classifier']
        preprocessor = pipeline.named_steps['preprocessor']
        
        # Transform data to get feature names after preprocessing
        # This is tricky with ColumnTransformer, but let's try a sample
        X_sample = X_train.sample(min(100, len(X_train)))
        X_transformed = preprocessor.transform(X_sample)
        
        # Determine feature names (simplified)
        # In a real scenario, we'd extract from preprocessor.get_feature_names_out()
        try:
            feature_names = preprocessor.get_feature_names_out()
        except:
            feature_names = [f"Feature {i}" for i in range(X_transformed.shape[1])]

        # Explainer
        if hasattr(model, "feature_importances_"):
            explainer = shap.TreeExplainer(model)
            shap_values = explainer.shap_values(X_transformed)
        else:
            # Fallback for KNN or other models
            # Use a small background set for KernelExplainer
            background = shap.sample(X_transformed, 10)
            explainer = shap.KernelExplainer(model.predict_proba, background)
            shap_values = explainer.shap_values(X_transformed)

        plt.figure(figsize=(12, 8))
        shap.summary_plot(shap_values, X_transformed, feature_names=feature_names, show=False)
        plt.title("SHAP Feature Importance Summary", fontsize=14, fontweight='bold')
        plt.tight_layout()
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        plt.close()
        print(f"Saved: {save_path}")
    except Exception as e:
        print(f"[ERROR] Failed to generate SHAP plot: {e}")



# ---------------------------------------------------------------------------
if __name__ == "__main__":
    plot_benchmarks()
    plot_convergence_curves()
    plot_experiment_results()
    plot_rf_convergence()
    print_results_table()
