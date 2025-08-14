from flask import Blueprint, request, jsonify
from typing import get_type_hints, ClassVar
from services.loader import get_connectors

api_bp = Blueprint('api', __name__)


@api_bp.route("/preview", methods=["POST"])
def preview():
    data = request.json or {}
    name = data.pop("__connector", None)
    sub = data.pop("__sub", None)
    
    if not name or not sub:
        return jsonify(error="connector/sub missing"), 400
    
    connectors = get_connectors()
    cls = connectors.get(name)
    
    if not cls or sub not in cls.sub_modules:
        return jsonify(error="unknown"), 404

    try:
        cmd = _generate_command(cls, data, sub)
        return jsonify(command=cmd)
    except Exception as e:
        return jsonify(error=str(e)), 500


def _generate_command(cls, data, sub):
    hints = get_type_hints(cls, include_extras=True)
    
    global_kwargs = {
        k: data[k]
        for k in hints
        if k in data
        and not getattr(
            hints[k].__origin__ if hasattr(hints[k], "__origin__") else None,
            "__origin__",
            None,
        )
        is ClassVar
    }
    
    inst = cls(**global_kwargs)
    extras = {k: data[k] for k in data if k not in global_kwargs}
    
    return inst.run_sub_module(sub, **extras)