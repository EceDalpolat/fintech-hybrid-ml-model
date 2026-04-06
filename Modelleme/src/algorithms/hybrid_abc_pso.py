import numpy as np
import random
from niapy.algorithms.algorithm import Algorithm

class ABCPSO(Algorithm):
    """
    Hybrid ABC-PSO Algorithm.
    Based on: Khuat, T. T., & Le, M. H. (2018). 
    A Novel Hybrid ABC-PSO Algorithm for Effort Estimation of Software Projects Using Agile Methodologies.
    """
    def __init__(self, population_size=40, w=0.729, c1=1.494, c2=1.494, limit=100, *args, **kwargs):
        super().__init__(population_size, *args, **kwargs)
        self.w = w
        self.c1 = c1
        self.c2 = c2
        self.limit = limit

    def set_parameters(self, population_size=40, w=0.729, c1=1.494, c2=1.494, limit=100, **kwargs):
        super().set_parameters(population_size=population_size, **kwargs)
        self.w = w
        self.c1 = c1
        self.c2 = c2
        self.limit = limit

    def get_parameters(self):
        d = super().get_parameters()
        d.update({
            'w': self.w,
            'c1': self.c1,
            'c2': self.c2,
            'limit': self.limit
        })
        return d

    def init_population(self, task):
        pop, fpos, _ = super().init_population(task)
        # Initialize velocity for PSO
        velocity = np.zeros((self.population_size, task.dimension))
        for i in range(self.population_size):
            velocity[i] = task.lower + np.random.rand(task.dimension) * (task.upper - task.lower)
            
        # Pbest (Personal best) positions and fitness
        pbest_x = np.copy(pop)
        pbest_f = np.copy(fpos)
        
        # Trial counters for scouting
        trial = np.zeros(self.population_size)

        # Global best
        best_idx = np.argmin(fpos)
        self.best_x = np.copy(pop[best_idx])
        self.best_f = fpos[best_idx]
        
        return pop, fpos, velocity, pbest_x, pbest_f, trial

    def run_iteration(self, task, pop, fpos, velocity, pbest_x, pbest_f, trial, **params):
        # 1. Employed Bees / PSO Phase
        for i in range(self.population_size):
            # Update velocity
            r1, r2 = np.random.rand(task.dimension), np.random.rand(task.dimension)
            velocity[i] = self.w * velocity[i] + \
                          self.c1 * r1 * (pbest_x[i] - pop[i]) + \
                          self.c2 * r2 * (self.best_x - pop[i])
            
            # Update position
            pop[i] = pop[i] + velocity[i]
            pop[i] = task.repair(pop[i], **params)
            fpos[i] = task.eval(pop[i])
            
            # Update Pbest
            if fpos[i] < pbest_f[i]:
                pbest_f[i] = fpos[i]
                pbest_x[i] = np.copy(pop[i])
                trial[i] = 0
            else:
                trial[i] += 1

        # 2. Onlooker Bees Phase
        # Better fitness calculation to avoid div by zero or extreme values
        fitness = np.zeros(self.population_size)
        eps = 1e-10
        for i in range(self.population_size):
            if pbest_f[i] >= 0:
                fitness[i] = 1.0 / (1.0 + pbest_f[i] + eps)
            else:
                fitness[i] = 1.0 + np.abs(pbest_f[i])
        
        sum_fit = np.sum(fitness)
        if sum_fit == 0 or np.isnan(sum_fit):
            prob = np.ones(self.population_size) / self.population_size
        else:
            prob = fitness / sum_fit
        
        for _ in range(self.population_size):
            # Selection
            i = np.random.choice(range(self.population_size), p=prob)
            
            # Update
            new_x = np.copy(pbest_x[i])
            m = np.random.randint(task.dimension)
            k = np.random.randint(self.population_size)
            while k == i and self.population_size > 1:
                k = np.random.randint(self.population_size)
            
            phi = np.random.uniform(-1, 1)
            new_x[m] = pbest_x[i][m] + phi * (pbest_x[i][m] - pbest_x[k][m])
            new_x = task.repair(new_x, **params)
            new_f = task.eval(new_x)
            
            # Selection
            if new_f < pbest_f[i]:
                pbest_f[i] = new_f
                pbest_x[i] = np.copy(new_x)
                pop[i] = np.copy(new_x)
                fpos[i] = new_f
                trial[i] = 0
            else:
                trial[i] += 1

        # 3. Scout Bees Phase
        for i in range(self.population_size):
            if trial[i] > self.limit:
                pop[i] = task.lower + np.random.uniform(0, 1, task.dimension) * (task.upper - task.lower)
                fpos[i] = task.eval(pop[i])
                pbest_x[i] = np.copy(pop[i])
                pbest_f[i] = fpos[i]
                velocity[i] = np.zeros(task.dimension)
                trial[i] = 0

        return pop, fpos, velocity, pbest_x, pbest_f, trial

    def run(self, task):
        pop, fpos, velocity, pbest_x, pbest_f, trial = self.init_population(task)
        history = []
        
        # Self variables for Algorithm class compatibility if needed
        self.best_x = pbest_x[np.argmin(pbest_f)]
        self.best_f = np.min(pbest_f)
        
        while not task.stopping_condition():
            pop, fpos, velocity, pbest_x, pbest_f, trial = self.run_iteration(
                task, pop, fpos, velocity, pbest_x, pbest_f, trial
            )
            
            best_idx = np.argmin(pbest_f)
            if pbest_f[best_idx] < self.best_f:
                self.best_f = pbest_f[best_idx]
                self.best_x = np.copy(pbest_x[best_idx])
            
            history.append(self.best_f)
            task.next_iter()
                
        return self.best_x, self.best_f, history
