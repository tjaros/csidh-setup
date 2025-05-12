#!/usr/bin/env python
# coding: utf-8

# # Comparison of random search versus genetic algorithm
# In this notebook, we first perform an experiment with random search glitching, following that we do the same using the genetic algorithm. 

# In[ ]:


SCOPETYPE = 'OPENADC'
PLATFORM = 'CW308_STM32F3'
SS_VER = 'SS_VER_2_1'
PATH = "/home/xjaros2/Documents/git/csidh-setup/csidh-target/src/"
attack_type = "A1"


# In[ ]:


from csidh import CSIDHCW
import chipwhisperer as cw
from tqdm import tqdm
import random
import time
import sys
import numpy as np
from csidh.search import Unit, generate_population, evaluate_batch, selection_roulette, cache, write_cache_to_file, evaluate_unit_default


# In[ ]:


csidh = CSIDHCW(PATH, attack_type=attack_type)
csidh.setup()


# In[ ]:


csidh.flash_target()


# In[ ]:


csidh.reset_target()
csidh.scope.arm()
csidh.action()
ret = csidh.scope.capture()
if ret:
    print("Timeout happened during acquisition")
PUBLIC_EXPECTED = csidh.public_with_errors
MAX_EXT_OFFSET = csidh.scope.adc.trig_count
print("Public key:", PUBLIC_EXPECTED)
print("Max ext offset:", MAX_EXT_OFFSET)


# In[ ]:


# csidh.voltage_glitching_setup()
csidh.scope.cglitch_setup()


# In[ ]:


Unit.is_husky = csidh.scope._is_husky

if Unit.is_husky:
    Unit.OFFSET_MIN = 0 
    Unit.OFFSET_MAX = csidh.scope.glitch.phase_shift_steps // 2 	
    Unit.OFFSET_RANGE = Unit.OFFSET_MAX - Unit.OFFSET_MIN

    Unit.WIDTH_MIN = 0
    Unit.WIDTH_MAX = csidh.scope.glitch.phase_shift_steps // 2
    Unit.WIDTH_RANGE = Unit.WIDTH_MAX - Unit.WIDTH_MIN
else:
    Unit.OFFSET_MIN = -48 	 
    Unit.OFFSET_MAX = 48
    Unit.OFFSET_RANGE = Unit.OFFSET_MAX - Unit.OFFSET_MIN

    Unit.WIDTH_MIN = 0
    Unit.WIDTH_MAX = 48
    Unit.WIDTH_RANGE = Unit.WIDTH_MAX - Unit.WIDTH_MIN

Unit.EXT_OFFSET_MIN = 0
Unit.EXT_OFFSET_MAX = MAX_EXT_OFFSET // 4 
Unit.EXT_OFFSET_RANGE = Unit.EXT_OFFSET_MAX - Unit.EXT_OFFSET_MIN

Unit.REPEAT_MIN = 1
Unit.REPEAT_MAX = 10


# In[ ]:


# POPULATION_SIZE = 10000
# CACHE_INTERVAL = 10
# NUM_TRIES = 3

# cache.clear()

# def evaluate_unit(csidh, unit):
#     evaluate_unit_default(csidh, unit, NUM_TRIES)

# population = generate_population(POPULATION_SIZE)
# for i in tqdm(range(0, len(population), CACHE_INTERVAL)):
#     batch = population[i:i+CACHE_INTERVAL]
#     evaluate_batch(csidh, batch, evaluate_unit)
#     write_cache_to_file(f"husky-clock-param-search-random.json", cache, 1, len(cache), -1)  


# In[ ]:


N_ITERS = 40
POPSIZE = 250

cache.clear()

def algo_search(csidh):
    population = generate_population(POPSIZE)
    N_scanned = []
    for i in tqdm(range(N_ITERS)):
        fits = evaluate_batch(csidh, population)
        population = selection_roulette(population, elite_size=1)
        tgen = time.time()

    N_scanned.append(len(cache))
    write_cache_to_file("husky-clock-param-search-ga.json", cache, N_ITERS, POPSIZE, -1)

algo_search(csidh)

