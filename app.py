from flask import Flask
from rtr.init import register_routes
from services.connector_loader import load_connectors
from config import Config


def init():
    app = Flask(__name__)
    load_connectors()
    register_routes(app)
    return app


if __name__ == "__main__":
    app = init()
    app.run(
        host=Config.HOST,
        port=Config.PORT,
        debug=Config.DEBUG
    )
