# -*- coding: utf-8 -*-
"""
Created on Mon Apr 20 12:11:38 2026

@author: agilj

Here, we use a genetic algorithm to optimize the filter stack over a specified
loss function.
"""

import numpy as np
import polars as pl
import os
import matplotlib.pyplot as plt

from ClassFile_FilmStack_forOptim import film_stack

"""
Class to hold the genetic optimizer.

Parameters:
    pop_size: int
        The total size of the population. That is, the number of different
        filter stacks to keep track of at one time.
    perc_to_keep: float
        Between 0 and 1. The percentage of solutions that we keep / allow to
        reproduce.
    min_num_layers: int
        The minimum number of layers to allow in a filter.
    max_num_layers: int
        The maximum number of layers to allow in a filter.
    min_layer_thick: int
        The minimum thickness, in nm, of each layer.
    max_layer_thick: int
        The maximum thickness, in nm, of each layer.
    max_total_thick: float
        The maximum thickness, in nm, of the total filter stack.
    
"""
class genetic_optimizer():
    def __init__(self, pop_size, perc_to_keep, fitness_fun,
                 wvl_min = 450, wvl_max = 1000,
                 min_num_layers=10, max_num_layers=24, 
                 min_layer_thick=50, max_layer_thick=500,
                 max_total_thick=10000, seed=0):
        # Save optimization bounds.
        self.pop_size = pop_size
        self.perc_to_keep = perc_to_keep
        self.min_num_layers = min_num_layers
        self.max_num_layers = max_num_layers
        self.min_layer_thick = min_layer_thick
        self.max_layer_thick = max_layer_thick
        self.max_total_thick = max_total_thick
        
        # Get available materials.
        mat_loc = './materials/ThinFilmMaterials_vis'
        self.mat_list = os.listdir(mat_loc)
        self.mat_list = [self.mat_list[i][:-4] 
                    for i,_ in enumerate(self.mat_list)]
        self.mat_list.remove('Si')
        self.mat_list.append('Air')
        self.mat_funs_n = {}
        self.mat_funs_k = {}
        for mat in self.mat_list:
            if mat == 'Air':
                self.mat_funs_n[mat] = lambda wvl: np.ones_like(wvl)
                self.mat_funs_k[mat] = lambda wvl: np.zeros_like(wvl)
            else:
                real_fun, \
                imag_fun = self._prep_materials(mat_loc+'/'+mat+'.csv')
                
                self.mat_funs_n[mat] = real_fun
                self.mat_funs_k[mat] = imag_fun
        # Now tack on Si substrate material.
        real_fun, \
        imag_fun = self._prep_materials(mat_loc+'/Si.csv')
        self.mat_funs_n['Si'] = real_fun
        self.mat_funs_k['Si'] = imag_fun
        
        # Build RNG.
        self.rng = np.random.default_rng(seed)
        
        # Specify the fitness function.
        self.fitness_fun = fitness_fun
        
        # Save wavelengths.
        self.wvl = np.linspace(wvl_min, wvl_max, 500)
    
    def optimize(self):
        # Create initial population.
        stack_set = self._initialize()
        
        # Compute fitness
        
        # Keep the top X percent.
        
        # Those survivors reproduce to the total population size minus 3.
        
        # Parents die off (except the top 3).
        
        # Children mutate.
    
    """
    Method to create the initial population of filters.
    
    Returns:
        list: The population of filter stacks.
    """
    def _initialize(self):
        # Get parameters for each member of population.
        num_layers = self.rng.integers(self.min_num_layers, 
                                       self.max_num_layers+1,
                                       size=(self.pop_size,))
        layer_thicks = [self.rng.integers(self.min_layer_thick,
                                          self.max_layer_thick,
                                          size=(num_layers[i],)) 
                        for i in range(self.pop_size)]
        # Ensure we don't exceed the maximum filter thickness.
        filter_thicks = [layer_thicks[i].sum() 
                         for i in range(self.pop_size)]
        filter_thicks = np.asarray(filter_thicks)
        too_thick = (filter_thicks > self.max_total_thick)
        while too_thick.any():
            # Replace the too-thick filters.
            too_thick_inds = np.where(too_thick)[0]
            new_thicks = [self.rng.integers(self.min_layer_thick,
                                            self.max_layer_thick,
                                            size = (num_layers[i],))
                          for i in too_thick_inds]
            for i, stack in enumerate(new_thicks):
                layer_thicks[too_thick_inds[i]] = stack
            # Get new thicknesses
            filter_thicks = [layer_thicks[i].sum() 
                             for i in range(self.pop_size)]
            filter_thicks = np.asarray(filter_thicks)
            too_thick = (filter_thicks > self.max_total_thick)  
        # Get materials.
        num_mats = len(self.mat_list)
        mat_inds = [self.rng.integers(0, 
                                      num_mats,
                                      size=(num_layers[i]))
                    for i in range(self.pop_size)]
        layer_mats = [list(np.asarray(self.mat_list)[mat_inds[i]])
                      for i in range(self.pop_size)]
        for i in range(self.pop_size):
            layer_mats[i].append('Si')
            layer_mats[i].insert(0,'Air')
        # Now build filter stacks.
        pop = [film_stack(layer_mats[i],
                          layer_thicks[i], 
                          mat_funs=(self.mat_funs_n, self.mat_funs_k)) 
               for i in range(self.pop_size)]
    
    return pop

    def _compute_fitness(self, guess):
        pass
    
    def _select_survivors(self, num_survivors):
        pass
        
    def _reproduce(self):
        pass
    
    def _mutate(self, num_mutants, num_mutations):
        pass

    """
    Loads in the material files and creates the appropriate interpolation
    functions so that we don't have to do it for each of the film stacks.
    """
    def _prep_materials(self, matFile):
        # Air placeholder.
        if matFile == 'Air':
            return lambda wvl: np.ones_like(wvl), \
                   lambda wvl: np.zeros_like(wvl)
        # Actual file.
        if matFile[-4:] == '.csv':
            df = pl.read_csv(matFile,has_header=False)
            # Remove any missing data.
            df = df.drop_nulls()
            # Get all numeric data (as opposed to column headers) and create
            # a boolean column that indicates whether it is numeric or not.
            df = df.with_columns([
                pl.all_horizontal([
                    pl.col("column_1").cast(pl.Float64, strict=False)
                        .is_not_null(),
                    pl.col("column_2").cast(pl.Float64, strict=False)
                        .is_not_null()
                ]).alias("is_numeric")
            ])
            # Now group things between non-numeric entries.
            df = df.with_columns([
                    (~pl.col("is_numeric")).cast(pl.UInt32).cum_sum()\
                        .alias("group")
                 ])
            # Remove non-numeric entries.
            df_numeric = df.filter(pl.col("is_numeric")).select(["column_1", 
                                                                 "column_2", 
                                                                 "group"])
            # Convert grouped entries to arrays.
            arrays = [group.drop("group").cast(pl.Float64).to_numpy()
                      for _, group in df_numeric.group_by("group", 
                                                          maintain_order=True)
                     ]
            # The first array is the real part, the second is the imag part.
            nReal = arrays[0]
            try:
                nImag = arrays[1]
            except:
                nImag = np.concat((nReal[:,0][:,None],
                                   np.zeros_like(nReal[:,1][:,None])),axis=1)
            
            # Construct interpolation function for nReal.
            fInterp_real = lambda wvl: self._interp1d(nReal[:,0]*1e-6, #mm
                                                      nReal[:,1],
                                                      wvl)
            fInterp_imag = lambda wvl: self._interp1d(nImag[:,0]*1e-6, #mm
                                                      nImag[:,1],
                                                      wvl)
            return lambda wvl: fInterp_real(wvl), \
                   lambda wvl: fInterp_imag(wvl)

"""
The fitness function we want to optimize over.
"""
def fitness(filt):
    return 1
        
if __name__ == '__main__':
    # Specify parameters.
    pop_size = 1000
    perc_to_keep = 0.3
    fitness_fun = fitness
    
    # Build optimizer
    optim = genetic_optimizer(pop_size, perc_to_keep, fitness_fun)
    
    # Optimize
    outs = optim.optimize()

