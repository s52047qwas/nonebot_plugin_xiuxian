import json
import os
from pathlib import Path

GROUPSJSONPATH = Path(__file__).parent
FILEPATH = GROUPSJSONPATH / 'groups.json'
def read_group():
    with open(FILEPATH, "r", encoding="UTF-8") as f:
        data = f.read()
    return json.loads(data)


def save_group(data):
    data = json.dumps(data, ensure_ascii=False)
    save_mode = "w" if os.path.exists(FILEPATH) else "x"
    with open(FILEPATH, mode=save_mode, encoding="UTF-8") as f:
        f.write(data)
        f.close
    return True