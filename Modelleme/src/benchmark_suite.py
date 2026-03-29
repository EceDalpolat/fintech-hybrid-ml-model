import sys
import os
import numpy as np
import pandas as pd
import json

# Add project root to path
parent = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if parent not in sys.path:
    sys.path.insert(0, parent)

from niapy.task import Task
from niapy.problems import Sphere, Rosenbrock, Rastrigin, Griewank
from niapy.algorithms.basic import ParticleSwarmOptimization, ArtificialBeeColonyAlgorithm
from src.algorithms.hybrid_abc_pso import ABCPSO
import matplotlib.pyplot as plt

# Ensure output directory exists
os.makedirs('reports', exist_ok=True)

class ConvergenceLogger:
    def __init__(self):
        self.history = []
        self.best_f = float('inf')

    def log(self, fitness):
        if fitness < self.best_f:
            self.best_f = fitness
        self.history.append(self.best_f)

def run_experiment(problem_class, algorithm_name, dim=30, max_iters=50, pop_size=40, num_runs=5):
    final_results = []
    histories = []
    
    print(f"Running {algorithm_name} on {problem_class.__name__}...")
    
    for run in range(num_runs):
        problem = problem_class(dimension=dim)
        
        from niapy.problems import Problem
        class LoggedProblem(Problem):
            def __init__(self, p):
                super().__init__(dimension=p.dimension, lower=p.lower, upper=p.upper)
                self.p = p
                self.history = []
                self.best = float('inf')
            
            def _evaluate(self, x):
                f = self.p.evaluate(x)
                if f < self.best:
                    self.best = f
                # We log evaluations, but for convergence we want the best so far
                self.history.append(self.best)
                return f
            
            def repair(self, x, **params):
                return self.p.repair(x, **params)

        lp = LoggedProblem(problem)
        task = Task(problem=lp, max_iters=max_iters)
        
        if algorithm_name == 'PSO':
            algo = ParticleSwarmOptimization(population_size=pop_size)
        elif algorithm_name == 'ABC':
            algo = ArtificialBeeColonyAlgorithm(population_size=pop_size)
        elif algorithm_name == 'ABC-PSO':
            algo = ABCPSO(population_size=pop_size, limit=max_iters//10)
        
        result = algo.run(task)
        
        # Determine best fitness and history
        if algorithm_name == 'ABC-PSO':
            # Our custom run returns (best_x, best_f, history)
            best_x, best_f, h = result
        else:
            # NiaPy run returns (best_x, best_f)
            best_x, best_f = result
            # Use the history collected in lp.evaluate
            # Note: lp.history has length = evals. We want it more sampled or full.
            h = lp.history
            
        final_results.append(best_f)
        histories.append(h)
        
    return {
        'mean': np.mean(final_results),
        'std': np.std(final_results),
        'best': np.min(final_results),
        'histories': histories
    }

def main():
    problems = [Sphere, Rosenbrock, Rastrigin, Griewank]
    algorithms = ['PSO', 'ABC', 'ABC-PSO']
    
    results = {}
    
    for prob in problems:
        prob_name = prob.__name__
        results[prob_name] = {}
        for algo in algorithms:
            print(f"\n--- Starting Experiment: {algo} on {prob_name} ---")
            res = run_experiment(prob, algo, num_runs=5)
            results[prob_name][algo] = res
            print(f"Finished {algo} on {prob_name}. Mean Fitness: {res['mean']:.2e}")
            
    # Save Results
    with open('reports/benchmark_results.json', 'w') as f:
        json.dump(results, f, indent=4)
        
    # Print Table
    df_list = []
    for prob, algos in results.items():
        for algo, metrics in algos.items():
            df_list.append({
                'Problem': prob,
                'Algorithm': algo,
                'Mean Fitness': f"{metrics['mean']:.2e}",
                'Std': f"{metrics['std']:.2e}",
                'Best': f"{metrics['best']:.2e}"
            })
    
    df = pd.DataFrame(df_list)
    print("\nBenchmark Results Summary:")
    print(df.to_string(index=False))
    
    # Simple Plotting logic for a summary (Convergence testing would need more granular data)
    # We will generate convergence data in a more detailed run later for the main report.

if __name__ == '__main__':
    main()
