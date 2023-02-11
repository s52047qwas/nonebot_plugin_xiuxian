from pathlib import Path
from typing import Any, Tuple
from nonebot import on_regex
from nonebot.params import RegexGroup
from nonebot.adapters.onebot.v11 import (
    Bot,
    MessageEvent,
    GroupMessageEvent,
    MessageSegment,
)
import json
import os
from ..xiuxian2_handle import XiuxianDateManage
from datetime import datetime
from .bankconfig import get_config
from ..utils import data_check_conf, get_msg_pic, pic_msg_format
from ..xiuxian_config import XiuConfig

config = get_config()

bank = on_regex(
    r'^灵庄(存灵石|取灵石|升级会员|信息|结算)?(.*)?',
    priority=5,
)

BANKLEVEL = config["BANKLEVEL"]

__bank_help__ = f"""
灵庄帮助信息:
指令：
1、灵庄：查看灵庄帮助信息
2、灵庄存灵石：指令后加存入的金额，获取利息
3、灵庄取灵石：指令后加取出的金额，会先结算利息，再取出灵石
4、灵庄升级会员：灵庄利息倍率与灵庄会员等级有关，升级会员会提升利息倍率
5、灵庄信息：查询自己当前的灵庄信息
6、灵庄结算：结算利息
""".strip()

sql_message = XiuxianDateManage()  # sql类

PLAYERSDATA = Path() / "data" / "xiuxian" / "players"

