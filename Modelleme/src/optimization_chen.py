import numpy as np
import logging
import copy
from sklearn.model_selection import cross_val_score

logger = logging.getLogger(__name__)

class ChenHybridOptimizer:
    """
    Implementation of the Hybrid ABC-PSO Algorithm based on:
    Chen et al. (2020) - "A New Hybrid Algorithm Based on ABC and PSO for Function Optimization"
    """
    def __init__(self, pipeline, config):
        self.pipeline = pipeline
        self.config = config
        self.bounds = config['optimization']['niapy_params']['bounds']
        self.pop_size = config['optimization']['niapy_params'].get('population_size', 20)
        self.max_iters = config['optimization']['niapy_params'].get('max_iters', 20)
        self.cv = config['optimization'].get('cv', 3)
        self.scoring = config['optimization'].get('scoring', 'accuracy')
        
        self.param_names = list(self.bounds.keys())
        self.lower_bounds = np.array([self.bounds[p][0] for p in self.param_names])
        self.upper_bounds = np.array([self.bounds[p][1] for p in self.param_names])
        self.dim = len(self.param_names)
        self.fitness_cache = {}

    def _get_fitness(self, position, X, y):
        # Convert position to a tuple of rounded/formatted values for caching
        cache_key = tuple([round(p, 4) for p in position])
        if cache_key in self.fitness_cache:
            return self.fitness_cache[cache_key]
            
        params = {}
        for i, name in enumerate(self.param_names):
            val = position[i]
            # Handle integer parameters
            if name in ['classifier__n_estimators', 'classifier__max_depth', 'classifier__min_samples_split', 'classifier__min_samples_leaf']:
                params[name] = int(round(val))
            else:
                params[name] = val
        
        try:
            self.pipeline.set_params(**params)
            scores = cross_val_score(self.pipeline, X, y, cv=self.cv, scoring=self.scoring, n_jobs=1)
            fit_val = np.mean(scores)
            self.fitness_cache[cache_key] = fit_val
            return fit_val
        except Exception as e:
            logger.error(f"Fitness evaluation error: {e}")
            return 0.0

    def optimize(self, X, y):
        logger.info("Starting Optimized Chen (2020) Hybrid ABC-PSO...")
        
        # Initialization
        pop = np.random.uniform(self.lower_bounds, self.upper_bounds, (self.pop_size, self.dim))
        vel = np.zeros((self.pop_size, self.dim))
        fitness = np.array([self._get_fitness(p, X, y) for p in pop])
        
        pbest = copy.deepcopy(pop)
        pbest_fit = copy.deepcopy(fitness)
        gbest_idx = np.argmax(fitness)
        gbest = copy.deepcopy(pop[gbest_idx])
        gbest_fit = fitness[gbest_idx]
        
        history = []
        
        for t in range(self.max_iters):
            # Equation 10: Dynamic weight for sine-cosine balance
            w = 0.9 - t * (0.5 / self.max_iters) 
            
            for i in range(self.pop_size):
                # --- PSO Phase with Sine-Cosine (Equation 9) ---
                r1 = 2.0 * np.pi * np.random.rand()
                r2 = np.random.rand()
                
                old_pos = copy.deepcopy(pop[i])
                if r2 < 0.5:
                    vel[i] = w * vel[i] + np.sin(r1) * np.abs(pbest[i] - pop[i]) + np.sin(r1) * np.abs(gbest - pop[i])
                else:
                    vel[i] = w * vel[i] + np.cos(r1) * np.abs(pbest[i] - pop[i]) + np.cos(r1) * np.abs(gbest - pop[i])
                
                pop[i] = np.clip(pop[i] + vel[i], self.lower_bounds, self.upper_bounds)
                
                # Evaluate PSO move (using cache)
                fit_i = self._get_fitness(pop[i], X, y)
                
                # --- ABC Phase with Crossover (Equation 7-8) ---
                k = np.random.randint(0, self.pop_size)
                if self.pop_size > 1:
                    while k == i: k = np.random.randint(0, self.pop_size)
                
                r_cross = np.random.rand()
                offspring = r_cross * pop[i] + (1 - r_cross) * pop[k]
                offspring = np.clip(offspring, self.lower_bounds, self.upper_bounds)
                
                fit_off = self._get_fitness(offspring, X, y)
                
                if fit_off > fit_i:
                    pop[i] = offspring
                    fit_i = fit_off
                
                # Update personal and global best
                if fit_i > pbest_fit[i]:
                    pbest[i] = copy.deepcopy(pop[i])
                    pbest_fit[i] = fit_i
                    
                    if fit_i > gbest_fit:
                        gbest = copy.deepcopy(pop[i])
                        gbest_fit = fit_i
            
            history.append(gbest_fit)
            logger.info(f"Iter {t+1}/{self.max_iters} | Best Accuracy: {gbest_fit:.4f} | Cache Size: {len(self.fitness_cache)}")

            
        # Prepare final best params
        best_params = {}
        for i, name in enumerate(self.param_names):
            val = gbest[i]
            if name in ['classifier__n_estimators', 'classifier__max_depth', 'classifier__min_samples_split', 'classifier__min_samples_leaf']:
                best_params[name] = int(round(val))
            else:
                best_params[name] = val
                
        self.pipeline.set_params(**best_params)
        return self.pipeline, best_params, history
