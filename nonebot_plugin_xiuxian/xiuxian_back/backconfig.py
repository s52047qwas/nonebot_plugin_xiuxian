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
        "筑基丹":{
            "id":1400,
            "start_price":5000,
        },
        "聚顶丹":{
            "id":1401,
            "start_price":10000,
        },
        "朝元丹":{
            "id":1402,
            "start_price":10000,
        },
        "锻脉丹":{
            "id":1403,
            "start_price":20000,
        },
        "护脉丹":{
            "id":1404,
            "start_price":20000,
        },
        "天命淬体丹":{
            "id":1405,
            "start_price":40000,
        },
        "澄心塑魂丹":{
            "id":1406,
            "start_price":40000,
        },
        "混元仙体丹":{
            "id":1407,
            "start_price":40000,
        },
        "黑炎丹":{
            "id":1408,
            "start_price":80000,
        },
        "金血丸":{
            "id":1409,
            "start_price":80000,
        },
        "虚灵丹":{
            "id":1410,
            "start_price":160000,
        },
        "净明丹":{
            "id":1411,
            "start_price":160000,
        },
        "安神灵液":{
            "id":1412,
            "start_price":300000,
        },
        "魇龙之血":{
            "id":1413,
            "start_price":300000,
        },
        "化劫丹":{
            "id":1414,
            "start_price":300000,
        },
        "太上玄门丹":{
            "id":1415,
            "start_price":300000,
        },
        "天命血凝丹":{
            "id":1416,
            "start_price":300000,
        },
        "太乙炼髓丹":{
            "id":1417,
            "start_price":300000,
        }
    },
    "拍卖会定时参数":{#拍卖会生成的时间，每天的10-15点
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
