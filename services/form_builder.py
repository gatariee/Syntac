from typing import get_type_hints, ClassVar
import inspect


def build_connector_description(connectors):
    """Build connector descriptions for the frontend."""
    desc = {}
    
    for name, cls in connectors.items():
        hints = get_type_hints(cls, include_extras=True)
        
        globals_ = _extract_global_fields(cls, hints)
        subs = _extract_submodule_fields(cls, globals_)
        
        desc[name] = {"globals": globals_, "subs": subs}
    
    return desc


def _extract_global_fields(cls, hints):
    return [
        {
            "name": f,
            "type": getattr(hints[f], "__name__", str),
            "default": "" if getattr(cls, f, '') is inspect._empty else getattr(cls, f, ''),
        }
        for f, t in hints.items()
        if not getattr(t, "__origin__", None) is ClassVar
    ]


def _extract_submodule_fields(cls, globals_):
    """Extract submodule-specific fields."""
    subs = []
    global_names = {g["name"] for g in globals_}
    
    for key in cls.sub_modules:
        sig = cls._submodule_sigs[key]
        extras = [
            {
                "name": p.name,
                "type": getattr(p.annotation, "__name__", str),
                "default": "" if p.default is inspect._empty else p.default,
            }
            for p in sig.parameters.values()
            if p.name not in global_names
        ]
        subs.append({"key": key, "extras": extras})
    
    return subs