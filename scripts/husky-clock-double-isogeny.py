#!/usr/bin/env python
# coding: utf-8

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


# In[ ]:


csidh = CSIDHCW(PATH, attack_type=attack_type)
csidh.setup()


# In[ ]:


csidh.flash_target()


# In[ ]:


csidh.scope.adc.timeout = 5


# In[ ]:


csidh.reset_target()
csidh.scope.arm()
csidh.action()
ret = csidh.scope.capture()
if ret:
    print("Timeout happened during acquisition")
PUBLIC_EXPECTED = csidh.public_with_errors
max_ext_offset = csidh.scope.adc.trig_count
print("Public key:", PUBLIC_EXPECTED)
print("Max ext offset:", max_ext_offset)


# In[ ]:


EXT_OFFSET_FULL = 10528968
print(EXT_OFFSET_FULL - 10055348)
print(EXT_OFFSET_FULL - 10054576)
print(EXT_OFFSET_FULL - 10055640)


# In[ ]:


# isogeny_offsets = [
#     (5,474252), # The if statement in both branches before isogenies cost 8 cycles  
#     (7,574920),
#     (5,1109332),
#     (3,1638652),
#     (5,1799384),
#     (7,1952772),
#     (3,2377220)
# ]
isogeny_offsets = [
    (5, 118555, 139478),
    (7, 161541, 175472),
    (5, 312859, 333855), 
    (3, 462833, 478086),
    (5, 508058, 529109),
    (7, 551170, 565075),
    (3, 672017, 687331),
    #(3, 717500, 738726)
]



# In[ ]:


#csidh.voltage_glitching_setup()
csidh.scope.cglitch_setup()


# In[ ]:


from csidh.search import Unit, generate_population, write_cache_to_file
from collections import OrderedDict
import numpy as np
cache = OrderedDict()


def evaluate_unit(csidh, unit, num_measurements=5):
    """Evaluates a single unit"""
    csidh.scope.glitch.num_glitches = 1
    if csidh.scope._is_husky:
        csidh.scope.glitch.width = int(unit.width)
        csidh.scope.glitch.offset = int(unit.offset)
        if not isinstance(unit.repeat, list):
            csidh.scope.glitch.repeat = int(unit.repeat)
            csidh.scope.glitch.ext_offset = int(unit.ext_offset)
        else:
            csidh.scope.glitch.repeat = unit.repeat
            csidh.scope.glitch.ext_offset = unit.ext_offset
    else:
        csidh.scope.glitch.width = unit.width
        csidh.scope.glitch.offset = unit.offset
        csidh.scope.glitch.repeat = unit.repeat
        csidh.scope.glitch.ext_offset = unit.ext_offset

    # Perform the measurements
    measurements = []
    responses = []

    for _ in range(num_measurements):
        csidh.reset_target()
        csidh.scope.glitch.state = None
        csidh.scope.arm()
        ret = csidh.action()
        csidh.scope.io.vglitch_reset()
        if ret:
            logging.error("Timeout happened during acquisition")


        public_received = csidh.public_with_errors
        if not isinstance(public_received, int):
            measurements.append("RESET")
        elif public_received == PUBLIC_EXPECTED:
            measurements.append("NORMAL")
        else:
            measurements.append("JUSTRIGHT")
            responses.append(public_received)

    unit.width = csidh.scope.glitch.width  # CW rounds the values
    unit.offset = csidh.scope.glitch.offset
    unit.repeat = csidh.scope.glitch.repeat
    unit.measurements = measurements
    unit.responses = responses


    # Classify
    if not all(m == measurements[0] for m in measurements):
        unit.type = "CHANGING"
        N_normal = sum(1 for m in measurements if m == "NORMAL")
        N_reset = sum(1 for m in measurements if m == "RESET")
        N_justright = sum(1 for m in measurements if m == "JUSTRIGHT")
        unit.fitness = 4 + 1.2 * N_justright + 0.2 * N_normal + 0.5 * N_reset
    else:
        if measurements[0] == "NORMAL":
            unit.type = "NORMAL"
            unit.fitness = 2
        elif measurements[0] == "RESET":
            unit.type = "RESET"
            unit.fitness = 5
        elif measurements[0] == "JUSTRIGHT":
            unit.type = "JUSTRIGHT"
            unit.fitness = 10
    cache[unit] = unit.fitness
    #if unit.type in ["RESET", "JUSTRIGHT"]:
    print(unit)
    print(unit.measurements)
    print(unit.responses)


def evaluate_batch(csidh, population):
    uncached = [u for u in population if u not in cache]
    if not uncached:
        return [u.fitness for u in population]

    to_visit = np.array(uncached)

    for unit in population:
        if unit in cache:
            unit.fitness = cache[unit]

    for unit in to_visit:
        evaluate_unit(csidh, unit)

    return [u.fitness for u in population]


# In[ ]:


def generate_whole_population():
    population = []
    for offset in range(Unit.OFFSET_MIN, Unit.OFFSET_MAX+1):
        for width in range(Unit.WIDTH_MIN, Unit.WIDTH_MAX+1):
            for ext_offset in range(Unit.EXT_OFFSET_MIN, Unit.EXT_OFFSET_MAX+1):
                for repeat in range(Unit.REPEAT_MIN, Unit.REPEAT_MAX+1):
                    unit = Unit(repr=f"{ext_offset},{offset},{width},{repeat},None,0")
                    population.append(unit)
    return population


# In[ ]:


from copy import deepcopy
import json
import pandas as pd
import seaborn as sns
from csidh.search import Unit

