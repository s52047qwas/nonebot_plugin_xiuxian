import re
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
from .boss_handle import BossDateManage, readf, savef
from nonebot.log import logger
from ..xiuxian2_handle import XiuxianDateManage
from .makeboss import createboss
import json
from .bossconfig import get_config

# 定时任务
setboss = require("nonebot_plugin_apscheduler").scheduler

create = on_command("生成世界boss", aliases={"生成世界Boss", "生成世界BOSS"}, priority=5, permission= GROUP and (SUPERUSER | GROUP_ADMIN | GROUP_OWNER))
bossinfo = on_command("查询世界boss", aliases={"查询世界Boss", "查询世界BOSS"}, priority=5, permission= GROUP)
setgroupboss = on_regex(r"^世界boss(开启|关闭)?", priority=5, permission= GROUP and (SUPERUSER | GROUP_ADMIN | GROUP_OWNER))
battle = on_command("讨伐boss", aliases={"讨伐世界boss", "讨伐Boss", "讨伐BOSS", "讨伐世界Boss","讨伐世界BOSS"}, priority=5, permission= GROUP)
bosshelp = on_command("世界boss帮助", aliases={"世界Boss帮助", "世界BOSS帮助"}, priority=4, block=True)

groupboss = {}
groups = {}
try:
    groups = readf()
except:
    groups['open'] = []

config = get_config()

# 定时任务生成世界boss
@setboss.scheduled_job("cron",hour=config["生成时间"])
async def _():
    bot = get_bot()
    if groups['open'] != []:
        for g in groups['open']:
            try:
                groupboss[g]
            except:
                groupboss[g] = []

            bossinfo = createboss()
            groupboss[g].append(bossinfo)
            msg = f"已生成{bossinfo['jj']}Boss:{bossinfo['name']}，诸位道友请击败Boss获得奖励吧！"
            await bot.send_group_msg(group_id=int(g), message=msg)
            logger.info('已生成世界boss')
        
        
@bosshelp.handle()
async def _():
    msg = "世界Boss帮助：\n1、超级管理员可以使用命令：生成世界boss来生成boss。\n2、超级管理员命令：世界boss开启、关闭来管理本群世界boss的自动生成\n3、其余命令：查询世界boss、查询世界boss+对应的boss编号、讨伐boss+对应的boss编号"
    await bosshelp.finish(msg)

    

