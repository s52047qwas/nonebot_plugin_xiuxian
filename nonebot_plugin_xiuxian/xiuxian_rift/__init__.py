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
from ..utils import data_check_conf
from .jsondata import readgroup, savegroup

# 定时任务
setrift = require("nonebot_plugin_apscheduler").scheduler
setgrouprift = on_command("群秘境", priority=5, permission= GROUP and (SUPERUSER | GROUP_ADMIN | GROUP_OWNER))

__rift_help__ = f"""
秘境帮助信息:
指令：
1、群秘境开启、关闭：开启本群的秘境生成任务，管理员权限
非指令：

""".strip()

grouprift = {}
groups = {}
try:
    groups = readgroup()
except:
    groups['open'] = []
    
# 定时任务生成群秘境
@setrift.scheduled_job("cron", hour=18, minute=30)
async def _():
    bot = get_bot()
    if groups['open'] != []:
        for g in groups['open']:
            grouprift[g]
            msg = f"已生成秘境"
            await bot.send_group_msg(group_id=int(g), message=msg)


@setgrouprift.handle()
async def _(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    await data_check_conf(bot, event)
    mode = args.extract_plain_text().strip()
    group_id = event.group_id
    isInGroup = isInGroups(event) #True在，False不在

    if mode == '开启':
        if isInGroup:
            await setgrouprift.finish(f'本群已开启群秘境，请勿重复开启!')
        else:
            groups['open'].append(group_id)
            savegroup(groups)
            await setgrouprift.finish(f'已开启本群秘境!')

    elif mode == '关闭':
        if isInGroup:
            groups['open'].remove(group_id)
            savegroup(groups)
            await setgrouprift.finish(f'已关闭本群秘境!')
        else:
            await setgrouprift.finish(f'本群未开启群秘境!')
    
    elif mode == '':
        await setgrouprift.finish(__rift_help__)
    else:
        await setgrouprift.finish(f'请输入正确的指令：群秘境开启或关闭!')
        
def isInGroups(event: GroupMessageEvent):
    return event.group_id in groups['open']