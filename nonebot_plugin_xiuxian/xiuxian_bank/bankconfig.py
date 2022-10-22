import json
import os
from pathlib import Path

configkey = ["BANKLEVEL"]
CONFIG = {
    "BANKLEVEL" : {
    #钱庄等级参数。savemax：当前等级可以存储上限，levelup：升级钱庄等级消耗的灵石数量，interest：每小时给与的利息，level：当前等级会员的名称
    "1":{"savemax":10000,"levelup":100000,'interest':0.002,"level":"普通会员"},
    "2":{"savemax":20000,"levelup":200000,'interest':0.0021,"level":"小会员"},
    "3":{"savemax":40000,"levelup":400000,'interest':0.0022,"level":"大会员"},
    "4":{"savemax":80000,"levelup":800000,'interest':0.0023,"level":"优质会员"},
    "5":{"savemax":160000,"levelup":1600000,'interest':0.0024,"level":"黄金会员"},
    "6":{"savemax":320000,"levelup":3200000,'interest':0.0025,"level":"钻石会员"},
    "7":{"savemax":640000,"levelup":0,'interest':0.0028,"level":"终极会员"},
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