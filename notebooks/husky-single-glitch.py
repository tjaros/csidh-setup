#!/usr/bin/env python
# coding: utf-8

# In[1]:


PATH = "/home/xjaros2/Documents/git/csidh-setup/"
SCOPETYPE = 'OPENADC'
PLATFORM = 'CW308_STM32F3'

SS_VER = 'SS_VER_2_1'
ATTACK_TYPE = "A1"
OPT="s"


# In[2]:


BENCH_MODE = 'NORMAL'
get_ipython().run_line_magic('cd', '$PATH/notebooks')
get_ipython().run_line_magic('run', './init.ipynb')
get_ipython().run_line_magic('cd', '$PATH/notebooks')


# For measuring time of successful glitches, we wait for acknowledgement packet
# 
# Otherwise we need to add a delay after `csidh.action()` is called, typically is around 0.2-0.25 seconds (dummy-free) approximately, if we run at 14MHz.

# In[3]:


csidh.wait_ack = True


# In[4]:


csidh.reset_target()
csidh.scope.arm()
csidh.action()
ret = csidh.scope.capture()
if ret:
    print("Timeout happened during acquisition")
PUBLIC_EXPECTED = csidh.public_with_errors
MAX_EXT_OFFSET = csidh.scope.adc.trig_count
print("#" * 80)
print(f"PUBLIC: {PUBLIC_EXPECTED}")
print(f"TRIGS:  {MAX_EXT_OFFSET}")
print("#" * 80)


# To make sure there were no unexpected changes to implementations, we hardcode the clock cycles based on different optimization levels, and make sure the first run corresponds to one of them.

# In[5]:


ext_offsets = {
    ("dummy", (0,0,0)): 955156,
    ("dummy", (5, -3, 1)): 1176474,
    ("dummy-free", (10, -6, 2)): 2789284
}
assert MAX_EXT_OFFSET in list(ext_offsets.values())

KEY = None
for (TYPE, key), cycles in ext_offsets.items():
    if cycles == MAX_EXT_OFFSET:
        KEY = key
        print(f"Implementation: {TYPE=} {key=}")

assert KEY


# In[ ]:


TYPE = 'clock'
csidh.scope.cglitch_setup(default_setup=False)
# csidh.scope.vglitch_setup(3, default_setup=False)
# csidh.scope.glitch.output = 'enable_only'


# Arbitrarily chosen parameter combination based on the best parameter combinations from parameter search

# In[ ]:


# This was used for dummy-free as one of the best parameter combinations
offset  = 216
width   = 285
repeat  = 14
base_units = [(offset, width, repeat)]

# PARAM_COMBINATIONS = PATH + "/notebooks/data/parameter-search/husky/husky-clock-best-parameter-combinations.json"
# from csidhtools.search.io import read_caches_into_dataframe
# df = read_caches_into_dataframe([PARAM_COMBINATIONS])
# df = df[['offset', 'width', 'repeat']]
# base_units = [tuple(x) for x in df.to_numpy()]
# base_units


# In[ ]:





# In[ ]:


NUM_GLITCHES = 900000 - 588425


# In[ ]:


from csidhtools import Unit
population = []

import random

TYPE = 'random'
population = []
for offset, width, repeat in base_units:
    used_offsets = set()
    for _ in range(NUM_GLITCHES):
        unit = Unit()
        unit.width = int(width)
        unit.offset = int(offset)
        unit.repeat = int(repeat)
        ext_offset = None
        while (ext_offset := random.randint(1, MAX_EXT_OFFSET)) in used_offsets:
            pass
        unit.ext_offset = ext_offset
        used_offsets.add(ext_offset)
        population.append(unit)    


# TYPE = 'chosen-isogenies-random'
# import pandas as pd
# APPROX_EXECUTION_TIME = pd.DataFrame({
#         "degree": [3, -5, 7, 3, -5, 7, -5, 3, 7, 3, -5, 7, 3, -5, 7],
#         "setup_start": [0, 82034, 133063, 169116, 294283, 345482, 381485, 542726, 689691, 755962, 880624, 933569, 969524, 1070086, 1122983],
#         "isogeny_start": [66929, 111962, 155177, 279034, 324445, 367158, 521621, 674420, 741649, 865413, 910630, 955141, 1054981, 1100186, 1144895],
#         "isogeny_end": [82033, 133062, 169115, 294282, 345481, 381484, 542725, 689690, 755961, 880623, 933568, 969523, 1070085, 1122982, 1159199]

