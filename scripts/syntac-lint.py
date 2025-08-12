#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This script is a basic syntax linter for connectors, this just makes sure that your connectors follow the stipulated format.
"""


import sys
import os
import importlib.util
import inspect
from pathlib import Path

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from services.parser import pretty_print

def lazy_import(pkg_path: str):
    path = Path(pkg_path).resolve()
    
    if not path.exists():
        raise FileNotFoundError(f"File not found: {pkg_path}")
    
    if not path.suffix == '.py':
        raise ValueError(f"File must be a Python file (.py): {pkg_path}")
    
    parent_dir = str(path.parent)
    original_path = sys.path.copy()
    
    if parent_dir not in sys.path:
        sys.path.insert(0, parent_dir)
    
    project_root = path.parent.parent
    if project_root.exists() and str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    
    try:
        module_name = path.stem
        spec = importlib.util.spec_from_file_location(module_name, path)
        
        if spec is None:
            raise ImportError(f"Could not create module spec for: {pkg_path}")
        
        module = importlib.util.module_from_spec(spec)
        
        if hasattr(spec.loader, 'get_filename'):
            module.__file__ = spec.loader.get_filename()
        
        relative_path = path.relative_to(project_root) if project_root.exists() else path
        package_parts = relative_path.parts[:-1]
        if package_parts:
            module.__package__ = '.'.join(package_parts)
        
        spec.loader.exec_module(module)
        
        classes = []
        for _, obj in inspect.getmembers(module, inspect.isclass):
            if hasattr(obj, '__module__') and (
                obj.__module__ == module_name or 
                obj.__module__ == module.__name__
            ):
                classes.append(obj)
        
        if len(classes) == 0:
            raise ValueError(f"No classes found in: {pkg_path}")
        elif len(classes) > 1:
            class_names = [cls.__name__ for cls in classes]
            raise ValueError(
                f"Multiple classes found in {pkg_path}: {class_names}. "
                "Expected exactly one class."
            )
        
        return classes[0]
        
    finally:
        sys.path = original_path


def main():
    if len(sys.argv) != 2:
        print("Usage: python syntac-lint.py <path_to_python_file>")
        sys.exit(1)
    
    pkg_path = sys.argv[1]
    imported_class = lazy_import(pkg_path)
    
    print(f"+ Imported class: {imported_class.__name__} from {pkg_path}")

    # If this fails, your class is probably broken!
    pretty_print({imported_class.__name__: imported_class})

if __name__ == "__main__":
    main()