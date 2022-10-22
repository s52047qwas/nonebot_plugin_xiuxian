import json
import os
from pathlib import Path

configkey = ["Boss灵石", "Boss名字", "生成时间", "Boss倍率", "Boss个数上限"]
CONFIG = {
    "Boss灵石" : {
    #生成Boss给的灵石
    '练气境':1000,
    '筑基境':2000,
    '结丹境':5000,
    '元婴境':10000,
    '化神境':20000,
    '炼虚境':60000,
    '合体境':120000,
    '大乘境':300000,
    '渡劫境':700000,
    },
    "Boss名字":["墨蛟","婴鲤兽","千目妖","鸡冠蛟","妖冠蛇","铁火蚁","天晶蚁","银光鼠","紫云鹰","狗青"],#生成的Boss名字，自行修改
    "生成时间":'9-22',#生成的时间，9-22点每小时生成一个boss
    "Boss个数上限":10,
    "Boss倍率":{
        #Boss属性：大境界平均修为是基础数值，气血：15倍，真元：10倍，攻击力：0.2倍
        #作为参考：人物的属性，修为是基础数值，气血：0.5倍，真元：1倍，攻击力：0.1倍
        "气血":15,
        "真元":10,
        "攻击":0.2
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