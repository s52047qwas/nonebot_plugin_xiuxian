from pathlib import Path
from typing import Any, Tuple
from nonebot import on_regex
from nonebot.params import RegexGroup
from nonebot.adapters.onebot.v11 import (
    Bot,
    MessageEvent,
)
import json
import os
from ..xiuxian2_handle import XiuxianDateManage
from datetime import datetime

bank = on_regex(
    r'^钱庄(存钱|取钱|升级会员|信息|结算)?(.*)?',
    priority=5,
)

BANKLEVEL = {
    "1":{"savemax":100000,"levelup":100000,'interest':0.002,"level":"普通会员"},
    "2":{"savemax":200000,"levelup":200000,'interest':0.0021,"level":"小会员"},
    "3":{"savemax":400000,"levelup":400000,'interest':0.0022,"level":"大会员"},
    "4":{"savemax":800000,"levelup":800000,'interest':0.0023,"level":"优质会员"},
    "5":{"savemax":1600000,"levelup":1600000,'interest':0.0024,"level":"黄金会员"},
    "6":{"savemax":3200000,"levelup":3200000,'interest':0.0025,"level":"钻石会员"},
    "7":{"savemax":6400000,"levelup":0,'interest':0.0028,"level":"终极会员"},
}

sql_message = XiuxianDateManage()  # sql类

PLAYERSDATA = Path() / "data" / "xiuxian" / "players"

