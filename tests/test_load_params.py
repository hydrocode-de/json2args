import os
from pathlib import Path
from datetime import datetime as dt

import pytest
from json2args.exceptions import ToolConfigMissingError

from json2args.util import get_param_and_config, _raw_read_files
from json2args.parameter import _parse_param, get_param_and_config, get_parameter


# use the absolute path of this file
base = Path(os.path.dirname(__file__)).resolve()


# define default kwargs for overwrites in tests
kwargs = dict(
        CONF_FILE = base / 'default.yml',
        PARAM_FILE = base / 'default.json'
    )

def test_load_files():
    # get the params and their config
    sec, params, param_conf = _raw_read_files(**kwargs)
    
    # parse the conf like the parsers would do
    conf = param_conf['tools'][sec]['parameters']
    # add some asserts on param_conf
    assert isinstance(param_conf, dict)
    assert isinstance(conf, dict)
    assert len(conf) == 7
    assert conf['foo_float'].get('optional', False) == True
    
    # add some asserts on params
    assert isinstance(params, dict)
    assert len(params[sec]) == 2
    assert 'parameters' in params[sec]
    assert 'data' in params[sec]


def test_parse_literal():
    # get the kwargs parsed by get_parameter
    args = get_parameter(**kwargs)

    # assert the numbers
    assert args['foo_int'] == 42
    assert args['foo_float'] - 13.12 < 0.001
    assert isinstance(args['foo_bool'], bool) and args['foo_bool']
    assert args['foo_string'] == 'bar'
    assert args['foo_enum'] == 'bar'
    
    # assert the array
    arr = args['foo_float_array']
    assert len(arr) == 3
    assert arr[1] - 2.2 < 0.001

    # assert datetime
    assert isinstance(args['foo_time'], dt)
    assert args['foo_time'].year == 2019
    assert args['foo_time'].hour == 14


def test_fail_on_range_error():
    params, params_conf = get_param_and_config(**kwargs)

    with pytest.raises(ValueError) as e:
        _parse_param('foo_int', 100, params_conf)
    
    assert 'must be between 5 and 90' in str(e.value)


def test_fail_on_enum():
    _, params_conf = get_param_and_config(**kwargs)

    with pytest.raises(ValueError) as e:
        _parse_param('foo_enum', 'noValidValue', params_conf)

    assert 'noValidValue is not contained in' in str(e.value)


def test_missing_config():
    _, params_conf = get_param_and_config(**kwargs)

    with pytest.raises(ToolConfigMissingError) as e:
        _parse_param('foo_missing', 'nan', params_conf)
    
    assert 'The pair foo_missing: nan could not be parsed' in str(e.value)

def test_optional_and_default_values():
    # overwrite the params file
    kwargs['PARAM_FILE'] = base / 'optional.json'

    # get the args as parsed by get_parameter
    args = get_parameter(**kwargs)

    # the optionals must not be there
    assert 'foo_float' not in args

    # the defaults must be there with default value
    assert 'foo_string' in args
    assert 'foo_bool' in args
    assert args['foo_string'] == 'foo'  # not bar anymore
    assert args['foo_bool'] == False    # not True anymore 
