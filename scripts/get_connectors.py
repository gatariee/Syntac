# dirty trick because i'm too lazy to make this a proper package
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services.loader import load_connectors, get_connectors
from services.parser import pretty_print


if __name__ == "__main__":
    CFG_PATH = "../connectors"
    F_CFG_PATH = os.path.abspath(CFG_PATH)
    assert os.path.exists(F_CFG_PATH), f"Path {F_CFG_PATH} does not exist"

    load_connectors(F_CFG_PATH)

    CONNECTORS = get_connectors()
    assert len(CONNECTORS) > 0, "No connectors loaded"
    print(f"+ loaded {len(CONNECTORS)} connectors")

    pretty_print(CONNECTORS)