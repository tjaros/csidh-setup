from .unit import Unit
from collections import OrderedDict
from typing import List
import json
from copy import deepcopy
import pandas as pd
import seaborn as sns



def write_cache_to_file(filename: str, cache: OrderedDict):
    result = {}
    measurements = []
    for i, unit in enumerate(cache):
        entry = {}
        entry["unit"] = repr(unit)
        entry["responses"] = unit.responses
        entry["measurements"] = unit.measurements
        measurements.append(entry)
    result["measurements"] = measurements

    with open(filename, "w") as f:
        json.dump(result, f)


def read_cache_from_file(filename) -> OrderedDict:
    with open(filename, "r") as f:
        data = json.load(f)
    result = []
    measurements = data["measurements"]
    for i in range(len(measuremens)):
        unit = Unit(repr=measurements[i]["unit"])
        unit.measurements = measurements[i]["measurements"]
        unit.responses = measurements[i]["responses"]
        del measurements[i]["index"]
        measurements[i]["unit"] = unit
        result.append(measurements[i])
    return result

def to_unit(entry):
    unit = Unit()
    unit.ext_offset = entry["ext_offset"]
    unit.offset = entry["offset"]
    unit.width = entry["width"]
    unit.repeat = entry["repeat"]
    unit.measurements = entry["measurements"]
    unit.responses = entry["responses"]
    return unit

def read_caches_into_dataframe(filenames: List[str]):
    df = None
    for filename in filenames:
        result = pd.DataFrame(read_cache_from_file(filename))
        df = result if df is None else pd.concat([df, result], ignore_index=True, sort=False)
    return False
    
