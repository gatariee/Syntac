import os

class Config:
    HOST = "0.0.0.0"
    PORT = 5000
    DEBUG = True
    CONNECTORS_PATH = os.path.join(os.path.dirname(__file__), "connectors")