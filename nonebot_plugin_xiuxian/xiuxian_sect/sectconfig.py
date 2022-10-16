import json
import os
from pathlib import Path

configkey = ["LEVLECOST", "等级建设度", "发放宗门资材", "每日宗门任务次上限", "宗门任务完成cd", "宗门任务"]
CONFIG = {
    "LEVLECOST" : {
    #攻击修炼的灵石消耗
    '0':10000,
    '1':20000,
    '2':40000,
    '3':80000,
    '4':160000,
    '5':320000,
    '6':500000,
    '7':500000,
    '8':500000,
    '9':500000,
    '10':500000,
    '11':500000,
    '12':500000,
    '13':500000,
    '14':500000,
    '15':500000,
    '16':500000,
    '17':500000,
    '18':500000,
    '19':500000,
    '20':500000,
    '21':500000,
    '22':500000,
    '23':500000,
    '24':500000,
    '25':0,
    },
    "等级建设度":5000000,#决定宗门修炼上限等级的参数，500万贡献度每级
    "发放宗门资材":{
        "时间":"11-12",#定时任务发放宗门资材，每日11-12点根据 对应宗门贡献度的 * 倍率 发放资材
        "倍率":1,#倍率
    },
    "每日宗门任务次上限":3,
    "宗门任务完成cd":1800,#宗门任务每次完成间隔，单位秒
    "宗门任务":{
        #type=1：需要扣气血，type=2：需要扣灵石
        #cost：消耗，type=1时，气血百分比，type=2时，消耗灵石
        #give：给与玩家当前修为的百分比修为
        #sect：给与所在宗门 储备的灵石，同时会增加灵石 * 10 的建设度
        "巡逻周边":{
            "desc":"宗门附近有人在捣乱，请道友去周边震慑宵小吧",
            "type":1,
            "cost":0.1,
            "give":0.002,
            "sect":20000,
        },
        "寻找宝物":{
            "desc":"宗门现在需要宝物：捆仙锁，请道友去寻来交给宗门吧",
            "type":2,
            "cost":30000,
            "give":0.05,
            "sect":50000,
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