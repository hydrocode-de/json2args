from typing import List
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field, create_model, ConfigDict

from json2args.util import _raw_read_files

TYPE_MAPPING = {
    'integer': int,
    'float': float,
    'string': str,
    'boolean': bool,
    'datetime': datetime
}


def model_factory(section: str, param_conf: dict) -> type[BaseModel]:
    """
    """
    # first off load the parameters config
    #section, _, config = _raw_read_files(**kwargs)
    #param_conf = config['tools'][section]['parameters']
    
    # get the class name
    class_name = section.capitalize() + 'Parameter'

    # create the fields
    fields = {}

    # iterate over the parameters
    for par_name, par_attrs in param_conf.items():
        # get the type
        if par_attrs['type'] == 'enum':
            T = Enum(f"{par_name.capitalize()}Enum", {v: v for v in par_attrs['values']})
        else:
            T = TYPE_MAPPING.get(par_attrs['type'], str)
        
        # handle arrays
        if par_attrs.get('array', False):
            T = List[T]

        # configure the filed
        field = Field(
            description=par_attrs.get('description', None),
            optional=par_attrs.get('optional', False),
            default=par_attrs.get('default', None),
            ge=par_attrs.get('min', None),
            le=par_attrs.get('max', None),
        )

        # add the field
        fields[par_name] = (T, field)

    # create a model and return it
    return create_model(class_name, **fields, __config__=ConfigDict(use_enum_values=True))
