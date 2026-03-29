import numpy as np
import logging
from niapy.problems import Problem
from niapy.task import Task
from niapy.algorithms.basic import ParticleSwarmOptimization, ArtificialBeeColonyAlgorithm
from src.algorithms.hybrid_abc_pso import ABCPSO
from sklearn.model_selection import cross_val_score
from sklearn.base import clone

logger = logging.getLogger(__name__)

class HyperparameterOptimizationProblem(Problem):
    def __init__(self, model, X, y, param_bounds, cv=3, n_jobs=-1, scoring='f1_weighted', population_size=20):
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
        self.scoring = scoring
        self.population_size = population_size
        
        dimension = len(self.param_names)
        lower = [b[0] for b in param_bounds.values()]
        upper = [b[1] for b in param_bounds.values()]
        
        super().__init__(dimension=dimension, lower=lower, upper=upper)
        self.call_count = 0
        self.best_score_so_far = -1.0

    @staticmethod
    def _map_params(x, param_names):
        """
        Convert continuous NiaPy values to correct types and ranges.
        """
        params = {}
        for i, name in enumerate(param_names):
            val = x[i]
            # RF and other integer parameters
            if any(k in name for k in ['n_estimators', 'max_depth', 'min_samples_split', 'min_samples_leaf', 'num_leaves']):
                val = int(round(val))
                # Constraints
                if 'min_samples_split' in name: val = max(2, val)
                elif 'min_samples_leaf' in name: val = max(1, val)
                elif 'n_estimators' in name: val = max(10, val) # Realistic minimum
                elif 'max_depth' in name and val < 1: val = None # Support None for max_depth
            
            params[name] = val
        return params

    def _evaluate(self, x):
        """
        Fitness function: Evaluate model performance.
        """
        params = self._map_params(x, self.param_names)
        model = clone(self.model)
        model.set_params(**params)
        
        try:
            scores = cross_val_score(model, self.X, self.y, cv=self.cv, n_jobs=self.n_jobs, scoring=self.scoring)
            mean_score = scores.mean()
            fitness = 1 - mean_score
            self.call_count += 1
            
            logger.debug(f"Parameters: {params} -> {self.scoring}: {mean_score:.4f}")
            
            if mean_score > self.best_score_so_far:
                self.best_score_so_far = mean_score
            
            # Dynamic logging based on population size (every iteration)
            if self.call_count % self.population_size == 0:
                logger.info(f"Iteration {self.call_count // self.population_size}: Best {self.scoring} so far: {self.best_score_so_far:.4f}")
                
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
            n_jobs=self.opt_config.get('n_jobs', -1),
            scoring=self.opt_config.get('scoring', 'f1_weighted'),
            population_size=self.niapy_params.get('population_size', 20)
        )
        
        max_iters = self.niapy_params.get('max_iters', 100)
        task = Task(problem, max_iters=max_iters)
        
        pop_size = self.niapy_params.get('population_size', 20)
        
        if algorithm == 'pso':
            algo = ParticleSwarmOptimization(population_size=pop_size)
        elif algorithm == 'abc':
            algo = ArtificialBeeColonyAlgorithm(population_size=pop_size)
        elif algorithm == 'abc-pso':
            algo = ABCPSO(population_size=pop_size, 
                          w=self.niapy_params.get('w', 0.729),
                          c1=self.niapy_params.get('c1', 1.494),
                          c2=self.niapy_params.get('c2', 1.494),
                          limit=self.niapy_params.get('limit', 100))
        else:
            raise ValueError(f"Unknown algorithm: {algorithm}")
            
        logger.info(f"Running optimization for {max_iters} iterations with population {pop_size}...")
        best_x, best_fitness = algo.run(task)
        
        # Extract best parameters using centralized mapping
        best_params = problem._map_params(best_x, list(self.bounds.keys()))
            
        logger.info("Optimization complete.")
        logger.info(f"Best Fitness (Error): {best_fitness:.4f}")
        logger.info(f"Best {problem.scoring}: {1 - best_fitness:.4f}")
        logger.info(f"Best Params: {best_params}")
        
        best_model = clone(self.model)
        best_model.set_params(**best_params)
        best_model.fit(X, y)
        
        return best_model, best_params