# })
# chosen_intervals = [1, 2,4,6]
# population = []
# used_offsets = set()
# for i in chosen_intervals:
#     l = APPROX_EXECUTION_TIME.iloc[i]['setup_start']
#     r = APPROX_EXECUTION_TIME.iloc[i]['isogeny_end']
#     d = APPROX_EXECUTION_TIME.iloc[i]['degree']
#     print(d,l,r)
#     for offset, width, repeat in base_units:
#         for _ in range(NUM_GLITCHES):
#             unit = Unit()
#             unit.width = int(width)
#             unit.offset = int(offset)
#             unit.repeat = int(repeat)
#             ext_offset = None

#             while (ext_offset := random.randint(l,r)) in used_offsets:
#                 pass
#             unit.ext_offset = ext_offset
#             used_offsets.add(ext_offset)
#             population.append(unit)    



# TYPE += '-linspace'
# import numpy as np
# for ext_offset in list(np.linspace(0, MAX_EXT_OFFSET, NUM_GLITCHES)):
#     unit = Unit()
#     unit.width = width
#     unit.offset = offset
#     unit.repeat = repeat
#     unit.ext_offset = int(ext_offset)
#     population.append(unit)

print(len(population))
print(population[0])
print(population[-1])
print(min(population, key=lambda x: x.ext_offset))
print(max(population, key=lambda x: x.ext_offset))


# In[ ]:


from collections import OrderedDict

def split_into_batches(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i+n]

import numpy as np
from csidhtools.search.ga import evaluate_unit_default, evaluate_batch
import csidhtools
csidhtools.search.ga.PUBLIC_EXPECTED = PUBLIC_EXPECTED
csidh.ack_timeout = 150
# Set the measurements per unit
MEASUREMENTS_PER_UNIT = 1
cache = OrderedDict()
evaluate_unit = lambda csidh, unit, cache: evaluate_unit_default(csidh, unit, cache, MEASUREMENTS_PER_UNIT)
CACHE_INTERVAL = 10
# Output filename
FILENAME = f"husky-{KEY}-{TYPE}-dummy-isogeny-single-glitches-18a8153-6.json"
for batch in tqdm(list(split_into_batches(population, CACHE_INTERVAL))):
    evaluate_batch(csidh, batch, cache, evaluate_unit)
    write_cache_to_file(FILENAME, cache)


# In[6]:


csidh.dis()


# In[ ]:


# cache = OrderedDict()
# REPEATS = 20000
# cache_interval = 2
# for _ in tqdm(range(REPEATS//cache_interval)):
#     batch = []
#     for _ in range(cache_interval):
#         i = random.randint(0, len(single_skips)-1)
#         j = i
#         while j == i:
#             j = random.randint(0, len(single_skips)-1)

#         fst = single_skips[i]
#         snd = single_skips[j]
#         swap = lambda x, y: (y, x)
#         if fst.ext_offset > snd.ext_offset:
#             fst, snd = swap(fst, snd)

#         unit1 = Unit(repr=repr(fst))
#         unit1.repeat = [fst.repeat, fst.repeat]
#         unit1.ext_offset = [fst.ext_offset, snd.ext_offset-fst.ext_offset]

#         unit2 = Unit(repr=repr(snd))
#         unit2.repeat = [snd.repeat, snd.repeat]
#         unit2.ext_offset = [fst.ext_offset, snd.ext_offset-fst.ext_offset]

#         unit3 = Unit(repr=repr(fst))
#         unit3.repeat = [fst.repeat, snd.repeat]
#         unit3.ext_offset = [fst.ext_offset, snd.ext_offset-fst.ext_offset]

#         unit4 = Unit(repr=repr(snd))
#         unit4.repeat = [fst.repeat, snd.repeat]
#         unit4.ext_offset = [fst.ext_offset, snd.ext_offset-fst.ext_offset]

#         print(unit1)
#         print(unit2)
#         print(unit3)
#         print(unit4)

#         batch.append(unit1)
#         batch.append(unit2)       
#         batch.append(unit3)
#         batch.append(unit4)

#     evaluate_batch(csidh, batch)
#     write_cache_to_file(f"husky-clock-ISOGENY-DOUBLE-SKIP.json", cache, 1, len(cache), -1)   


# In[ ]:


