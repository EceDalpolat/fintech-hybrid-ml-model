"""
Benchmark Suite for Thesis
Validates PSO, ABC, and hybrid ABC-PSO on standard mathematical optimization problems.
Settings match the literature (Khuat & Le 2018; Chen et al. 2020):
  - D = 30
  - 500 iterations
  - 25 independent runs
  - Problems: Sphere, Rosenbrock, Rastrigin, Griewank
"""
import sys
import os
import numpy as np
import pandas as pd
import json

parent = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if parent not in sys.path:
    sys.path.insert(0, parent)

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from niapy.task import Task
from niapy.problems import Sphere, Rosenbrock, Rastrigin, Griewank
from niapy.problems import Problem
from niapy.algorithms.basic import ParticleSwarmOptimization, ArtificialBeeColonyAlgorithm
from src.algorithms.hybrid_abc_pso import ABCPSO

os.makedirs('reports', exist_ok=True)


# ---------------------------------------------------------------------------
# Logged Problem Wrapper
# ---------------------------------------------------------------------------
class LoggedProblem(Problem):
    """Wraps a NiaPy problem to record best-fitness at every function evaluation."""

    def __init__(self, base_problem):
        super().__init__(
            dimension=base_problem.dimension,
            lower=base_problem.lower,
            upper=base_problem.upper,
        )
        self._base = base_problem
        self._best = float('inf')
        self.history_fe = []        # best fitness at each FE
        self.history_iter = []      # best fitness sampled once per iteration

    def _evaluate(self, x):
        f = self._base._evaluate(x)
        if f < self._best:
            self._best = f
        self.history_fe.append(self._best)
        return f

    def repair(self, x, **kw):
        return self._base.repair(x, **kw)


# ---------------------------------------------------------------------------
# Single Run
# ---------------------------------------------------------------------------
def _run_single(algo_name, problem_cls, dim, max_iters, pop_size, seed):
    """
    Execute one independent run.
    Returns (final_best, iter_history) where iter_history has len == max_iters.
    """
    np.random.seed(seed)

    base_prob = problem_cls(dimension=dim)
    lp = LoggedProblem(base_prob)
    task = Task(problem=lp, max_iters=max_iters)

    if algo_name == 'PSO':
        algo = ParticleSwarmOptimization(population_size=pop_size)
        algo.run(task)
        # Convert per-FE history to per-iteration (sample at every pop_size FEs)
        fe_hist = lp.history_fe
        iter_hist = _fe_to_iter(fe_hist, pop_size, max_iters)

    elif algo_name == 'ABC':
        algo = ArtificialBeeColonyAlgorithm(population_size=pop_size)
        algo.run(task)
        fe_hist = lp.history_fe
        # ABC evaluates pop_size + pop_size FEs per iteration (employed + onlooker)
        iter_hist = _fe_to_iter(fe_hist, pop_size, max_iters)

    elif algo_name == 'ABC-PSO':
        algo = ABCPSO(population_size=pop_size)
        _, _, history_iter = algo.run(task)
        # history_iter already has one value per iteration
        iter_hist = _pad(history_iter, max_iters)

    else:
        raise ValueError(f"Unknown algorithm: {algo_name}")

    final_best = iter_hist[-1] if iter_hist else lp._best
    return final_best, iter_hist


def _fe_to_iter(fe_hist, pop_size, max_iters):
    """Sample best-fitness from per-FE history at the end of each iteration."""
    step = max(1, pop_size)
    iter_hist = []
    for i in range(max_iters):
        end_idx = min((i + 1) * step, len(fe_hist)) - 1
        if end_idx < 0:
            val = float('inf') if not iter_hist else iter_hist[-1]
        else:
            val = fe_hist[end_idx]
        iter_hist.append(val)
    return iter_hist


def _pad(hist, target_len):
    """Extend or trim a list to exactly target_len using last value."""
    if len(hist) >= target_len:
        return hist[:target_len]
    return hist + [hist[-1]] * (target_len - len(hist))


