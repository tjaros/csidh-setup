#!/usr/bin/env python
# coding: utf-8

# # Filtering out units for double glitching
# 
# In this notebook we first create batches for double glitches we want to perform, then we perform double glitching of isogenies
# 

# In[1]:


PATH = "/home/xjaros2/Documents/git/csidh-setup/"
SCOPETYPE = 'OPENADC'
PLATFORM = 'CW308_STM32F3'

SS_VER = 'SS_VER_2_1'
attack_type = "A1"


# This is just sanity check, to make sure the implementation code is fixed, and we did not accidentally changed implementation when going glitching for real

# In[2]:


IMPL = "dummy-free"


# - `ISOGENY_NEIGHBOURS`
#     - Values of up to distance 1 or 2 from the expected public key.

# In[3]:


DUMMY_FREE_ISOGENY_NEIGHBOURS= {
    158: ("($+$)$3$", 3), 
    368: ("($-$)$3$", -3),
    40:  ("($+$)$5$", +5),
    29:  ("($-$)$5$", -5),
    51:  ("($+$)$7$", +7),
    191: ("($-$)$7$", -7),
    404: ("($--$)$3$", -3**2),
    0:   ("($++$)$3$", +3**2),
    261: ("($--$)$5$", -5**2),
    75:  ("($++$)$5$", +5**2),
    199: ("($--$)$7$", -7**2),
    245: ("($++$)$7$", +7**2)
}

DUMMY_ISOGENY_NEIGHBOURS= {
    0: ("($+$)$3$",3), 
    261: ("($++$) $3$",3**2), 
    410: ("($-$) $3$",-3),
    368: ("($--$) $3$",-3**2),

    295: ("($+$) $5$",5),
    404: ("($++$) $5$",5**2),
    390: ("($-$) $5$", -5),
    9: ("($--$) $5$",-5**2),

    15: ("($+$) $7$",7),
    6: ("($++$) $7$",7**2),
    144: ("($-$) $7$",-7),
    124: ("($--$) $7$",-7**2)
}

if IMPL == "dummy":
    ISOGENY_NEIGHBOURS = DUMMY_ISOGENY_NEIGHBOURS
elif IMPL == "dummy-free":
    ISOGENY_NEIGHBOURS = DUMMY_FREE_ISOGENY_NEIGHBOURS
else:
    assert False, "IMPL should be either \"dummy\" or \"dummy-free\""


# As a result of profiling, we get (The actual degrees are just a help and we can only use their absolute values):
# - `APPROX_TOTAL_EXECUTION_TIME`
#     - Should not be too far off the fixed value for expected EXT_OFFSET
# - `APPROX_EXCECUTION_TIME`
#     - Table of execution times per isogeny and their degrees

# In[4]:


import pandas as pd
if IMPL == "dummy":
    APPROX_TOTAL_EXECUTION_TIME = 1178027
    df = pd.DataFrame({
        "degree": [3, -5, 7, 3, -5, 7, -5, 3, 7, 3, -5, 7, 3, -5, 7],
        "setup_start": [0, 82034, 133063, 169116, 294283, 345482, 381485, 542726, 689691, 755962, 880624, 933569, 969524, 1070086, 1122983],
        "isogeny_start": [66929, 111962, 155177, 279034, 324445, 367158, 521621, 674420, 741649, 865413, 910630, 955141, 1054981, 1100186, 1144895],
        "isogeny_end": [82033, 133062, 169115, 294282, 345481, 381484, 542725, 689690, 755961, 880623, 933568, 969523, 1070085, 1122982, 1159199]

    })
else:
    APPROX_TOTAL_EXECUTION_TIME = 2792802
    df = pd.DataFrame({
        "degree": [3, -5, 7, 3, -5, 7, 3, -5, 7, -7, 3, -5, -7, 3, -5, 7, -5, 3, -5, 7, 3, 5, -7, 5, 3, -5, -7, 7, 3, 3],
        "setup_start": [0, 82147, 133296, 169466, 294749, 346068, 382210, 507471, 558784, 594982, 770348, 895535, 946948, 982686, 1107398, 1158593, 1194579, 1355742, 1503240, 1554605, 1590757, 1715685, 1766304, 1802328, 1965964, 2274608, 2325879, 2361603, 2510953, 2630558],
        "isogeny_start": [67018, 112171, 155505, 279476, 325007, 368291, 492284, 537617, 581065, 756401, 880236, 925665, 968765, 1092321, 1137502, 1180670, 1334669, 1488043, 1533528, 1576870, 1700412, 1745291, 1788393, 1944775, 2259411, 2304742, 2347804, 2497010, 2615361, 2758780],
        "isogeny_end": [82146, 133295, 169465, 294748, 346067, 382209, 507470, 558783, 594981, 770347, 895534, 946947, 982685, 1107397, 1158592, 1194578, 1355741, 1503239, 1554604, 1590756, 1715684, 1766303, 1802327, 1965963, 2274607, 2325878, 2361602, 2510952, 2630557, 2773928 ]
    })

