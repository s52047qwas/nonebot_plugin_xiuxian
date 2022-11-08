import json
import os
from pathlib import Path

configkey = ["open", "auction_config", "拍卖会定时参数"]
CONFIG = {
    "open":[],
    "auction_config":{
        "auction_id_list":[1999,6001,6011,6031,7001,7002,7003,7011],#之后会修改
        "auction_start_prict":100000,
    },
    "拍卖会定时参数":{#拍卖会生成的时间，每天的10-15点
        "hours":"10-15"
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
