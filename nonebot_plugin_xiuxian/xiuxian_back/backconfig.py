import json
import os
from pathlib import Path

configkey = ["open", "auctions", "交友会定时参数"]
CONFIG = {
    "open":[],
    "auctions": {
      "生骨丹": {
         "id": 1101,
         "start_price": 500
      },
      "化瘀丹": {
         "id": 1102,
         "start_price": 1000
      },
      "固元丹": {
         "id": 1103,
         "start_price": 3500
      },
      "培元丹": {
         "id": 1104,
         "start_price": 4000
      },
      "洗髓丹": {
         "id": 2000,
         "start_price": 15000
      },
      "养气丹": {
         "id": 2001,
         "start_price": 20000
      },
      "筑基丹": {
         "id": 1400,
         "start_price": 3000
      },
      "聚顶丹": {
         "id": 1401,
         "start_price": 15000
      },
      "朝元丹": {
         "id": 1402,
         "start_price": 15000
      },
      "锻脉丹": {
         "id": 1403,
         "start_price": 15000
      },
      "摄魂鬼丸": {
         "id": 2009,
         "start_price": 25000
      },
      "一级聚灵旗": {
         "id": 2500,
         "start_price": 15000
      },
      "化尘道袍": {
         "id": 6011,
         "start_price": 25000
      },
      "阴磷甲": {
         "id": 6021,
         "start_price": 35000
      },
      "御灵盾": {
         "id": 6031,
         "start_price": 40000
      },
      "恒心草": {
         "id": 3001,
         "start_price": 1000
      },
      "红绫草": {
         "id": 3002,
         "start_price": 1000
      },
      "罗犀草": {
         "id": 3003,
         "start_price": 1000
      },
      "天青花": {
         "id": 3004,
         "start_price": 1000
      },
      "小气血丹": {
         "id": 2,
         "start_price": 5000
      }
    },
    "交友会定时参数":{#交友会生成的时间，每天的10-15点
        "hours":"17-23"
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