APPROX_EXECUTION_TIME = df


# We parse the single glitch results into dataframes

# In[5]:


# from csidhtools.search.io import read_caches_into_dataframe
# %cd $PATH

# if IMPL == "dummy":
#     SINGLE_GLITCH_MEASUREMENTS = [
#         "notebooks/data/dummy-results/husky/husky-(5, -3, 1)-random-dummy-isogeny-single-glitches-18a8153-0.json",
#         "notebooks/data/dummy-results/husky/husky-(5, -3, 1)-random-dummy-isogeny-single-glitches-18a8153-1.json",
#         "notebooks/data/dummy-results/husky/husky-(5, -3, 1)-random-dummy-isogeny-single-glitches-18a8153-2.json",
#         # "notebooks/data/dummy-results/husky/husky-(5, -3, 1)-chosen-isogenies-random-dummy-isogeny-single-glitches-18a8153.json"
#     ]
# else:
#     SINGLE_GLITCH_MEASUREMENTS = [
#     "notebooks/data/dummy-free-results/husky/husky-clock-random-dummy-free-isogeny-single-glitches-3b62362-0.json",
#     "notebooks/data/dummy-free-results/husky/husky-clock-random-dummy-free-isogeny-single-glitches-3b62362-1.json",
#     "notebooks/data/dummy-free-results/husky/husky-clock-random-dummy-free-isogeny-single-glitches-3b62362-2.json",
#     "notebooks/data/dummy-free-results/husky/husky-clock-random-dummy-free-isogeny-single-glitches-3b62362-3.json",
#     "notebooks/data/dummy-free-results/husky/husky-clock-random-dummy-free-isogeny-single-glitches-3b62362-4.json",
#     "notebooks/data/dummy-free-results/husky/husky-clock-random-dummy-free-isogeny-single-glitches-3b62362-5.json",
#     "notebooks/data/dummy-free-results/husky/husky-clock-random-dummy-free-isogeny-single-glitches-18a8153-6.json"
#     ]


# df = read_caches_into_dataframe(SINGLE_GLITCH_MEASUREMENTS)
# df.loc[:, 'response'] = df['responses'].apply(lambda x: x[0] if x else None)
# df.loc[:, 'timing'] = df['timing'].apply(lambda x: x[0] if x else None)


# - Filter the data to be only the faulty results
# - And label the data (degrees, ....)

# In[ ]:


# df.groupby(["type"])['ext_offset'].max() < APPROX_TOTAL_EXECUTION_TIME


# In[ ]:


# SUCCESSFUL_GLITCHES = df[df.type == 'JUSTRIGHT'].copy()
# SUCCESSFUL_GLITCHES = SUCCESSFUL_GLITCHES[SUCCESSFUL_GLITCHES['response'].isin(ISOGENY_NEIGHBOURS.keys())]
# SUCCESSFUL_GLITCHES.loc[:,'expected_degree'] = SUCCESSFUL_GLITCHES['response'].apply(lambda x: ISOGENY_NEIGHBOURS[int(x)][1])
# SUCCESSFUL_GLITCHES.loc[:,'expected_absolute_degree'] = SUCCESSFUL_GLITCHES['response'].apply(lambda x: abs(ISOGENY_NEIGHBOURS[int(x)][1]))
# SUCCESSFUL_GLITCHES['interval'] = -1  # default (no match)
# SUCCESSFUL_GLITCHES['actual_absolute_degree'] = None
# SUCCESSFUL_GLITCHES['actual_degree'] = None


