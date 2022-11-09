import json
import os
from pathlib import Path

configkey = ["open", "拍卖会定时参数", "auctions"]
CONFIG = {
    "open":[],
    "auctions":{
        "渡厄丹":{
            "id":1999,
            "start_price":100000,
        },
        "吐纳功法":{
            "id":9001,
            "start_price":5000,
        },
        "冰心丹":{
            "id":1500,
            "start_price":50000,
        },
        "明心丹":{
            "id":1501,
            "start_price":100000,
        },
        "幻心玄丹":{
            "id":1502,
            "start_price":120000,
        },
        "鬼面炼心丹":{
            "id":1503,
            "start_price":150000,
        },
        "少阴清灵丹":{
            "id":1504,
            "start_price":180000,
        },
        "天命炼心丹":{
            "id":1505,
            "start_price":200000,
        },
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
