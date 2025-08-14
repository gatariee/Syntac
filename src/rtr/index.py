from flask import Blueprint, render_template
from services.loader import get_connectors
from services.parser import build_connector_description

index_bp = Blueprint('index', __name__)


@index_bp.route("/")
def index():
    connectors = get_connectors()
    connector_desc = build_connector_description(connectors)
    return render_template('index.html', connectors=connector_desc)