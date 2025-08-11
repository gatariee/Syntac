import os
import importlib
from config import Config
from connectors.base import get_registered_modules

_CONNECTORS = None


def load_connectors():
    """
    Loads all connectors from the specified path in the configuration.
    Default: ./connectors/*.py
    """
    global _CONNECTORS
    
    pkg = Config.CONNECTORS_PATH
    for f in os.listdir(pkg):
        if f.endswith(".py") and f != "__init__.py":
            module_name = f"{os.path.basename(pkg)}.{f[:-3]}"
            importlib.import_module(module_name)
    
    _CONNECTORS = get_registered_modules()
    return _CONNECTORS


def get_connectors():
    global _CONNECTORS
    if _CONNECTORS is None:
        load_connectors()
    return _CONNECTORS