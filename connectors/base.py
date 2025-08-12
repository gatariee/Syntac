import inspect
from abc import ABC
from dataclasses import dataclass
from typing import (
    Any, Callable, ClassVar, Dict, List, OrderedDict, Type,
    get_type_hints,
)

def sub_module(key: str) -> Callable[[Callable], Callable]:
    def decorator(fn: Callable) -> Callable:
        setattr(fn, "_sub_module_key", key)
        return fn
    return decorator


@dataclass(init=False)
class Module(ABC):
    name:        ClassVar[str]       = ""
    description: ClassVar[str]       = ""

    sub_modules:         ClassVar[Dict[str, Callable]]     = {}
    _submodule_sigs:     ClassVar[Dict[str, inspect.Signature]] = {}

    def __init_subclass__(cls, **kwargs: Any):
        super().__init_subclass__(**kwargs)
        mods: Dict[str, Callable] = {}
        sigs: Dict[str, inspect.Signature] = {}
        for attr, val in cls.__dict__.items():
            if callable(val) and hasattr(val, "_sub_module_key"):
                key = getattr(val, "_sub_module_key")
                mods[key] = val
                sig = inspect.signature(val)
                params = list(sig.parameters.values())[1:]
                sigs[key] = inspect.Signature(params)
        cls.sub_modules = mods
        cls._submodule_sigs = sigs

    def __init__(self, **kwargs: Any):
        cls = type(self)
        self.name        = cls.name
        self.description = cls.description

        hints = get_type_hints(cls, include_extras=True)
        self._global_fields = [
            k for k, t in hints.items()
            if not getattr(t, "__origin__", None) is ClassVar
        ]
        for field in self._global_fields:
            default = getattr(cls, field, None)
            val = kwargs.pop(field, default)
            setattr(self, field, val)

        if kwargs:
            bad = ", ".join(kwargs)
            raise TypeError(f"{cls.__name__} got unexpected kwargs: {bad}")

    def get_params(self) -> Dict[str, Any]:
        params = {field: getattr(self, field) for field in self._global_fields}
        return params
    
    def get_submodules(self) -> List[str]:
        return list(self.sub_modules.keys())

    def get_submodule_params(self, key: str) -> OrderedDict[str, inspect.Parameter]:
        if key not in self.sub_modules:
            raise KeyError(f"{self.name} has no sub_module {key}")
        sig = self._submodule_sigs[key]
        params = OrderedDict(sig.parameters)
        return params

    def run_sub_module(self, key: str, **kwargs: Any) -> Any:
        if key not in self.sub_modules:
            raise KeyError(f"{self.name} has no sub_module {key}")

        opts = self.get_params()
        opts.update(kwargs)

        sig = self._submodule_sigs[key]
        call_args = {}
        for name, param in sig.parameters.items():
            if name in opts:
                call_args[name] = opts[name]
            elif param.default is inspect._empty:
                raise TypeError(
                    f"{key} missing required argument '{name}'"
                )

        method = self.sub_modules[key]
        return method(self, **call_args)

_MODULE_REGISTRY: Dict[str, Type[Module]] = {}

def register_module(cls: Type[Module]) -> Type[Module]:
    _MODULE_REGISTRY[cls.name] = cls
    return cls

def get_registered_modules() -> Dict[str, Type[Module]]:
    return dict(_MODULE_REGISTRY)