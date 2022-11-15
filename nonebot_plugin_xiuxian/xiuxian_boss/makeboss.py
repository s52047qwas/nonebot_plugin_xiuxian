from pathlib import Path
import json
import random
from ..xiuxian2_handle import XiuxianDateManage
from .bossconfig import get_config

config = get_config()
DATEPATH = Path() / "data" / "xiuxian"
jingjie = ['练气境', '筑基境', '结丹境', '元婴境', '化神境', '炼虚境', '合体境', '大乘境', '渡劫境','真仙境','金仙境','太乙境']
sql_message = XiuxianDateManage()  # sql类

def createboss():
    flag = True
    while(flag):
        nowjj = randomjj()
        alluserexps = sql_message.get_all_user_exp(nowjj)
        if alluserexps != []:
            flag = False
    bossinfo = get_boss_exp(alluserexps)
    bossinfo['name'] = random.choice(config["Boss名字"])
    bossinfo['jj'] = nowjj
    bossinfo['stone'] = config["Boss灵石"][nowjj]
    return bossinfo



def randomjj():
    return random.choice(jingjie)

def get_boss_exp(alluserexp):
    bossexp = 0
    bossinfo = {}
    for e in alluserexp:
        bossexp += e[0]
    
    bossexp = int(bossexp / len(alluserexp))
    bossinfo['气血'] = bossexp * config["Boss倍率"]["气血"]
    bossinfo['总血量'] = bossexp * config["Boss倍率"]["气血"]
    bossinfo['真元'] = bossexp * config["Boss倍率"]["真元"]
    bossinfo['攻击'] = int(bossexp * config["Boss倍率"]["攻击"])
    return bossinfo
