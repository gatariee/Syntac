from typing import get_type_hints, ClassVar, Dict, Any, List
import inspect
import markdown

def to_html(text: str) -> str:
    return markdown.markdown(text, extensions=["fenced_code", "tables", "codehilite"])

def _format_default(default: Any) -> str:
    if default is inspect._empty:
        return "<not specified>, you should really specify this!"
    
    if ( type(default) is str ) and ( len(default) == 0 ):
        return "\"\""

    return str(default)


def pretty_print(connectors: Dict[str, Any], printer: callable = print) -> None:
    for name, cls in connectors.items():
        hints = get_type_hints(cls, include_extras=True)
        printer(f"┌─ Connector: {name}")
        
        printer("│  Globals Variables:")
        gv = []
        has_globals = False
        for f, t in hints.items():
            if getattr(t, "__origin__", None) is not ClassVar:
                gv.append(f)
                default = getattr(cls, f, inspect._empty)
                printer(f"│    - {f}: {getattr(t, '__name__', str)} (default: {_format_default(default)})")
                has_globals = True
        
        if not has_globals:
            printer("│    - None")

        printer("│  Submodules:")
        if not cls.sub_modules:
            printer("│    - None")
        else:
            for key in cls.sub_modules:
                sig = cls._submodule_sigs[key]
                printer(f"│    - {key}:")
                
                has_params = False
                for p in sig.parameters.values():
                    if p.name in gv:
                        has_params = True
                        pass
                    else:
                        has_params = True
                        printer(f"│      - {p.name}: {getattr(p.annotation, '__name__', str)} (default: {_format_default(p.default)})")
                
                if not has_params:
                    printer("│        (No parameters)")
        printer("└" + "─" * 40)


def build_connector_description(connectors: Dict[str, Any]) -> Dict[str, Any]:
    desc: Dict[str, Any] = {}
    for name, cls in connectors.items():
        hints = get_type_hints(cls, include_extras=True)
        globals_ = _extract_global_fields(cls, hints)
        subs = _extract_submodule_fields(cls, globals_)
        
        for sub in subs:
            sub_key = sub["key"]
            sub["doc"] = cls().get_doc(sub_module=sub_key)
            try:
                sub["doc"] = to_html(sub["doc"])
            except Exception as e:
                sub["doc"] = f"<p>Error converting doc to HTML: {e}</p>"
        
        desc[name] = {"globals": globals_, "subs": subs}
    return desc


def _extract_global_fields(cls: Any, hints: Dict[str, Any]) -> List[Dict[str, Any]]:
    fields: List[Dict[str, Any]] = []
    for f, t in hints.items():
        if not getattr(t, "__origin__", None) is ClassVar:
            fields.append({
                "name": f,
                "type": getattr(hints[f], "__name__", str),
                "default": "" if getattr(cls, f, '') is inspect._empty else getattr(cls, f, ''),
            })
    return fields


def _extract_submodule_fields(cls: Any, globals_: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    subs: List[Dict[str, Any]] = []
    global_names = {g["name"] for g in globals_}
    for key in cls.sub_modules:
        sig = cls._submodule_sigs[key]
        extras: List[Dict[str, Any]] = [
            {
                "name": p.name,
                "type": getattr(p.annotation, '__name__', str),
                "default": "" if p.default is inspect._empty else p.default,
            }
            for p in sig.parameters.values()
            if p.name not in global_names
        ]
        subs.append({"key": key, "extras": extras})
    return subs