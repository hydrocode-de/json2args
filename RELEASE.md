# json2args

The `json2args` package can be used in docker container following the [Tool specification](https://github.com/vforwater/tool-specs).
Following these specifications, docker-based and reproducible scientifc tools or workflows can be implemented
upon a set of additional files inside the container. Minimal metadata is added via a `tool.yml` and the 
parameterization and data specification is done via a `input.json`, mounted along with the data files into the container.

This package is a utility for Python based docker tools, that loads, parses and validates the input parameters.
Optionally, you can use the package to pre-load standard input files into the appropriate Python data strurctures.

```python
from json2args import get_parameter, get_data

params = get_parameter()
iris_dataset = get_data('iris')  # optional

# usage
params['foo']   # can be a string 'bar'
iris_dataset    # This is a pandas.Dataframe, loaded from a standard CSV
```