# for i, entry in enumerate(APPROX_EXECUTION_TIME.to_dict('records')):
#     interval_start = entry['setup_start']
#     interval_end = entry['isogeny_end'] if not i == len(APPROX_EXECUTION_TIME) - 1 else APPROX_TOTAL_EXECUTION_TIME 
#     actual_degree = entry['degree']

#     # Assign interval ID where offset falls in range
#     mask = (interval_start < SUCCESSFUL_GLITCHES['ext_offset']) & (SUCCESSFUL_GLITCHES['ext_offset'] < interval_end)
#     SUCCESSFUL_GLITCHES.loc[mask, 'interval'] = i
#     SUCCESSFUL_GLITCHES.loc[mask, 'actual_absolute_degree'] = abs(actual_degree)
#     SUCCESSFUL_GLITCHES.loc[mask, 'actual_degree'] = actual_degree

#     mask = ()
# len(SUCCESSFUL_GLITCHES)


# In[ ]:


# from csidhtools import Unit
# import numpy as np


# # Split data based on degree
# df = SUCCESSFUL_GLITCHES

# groups = {
#     # 3: df[(df['actual_absolute_degree'] == 3) & df['expected_degree'].isin([3, -3, 3**2, -3**2])],
#     # 5: df[(df['actual_absolute_degree'] == 5) & df['expected_degree'].isin([5, -5, 5**2, -5**2])],
#     # 7: df[(df['actual_absolute_degree'] == 7) & df['expected_degree'].isin([7, -7, 7**2, -7**2])]

#     # We combine glitches, which were effectively skipping isogenies
#     3: df[(df['actual_absolute_degree'] == 3) & (df.expected_degree == df.actual_degree)],
#     5: df[(df['actual_absolute_degree'] == 5) & (df.expected_degree == df.actual_degree)],
#     7: df[(df['actual_absolute_degree'] == 7) & (df.expected_degree == df.actual_degree)]

# }

# if IMPL == "dummy":
#     del groups[7]

#     df = groups[3].sort_values("ext_offset").reset_index(drop=True)
#     threshold = 280
#     keep = [True]
#     for i in range(1, len(df)):
#         if df.loc[i, "ext_offset"] - df.loc[i - 1, "ext_offset"] < threshold:
#             keep.append(False)
#         else:
#             keep.append(True)
#     df =  df[keep]
#     groups[3] = df


# print("Sizes of groups per degree:", [len(g) for g in groups.values()])

# # Now split each group based on the interval
# for d in groups.keys():
#     group = groups[d]
#     group = [g for _, g in group.groupby('interval')]
#     # We also need to sort group according to interval since we only glitch pairs of neighbouring intervals
#     group = sorted(group, key=lambda x: x.iloc[0].interval)
#     print("Sorted intervals:", [g.iloc[0].interval for g in group])
#     groups[d] = group
#     for g in group:
#         unique = g.expected_degree.unique() # We at least need to have some potentional skips
#         print(f"Entries in interval {g.iloc[0].interval}", len(g), unique)
#         assert set(unique) == set([d, -d]) or (set(unique) in [set([d]), set([-d])]) # We need to have result for each at least


# In[ ]:


# if IMPL == "dummy": 
#     import matplotlib.pyplot as plt
#     import seaborn as sns


#     populations = {}
#     # Now we proceed to create populations 
#     for d in groups.keys():
#         print(f"=====Creating population for degree {d}=====")
#         group = groups[d]

#         populations[d] = []
#         for i in range(len(group)):
#             for j in range(i+1, len(group)):
#                 fst = group[i]
#                 snd = group[j]

#                 assert fst.offset.unique() == snd.offset.unique()
#                 assert fst.width.unique() == snd.width.unique()
#                 assert fst.repeat.unique() == snd.repeat.unique()

#                 offset = int(fst.offset.unique()[0])
#                 width = int(fst.width.unique()[0])
#                 repeat = int(fst.repeat.unique()[0])
#                 ext_1 = list(fst.ext_offset)
#                 ext_2 = list(snd.ext_offset)
#                 print(
#                     f"Creating pairs for intervals {fst.interval.unique()}{snd.interval.unique()}\n"
#                     f"{offset=},{width=},{repeat=}"
#                 )
#                 pstart = len(populations[d])
#                 for e1 in ext_1:
#                     for e2 in ext_2:
#                         unit = Unit()
#                         unit.is_husky = True
#                         unit.repeat = [repeat] * 2
#                         unit.offset = offset
#                         unit.width  = width
#                         assert e1 < e2
#                         unit.ext_offset = [int(e1), int(e2-e1)]
#                         populations[d].append(unit)
#                 pend = len(populations[d])
#                 print(f"Population length: {pend-pstart}")



