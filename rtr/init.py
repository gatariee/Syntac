from .main import main_bp
from .api import api_bp


def register_routes(app):
    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp)