from .index import index_bp
from .api import api_bp


def register_routes(app):
    app.register_blueprint(index_bp)
    app.register_blueprint(api_bp)