import os
from pathlib import Path

import pandas as pd

from json2args.data import get_data

# use the absolute path of this file
base = Path(os.path.dirname(__file__)).resolve()


# define default kwargs for overwrites in tests
kwargs = dict(
        CONF_FILE = base / 'default.yml',
        PARAM_FILE = base / 'default.json'
    )


def test_load_defaults():
    # preload data
    args = get_data(as_dict=True, **kwargs)

    # assert that it is a dictionary
    assert isinstance(args, dict)

    # get the iris dataset
    assert 'iris' in args
    iris = args['iris']

    # make sure it's a dataframe
    assert isinstance(iris, pd.DataFrame)
    assert iris.shape == (150, 5)

def test_load_single_dataset():
    # preload iris as dataframe directly
    iris = get_data('iris', **kwargs)

    # make sure it's a dataframe
    assert isinstance(iris, pd.DataFrame)
    assert iris.shape == (150, 5)


def test_load_batched_csv():
    # use the batch_data.json3
    args = kwargs.copy()
    args['PARAM_FILE'] = base / 'batch_data.json'

    # load the batched data
    iris = get_data('iris', **args)

    # this should result in a single dataframe with identical shape (like above)
    assert isinstance(iris, pd.DataFrame)
    assert iris.shape == (150, 5)
