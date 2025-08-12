import os
import importlib
from connectors.base import get_registered_modules

_CONNECTORS = None


def load_connectors(pkg_path: str):
    global _CONNECTORS
    for f in os.listdir(pkg_path):
        if f.endswith(".py") and f != "__init__.py":
            module_name = f"{os.path.basename(pkg_path)}.{f[:-3]}"
            importlib.import_module(module_name)
    
    _CONNECTORS = get_registered_modules()
    return _CONNECTORS

def get_connectors():
    global _CONNECTORS
    if _CONNECTORS is None:
        load_connectors()
    return _CONNECTORS