# ---------------------------------------------------------------------------
# Benchmark Runner
# ---------------------------------------------------------------------------
def run_benchmark(problem_classes=None, algorithm_names=None,
                  dim=30, max_iters=500, pop_size=40, num_runs=25):
    """
    Full benchmark suite. Returns nested dict:
      results[prob_name][algo_name] = {mean, std, best, runs, mean_iter_history}
    """
    if problem_classes is None:
        problem_classes = [Sphere, Rosenbrock, Rastrigin, Griewank]
    if algorithm_names is None:
        algorithm_names = ['PSO', 'ABC', 'ABC-PSO']

    total = len(problem_classes) * len(algorithm_names) * num_runs
    done = 0
    results = {}

    for prob_cls in problem_classes:
        pname = prob_cls.__name__
        results[pname] = {}

        for algo in algorithm_names:
            bests = []
            iter_histories = []

            for run in range(num_runs):
                seed = 42 + run * 137   # deterministic but varied seeds
                best_f, iter_hist = _run_single(algo, prob_cls, dim, max_iters, pop_size, seed)
                bests.append(best_f)
                iter_histories.append(iter_hist)
                done += 1
                if done % max(1, total // 20) == 0:
                    pct = 100 * done / total
                    print(f"  [{pct:5.1f}%] {algo} on {pname} run {run+1}/{num_runs}  best={best_f:.4e}")

            # Align to same length (should already be identical)
            max_len = max(len(h) for h in iter_histories)
            padded = [_pad(h, max_len) for h in iter_histories]
            mean_hist = np.mean(padded, axis=0).tolist()

            results[pname][algo] = {
                'mean': float(np.mean(bests)),
                'std':  float(np.std(bests)),
                'best': float(np.min(bests)),
                'worst': float(np.max(bests)),
                'median': float(np.median(bests)),
                'runs': [float(b) for b in bests],
                'mean_iter_history': mean_hist,
            }
            print(f"  >> {algo:8s} on {pname:12s}: "
                  f"mean={np.mean(bests):.4e}  std={np.std(bests):.4e}  best={np.min(bests):.4e}")

    return results


# ---------------------------------------------------------------------------
# Visualisation
# ---------------------------------------------------------------------------

_ALGO_STYLES = {
    'PSO':     {'color': '#1f77b4', 'linestyle': '--',  'linewidth': 2.0, 'marker': None},
    'ABC':     {'color': '#ff7f0e', 'linestyle': '-.',  'linewidth': 2.0, 'marker': None},
    'ABC-PSO': {'color': '#2ca02c', 'linestyle': '-',   'linewidth': 2.5, 'marker': None},
}


def plot_convergence(results, save_path='reports/benchmark_convergence.png',
                     max_points=500):
    """
    4-panel convergence figure matching Chen et al. 2020, Figure 1.
    X-axis: iteration number; Y-axis: best fitness (log scale).
    """
    problems = list(results.keys())
    n_prob = len(problems)
    cols = 2
    rows = (n_prob + cols - 1) // cols

    fig, axes = plt.subplots(rows, cols, figsize=(14, 10))
    axes = axes.flatten()

    for idx, pname in enumerate(problems):
        ax = axes[idx]
        for algo, style in _ALGO_STYLES.items():
            if algo not in results[pname]:
                continue
            hist = results[pname][algo]['mean_iter_history']
            # Replace zeros / negatives with a small positive for log scale
            hist_arr = np.clip(hist, 1e-20, None)
            # Downsample for clarity
            if len(hist_arr) > max_points:
                idx_pts = np.linspace(0, len(hist_arr) - 1, max_points, dtype=int)
                y = hist_arr[idx_pts]
                x = idx_pts
            else:
                y = hist_arr
                x = np.arange(len(y))

            ax.semilogy(x, y, label=algo,
                        color=style['color'],
                        linestyle=style['linestyle'],
                        linewidth=style['linewidth'])

        ax.set_title(f'{pname} (D=30)', fontsize=13, fontweight='bold')
        ax.set_xlabel('Iteration', fontsize=11)
        ax.set_ylabel('Best Fitness (log)', fontsize=11)
        ax.legend(fontsize=10)
        ax.grid(True, which='both', alpha=0.3)

    # Hide extra subplots
    for idx in range(n_prob, len(axes)):
        axes[idx].set_visible(False)

    fig.suptitle(
        'Algorithm Convergence on Benchmark Functions\n'
        'PSO vs ABC vs ABC-PSO  (D=30, Pop=40, 25 runs avg.)',
        fontsize=14, fontweight='bold'
    )
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    print(f"Convergence plot saved: {save_path}")
    plt.close()

    # Also save individual per-function plots
    for pname in problems:
        fig2, ax2 = plt.subplots(figsize=(8, 5))
        for algo, style in _ALGO_STYLES.items():
            if algo not in results[pname]:
                continue
            hist = np.clip(results[pname][algo]['mean_iter_history'], 1e-20, None)
            ax2.semilogy(hist, label=algo,
                         color=style['color'],
                         linestyle=style['linestyle'],
                         linewidth=style['linewidth'])
        ax2.set_title(f'{pname} Function – Convergence (D=30)', fontsize=13, fontweight='bold')
        ax2.set_xlabel('Iteration', fontsize=11)
        ax2.set_ylabel('Best Fitness (log)', fontsize=11)
        ax2.legend(fontsize=11)
        ax2.grid(True, which='both', alpha=0.3)
        plt.tight_layout()
        single_path = f'reports/convergence_{pname}.png'
        plt.savefig(single_path, dpi=150, bbox_inches='tight')
        print(f"  Saved: {single_path}")
        plt.close()


def plot_bar_comparison(results, save_path='reports/benchmark_comparison.png'):
    """
    Grouped bar chart: mean best fitness per function/algorithm (log scale).
    Includes error bars (std).
    """
    problems = list(results.keys())
    algorithms = list(_ALGO_STYLES.keys())
    colors = [_ALGO_STYLES[a]['color'] for a in algorithms]

    x = np.arange(len(problems))
    width = 0.25

    fig, ax = plt.subplots(figsize=(12, 6))

    for j, (algo, color) in enumerate(zip(algorithms, colors)):
        means = [results[p][algo]['mean'] for p in problems]
        stds  = [results[p][algo]['std']  for p in problems]
        ax.bar(x + j * width, means, width, label=algo, color=color, alpha=0.85,
               yerr=stds, capsize=4, error_kw={'linewidth': 1.2})

    ax.set_xlabel('Benchmark Function', fontsize=12)
    ax.set_ylabel('Mean Best Fitness (log scale)', fontsize=12)
    ax.set_title('Algorithm Comparison on Benchmark Functions\n(Lower is Better)',
                 fontsize=13, fontweight='bold')
    ax.set_xticks(x + width)
    ax.set_xticklabels(problems, fontsize=11)
    ax.set_yscale('log')
    ax.legend(fontsize=11)
    ax.grid(axis='y', alpha=0.3)

    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    print(f"Bar comparison saved: {save_path}")
    plt.close()


# ---------------------------------------------------------------------------
# Summary Table
# ---------------------------------------------------------------------------
def print_summary_table(results):
    """Print and return a nicely-formatted DataFrame."""
    rows = []
    for pname, algos in results.items():
        for algo, stats in algos.items():
            rows.append({
                'Problem':   pname,
                'Algorithm': algo,
                'Mean':      f"{stats['mean']:.4e}",
                'Std':       f"{stats['std']:.4e}",
                'Best':      f"{stats['best']:.4e}",
                'Worst':     f"{stats['worst']:.4e}",
            })
    df = pd.DataFrame(rows)
    sep = '=' * 72
    print(f"\n{sep}")
    print("  BENCHMARK RESULTS  (D=30, 25 runs, 500 iterations, Pop=40)")
    print(sep)
    print(df.to_string(index=False))
    print(sep)
    return df


# ---------------------------------------------------------------------------
# Entry Point
# ---------------------------------------------------------------------------
def main(dim=30, max_iters=500, pop_size=40, num_runs=25):
    problems   = [Sphere, Rosenbrock, Rastrigin, Griewank]
    algorithms = ['PSO', 'ABC', 'ABC-PSO']

    print("\n" + "=" * 60)
    print("  STARTING BENCHMARK SUITE")
    print("=" * 60)
    print(f"  Problems   : {[p.__name__ for p in problems]}")
    print(f"  Algorithms : {algorithms}")
    print(f"  Dimension  : {dim}")
    print(f"  Max Iters  : {max_iters}")
    print(f"  Pop Size   : {pop_size}")
    print(f"  Num Runs   : {num_runs}")
    print(f"  Total runs : {len(problems) * len(algorithms) * num_runs}")
    print("=" * 60 + "\n")

    results = run_benchmark(problems, algorithms,
                            dim=dim, max_iters=max_iters,
                            pop_size=pop_size, num_runs=num_runs)

    # Persist
    with open('reports/benchmark_results.json', 'w') as f:
        json.dump(results, f, indent=4)
    print("\nResults saved → reports/benchmark_results.json")

    # Plots
    plot_convergence(results)
    plot_bar_comparison(results)

    # Table
    df = print_summary_table(results)
    df.to_csv('reports/benchmark_summary.csv', index=False)
    print("Summary CSV  → reports/benchmark_summary.csv")

    return results


if __name__ == '__main__':
    main()
