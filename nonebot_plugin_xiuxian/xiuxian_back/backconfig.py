import json
import os
from pathlib import Path

configkey = ["open", "auctions", "交友会定时参数"]
CONFIG = {
    "open":[],
    "auctions":{
        "渡厄丹":{
            "id":1999,
            "start_price":100000,
        },
        "鬼面炼心丹":{
            "id":1503,
            "start_price":150000,
        },
    },
    "交友会定时参数":{#交友会生成的时间，每天的10-15点
        "hours":"18-23"
    }
}

def get_config():
    try:
        config = readf()
        for key in configkey:
            if key not in list(config.keys()):
                config[key] = CONFIG[key]
        savef(config)
    except:
        config = CONFIG
        savef(config)
    return config

CONFIGJSONPATH = Path(__file__).parent
FILEPATH = CONFIGJSONPATH / 'config.json'
def readf():
    with open(FILEPATH, "r", encoding="UTF-8") as f:
        data = f.read()
    return json.loads(data)


def savef(data):
    data = json.dumps(data, ensure_ascii=False, indent=3)
    savemode = "w" if os.path.exists(FILEPATH) else "x"
    with open(FILEPATH, mode=savemode, encoding="UTF-8") as f:
        f.write(data)
        f.close
    return True
