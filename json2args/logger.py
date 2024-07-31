import logging
import os
from pathlib import Path

# set some paths
processing_path = Path(os.environ.get('PROCESSING_LOG', '/out/processing.log'))
error_path = Path(os.environ.get('ERROR_LOG', '/out/errors.log'))

# check if the paths exist
if not processing_path.parent.exists():
    processing_path = Path('./').resolve() / 'processing.log'

if not error_path.parent.exists():
    error_path = Path('./').resolve() / 'errors.log'

# create a new logger
logger = logging.getLogger('tools')

# set the log level to debug
logger.setLevel(logging.DEBUG)

# create a file handler for all messages
processing_handler = logging.FileHandler(str(processing_path))

# create a file handler for warnings and errors
error_handler = logging.FileHandler(str(error_path))
error_handler.setLevel(logging.WARNING)

# create a console handler for all messages
console_handler = logging.StreamHandler()
console_handler.setLevel(getattr(logging, os.environ.get('LOG_LEVEL', 'INFO')))

# create a formatter for the file handlers
formatter = logging.Formatter('[%(asctime)s] - [%(levelname)s] - [%(message)s]')

# create a formatter to the console
console_formatter = logging.Formatter('[%(levelname)s]: %(message)s')

# set the formatters
processing_handler.setFormatter(formatter)
error_handler.setFormatter(formatter)
console_handler.setFormatter(console_formatter)

# add the handlers to the logger
logger.addHandler(processing_handler)
logger.addHandler(error_handler)
logger.addHandler(console_handler)