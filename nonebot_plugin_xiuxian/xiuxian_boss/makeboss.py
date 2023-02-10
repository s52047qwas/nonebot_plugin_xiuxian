from pathlib import Path
import json
import random
from ..xiuxian2_handle import XiuxianDateManage
from .bossconfig import get_config

config = get_config()

def get_boss_jinjie_dict():
    CONFIGJSONPATH = Path() / "data" / "xiuxian" / "境界.json"
    with open(CONFIGJSONPATH, "r", encoding="UTF-8") as f:
        data = f.read()
    temp_dict = {}
    data = json.loads(data)
    for k, v in data.items():
        temp_dict[k] = v['exp']
    return temp_dict

JINGJIEEXP = get_boss_jinjie_dict()
MINJINJIE = 24 #向下取12个小境界(3个大境界)
jinjie_list = [k for k, v in JINGJIEEXP.items()]
sql_message = XiuxianDateManage()  # sql类

def createboss():
    top_user_info = sql_message.get_top1_user()
    top_user_level = top_user_info.level
    now_jinjie_index = jinjie_list.index(top_user_level) + 1
    if now_jinjie_index <= MINJINJIE:
        boss_jj = random.choice(jinjie_list[:now_jinjie_index])
    else:
        boss_jj = random.choice(jinjie_list[now_jinjie_index - MINJINJIE:now_jinjie_index])
    bossinfo = get_boss_exp(boss_jj)
    bossinfo['name'] = random.choice(config["Boss名字"])
    bossinfo['jj'] = boss_jj
    bossinfo['stone'] = config["Boss灵石v1.1"][boss_jj]
    return bossinfo

def createboss_jj(boss_jj):
    bossinfo = get_boss_exp(boss_jj)
    bossinfo['name'] = random.choice(config["Boss名字"])
    bossinfo['jj'] = boss_jj
    bossinfo['stone'] = config["Boss灵石v1.1"][boss_jj]
    return bossinfo

def get_boss_exp(boss_jj):
    bossexp = JINGJIEEXP[boss_jj]
    bossinfo = {}
    bossinfo['气血'] = bossexp * config["Boss倍率"]["气血"]
    bossinfo['总血量'] = bossexp * config["Boss倍率"]["气血"]
    bossinfo['真元'] = bossexp * config["Boss倍率"]["真元"]
    bossinfo['攻击'] = int(bossexp * config["Boss倍率"]["攻击"])
    return bossinfo
