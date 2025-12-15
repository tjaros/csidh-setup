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
        entry["timing"] = unit.timing
        measurements.append(entry)
    result["measurements"] = measurements

    with open(filename, "w") as f:
        json.dump(result, f)


def read_cache_from_file(filename) -> OrderedDict:
    with open(filename, "r") as f:
        data = json.load(f)
    result = []
    measurements = data["measurements"]
    for i in range(len(measurements)):
        unit = Unit(repr=measurements[i]["unit"], parser=True)
        unit.measurements = measurements[i]["measurements"]
        unit.responses = measurements[i]["responses"]
        unit.timing = measurements[i].get("timing", [])

        entry = {"unit": unit}
        entry.update(unit.__dict__())
        entry["measurements"] = unit.measurements
        entry["responses"] = unit.responses
        entry["timing"] = unit.timing
        result.append(entry)
    return result


def to_unit(entry):
    unit = Unit()
    unit.ext_offset = entry["ext_offset"]
    unit.offset = entry["offset"]
    unit.width = entry["width"]
    unit.repeat = entry["repeat"]
    unit.measurements = entry["measurements"]
    unit.responses = entry["responses"]
    unit.timing = entry["timing"]
    return unit


def read_caches_into_dataframe(filenames: List[str]):
    df = None
    for filename in filenames:
        result = pd.DataFrame(read_cache_from_file(filename))
        df = (
            result
            if df is None
            else pd.concat([df, result], ignore_index=True, sort=False)
        )
    return df
