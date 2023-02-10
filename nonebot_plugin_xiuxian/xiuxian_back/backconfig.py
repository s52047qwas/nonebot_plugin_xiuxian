import json
import os
from pathlib import Path

configkey = ["open", "auctions", "交友会定时参数"]
CONFIG = {
    "open": [],
    "auctions": {
        "渡厄丹": {
            "id": 1999,
            "start_price": 100000,
        },
        "鬼面炼心丹": {
            "id": 1503,
            "start_price": 150000,
        },
        "生骨丹": {
            "id": 1101,
            "start_price": 1000,
        },
        "化瘀丹": {
            "id": 1102,
            "start_price": 2000,
        },
        "固元丹": {
            "id": 1103,
            "start_price": 3000,
        },
        "培元丹": {
            "id": 1104,
            "start_price": 4000,
        },
        "黄龙丹": {
            "id": 1105,
            "start_price": 5000,
        },
        "回元丹": {
            "id": 1106,
            "start_price": 6000,
        },
        "回春丹": {
            "id": 1107,
            "start_price": 7000,
        },
        "养元丹": {
            "id": 1108,
            "start_price": 8000,
        },
        "太元真丹": {
            "id": 1109,
            "start_price": 9000,
        },
        "归藏灵丹": {
            "id": 1110,
            "start_price": 10000,
        },

    },
    "交友会定时参数": {  # 交友会生成的时间，每天的10-15点
        "hours": "18-23"
    },
    "shop_auto_add": {
        "生骨丹": {
            "id": 1101,
            "start_price": 1000,
        },
        "化瘀丹": {
            "id": 1102,
            "start_price": 2000,
        },
        "固元丹": {
            "id": 1103,
            "start_price": 3000,
        },
        "培元丹": {
            "id": 1104,
            "start_price": 4000,
        },
        "黄龙丹": {
            "id": 1105,
            "start_price": 5000,
        },
        "回元丹": {
            "id": 1106,
            "start_price": 6000,
        },
        "回春丹": {
            "id": 1107,
            "start_price": 7000,
        },
        "养元丹": {
            "id": 1108,
            "start_price": 8000,
        },
        "太元真丹": {
            "id": 1109,
            "start_price": 9000,
        },
        "归藏灵丹": {
            "id": 1110,
            "start_price": 10000,
        },

    },
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
