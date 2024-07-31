from typing import Tuple
import os
import json
from yaml import load, Loader


CONF_FILE = ['/src/tool.yml']
PARAM_FILES = ['/in/input.json', '/in/inputs.json']

def _get_env(**kwargs) -> dict:
    # get the config file
    conf = kwargs.get('CONF_FILE', os.environ.get('CONF_FILE'))

    # if conf is none, try any of the CONF_FILE
    if not conf:
        for c in CONF_FILE:
            conf = c
            if os.path.exists(c):
                break


    # get the input file 
    param_file = kwargs.get('PARAM_FILE', os.environ.get('PARAM_FILE'))

    # test all param files until we find one
    if param_file is None:
        for p in PARAM_FILES:
            param_file = p
            if os.path.exists(p):
                break

    return {
        'conf_file': conf,
        'param_file': param_file
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

    return section, param, param_conf



def get_data_and_config(**kwargs) -> Tuple[dict, dict]:
    # read the files
    section, p, config = _raw_read_files(**kwargs)

    # find data section in config
    data_conf = config['tools'][section]['data']

    # find data section in input
    data = p[section]['data']

    return data, data_conf
