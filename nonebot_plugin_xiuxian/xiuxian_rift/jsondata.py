import json
import os
from pathlib import Path

SKILLPATH = Path() / "data" / "xiuxian" / "功法" / "功法概率设置.json"

def read_f():
    with open(SKILLPATH, "r", encoding="UTF-8") as f:
        data = f.read()
    return json.loads(data)