@bank.handle()
async def _(bot: Bot, event: MessageEvent, args: Tuple[Any, ...] = RegexGroup()):
    
    mode = args[0] #存钱、取钱、升级会员、信息查看
    num = args[1] #数值
    if mode == None:
        await bank.finish(f'钱庄服务，可以存钱、取钱，给与利息。利息取决于钱庄会员等级，会员等级可消耗灵石升级！\n命令：钱庄+存钱、取钱、升级会员、信息、结算，存取需要加数值')
    
    if mode == '存钱' or mode == '取钱':
        try:
            num = int(num)
            if num <= 0:
                await bank.finish(f'请输入正确的金额！', at_sender=True)
        except ValueError:
            await bank.finish(f'请输入正确的金额！', at_sender=True)
        
    user_id = event.get_user_id()
    userinfo = sql_message.get_user_message(user_id)
    
    if sql_message.get_user_message(user_id) is None:
        await bank.finish("修仙界没有道友的信息，请输入【我要修仙】加入！")
    
    try:
        bankinfo = readf(user_id)
    except:
        bankinfo = {
            'savestone':0,
            'savetime': str(datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
            'banklevel':'1',
        }
    
    if mode == '存钱':#存钱逻辑
        if int(userinfo.stone) < num:
            await bank.finish(f"道友所拥有的灵石为{userinfo.stone}枚，金额不足，请重新输入！", at_sender=True)

        max = BANKLEVEL[bankinfo['banklevel']]['savemax']
        nowmax = max - bankinfo['savestone']
        
        if num > nowmax:
            await bank.finish(f"道友当前钱庄会员等级为{BANKLEVEL[bankinfo['banklevel']]['level']}，可存储的最大灵石为{max}枚,当前已存{bankinfo['savestone']}枚灵石，可以继续存{nowmax}枚灵石！", at_sender=True)
        
        userinfonowstone = int(userinfo.stone) - num
        bankinfo['savestone'] += num
        sql_message.update_ls(user_id, num, 2)
        bankinfo['savetime'] = str(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        savef(user_id, json.dumps(bankinfo, ensure_ascii=False))
        await bank.finish(f"道友存入灵石{num}枚，当前所拥有灵石{userinfonowstone}枚，钱庄存有灵石{bankinfo['savestone']}枚", at_sender=True)

    elif mode == '取钱':#取钱逻辑
        if int(bankinfo['savestone']) < num:
            await bank.finish(f"道友当前钱庄所存有的灵石为{bankinfo['savestone']}枚，金额不足，请重新输入！", at_sender=True)
        
        #先结算利息
        bankinfo, give_stone, timedeff = get_give_stone(bankinfo)

        userinfonowstone = int(userinfo.stone) + num + give_stone
        bankinfo['savestone'] -= num
        sql_message.update_ls(user_id, num + give_stone, 1)
        savef(user_id, json.dumps(bankinfo, ensure_ascii=False))
        await bank.finish(f"道友本次结息时间为：{timedeff}小时，获得灵石：{give_stone}枚!\n取出灵石{num}枚，当前所拥有灵石{userinfonowstone}枚，钱庄存有灵石{bankinfo['savestone']}枚!", at_sender=True)
        
    elif mode == '升级会员':#升级会员逻辑
        userlevel = bankinfo["banklevel"]
        if userlevel == '7':
            await bank.finish(f"道友已经是本钱庄最大的会员啦！", at_sender=True)
        
        stonecost = BANKLEVEL[f'{int(userlevel)}']['levelup']
        if int(userinfo.stone) < stonecost:
            await bank.finish(f"道友所拥有的灵石为{userinfo.stone}枚，当前升级会员等级需求灵石{stonecost}枚金额不足，请重新输入！", at_sender=True)
        
        sql_message.update_ls(user_id, stonecost, 2)
        bankinfo['banklevel'] = f'{int(userlevel) + 1}'
        savef(user_id, json.dumps(bankinfo, ensure_ascii=False))
        await bank.finish(f"道友成功升级钱庄会员等级，消耗灵石{stonecost}枚，当前为：{BANKLEVEL[f'{int(userlevel) + 1}']['level']}，钱庄可存有灵石上限{BANKLEVEL[f'{int(userlevel) + 1}']['savemax']}枚", at_sender=True)
    
    elif mode == '信息':#查询钱庄信息
        await bank.finish(f'''
道友的钱庄信息：
已存：{bankinfo['savestone']}灵石
存入时间：{bankinfo['savetime']}
钱庄会员等级：{BANKLEVEL[bankinfo['banklevel']]['level']}
当前拥有灵石：{userinfo.stone}
当前等级存储灵石上限：{BANKLEVEL[bankinfo['banklevel']]['savemax']}枚
                        ''', at_sender=True)
    
    elif mode == '结算':

        bankinfo, give_stone, timedeff = get_give_stone(bankinfo)
        sql_message.update_ls(user_id, give_stone, 1)
        savef(user_id, json.dumps(bankinfo, ensure_ascii=False))
        await bank.finish(f'道友本次结息时间为：{timedeff}小时，获得灵石：{give_stone}枚！', at_sender=True)


def get_give_stone(bankinfo):
    "获取利息：利息=give_stone，结算时间=timedeff"
    savetime = bankinfo['savetime'] #str
    nowtime = datetime.now().strftime('%Y-%m-%d %H:%M:%S') #str
    timedeff = round((datetime.strptime(nowtime, '%Y-%m-%d %H:%M:%S') - datetime.strptime(savetime, '%Y-%m-%d %H:%M:%S')).total_seconds() / 3600, 2)
    give_stone = int(bankinfo['savestone'] * timedeff * BANKLEVEL[bankinfo['banklevel']]['interest'])
    bankinfo['savetime'] = nowtime

    return bankinfo, give_stone, timedeff


def readf(user_id):
    user_id = str(user_id)
    
    FILEPATH = PLAYERSDATA / user_id / "bankinfo.json"
    with open(FILEPATH, "r", encoding="UTF-8") as f:
        data = f.read()
    return json.loads(data)

def savef(user_id, data):
    user_id = str(user_id)
    
    if not os.path.exists(PLAYERSDATA / user_id):
        print("目录不存在，创建目录")
        os.makedirs(PLAYERSDATA / user_id)
    
    FILEPATH = PLAYERSDATA / user_id / "bankinfo.json"
       
    savemode = "w" if os.path.exists(FILEPATH) else "x"
    with open(FILEPATH, mode=savemode, encoding="UTF-8") as f:
        f.write(data)
        f.close
    return True