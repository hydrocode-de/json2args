from typing import Union, List
from typing_extensions import Literal
from pathlib import Path
from glob import glob
import json

try:
    import numpy as np
    import polars as pl
    import xarray as xr
    WITH_PRELOAD = True
except ImportError:
    WITH_PRELOAD = False

from json2args.exceptions import FileExtensionError, ToolConfigMissingError
from json2args.util import get_data_and_config


def _preload_dataset(key: str, value: str, data_conf: dict):
    # get the specs
    try:
        specs = [conf for conf in data_conf if list(conf.keys())[0] == key][0][key]
    except KeyError:
        msg = f"The data input {key} is not configured in the data section of tool.yml. Check the tool.yml and input.json for misspellings first."
        raise ToolConfigMissingError(msg)
    
    # handle the inputs
    
    # get the file extension
    ext = Path(value).suffix.lower()

    # check if the dataset is given with the correct extension
    if 'extension' in specs:
        allowed = specs['extension']
        
        # extension can be a list or a string
        if isinstance(allowed, str):
            allowed = [allowed]
        
        if ext not in [el.lower() for el in allowed]:
            raise FileExtensionError(f"The dataset {key} must have one of the following extensions: {allowed}")
    
    # otherwise the input is allowed - check if we have a wildcard
    if '*' in value:
        paths = [Path(v).resolve() for v in glob(value)]
    else:
        paths = [Path(value).resolve()]

    # check if the file exists
    for path in paths:
        if not path.exists():
            raise FileNotFoundError(f"The dataset {key} does not exist at {path}")

    # get the extension
    
    # DAT
    if ext == '.dat':
        if len(paths) == 1:
            return np.loadtxt(paths[0])
        else:
            np.column_stack([np.loadtxt(path) for path in paths])
    
    # CSV
    elif ext == '.csv':
        return pl.read_csv(value, try_parse_dates=True).to_pandas()
    
    # netCDF
    elif ext in ('.nc', '.nc4', '.cdf', '.netcdf'):
        if len(paths) == 1:
            return xr.open_dataset(paths[0])
        else:
            return xr.open_mfdataset(paths, parallel=True)

    # json
    elif ext == '.json':
        if len(paths) == 1:
            with open(str(paths[0]), 'r') as f:
                return json.load(f)
        else:
            out = []
            for path in paths:
                with open(str(path), 'r') as f:
                    out.append(json.load(f))
            return out

    # any other case, use the path
    else:
        if len(paths) == 1:
            return str(paths[0])
        else:
            return [str(path) for path in paths]


def get_data(datasets: Union[Literal['all'], str, List[str]] = 'all', as_dict: bool = False, **kwargs) -> dict:
    if not WITH_PRELOAD:
        raise ImportError("The preload extras are not installed. Please install json2args with `pip install json2args[preload]`. If you only need the data paths, use `json2args.get_data_paths`")
    # load params and config
    data_param, data_conf = get_data_and_config(**kwargs)

    # handle the dataset input
    if datasets == 'all':
        datasets = list(data_param.keys())
    if isinstance(datasets, str):
        datasets = [datasets]
    
    # container for parsed data
    data = {}

    # first map all string values to an empty dict (no config given)
    empty_conf = [{el: {}} for el in data_conf if isinstance(el, str)]
    
    # then concat them together with the ones that have a config
    data_conf = [*empty_conf, *[it for it in data_conf if isinstance(it, dict)]]

    # parse all data values
    for key, value in data_param.items():
        if key in datasets:
            data[key] = _preload_dataset(key, value, data_conf)

    if as_dict:
        return data
    else:
        datatsets = list(data.values())
        if len(datatsets) == 1:
            return datatsets[0]
        else:
            return datatsets

def get_data_paths(**kwargs):
    # load params and config
    data_param, _ = get_data_and_config(**kwargs)

    # return only the data_param
    return data_param