#     print("Total:", sum([len(p) for p in populations.values()]))     


# In[ ]:


# if IMPL == "dummy-free": 
#     import matplotlib.pyplot as plt
#     import seaborn as sns


#     populations = {}
#     # Now we proceed to create populations 
#     for d in groups.keys():
#         print(f"=====Creating population for degree {d}=====")
#         group = groups[d]


#         populations[d] = []
#         for i in range(0,10, 2):
#             fst = group[i]
#             snd = group[i+1]

#             offset = int(fst.offset.unique()[0])
#             width = int(fst.width.unique()[0])
#             repeat = int(fst.repeat.unique()[0])
#             ext_1 = list(fst.ext_offset)
#             ext_2 = list(snd.ext_offset)
#             print(
#                 f"Creating pairs for intervals {fst.interval.unique()}{snd.interval.unique()}\n"
#                 f"{offset=},{width=},{repeat=}"
#             )
#             pstart = len(populations[d])
#             for e1 in ext_1:
#                 for e2 in ext_2:
#                     unit = Unit()
#                     unit.is_husky = True
#                     unit.repeat = [repeat] * 2
#                     unit.offset = offset
#                     unit.width  = width
#                     assert e1 < e2
#                     unit.ext_offset = [int(e1), int(e2-e1-2)]
#                     populations[d].append(unit)
#             pend = len(populations[d])
#             print(f"Population length: {pend-pstart}")



#     print("Total:", sum([len(p) for p in populations.values()]))     


# Random glitching

# In[6]:


APPROX_EXECUTION_TIME['absolute_degree'] = abs(APPROX_EXECUTION_TIME['degree'])
groups = [g.reset_index(drop=True) for _, g in APPROX_EXECUTION_TIME.groupby("absolute_degree")]


# In[7]:


from csidhtools import Unit
import numpy as np


offset = 332
width = 192
repeat = 14
NUM_MEASUREMENTS_PER_PAIR = 15000

if IMPL == "dummy-free": 
    import matplotlib.pyplot as plt
    import seaborn as sns
    import random


    populations = {}
    # Now we proceed to create populations 
    for i in range(3):
        group = groups[i]
        d = group['absolute_degree'].unique()[0]
        print(f"=====Creating population for degree {d}=====")    
        populations[d] = []
        for i in range(0,10, 2):
            fst = group.iloc[i]
            snd = group.iloc[i+1]

            print(
                f"Creating pairs for intervals {i} {i+1}\n"
                f"{offset=},{width=},{repeat=}"
            )
            pstart = len(populations[d])
            for _ in range(NUM_MEASUREMENTS_PER_PAIR):
                    unit = Unit()
                    unit.is_husky = True
                    unit.repeat = [repeat] * 2
                    unit.offset = offset
                    unit.width  = width
                    e1 = random.randint(fst.setup_start, fst.isogeny_end)
                    e2 = random.randint(snd.setup_start, snd.isogeny_end)
                    assert e1 < e2
                    unit.ext_offset = [int(e1), int(e2-e1)]
                    populations[d].append(unit)
            pend = len(populations[d])
            print(f"Population length: {pend-pstart}")                

    print("Total:", sum([len(p) for p in populations.values()]))


# In[ ]:


# from csidhtools import Unit

# groups = {
#     3: APPROX_EXECUTION_TIME[APPROX_EXECUTION_TIME.degree.isin([3,-3])],
#     5: APPROX_EXECUTION_TIME[APPROX_EXECUTION_TIME.degree.isin([5,-5])],
#     7: APPROX_EXECUTION_TIME[APPROX_EXECUTION_TIME.degree.isin([7,-7])]
# }

# import random

