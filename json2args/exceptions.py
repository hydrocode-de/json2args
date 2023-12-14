# introduce some specific exceptions

class ToolConfigMissingError(ValueError):
    pass

class FileExtensionError(ValueError):
    pass