import os
os.chdir("/home/xjaros2/Documents/git/csidh-setup/csidh-target/scripts/")

def read_cachefile(filename):
    with open(filename, "r") as f:
        measurements = json.load(f)
    measurements = measurements["measurements"]
    result = []
    for i in range(len(measurements)):
        unit = Unit(repr=measurements[i]["unit"])
        measurements[i].update(unit.__dict__())
        unit.measurements = measurements[i]["measurements"]
        unit.responses = measurements[i]["responses"]
        del measurements[i]["index"]
        measurements[i]["unit"] = unit
        result.append(measurements[i])
    return result

def read_cachefiles_to_dataframe(cachefiles):
    df = None
    for filename in cachefiles:
        result = pd.DataFrame(read_cachefile(filename))
        if df is None:
            df = result
        else:
            df = pd.concat([df, result], ignore_index=True, sort=False)
    return df


# In[ ]:


husky = [
    "./husky-clock-ISOGENY-SKIP-SEARCH.json"
]

df = read_cachefiles_to_dataframe(husky)
df = df[df["type"] == "JUSTRIGHT"].reset_index()
df


# In[ ]:


from csidh import CSIDHDLL
PATH = "/home/xjaros2/Documents/git/csidh-setup/csidh-target/src/"
csidhdll = CSIDHDLL(src_path=PATH)


def isogeny_in_distance(public, i):
    csidhdll.public = csidhdll.to_projective(public)
    private = [0, 0, 0]

    private[i] = -1
    csidhdll.private = private
    positive_isogeny_skipped =  csidhdll.from_projective(csidhdll.action())

    private[i] = 1
    csidhdll.private = private
    negative_isogeny_skipped = csidhdll.from_projective(csidhdll.action())
    return [positive_isogeny_skipped, negative_isogeny_skipped]


# In[ ]:


SINGLE_ISOGENY_PUBLIC_SKIPS = [isogeny_in_distance(0, 0)[0], isogeny_in_distance(0, 1)[1], isogeny_in_distance(0, 2)[0]]
SINGLE_ISOGENY_PUBLIC_SKIPS


# In[ ]:


potential_skips = df.iloc[[i for i, x in enumerate(df["responses"]) if any(y in x for y in SINGLE_ISOGENY_PUBLIC_SKIPS)]]
potential_skips.responses = potential_skips.responses.apply(lambda x: x[0])
potential_skips


# In[ ]:


isogeny_offsets


# In[ ]:


import seaborn as sns
import matplotlib.pyplot as plt


# In[ ]:


palette = sns.color_palette("pastel6").as_hex()[:3]
ax = sns.scatterplot(potential_skips, x="ext_offset", y="responses", hue="responses", palette=palette)
ax.legend().set_title("Isogenies")
for label in ax.legend().texts:
    if label.get_text() == "261":
        label.set_text("3-isogeny")
    if label.get_text() == "199":
        label.set_text("5-isogeny")
    if label.get_text() == "344":
        label.set_text("7-isogeny")


bgmap = {
    3 : palette[1],
    5 : palette[0],
    7 : palette[2]
}

for i in range(len(isogeny_offsets)):
    if i == 0:
        xmin = 0
        xmax = isogeny_offsets[i][1]
    else:
        xmin = isogeny_offsets[i-1][2]
        xmax = isogeny_offsets[i][1]
    l = isogeny_offsets[i][0]
    plt.axvspan(xmin=xmin, xmax=xmax, alpha=0.1, color=bgmap[l])


sns.move_legend(ax, "upper left", bbox_to_anchor=(1, 1))


# In[ ]:


single_skips = list(set(potential_skips["unit"]))


# In[ ]:


csidh.scope.glitch.num_glitches = 2


# In[ ]:


cache = OrderedDict()
REPEATS = 20000
cache_interval = 2
for _ in tqdm(range(REPEATS//cache_interval)):
    batch = []
    for _ in range(cache_interval):
        i = random.randint(0, len(single_skips)-1)
        j = i
        while j == i:
            j = random.randint(0, len(single_skips)-1)

        fst = single_skips[i]
        snd = single_skips[j]
        swap = lambda x, y: (y, x)
        if fst.ext_offset > snd.ext_offset:
            fst, snd = swap(fst, snd)

        unit1 = Unit(repr=repr(fst))
        unit1.repeat = [fst.repeat, fst.repeat]
        unit1.ext_offset = [fst.ext_offset, snd.ext_offset-fst.ext_offset]

        unit2 = Unit(repr=repr(snd))
        unit2.repeat = [snd.repeat, snd.repeat]
        unit2.ext_offset = [fst.ext_offset, snd.ext_offset-fst.ext_offset]

        unit3 = Unit(repr=repr(fst))
        unit3.repeat = [fst.repeat, snd.repeat]
        unit3.ext_offset = [fst.ext_offset, snd.ext_offset-fst.ext_offset]

        unit4 = Unit(repr=repr(snd))
        unit4.repeat = [fst.repeat, snd.repeat]
        unit4.ext_offset = [fst.ext_offset, snd.ext_offset-fst.ext_offset]

        print(unit1)
        print(unit2)
        print(unit3)
        print(unit4)

        batch.append(unit1)
        batch.append(unit2)       
        batch.append(unit3)
        batch.append(unit4)

    evaluate_batch(csidh, batch)
    write_cache_to_file(f"husky-clock-ISOGENY-DOUBLE-SKIP.json", cache, 1, len(cache), -1)   


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




