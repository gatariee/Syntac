from flask import Blueprint, render_template
from services.connector_loader import get_connectors
from services.form_builder import build_connector_description

main_bp = Blueprint('main', __name__)


@main_bp.route("/")
def index():
    connectors = get_connectors()
    connector_desc = build_connector_description(connectors)
    return render_template('index.html', connectors=connector_desc)