from pathlib import Path
import json
import random
from ..xiuxian2_handle import XiuxianDateManage

DATEPATH = Path() / "data" / "xiuxian"
jingjie = ['练气境', '筑基境', '结丹境', '元婴境', '化神境', '炼虚境', '合体境', '大乘境', '渡劫境']
bossstone = {
    '练气境':20000,
    '筑基境':50000,
    '结丹境':100000,
    '元婴境':200000,
    '化神境':300000,
    '炼虚境':400000,
    '合体境':500000,
    '大乘境':600000,
    '渡劫境':700000,
}
sql_message = XiuxianDateManage()  # sql类

def createboss():
    flag = True
    while(flag):
        nowjj = randomjj()
        alluserexps = sql_message.get_all_user_exp(nowjj)
        if alluserexps != []:
            flag = False
    bossinfo = get_boss_exp(alluserexps)
    bossnamelist = readf()
    bossinfo['name'] = random.choice(bossnamelist['Boss'])
    bossinfo['jj'] = nowjj
    bossinfo['stone'] = bossstone[nowjj]
    return bossinfo



def randomjj():
    return random.choice(jingjie)

def get_boss_exp(alluserexp):
    bossexp = 0
    bossinfo = {}
    for e in alluserexp:
        bossexp += e[0]
    
    bossexp = int(bossexp / len(alluserexp))
    bossinfo['气血'] = bossexp * 15
    bossinfo['真元'] = bossexp * 10
    bossinfo['攻击'] = int(bossexp / 5)
    return bossinfo

BOSSDATA = DATEPATH / "boss.json"
def readf():
    
    with open(BOSSDATA, "r", encoding="UTF-8") as f:
        data = f.read()
    return json.loads(data)
