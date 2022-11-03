import json
import os
from pathlib import Path

SKILLPATH = Path() / "data" / "xiuxian" / "功法" / "功法概率设置.json"
PLAYERSDATA = Path() / "data" / "xiuxian" / "players"

def read_f():
    with open(SKILLPATH, "r", encoding="UTF-8") as f:
        data = f.read()
    return json.loads(data)

def read_rift_data(user_id):
    user_id = str(user_id)
    FILEPATH = PLAYERSDATA / user_id / "riftinfo.json"
    with open(FILEPATH, "r", encoding="UTF-8") as f:
        data = f.read()
    return json.loads(data)

def save_rift_data(user_id, data):
    user_id = str(user_id)
    if not os.path.exists(PLAYERSDATA / user_id):
        print("目录不存在，创建目录")
        os.makedirs(PLAYERSDATA / user_id)
    FILEPATH = PLAYERSDATA / user_id / "riftinfo.json"
    data = json.dumps(data, ensure_ascii=False, indent=3)
    save_mode = "w" if os.path.exists(FILEPATH) else "x"
    with open(FILEPATH, mode=save_mode, encoding="UTF-8") as f:
        f.write(data)
        f.close
    return True