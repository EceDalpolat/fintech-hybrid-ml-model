"""
Hyperparameter optimisation via NiaPy meta-heuristics.
Supports PSO, ABC, and the hybrid ABC-PSO algorithm.
Convergence history (best CV score per iteration) is tracked and returned.
"""
import numpy as np
import logging
from niapy.problems import Problem
from niapy.task import Task
from niapy.algorithms.basic import ParticleSwarmOptimization, ArtificialBeeColonyAlgorithm
from src.algorithms.hybrid_abc_pso import ABCPSO
from sklearn.model_selection import cross_validate, ShuffleSplit
from sklearn.base import clone

logger = logging.getLogger(__name__)


class HyperparameterOptimizationProblem(Problem):
    """
    NiaPy Problem wrapper: maps a continuous vector to RF hyperparameters
    and evaluates them via stratified cross-validation.

    Convergence tracking
    --------------------
    - `self.iter_history`  : list of best CV score seen *at the end of each
                              complete iteration* (one value per pop_size calls).
    - `self.eval_history`  : best CV score seen at *every individual call*
                              (useful for fine-grained analysis).
    """

    def __init__(self, model, X, y, param_bounds,
                 cv=3, n_jobs=-1, scoring='f1_weighted', population_size=20):
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
        self.eval_history = []     # (call_index, best_score) at every eval
        self.iter_history = []     # best_score at end of each iteration

    # ------------------------------------------------------------------
    @staticmethod
    def _map_params(x, param_names):
        """Convert continuous NiaPy vector to typed hyperparameters."""
        params = {}
        for i, name in enumerate(param_names):
            val = x[i]
            if any(k in name for k in [
                    'n_estimators', 'max_depth', 'n_neighbors',
                    'min_samples_split', 'min_samples_leaf', 'num_leaves']):
                val = int(round(val))
                if 'min_samples_split' in name:
                    val = max(2, val)
                elif 'min_samples_leaf' in name:
                    val = max(1, val)
                elif 'n_estimators' in name:
                    val = max(10, val)
                elif 'n_neighbors' in name:
                    val = max(1, val)
                elif 'max_depth' in name and val < 1:
                    val = None
            params[name] = val
        return params

    # ------------------------------------------------------------------
    def _evaluate(self, x):
        params = self._map_params(x, self.param_names)
        model = clone(self.model)
        model.set_params(**params)

        try:
            # We track multiple metrics but optimize for the one in config
            scoring_list = ['accuracy', 'balanced_accuracy', 'f1_weighted', 'precision_weighted', 'recall_weighted']
            cv_results = cross_validate(
                model, self.X, self.y,
                cv=self.cv, n_jobs=self.n_jobs, scoring=scoring_list
            )
            
            # Map of results
            scores_map = {m: cv_results[f'test_{m}'].mean() for m in scoring_list}
            mean_score = float(scores_map.get(self.scoring, 0.0))
            
            # Save all metrics for the log
            self.current_metrics = scores_map
            
        except Exception as e:
            logger.error(f"Error evaluating params {params}: {e}")
            mean_score = 0.0
            self.current_metrics = {}

        fitness = 1.0 - mean_score
        self.call_count += 1

        # Update running best
        if mean_score > self.best_score_so_far:
            self.best_score_so_far = mean_score

        # Per-evaluation record
        self.eval_history.append(self.best_score_so_far)

        # Per-iteration record (logged once per full population sweep)
        if self.call_count % self.population_size == 0:
            iteration = self.call_count // self.population_size
            self.iter_history.append(self.best_score_so_far)
            
            # Formulate a nice log string with multiple metrics
            m = self.current_metrics
            metrics_str = f"Acc: {m.get('accuracy',0):.4f} | BalAcc: {m.get('balanced_accuracy',0):.4f} | F1: {m.get('f1_weighted',0):.4f}"
            
            logger.info(
                f"Iter {iteration:3d} | BEST {self.scoring}: {self.best_score_so_far:.4f} | "
                f"Current {metrics_str} | params: {params}"
            )

        logger.debug(f"Params: {params} -> {self.scoring}: {mean_score:.4f}")
        return fitness


# ---------------------------------------------------------------------------
class NiapyOptimizer:
    """Wraps a NiaPy algorithm to optimise a sklearn pipeline's hyperparameters."""

    def __init__(self, model, config):
        self.model = model
        self.config = config
        self.opt_config   = config.get('optimization', {})
        self.niapy_params = self.opt_config.get('niapy_params', {})
        self.bounds       = self.niapy_params.get('bounds', {})

        if not self.bounds:
            raise ValueError("No parameter bounds defined for Niapy optimization.")

    # ------------------------------------------------------------------
    def optimize(self, X, y, algorithm='pso'):
        """
        Run meta-heuristic optimisation.

        Returns
        -------
        best_model   : fitted sklearn pipeline with best parameters
        best_params  : dict of best hyperparameter values
        iter_history : list[float] – best CV score at end of each iteration
        """
        pop_size  = self.niapy_params.get('population_size', 20)
        max_iters = self.niapy_params.get('max_iters', 100)

        logger.info(
            f"Starting {algorithm.upper()} | pop={pop_size} | iters={max_iters} "
            f"| total evals≈{pop_size * max_iters}"
        )

        cv_param = self.opt_config.get('cv', 3)
        if cv_param == 1:
            cv_param = ShuffleSplit(n_splits=1, test_size=0.2, random_state=42)

        problem = HyperparameterOptimizationProblem(
            self.model, X, y, self.bounds,
            cv=cv_param,
            n_jobs=1,
            scoring=self.opt_config.get('scoring', 'f1_weighted'),
            population_size=pop_size,
        )
        task = Task(problem, max_iters=max_iters)

        if algorithm == 'pso':
            algo = ParticleSwarmOptimization(population_size=pop_size)
        elif algorithm == 'abc':
            algo = ArtificialBeeColonyAlgorithm(population_size=pop_size)
        elif algorithm == 'abc-pso':
            algo = ABCPSO(
                population_size=pop_size,
                w=self.niapy_params.get('w', 0.729),
                c1=self.niapy_params.get('c1', 1.494),
                c2=self.niapy_params.get('c2', 1.494),
                limit=self.niapy_params.get('limit', 100),
            )
        else:
            raise ValueError(f"Unknown algorithm: {algorithm}")

        run_result = algo.run(task)
        if len(run_result) == 3:
            best_x, best_fitness, _ = run_result
        else:
            best_x, best_fitness = run_result

        # Map best vector → hyperparameter dict (strip prefix if present)
        raw_params = problem._map_params(best_x, list(self.bounds.keys()))
        # Remove pipeline prefix (e.g. 'classifier__') for clean logging
        best_params = {k.replace('classifier__', ''): v for k, v in raw_params.items()}

        best_cv = 1.0 - best_fitness
        logger.info("=" * 50)
        logger.info(f"Optimisation complete: {algorithm.upper()}")
        logger.info(f"  Best fitness (error) : {best_fitness:.4f}")
        logger.info(f"  Best {problem.scoring:15s}: {best_cv:.4f}")
        logger.info(f"  Best params          : {raw_params}")
        logger.info("=" * 50)

        # Refit on full training set with best params
        best_model = clone(self.model)
        best_model.set_params(**raw_params)
        best_model.fit(X, y)

        iter_history = problem.iter_history
        return best_model, raw_params, iter_history