# potential = [
#     "./husky-clock-xISOG-first-5-isogeny-skip-search-until7.json"
# ]

# df = read_cachefiles_to_dataframe(potential)
# df = df[(df["type"] == "JUSTRIGHT")].reset_index()
# indices = [i  for i,x in enumerate(df["responses"]) if 199 in x]
# potential_skips = df.iloc[indices]
# batch = list(set(potential_skips["unit"]))
# batch.sort(key=lambda unit: -unit.ext_offset)
# batch
# cache = OrderedDict()
# uut = batch[-1]
# uut.offset = 2706
# uut.width = 2600
# uut.repeat = 4
# evaluate_batch(csidh, [uut])
# write_cache_to_file(f"first-5-isogeny-potential-skips.json", cache, 1, len(cache), -1)   


# In[ ]:


# cache = OrderedDict()
# REPEATS = 20000
# cache_interval = 2
# for _ in tqdm(range(REPEATS//cache_interval)):
#     batch = []
#     for _ in range(cache_interval):
#         i = random.randint(0, len(candidates)-1)
#         base_unit = candidates[i]
#         for j in range(len(isogeny_offsets)):
#             if j == 0:
#                 eof_min = 0
#                 eof_max = isogeny_offsets[0][1]
#             else:
#                 eof_min = isogeny_offsets[j-1][2]
#                 eof_max = isogeny_offsets[j][1]
#             unit = Unit(repr=repr(base_unit))
#             unit.ext_offset = random.randint(eof_min, eof_max)
#             print(unit)
#             batch.append(unit)

#     evaluate_batch(csidh, batch)
#     write_cache_to_file(f"husky-clock-ISOGENY-SKIP-SEARCH.json", cache, 1, len(cache), -1)   


# In[ ]:


# cache = OrderedDict()

# REPEATS = 17500
# cache_interval = 10
# for _ in tqdm(range(REPEATS//cache_interval)):
#     batch = []
#     for _ in range(cache_interval):
#         # width = random.randint(2650, 2750)
#         # offset = random.randint(2560, 2610)
#         # repeat = random.randint(4, 5)
#         width = random.randint(0, csidh.scope.glitch.phase_shift_steps//2)
#         offset = random.randint(0, csidh.scope.glitch.phase_shift_steps)
#         repeat = random.randint(1, 18)

#         ext_offset = random.randint((474252//4 )+2000, (474252//4 ) + 3200)

#         unit = Unit(repr=f"{ext_offset},{offset},{width},{repeat},None,0")
#         batch.append(unit)

#     evaluate_batch(csidh, batch)
#     write_cache_to_file(f"husky-clock-xISOG-first-5-isogeny-skip-parameter-search.json", cache, 1, len(cache), -1)   


# In[ ]:


# population = []
# cache = OrderedDict()
# for i, (_, isogeny_offset) in tqdm(enumerate(isogeny_offsets[:1])):
#     Unit.is_husky = csidh.scope._is_husky
#     Unit.OFFSET_MIN = 2705 	 
#     Unit.OFFSET_MAX = 2705 	
#     Unit.OFFSET_RANGE = Unit.OFFSET_MAX - Unit.OFFSET_MIN

#     Unit.WIDTH_MIN = 2601
#     Unit.WIDTH_MAX = 2601
#     Unit.WIDTH_RANGE = Unit.WIDTH_MAX - Unit.WIDTH_MIN

#     Unit.EXT_OFFSET_MIN = isogeny_offset // 4 + 0
#     Unit.EXT_OFFSET_MAX = isogeny_offset // 4 + 10000
#     Unit.EXT_OFFSET_RANGE = Unit.EXT_OFFSET_MAX - Unit.EXT_OFFSET_MIN

#     Unit.REPEAT_MIN = 4
#     Unit.REPEAT_MAX = 4
#     Unit.repeat_range = Unit.REPEAT_MAX - Unit.REPEAT_MIN
#     batch = generate_whole_population()
#     print(f"Evaluating population for Isogeny number: {i}, {Unit.EXT_OFFSET_MIN=}, {Unit.EXT_OFFSET_MAX=}, Batch size: {len(batch)}")
#     population += batch
#     print(len(population))
#     evaluate_batch(csidh, batch)
#     write_cache_to_file(f"xISOG-5-isogeny-skip-test.json", cache, 1, len(population), -1)   


# In[ ]:




