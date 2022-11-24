from pathlib import Path
import json
import random
from ..xiuxian2_handle import XiuxianDateManage
from .bossconfig import get_config

config = get_config()
JINGJIEEXP = {#数值为中期和圆满的平均值
    "练气境":2500,
    "筑基境":9000,
    "结丹境":75000,
    "元婴境":168000,
    "化神境":400000,
    "炼虚境":928000,
    "合体境":2112000,
    "大乘境":4736000,
    "渡劫境":13658000,
    "真仙境":36418000,
    "金仙境":75968000,
    "太乙境":150968000,
}
jinjie_list = [k for k, v in JINGJIEEXP.items()]
sql_message = XiuxianDateManage()  # sql类

def createboss():
    top_user_info = sql_message.get_top1_user()
    top_user_level = top_user_info.level
    if top_user_level == "半步真仙":
        level = "渡劫境"
    else:
        level = top_user_level[:3]
    boss_jj = random.choice(jinjie_list[:jinjie_list.index(level) + 1])
    bossinfo = get_boss_exp(boss_jj)
    bossinfo['name'] = random.choice(config["Boss名字"])
    bossinfo['jj'] = boss_jj
    bossinfo['stone'] = config["Boss灵石"][boss_jj]
    return bossinfo

def get_boss_exp(boss_jj):
    bossexp = JINGJIEEXP[boss_jj]
    bossinfo = {}
    bossinfo['气血'] = bossexp * config["Boss倍率"]["气血"]
    bossinfo['总血量'] = bossexp * config["Boss倍率"]["气血"]
    bossinfo['真元'] = bossexp * config["Boss倍率"]["真元"]
    bossinfo['攻击'] = int(bossexp * config["Boss倍率"]["攻击"])
    return bossinfo