@bank.handle()
async def _(bot: Bot, event: GroupMessageEvent, args: Tuple[Any, ...] = RegexGroup()):
    await data_check_conf(bot, event)
    mode = args[0] #存灵石、取灵石、升级会员、信息查看
    num = args[1] #数值
    if mode == None:
        msg = __bank_help__
        if XiuConfig().img:
            msg = await pic_msg_format(msg, event)
            pic = await get_msg_pic(msg)
            await bank.finish(MessageSegment.image(pic))
        else:
            await bank.finish(msg, at_sender=True)

    
    if mode == '存灵石' or mode == '取灵石':
        try:
            num = int(num)
            if num <= 0:
                msg = f'请输入正确的金额！'
                if XiuConfig().img:
                    msg = await pic_msg_format(msg, event)
                    pic = await get_msg_pic(msg)
                    await bank.finish(MessageSegment.image(pic))
                else:
                    await bank.finish(msg, at_sender=True)
        except ValueError:
            msg = f'请输入正确的金额！'
            if XiuConfig().img:
                msg = await pic_msg_format(msg, event)
                pic = await get_msg_pic(msg)
                await bank.finish(MessageSegment.image(pic))
            else:
                await bank.finish(msg, at_sender=True)
        
    user_id = event.get_user_id()
    userinfo = sql_message.get_user_message(user_id)
    
    if sql_message.get_user_message(user_id) is None:
        msg = "修仙界没有道友的信息，请输入【我要修仙】加入！"
        if XiuConfig().img:
            msg = await pic_msg_format(msg, event)
            pic = await get_msg_pic(msg)
            await bank.finish(MessageSegment.image(pic))
        else:
            await bank.finish(msg, at_sender=True)
    
    try:
        bankinfo = readf(user_id)
    except:
        bankinfo = {
            'savestone':0,
            'savetime': str(datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
            'banklevel':'1',
        }
    
    if mode == '存灵石':#存灵石逻辑
        if int(userinfo.stone) < num:
            msg = f"道友所拥有的灵石为{userinfo.stone}枚，金额不足，请重新输入！"
            if XiuConfig().img:
                msg = await pic_msg_format(msg, event)
                pic = await get_msg_pic(msg)
                await bank.finish(MessageSegment.image(pic))
            else:
                await bank.finish(msg, at_sender=True)

        max = BANKLEVEL[bankinfo['banklevel']]['savemax']
        nowmax = max - bankinfo['savestone']
        
        if num > nowmax:
            msg = f"道友当前灵庄会员等级为{BANKLEVEL[bankinfo['banklevel']]['level']}，可存储的最大灵石为{max}枚,当前已存{bankinfo['savestone']}枚灵石，可以继续存{nowmax}枚灵石！"
            if XiuConfig().img:
                msg = await pic_msg_format(msg, event)
                pic = await get_msg_pic(msg)
                await bank.finish(MessageSegment.image(pic))
            else:
                await bank.finish(msg, at_sender=True)
            
            
        bankinfo, give_stone, timedeff = get_give_stone(bankinfo)
        userinfonowstone = int(userinfo.stone) - num
        bankinfo['savestone'] += num
        sql_message.update_ls(user_id, num , 2)
        sql_message.update_ls(user_id, give_stone , 1)
        bankinfo['savetime'] = str(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        savef(user_id, bankinfo)
        msg = f"道友本次结息时间为：{timedeff}小时，获得灵石：{give_stone}枚!\n道友存入灵石{num}枚，当前所拥有灵石{userinfonowstone + give_stone}枚，灵庄存有灵石{bankinfo['savestone']}枚"
        if XiuConfig().img:
            msg = await pic_msg_format(msg, event)
            pic = await get_msg_pic(msg)
            await bank.finish(MessageSegment.image(pic))
        else:
            await bank.finish(msg, at_sender=True)

    elif mode == '取灵石':#取灵石逻辑
        if int(bankinfo['savestone']) < num:
            msg = f"道友当前灵庄所存有的灵石为{bankinfo['savestone']}枚，金额不足，请重新输入！"
            if XiuConfig().img:
                msg = await pic_msg_format(msg, event)
                pic = await get_msg_pic(msg)
                await bank.finish(MessageSegment.image(pic))
            else:
                await bank.finish(msg, at_sender=True)
        
        #先结算利息
        bankinfo, give_stone, timedeff = get_give_stone(bankinfo)

        userinfonowstone = int(userinfo.stone) + num + give_stone
        bankinfo['savestone'] -= num
        sql_message.update_ls(user_id, num + give_stone, 1)
        savef(user_id, bankinfo)
        msg = f"道友本次结息时间为：{timedeff}小时，获得灵石：{give_stone}枚!\n取出灵石{num}枚，当前所拥有灵石{userinfonowstone}枚，灵庄存有灵石{bankinfo['savestone']}枚!"
        if XiuConfig().img:
            msg = await pic_msg_format(msg, event)
            pic = await get_msg_pic(msg)
            await bank.finish(MessageSegment.image(pic))
        else:
            await bank.finish(msg, at_sender=True)
        
    elif mode == '升级会员':#升级会员逻辑
        userlevel = bankinfo["banklevel"]
        if userlevel == str(len(BANKLEVEL)):
            msg = f"道友已经是本灵庄最大的会员啦！"
            if XiuConfig().img:
                msg = await pic_msg_format(msg, event)
                pic = await get_msg_pic(msg)
                await bank.finish(MessageSegment.image(pic))
            else:
                await bank.finish(msg, at_sender=True)
        
        stonecost = BANKLEVEL[f'{int(userlevel)}']['levelup']
        if int(userinfo.stone) < stonecost:
            msg = f"道友所拥有的灵石为{userinfo.stone}枚，当前升级会员等级需求灵石{stonecost}枚金额不足，请重新输入！"
            if XiuConfig().img:
                msg = await pic_msg_format(msg, event)
                pic = await get_msg_pic(msg)
                await bank.finish(MessageSegment.image(pic))
            else:
                await bank.finish(msg, at_sender=True)
        
        sql_message.update_ls(user_id, stonecost, 2)
        bankinfo['banklevel'] = f'{int(userlevel) + 1}'
        savef(user_id, bankinfo)
        msg = f"道友成功升级灵庄会员等级，消耗灵石{stonecost}枚，当前为：{BANKLEVEL[f'{int(userlevel) + 1}']['level']}，灵庄可存有灵石上限{BANKLEVEL[f'{int(userlevel) + 1}']['savemax']}枚"
        if XiuConfig().img:
            msg = await pic_msg_format(msg, event)
            pic = await get_msg_pic(msg)
            await bank.finish(MessageSegment.image(pic))
        else:
            await bank.finish(msg, at_sender=True)
    
    elif mode == '信息':#查询灵庄信息
        msg = f'''
道友的灵庄信息：
已存：{bankinfo['savestone']}灵石
存入时间：{bankinfo['savetime']}
灵庄会员等级：{BANKLEVEL[bankinfo['banklevel']]['level']}
当前拥有灵石：{userinfo.stone}
当前等级存储灵石上限：{BANKLEVEL[bankinfo['banklevel']]['savemax']}枚
                        '''
        if XiuConfig().img:
            msg = await pic_msg_format(msg, event)
            pic = await get_msg_pic(msg)
            await bank.finish(MessageSegment.image(pic))
        else:
            await bank.finish(msg, at_sender=True)
    
    elif mode == '结算':

        bankinfo, give_stone, timedeff = get_give_stone(bankinfo)
        sql_message.update_ls(user_id, give_stone, 1)
        savef(user_id, bankinfo)
        msg = f'道友本次结息时间为：{timedeff}小时，获得灵石：{give_stone}枚！'
        if XiuConfig().img:
            msg = await pic_msg_format(msg, event)
            pic = await get_msg_pic(msg)
            await bank.finish(MessageSegment.image(pic))
        else:
            await bank.finish(msg, at_sender=True)


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
    data = json.dumps(data, ensure_ascii=False, indent=3)
    savemode = "w" if os.path.exists(FILEPATH) else "x"
    with open(FILEPATH, mode=savemode, encoding="UTF-8") as f:
        f.write(data)
        f.close
    return True