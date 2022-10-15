import json
import os
from pathlib import Path

configkey = ["Boss灵石", "Boss名字", "生成时间", "Boss倍率"]
CONFIG = {
    "Boss灵石" : {
    #生成Boss给的灵石
    '练气境':20000,
    '筑基境':50000,
    '结丹境':100000,
    '元婴境':200000,
    '化神境':300000,
    '炼虚境':400000,
    '合体境':500000,
    '大乘境':600000,
    '渡劫境':700000,
    },
    "Boss名字":["毛毛虫","蝼蚁","臭鼬","呃呃啊啊啊啊啊","我是SB","叶猫","鳖鳖","七彩通天蟒","乌龟王八蛋"],#生成的Boss名字，自行修改
    "生成时间":'9-22',#生成的时间，9-22点每小时生成一个boss
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
        savef(json.dumps(config, ensure_ascii=False, indent=3))
    except:
        config = CONFIG
        savef(json.dumps(config, ensure_ascii=False, indent=3))
    return config

CONFIGJSONPATH = Path(__file__).parent
FILEPATH = CONFIGJSONPATH / 'config.json'
def readf():
    with open(FILEPATH, "r", encoding="UTF-8") as f:
        data = f.read()
    return json.loads(data)


def savef(data):
    savemode = "w" if os.path.exists(FILEPATH) else "x"
    with open(FILEPATH, mode=savemode, encoding="UTF-8") as f:
        f.write(data)
        f.close
    return True