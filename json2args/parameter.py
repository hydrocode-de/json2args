"""
Use these tools inside the docker container to read and
parse the tool configuration and the parameters.
"""
import os
import json
from yaml import load, Loader
from itertools import chain

import numpy as np
import pandas as pd


CONF_FILE = '/src/tool.yml'
PARAM_FILE = '/in/parameters.json'

def get_env() -> dict:
    return {
        'conf_file': os.environ.get('CONF_FILE', CONF_FILE),
        'param_file': os.environ.get('PARAM_FILE', PARAM_FILE)
    }


def read_config() -> dict:
    # get the config file
    with open(get_env()['conf_file'], 'r') as f:
        return load(f.read(), Loader=Loader)


def _parse_param(key: str, val: str, param_config: dict):
    # switch the type
    c = param_config[key]

    # handle arrays
    # TODO: add an optional shape parameter. if set -> np.flatten().reshape(shape)
    if isinstance(val, (list, tuple)):
        return [_parse_param(key, _, param_config) for _ in val]
    
    # get type from tool yaml
    t = c['type'].strip()

    # handle specific types
    if t == 'enum':
        val = val.strip()
        if val not in c['values']:
            raise ValueError(f"The value {val} is not contained in {c['values']}")
        return val
    elif t.lower() in ('datetime', 'date', 'time'):
        # TODO: implement this
        raise NotImplementedError
    elif t == 'file':
        # get the ext and use the corresponding reader
        _, ext = os.path.splitext(val)
        
        # use numpy for matrix files
        if ext.lower() == '.dat':
            val = np.loadtxt(val)
        elif ext.lower() == '.csv':
            val = pd.read_csv(val)
        elif ext.lower() == '.json':
            with open(val, 'r') as f:
                val = json.load(f)
        return val
    elif t.lower() in ('integer', 'float'):
        # check for min and max values in config
        min = c.get('min', None)
        max = c.get('max', None)

        # check wether val is in min and max range
        if min and max:
            # check if min is smaller than max
            if max < min:
                raise ValueError(f"There is an error in your parameter configuration / tool.yml, as the given minimum value ({min}) for parameter '{key}' is higher than the maximum number ({max}).")
            elif not (min <= val <= max):
                raise ValueError(f"{key} is {val}, but it must be between {min} and {max}.")
        elif min and not min <= val:
            raise ValueError(f"{key} is {val}, but must be higher than {min}.")
        elif max and not val <= max:
            raise ValueError(f"{key} is {val}, but must be smaller than {max}.")
        else:
            return val
    else:
        return val


def get_parameter() -> dict:
    # load the parameter file
    with open(get_env()['param_file']) as f:
        p = json.load(f)

    # load the config
    config = read_config()

    # load only the first section
    # TODO: later, this should work on more than one tool
    section = os.environ.get('TOOL_RUN', list(p.keys())[0])

    # find parameters in config
    param_conf = config['tools'][section]['parameters']

    # container for parsed arguments
    kwargs = {}

    # get all parameters from param_config that have a default value and are not optional to parse default values
    default_params = {name: x.get('default') for name, x in param_conf.items() if x.get('default') is not None and x.get('optional', False)==False}

    # combine parameters from param_file and default parameters
    params2parse = chain(p[section].items(), default_params.items())

    # parse all parameter
    for key, value in params2parse:
        kwargs[key] = _parse_param(key, value, param_conf)

    return kwargs

def parse_parameter() -> dict:
    """
    .. deprecated:: 
        Use get_parameter instead
    """
    print('[FutureWarning]: parse_parameters is deprecated and will be removed with one of the next releases. Please use get_parameters.')
    return get_parameter()
