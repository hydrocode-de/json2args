"""
Use these tools inside the docker container to read and
parse the tool configuration and the parameters.
"""
import os
import json
from itertools import chain

from dateutil.parser import parse, isoparse

from json2args.exceptions import ToolConfigMissingError
from json2args.util import get_param_and_config


def _parse_param(key: str, val: str, param_config: dict):
    # switch the type
    try:
        c = param_config[key]
    except KeyError:
        msg = f"The pair {key}: {val} could not be parsed. The config does not contain a specification for {key}. Check the tool.yml and input.json for misspellings first."
        raise ToolConfigMissingError(msg)

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
    
    # strings
    elif t.lower() in ('datetime', 'date', 'time'):
        # first try ISO 8601
        val = isoparse(val)
        if val is None:
            val = parse(val)
        return val
    
    # integer and float
    elif t.lower() in ('integer', 'float'):
        # check for min and max values in config
        min = c.get('min', None)
        max = c.get('max', None)

        # check wether val is in min and max range
        if min and max:
            # check if min is smaller than max
            if max <= min:
                raise ValueError(f"There is an error in your parameter configuration / tool.yml, as the given minimum value ({min}) for parameter '{key}' is higher than or equal to the maximum number ({max}).")
            elif not (min <= val <= max):
                raise ValueError(f"{key} is {val}, but it must be between {min} and {max}.")
        elif min and not min <= val:
            raise ValueError(f"{key} is {val}, but must be higher than {min}.")
        elif max and not val <= max:
            raise ValueError(f"{key} is {val}, but must be smaller than {max}.")
        
        # if no exception rasised, return the value
        if t.lower() == 'integer':
            return int(val)
        else:
            return float(val)
    
    # bools
    elif t.lower() in ('boolean', 'bool'):
        return bool(val)
    else:
        return val


def get_parameter(**kwargs) -> dict:
    # load params and config
    param, param_conf = get_param_and_config(**kwargs)

    # container for parsed arguments
    kwargs = {}

    # get all parameters from param_config that have a default value and are not optional to parse default values
    default_params = {name: x.get('default') for name, x in param_conf.items() if x.get('default') is not None and x.get('optional', False)==False}

    # combine parameters from param_file and default parameters
    # defaults have to go first, so that they can be overwritten by the params
    params2parse = chain(default_params.items(), param.items())

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
