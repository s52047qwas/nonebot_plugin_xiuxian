from pathlib import Path
from typing import Any, Tuple, Dict
from nonebot import on_regex, require
from nonebot.params import RegexGroup
from nonebot.adapters.onebot.v11 import (
    Bot,
    MessageEvent,
    PRIVATE_FRIEND,
    GROUP,
)
import json
import os

from numpy import save
from ..xiuxian2_handle import XiuxianDateManage
from datetime import datetime
from ..cd_manager import add_cd, check_cd, cd_msg
from nonebot.log import logger

bank = on_regex(
    r'^钱庄(存钱|取钱|升级会员|信息)?(.*)?',
    priority=5,
)

sql_message = XiuxianDateManage()  # sql类

PLAYERSDATA = Path() / "data" / "xiuxian" / "players"

@bank.handle()
async def _(bot: Bot, event: MessageEvent, args: Tuple[Any, ...] = RegexGroup()):
    
    mode = args[0] #存钱、取钱、升级会员、信息查看
    num = args[1] #数值
    if mode == None:
        await bank.finish(f'钱庄服务，可以存钱、取钱，给与利息。利息取决于钱庄会员等级，会员等级可消耗灵石升级')
    
    if mode != '信息' or mode !='升级会员':
        try:
            num = int(num)
            if num <= 0:
                await bank.finish(f'请输入正确的金额！')
        except ValueError:
            await bank.finish(f'请输入正确的金额！')
        
    user_id = event.get_user_id()
    userinfo = sql_message.get_user_message(user_id)
    
    if sql_message.get_user_message(user_id) is None:
        await bank.finish("修仙界没有道友的信息，请输入【我要修仙】加入！")
        
    try:
        bankinfo = readf(user_id)
    except:
        bankinfo = {
            'savestone':0,
            'savetime': '',
            'banklevel':1
        }
    
    if mode == '存钱':#存钱逻辑
        if int(userinfo.stone) < num:
            await bank.finish(f"道友所拥有的灵石为{userinfo.stone}枚，金额不足，请重新输入！")
        
        userinfonowstone = int(userinfo.stone) - num
        bankinfo['savestone'] += num
        sql_message.update_ls(user_id, num, 2)
        bankinfo['savetime'] = str(datetime.now())
        savef(user_id, json.dumps(bankinfo, ensure_ascii=False))
        await bank.finish(f"道友存入灵石{num}枚，当前所拥有灵石{userinfonowstone}枚，钱庄存有灵石{bankinfo['savestone']}枚")

    elif mode == '取钱':#取钱逻辑
        if int(bankinfo['savestone']) < num:
            await bank.finish(f"道友当前钱庄所存有的灵石为{bankinfo['savestone']}枚，金额不足，请重新输入！")
        
        userinfonowstone = int(userinfo.stone) + num
        bankinfo['savestone'] -= num
        sql_message.update_ls(user_id, num, 1)
        bankinfo['savetime'] = str(datetime.now())
        savef(user_id, json.dumps(bankinfo, ensure_ascii=False))
        await bank.finish(f"道友取出灵石{num}枚，当前所拥有灵石{userinfonowstone}枚，钱庄存有灵石{bankinfo['savestone']}枚")
        
    elif mode == '升级会员':#升级会员逻辑
        await bank.finish('没想好')
    
    elif mode == '信息':#查询钱庄信息
        await bank.finish(f'''
道友的钱庄信息：
已存:{bankinfo['savestone']}灵石
存入时间：{bankinfo['savetime']}
钱庄会员等级:{bankinfo['banklevel']}
当前拥有灵石：{userinfo.stone}
                        ''')
    
    

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