# offset = 147
# width = 294
# repeat = 9
# # Now split each group based on the interval
# populations = {}
# NUM_MEASUREMENTS_PER_GROUP = 10000
# for degree in groups.keys():
#     group = groups[degree]
#     populations[degree] = []
#     assert len(group) == 10
#     print(30 * "=")
#     for i in range(0, 10, 2):
#         fst_l = group.iloc[i]['setup_start']
#         fst_r = group.iloc[i]['isogeny_end']
#         snd_l = group.iloc[i+1]['setup_start']
#         snd_r = group.iloc[i+1]['isogeny_end']
#         print(f"Degree {degree}, group [{i, i+1}], {(fst_l,fst_r)}, {snd_l, snd_r}")
#         used_ext_offsets = set()
#         for _ in range(NUM_MEASUREMENTS_PER_GROUP):
#             while True:
#                 e1 = random.randint(fst_l, fst_r)
#                 e2 = random.randint(snd_l, snd_r)
#                 if (e1,e2) not in used_ext_offsets:
#                     break
#             used_ext_offsets.add((e1,e2))

#             unit = Unit()
#             unit.is_husky = True
#             unit.repeat = [repeat] * 2
#             unit.offset = offset
#             unit.width  = width
#             assert e1 < e2
#             unit.ext_offset = [int(e1), int(e2-e1)]
#             populations[degree].append(unit)
#     print(len(populations[degree]))


# In[ ]:


BENCH_MODE = 'NORMAL'
get_ipython().run_line_magic('cd', '$PATH/notebooks')
get_ipython().run_line_magic('run', './init.ipynb')
get_ipython().run_line_magic('cd', '$PATH/notebooks')


# In[ ]:


csidh.wait_ack = True


# In[ ]:


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


# In[ ]:


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

assert KEY


# In[ ]:


csidh.scope.cglitch_setup(default_setup=False)
csidh.scope.glitch.num_glitches = 2


# In[ ]:


from collections import OrderedDict

def split_into_batches(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i+n]

import numpy as np
from csidhtools.search.ga import evaluate_unit_default, evaluate_batch
import csidhtools
csidhtools.search.ga.PUBLIC_EXPECTED = PUBLIC_EXPECTED
# Set the measurements per unit
MEASUREMENTS_PER_UNIT = 1
evaluate_unit = lambda csidh, unit, cache: evaluate_unit_default(csidh, unit, cache, MEASUREMENTS_PER_UNIT)
CACHE_INTERVAL = 500
# Output filename
csidh.wait_ack = True
csidh.ack_timeout = 150

for degree, population in tqdm(list(populations.items())[::-1]):
    cache = OrderedDict()
    FILENAME = f"husky-clock-dummy-free-{degree}-isogeny-double-glitches-random-5x15k-10.json"
    for batch in tqdm(list(split_into_batches(population, CACHE_INTERVAL))):
        evaluate_batch(csidh, batch, cache, evaluate_unit)
        write_cache_to_file(FILENAME, cache)


# In[35]:


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


# # Dummy-free constants 
# ISOGENY_NEIGHBOURS = {
#     158: ("($+$) $3$-isogeny", 3), 
#     368: ("($-$) $3$-isogeny", 3),
#     40:  ("($+$) $5$-isogeny", 5),
#     29:  ("($-$) $5$-isogeny", 5),
#     51:  ("($+$) $7$-isogeny", 7),
#     191: ("($-$) $7$-isogeny", 7)
# }


# In[ ]:


# from csidhtools.search.io import read_caches_into_dataframe
# %cd $PATH

# husky_dummy_free = [
#     "./notebooks/data/dummy-free-results/husky/incorrect/husky-clock-dummy-free-isogeny-single-glitches-450k.json"
# ]

# df = read_caches_into_dataframe(husky_dummy_free)
# df

# df['interval'] = -1  # default (no match)
# df['actual_undirected_degree'] = None
# df['measurement'] = df['measurements'].apply(lambda x: str(x[0]))


# for i, entry in enumerate(APPROX_EXECUTION_TIME.to_dict('records')):
#     interval_start = entry['setup_start']
#     interval_end = entry['isogeny_end'] if not i == len(APPROX_EXECUTION_TIME) - 1 else APPROX_TOTAL_EXECUTION_TIME 
#     actual_undirected_degree = entry['degree']

#     # Assign interval ID where offset falls in range
#     mask = (interval_start < df['ext_offset']) & (df['ext_offset'] < interval_end)
#     df.loc[mask, 'interval'] = i
#     df.loc[mask, 'actual_undirected_degree'] = actual_undirected_degree

#     mask = ()

# df


# In[ ]:




