import numpy as np
import logging
from niapy.problems import Problem
from niapy.task import Task
from niapy.algorithms.basic import ParticleSwarmOptimization, ArtificialBeeColonyAlgorithm
from sklearn.model_selection import cross_val_score
from sklearn.base import clone

logger = logging.getLogger(__name__)

class HyperparameterOptimizationProblem(Problem):
    def __init__(self, model, X, y, param_bounds, cv=3, n_jobs=-1):
        """
        Problem definition for Niapy.
        """
        self.model = model
        self.X = X
        self.y = y
        self.param_bounds = param_bounds
        self.param_names = list(param_bounds.keys())
        self.cv = cv
        self.n_jobs = n_jobs
        
        dimension = len(self.param_names)
        lower = [b[0] for b in param_bounds.values()]
        upper = [b[1] for b in param_bounds.values()]
        
        super().__init__(dimension=dimension, lower=lower, upper=upper)
        self.call_count = 0
        self.best_f1_so_far = -1.0

    def _evaluate(self, x):
        """
        Fitness function: Evaluate model performance.
        """
        params = {}
        for i, param_name in enumerate(self.param_names):
            val = x[i]
            # Integer conversion logic
            if any(key in param_name for key in ['n_estimators', 'max_depth', 'min_samples_split', 'min_samples_leaf', 'num_leaves']):
                val = int(round(val))
                if 'min_samples_split' in param_name and val < 2: val = 2
                if 'min_samples_leaf' in param_name and val < 1: val = 1
                if 'n_estimators' in param_name and val < 1: val = 1
                if 'max_depth' in param_name and val < 1: val = 1
            
            params[param_name] = val
            
        model = clone(self.model)
        model.set_params(**params)
        
        try:
            scores = cross_val_score(model, self.X, self.y, cv=self.cv, n_jobs=self.n_jobs, scoring='f1_weighted')
            fitness = 1 - scores.mean()
            self.call_count += 1
            
            logger.debug(f"Parameters: {params} -> F1 weighted: {scores.mean():.4f}")
            
            if scores.mean() > self.best_f1_so_far:
                self.best_f1_so_far = scores.mean()
            
            # Assuming population_size is roughly where an "iteration" ends
            # We can log every 50 evaluations (our pop_size)
            if self.call_count % 50 == 0:
                logger.info(f"Evaluation progress: {self.call_count} calls done. Best F1 weighted so far: {self.best_f1_so_far:.4f}")
                
            return fitness
        except Exception as e:
            logger.error(f"Error evaluating parameters {params}: {e}")
            return 1.0 # Max error

class NiapyOptimizer:
    def __init__(self, model, config):
        self.model = model
        self.config = config
        self.opt_config = config.get('optimization', {})
        self.niapy_params = self.opt_config.get('niapy_params', {})
        self.bounds = self.niapy_params.get('bounds', {})
        
        if not self.bounds:
            logger.error("No parameter bounds defined for Niapy optimization.")
            raise ValueError("No parameter bounds defined for Niapy optimization.")

    def optimize(self, X, y, algorithm='pso'):
        logger.info(f"Starting {algorithm.upper()} optimization...")
        
        problem = HyperparameterOptimizationProblem(
            self.model, X, y, self.bounds, 
            cv=self.opt_config.get('cv', 3),
            n_jobs=self.opt_config.get('n_jobs', -1)
        )
        
        max_iters = self.niapy_params.get('max_iters', 100)
        task = Task(problem, max_iters=max_iters)
        
        pop_size = self.niapy_params.get('population_size', 20)
        
        if algorithm == 'pso':
            algo = ParticleSwarmOptimization(population_size=pop_size)
        elif algorithm == 'abc':
            algo = ArtificialBeeColonyAlgorithm(population_size=pop_size)
        else:
            raise ValueError(f"Unknown algorithm: {algorithm}")
            
        logger.info(f"Running optimization for {max_iters} iterations with population {pop_size}...")
        best_x, best_fitness = algo.run(task)
        
        best_params = {}
        param_names = list(self.bounds.keys())
        for i, param_name in enumerate(param_names):
            val = best_x[i]
            if any(key in param_name for key in ['n_estimators', 'max_depth', 'min_samples_split', 'min_samples_leaf', 'num_leaves']):
                val = int(round(val))
                if 'min_samples_split' in param_name and val < 2: val = 2
                if 'min_samples_leaf' in param_name and val < 1: val = 1
                if 'n_estimators' in param_name and val < 1: val = 1
                if 'max_depth' in param_name and val < 1: val = 1
            best_params[param_name] = val
            
        logger.info("Optimization complete.")
        logger.info(f"Best Fitness (F1 Error): {best_fitness:.4f}")
        logger.info(f"Best Params: {best_params}")
        
        best_model = clone(self.model)
        best_model.set_params(**best_params)
        best_model.fit(X, y)
        
        return best_model, best_params