@battle.handle()
async def _(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    try:
        user_id, userinfo = await data_check(bot, event)
    except MsgError:
        return
    
    msg = args.extract_plain_text().strip()
    group_id = event.group_id
    boss_num = re.findall("\d+", msg)  # boss编号
    
    isInGroup = isInGroups(event)
    if not isInGroup:#不在配置表内
        await battle.finish(f'本群尚未开启世界Boss，请联系管理员开启!')
    
    if boss_num:
        boss_num = int(boss_num[0])
    else:
        await battle.finish(f'请输入正确的世界Boss编号！')
    
    try:
        bosss = groupboss[group_id]
    except:
        await battle.finish(f'本群尚未生成世界Boss，请等待世界boss刷新!')
    
    if bosss == []:
        await battle.finish(f'本群尚未生成世界Boss，请等待世界boss刷新!')
    
    index = len(groupboss[group_id])
    
    if not (0 < boss_num <= index):
        await battle.finish(f'请输入正确的世界Boss编号！')
    
    if userinfo.hp is None or userinfo.hp == 0:
        # 判断用户气血是否为空
        XiuxianDateManage().update_user_hp(user_id)
    
    if userinfo.hp <= userinfo.exp / 10:
        await battle.finish("重伤未愈，动弹不得！", at_sender=True)
        
    player = {"user_id": None, "道号": None, "气血": None, "攻击": None, "真元": None, '会心': None, '防御': 0}
    userinfo = XiuxianDateManage().get_user_message(user_id)
    player['user_id'] = userinfo.user_id
    player['道号'] = userinfo.user_name
    player['气血'] = userinfo.hp
    player['攻击'] = userinfo.atk
    player['真元'] = userinfo.mp
    player['会心'] = 1
    
    bossinfo = groupboss[group_id][boss_num - 1]
    result, victor, bossinfo_new, get_stone = BossDateManage().player_fight(player, bossinfo, 1)
    await send_forward_msg(bot, event, 'Boss战', bot.self_id, result)
    if victor == bossinfo['name']:
        groupboss[group_id][boss_num - 1] = bossinfo_new
        XiuxianDateManage().update_ls(user_id, get_stone, 1)
        await battle.finish(f"道友不敌{bossinfo['name']}，重伤逃遁，临逃前收获灵石{get_stone}枚")
    elif victor == player['道号']:
        groupboss[group_id].remove(groupboss[group_id][boss_num - 1])
        XiuxianDateManage().update_ls(user_id, get_stone, 1)
        await battle.finish(f"恭喜道友击败{bossinfo['name']}，收获灵石{get_stone}枚")

@bossinfo.handle()
async def _(bot: Bot, event: MessageEvent, args: Message = CommandArg()):
    group_id = event.group_id
    isInGroup = isInGroups(event)
    if not isInGroup:#不在配置表内
        await bossinfo.finish(f'本群尚未开启世界Boss，请联系管理员开启!')
    
    try:
        bosss = groupboss[group_id]
    except:
        await bossinfo.finish(f'本群尚未生成世界Boss，请等待世界boss刷新!')
        
    msg = args.extract_plain_text().strip()
    boss_num = re.findall("\d+", msg)  # boss编号

    if bosss == []:
        await bossinfo.finish(f'本群尚未生成世界Boss，请等待世界boss刷新!')
    
    Flag = False#True查对应Boss
    if boss_num:
        boss_num = int(boss_num[0])
        index = len(groupboss[group_id])
        if not (0 < boss_num <= index):
            await bossinfo.finish(f'请输入正确的世界Boss编号！')
            
        Flag = True
    
    bossmsgs = ""
    if Flag:#查单个Boss信息
        boss = groupboss[group_id][boss_num - 1]
        bossmsgs = f'''
世界Boss：{boss['name']}
境界：{boss['jj']}
剩余血量：{boss['气血']}
攻击：{boss['攻击']}
携带灵石：{boss['stone']}
        '''
        await bossinfo.finish(bossmsgs)
    else:
        i = 1
        for boss in bosss:
            bossmsgs += f"编号{i}、{boss['jj']}Boss:{boss['name']} \n"
            i += 1
        await bossinfo.finish(bossmsgs)

@create.handle()
async def _(bot: Bot, event: MessageEvent):
    group_id = event.group_id
    isInGroup = isInGroups(event)
    if not isInGroup:#不在配置表内
        await create.finish(f'本群尚未开启世界Boss，请联系管理员开启!')
    
    bossinfo = createboss()
    try:
        groupboss[group_id]
    except:
        groupboss[group_id] = []
    groupboss[group_id].append(bossinfo)
    await create.finish(f"已生成{bossinfo['jj']}Boss:{bossinfo['name']}，诸位道友请击败Boss获得奖励吧！")



@setgroupboss.handle()
async def _(bot: Bot, event: MessageEvent, args: Tuple[Any, ...] = RegexGroup()):
    mode = args[0]
    if mode == None:
        await setgroupboss.finish(f'请输入正确的指令：世界boss开启或关闭!')
    group_id = event.group_id
    isInGroup = isInGroups(event) #True在，False不在

    if mode == '开启':
        if isInGroup:
            await setgroupboss.finish(f'本群已开启世界Boss，请勿重复开启!')
        else:
            groups['open'].append(group_id)
            savef(json.dumps(groups, ensure_ascii=False))
            await setgroupboss.finish(f'已开启本群世界Boss!')

    if mode == '关闭':
        if isInGroup:
            groups['open'].remove(group_id)
            savef(json.dumps(groups, ensure_ascii=False))
            await setgroupboss.finish(f'已关闭本群世界Boss!')
        else:
            await setgroupboss.finish(f'本群未开启世界Boss!')


async def data_check(bot, event):
    """
    判断用户信息是否存在
    """
    user_qq = event.get_user_id()
    msg = XiuxianDateManage().get_user_message(user_qq)

    if msg:
        pass
    else:
        await bot.send(event=event, message=f"没有您的信息，输入【我要修仙】加入！")
        raise MsgError

    return user_qq, msg


class MsgError(ValueError):
    pass

async def send_forward_msg(
    bot: Bot,
    event: MessageEvent,
    name: str,  # 转发的用户名称
    uin: str,  # qq
    msgs: list  # 转发内容
):
    """合并消息转发"""
    def to_json(msg):
        return {"type": "node", "data": {"name": name, "uin": uin, "content": msg}}

    messages = [to_json(msg) for msg in msgs]
    if isinstance(event, GroupMessageEvent):
        await bot.call_api(
            "send_group_forward_msg", group_id=event.group_id, messages=messages
        )
    else:
        await bot.call_api(
            "send_private_forward_msg", user_id=event.user_id, messages=messages
        )

def isInGroups(event: MessageEvent):
    return event.group_id in groups['open']
