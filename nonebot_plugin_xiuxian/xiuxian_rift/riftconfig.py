import json
import os
from pathlib import Path

configkey = ["open", "rift"]
CONFIG = {
    "open":[],
    "rift": {
        "东玄域": {
            "type_rate": 200,#概率
            "rank":1,#增幅等级
            "count":3,#次数
            "time":60,#时间，单位分
        },
        "西玄域": {
            "type_rate": 200,
            "rank":1,
            "count":3,
            "time":60,#时间，单位分
        },
        "妖域": {
            "type_rate": 100,
            "rank":2,
            "count":5,
            "time":90,#时间，单位分
        }, 
        "乱魔海": {
            "type_rate": 100,
            "rank":2,
            "count":5,
            "time":90,#时间，单位分
        },
        "幻雾林": {
            "type_rate": 50,
            "rank":4,
            "count":5,
            "time":120,#时间，单位分
        },
        "狐鸣山": {
            "type_rate": 50,
            "rank":4,
            "count":5,
            "time":120,#时间，单位分
        },
        "云梦泽": {
            "type_rate": 25,
            "rank":6,
            "count":5,
            "time":150,#时间，单位分
        },
        "乱星原": {
            "type_rate": 12,
            "rank":8,
            "count":5,
            "time":150,#时间，单位分
        },
        "黑水湖": {
            "type_rate": 6,
            "rank":10,
            "count":5,
            "time":180,#时间，单位分
        }
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
