from nonebot import get_bot, on_command, require
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import (
    Bot,
    MessageEvent,
    GROUP,
    Message,
    GroupMessageEvent,
    GROUP_ADMIN,
    GROUP_OWNER
)
from nonebot.permission import SUPERUSER
from nonebot.log import logger
from ..xiuxian2_handle import XiuxianDateManage
from ..utils import data_check_conf, check_user, send_forward_msg
from .riftconfig import get_config, savef
from .riftmake import Rift, get_goods_type, get_rift_type, get_story_type, NONEMSG, get_battle_type, get_dxsj_info, get_boss_battle_info, get_treasure_info
import random

config = get_config()
sql_message = XiuxianDateManage()  # sql类

# 定时任务
set_rift = require("nonebot_plugin_apscheduler").scheduler
set_group_rift = on_command("群秘境", priority=5, permission= GROUP and (SUPERUSER | GROUP_ADMIN | GROUP_OWNER))
explore_rift = on_command("探索秘境", priority=5, permission= GROUP)
create_rift = on_command("生成秘境", priority=5, permission= GROUP and SUPERUSER)

__rift_help__ = f"""
秘境帮助信息:
指令：
1、群秘境开启、关闭：开启本群的秘境生成，管理员权限
2、生成秘境：生成一个随机秘境，管理员权限
3、探索秘境：探索秘境获取随机奖励
非指令：

""".strip()

group_rift = {} #dict
groups = config['open'] #list
    
# 定时任务生成群秘境
@set_rift.scheduled_job("cron", hour=18, minute=30)
async def _():
    bot = get_bot()
    if groups != []:
        for group_id in groups:
            rift = Rift()
            rift.name = get_rift_type()
            rift.rank = config['rift'][rift.name]['rank']
            rift.count = config['rift'][rift.name]['count']
            group_rift[group_id] = rift
            msg = f"野生的{rift.name}出现了！秘境可探索次数：{group_rift[group_id]['count']}次，请诸位道友发送 探索秘境 来加入吧！"
            await bot.send_group_msg(group_id=int(group_id), message=msg)

#生成秘境
@create_rift.handle()
async def _(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    await data_check_conf(bot, event)
    group_id = event.group_id
    if group_id not in groups:
        msg = '本群尚未开启秘境，请联系管理员开启群秘境'
        await create_rift.finish(msg, at_sender=True)
    
    try:
        group_rift[group_id]
        msg = f"当前已存在{group_rift[group_id].name}，秘境可探索次数：{group_rift[group_id].count}次，请诸位道友发送 探索秘境 来加入吧！"
        await create_rift.finish(msg)
    except KeyError:
        rift = Rift()
        rift.name = get_rift_type()
        rift.rank = config['rift'][rift.name]['rank']
        rift.count = config['rift'][rift.name]['count']
        group_rift[group_id] = rift
        msg = f"野生的{rift.name}出现了！秘境可探索次数：{rift.count}次，请诸位道友发送 探索秘境 来加入吧！"
        await create_rift.finish(msg)


#探索秘境
@explore_rift.handle()
async def _(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    await data_check_conf(bot, event)

    isUser, user_info, msg = check_user(event)
    if not isUser:
        await explore_rift.finish(msg, at_sender=True)
    group_id = event.group_id
    if group_id not in groups:
        msg = '本群尚未开启秘境，请联系管理员开启群秘境'
        await explore_rift.finish(msg, at_sender=True)
    try:
        group_rift[group_id]
    except:
        msg = '野外秘境尚未生成，请道友耐心等待!'
        await explore_rift.finish(msg, at_sender=True)
    
    user_id = user_info.user_id
    if user_id in group_rift[group_id].l_user_id:
        msg = '道友已经参加过本次秘境啦，请把机会留给更多的道友！'
        await explore_rift.finish(msg, at_sender=True)
    group_rift[group_id].l_user_id.append(user_id)
    group_rift[group_id].count -= 1
    if group_rift[group_id].count == 0:
        del group_rift[group_id]
        logger.info('群{group_id}秘境已到上限次数！')
    #秘境结算逻辑
    rift_rank = group_rift[group_id].rank #秘境等级
    rift_type = get_story_type() #无事、宝物、战斗
    if rift_type == "无事":
        msg = random.choice(NONEMSG)
        await explore_rift.finish(msg, at_sender=True)
    elif rift_type == "战斗":
        rift_type = get_battle_type()
        if rift_type == "掉血事件":
            msg = get_dxsj_info("掉血事件", user_info)
            await explore_rift.finish(msg, at_sender=True)
        elif rift_type == "Boss战斗":
            result, msg = get_boss_battle_info(user_info)
            await send_forward_msg(bot, event, 'Boss战', bot.self_id, result)
            await explore_rift.finish(msg, at_sender=True)
    elif rift_type == "宝物":
        msg = get_treasure_info(user_info, rift_rank)
        await explore_rift.finish(msg, at_sender=True)
        


@set_group_rift.handle()
async def _(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    await data_check_conf(bot, event)
    mode = args.extract_plain_text().strip()
    group_id = event.group_id
    is_in_group = is_in_groups(event) #True在，False不在

    if mode == '开启':
        if is_in_group:
            await set_group_rift.finish(f'本群已开启群秘境，请勿重复开启!')
        else:
            config['open'].append(group_id)
            savef(config)
            await set_group_rift.finish(f'已开启本群秘境!')

    elif mode == '关闭':
        if is_in_group:
            config['open'].remove(group_id)
            savef(config)
            await set_group_rift.finish(f'已关闭本群秘境!')
        else:
            await set_group_rift.finish(f'本群未开启群秘境!')
    
    else:
        await set_group_rift.finish(__rift_help__)
        
def is_in_groups(event: GroupMessageEvent):
    return event.group_id in groups