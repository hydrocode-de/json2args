from typing import Tuple
import os
import json
from yaml import load, Loader


CONF_FILE = '/src/tool.yml'
PARAM_FILE = '/in/parameters.json'

def _get_env(**kwargs) -> dict:
    return {
        'conf_file': kwargs.get('CONF_FILE', os.environ.get('CONF_FILE', CONF_FILE)),
        'param_file': kwargs.get('PARAM_FILE', os.environ.get('PARAM_FILE', PARAM_FILE))
    }


def _read_config(**kwargs) -> dict:
    # get the config file
    with open(_get_env(**kwargs)['conf_file'], 'r') as f:
        return load(f.read(), Loader=Loader)


def _raw_read_files(**kwargs) -> Tuple[str, dict, dict]:
    # load the parameter file
    with open(_get_env(**kwargs)['param_file']) as f:
        p = json.load(f)

    # load the config
    config = _read_config(**kwargs)

    # load only the first section
    # TODO: later, this should work on more than one tool
    section = os.environ.get('TOOL_RUN', list(p.keys())[0])

    return section, p, config


def get_param_and_config(**kwargs) -> Tuple[dict, dict]:
    # read the files
    section, p, config = _raw_read_files(**kwargs)

    # find parameters section in config
    param_conf = config['tools'][section]['parameters']

    # find parameters section in input
    param = p[section]['parameters']

    return param, param_conf



def get_data_and_config(**kwargs) -> Tuple[dict, dict]:
    # read the files
    section, p, config = _raw_read_files(**kwargs)

    # find data section in config
    data_conf = config['tools'][section]['data']

    # find data section in input
    data = p[section]['data']

    return data, data_conf
