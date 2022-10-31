from typing import Any, Tuple
from nonebot import get_bot, on_command, on_regex, require
from nonebot.params import RegexGroup, CommandArg
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
import json
from ..player_fight import Boss_fight
from ..utils import data_check_conf, check_user
from .jsondata import read_group, save_group

# 定时任务
set_rift = require("nonebot_plugin_apscheduler").scheduler
set_group_rift = on_command("群秘境", priority=5, permission= GROUP and (SUPERUSER | GROUP_ADMIN | GROUP_OWNER))
explore_rift = on_command("探索秘境", priority=5, permission= GROUP)

__rift_help__ = f"""
秘境帮助信息:
指令：
1、群秘境开启、关闭：开启本群的秘境生成任务，管理员权限
2、探索秘境：探索秘境获取随机奖励
非指令：

""".strip()

group_rift = {}
groups = {}
try:
    groups = read_group()
except:
    groups['open'] = []
    
# 定时任务生成群秘境
@set_rift.scheduled_job("cron", hour=18, minute=30)
async def _():
    bot = get_bot()
    if groups['open'] != []:
        for g in groups['open']:
            group_rift[g]
            msg = f"已生成秘境"
            await bot.send_group_msg(group_id=int(g), message=msg)

#探索秘境
@explore_rift.handle()
async def _(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    await data_check_conf(bot, event)

    isUser, user_info, msg = check_user(event)
    if not isUser:
        await explore_rift.finish(msg, at_sender=True)
    group_id = event.group_id
    if group_id not in groups['open']:
        msg = '本群尚未开启秘境，请联系管理员开启群秘境'
        await explore_rift.finish(msg, at_sender=True)
    try:
        group_rift[group_id]
    except:
        msg = '野外秘境尚未生成，请道友耐心等待!'
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
            groups['open'].append(group_id)
            save_group(groups)
            await set_group_rift.finish(f'已开启本群秘境!')

    elif mode == '关闭':
        if is_in_group:
            groups['open'].remove(group_id)
            save_group(groups)
            await set_group_rift.finish(f'已关闭本群秘境!')
        else:
            await set_group_rift.finish(f'本群未开启群秘境!')
    
    elif mode == '':
        await set_group_rift.finish(__rift_help__)
    else:
        await set_group_rift.finish(f'请输入正确的指令：群秘境开启或关闭!')
        
def is_in_groups(event: GroupMessageEvent):
    return event.group_id in groups['open']