import os
from pathlib import Path

import pandas as pd
import xarray as xr

from json2args.data import get_data

# use the absolute path of this file
base = Path(os.path.dirname(__file__)).resolve()


# define default kwargs for overwrites in tests
kwargs = dict(
    CONF_FILE = base / 'default.yml',
    PARAM_FILE = base / 'default.json'
)

batches = dict(
    CONF_FILE = base / 'default.yml',
    PARAM_FILE = base / 'batch_data.json'
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

def test_load_single_csv():
    # preload iris as dataframe directly
    iris = get_data('iris', **kwargs)

    # make sure it's a dataframe
    assert isinstance(iris, pd.DataFrame)
    assert iris.shape == (150, 5)


def test_load_batched_csv():
    # load the batched data
    iris = get_data('iris', **batches)

    # this should result in a single dataframe with identical shape (like above)
    assert isinstance(iris, pd.DataFrame)
    assert iris.shape == (150, 5)


def test_load_single_nc():
    # preload march era5 as xarry dataset directly
    era5 = get_data('march', **batches)

    # make sure it's a xarray.Dataset
    assert isinstance(era5, xr.Dataset)
    assert len(era5.dims) == 3
    assert era5.swvl2.to_numpy().shape == (1, 77, 91)
    era5.close()


def test_load_batched_nc():
    # load the batched era5
    era5 = get_data('era5', **batches)

    # make sure it's a xarray.Dataset
    assert isinstance(era5, xr.Dataset)
    assert len(era5.dims) == 3
    assert era5.swvl2.to_numpy().shape == (4, 77, 91)  # loaded 4 monthly chunks
    era5.close()
