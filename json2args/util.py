from typing import Tuple
import os
import json
from yaml import load, Loader


CONF_FILE = '/src/tool.yml'
PARAM_FILE = '/in/parameters.json'

def get_env(**kwargs) -> dict:
    return {
        'conf_file': kwargs.get('CONF_FILE', os.environ.get('CONF_FILE', CONF_FILE)),
        'param_file': kwargs.get('PARAM_FILE', os.environ.get('PARAM_FILE', PARAM_FILE))
    }


def read_config(**kwargs) -> dict:
    # get the config file
    with open(get_env(**kwargs)['conf_file'], 'r') as f:
        return load(f.read(), Loader=Loader)


def get_param_and_config(**kwargs) -> Tuple[dict, dict]:
    # load the parameter file
    with open(get_env(**kwargs)['param_file']) as f:
        p = json.load(f)

    # load the config
    config = read_config(**kwargs)

    # load only the first section
    # TODO: later, this should work on more than one tool
    section = os.environ.get('TOOL_RUN', list(p.keys())[0])

    # find parameters in config
    param_conf = config['tools'][section]['parameters']

    return p[section], param_conf

    