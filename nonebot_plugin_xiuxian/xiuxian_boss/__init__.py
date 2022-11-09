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
    GROUP_OWNER,
    ActionFailed

)
from nonebot.permission import SUPERUSER
from nonebot.log import logger
from ..xiuxian2_handle import XiuxianDateManage
from .makeboss import createboss
from .bossconfig import get_config, savef
from ..player_fight import Boss_fight
from ..utils import data_check_conf, send_forward_msg_list
from ..read_buff import UserBuffDate

config = get_config()
# 定时任务
set_boss = require("nonebot_plugin_apscheduler").scheduler

create = on_command("生成世界boss", aliases={"生成世界Boss", "生成世界BOSS"}, priority=5, permission= GROUP and (SUPERUSER))
boss_info = on_command("查询世界boss", aliases={"查询世界Boss", "查询世界BOSS"}, priority=5, permission= GROUP)
set_group_boss = on_command("世界boss", aliases={"世界Boss", "世界BOSS"}, priority=5, permission= GROUP and (SUPERUSER | GROUP_ADMIN | GROUP_OWNER))
battle = on_command("讨伐boss", aliases={"讨伐世界boss", "讨伐Boss", "讨伐BOSS", "讨伐世界Boss","讨伐世界BOSS"}, priority=5, permission= GROUP)
boss_help = on_command("世界boss帮助", aliases={"世界Boss帮助", "世界BOSS帮助"}, priority=4, block=True)
boss_delete = on_command("天罚boss", aliases={"天罚世界boss", "天罚Boss", "天罚BOSS", "天罚世界Boss","天罚世界BOSS"}, priority=5, permission= GROUP and (SUPERUSER | GROUP_ADMIN | GROUP_OWNER))

boss_time = config["Boss生成时间参数"]
__boss_help__ = f"""
世界Boss帮助信息:
指令：
1、生成世界boss：生成一只随机大境界的世界Boss,超管权限
2、查询世界boss：查询本群全部世界Boss，可加Boss编号查询对应Boss信息
3、世界boss开启、关闭：开启后才可以生成世界Boss，管理员权限
4、讨伐boss、讨伐世界boss：讨伐世界Boss，必须加Boss编号
5、世界boss帮助、世界boss：获取世界Boss帮助信息
6、天罚boss、天罚世界boss：删除世界Boss，必须加Boss编号,管理员权限
非指令：
1、拥有定时任务：每{str(boss_time['hours']) + '小时' if boss_time['hours'] != 0 else ''}{str(boss_time['minutes']) + '分钟' if boss_time['minutes'] != 0 else ''}生成一只随机大境界的世界Boss
""".strip()

group_boss = {}
groups = config['open']
battle_flag = {}


# 定时任务生成世界boss
@set_boss.scheduled_job("interval", 
                       hours=boss_time['hours'], 
                       minutes=boss_time['minutes'])
async def _():
    bot = get_bot()
    if groups != []:
        for g in groups:
            try:
                group_boss[g]
            except:
                group_boss[g] = []
                
            if len(group_boss[g]) >= config['Boss个数上限']:
                continue

            bossinfo = createboss()
            group_boss[g].append(bossinfo)
            msg = f"已生成{bossinfo['jj']}Boss:{bossinfo['name']}，诸位道友请击败Boss获得奖励吧！"
            await bot.send_group_msg(group_id=int(g), message=msg)
            logger.info('已生成世界boss')
        
        
@boss_help.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    await data_check_conf(bot, event)
    await boss_help.finish(__boss_help__)

@boss_delete.handle()
async def _(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    await data_check_conf(bot, event)
    msg = args.extract_plain_text().strip()
    group_id = event.group_id
    boss_num = re.findall("\d+", msg)  # boss编号
    
    isInGroup = isInGroups(event)
    if not isInGroup:#不在配置表内
        await boss_delete.finish(f'本群尚未开启世界Boss，请联系管理员开启!')
    
    if boss_num:
        boss_num = int(boss_num[0])
    else:
        await boss_delete.finish(f'请输入正确的世界Boss编号！')
    
    try:
        bosss = group_boss[group_id]
    except:
        await boss_delete.finish(f'本群尚未生成世界Boss，请等待世界boss刷新!')
    
    if bosss == []:
        await boss_delete.finish(f'本群尚未生成世界Boss，请等待世界boss刷新!')
    
    index = len(group_boss[group_id])
    
    if not (0 < boss_num <= index):
        await boss_delete.finish(f'请输入正确的世界Boss编号！')
    
    group_boss[group_id].remove(group_boss[group_id][boss_num - 1])
    await boss_delete.finish(f"该世界Boss被突然从天而降的神雷劈中，烟消云散了", at_sender=True)

@battle.handle()
async def _(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    await data_check_conf(bot, event)
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
        bosss = group_boss[group_id]
    except:
        await battle.finish(f'本群尚未生成世界Boss，请等待世界boss刷新!')
    
    if bosss == []:
        await battle.finish(f'本群尚未生成世界Boss，请等待世界boss刷新!')
    
    index = len(group_boss[group_id])
    
    if not (0 < boss_num <= index):
        await battle.finish(f'请输入正确的世界Boss编号！')
        
    try:
        battle_flag[group_id]
    except:
        battle_flag[group_id] = False
    
    if battle_flag[group_id]:
        await battle.finish(f'当前有道友正在Boss战斗！')
    
    
    if userinfo.hp is None or userinfo.hp == 0:
        # 判断用户气血是否为空
        XiuxianDateManage().update_user_hp(user_id)
    
    if userinfo.hp <= userinfo.exp / 10:
        await battle.finish("重伤未愈，动弹不得！", at_sender=True)
        
    player = {"user_id": None, "道号": None, "气血": None, "攻击": None, "真元": None, '会心': None, '防御': 0}
    userinfo = XiuxianDateManage().get_user_real_info(user_id)
    user_weapon_data = UserBuffDate(userinfo.user_id).get_user_weapon_data()
    if user_weapon_data != None:
        player['会心'] = int(user_weapon_data['crit_buff'] * 100)
    else:
        player['会心'] = 1
    player['user_id'] = userinfo.user_id
    player['道号'] = userinfo.user_name
    player['气血'] = userinfo.hp
    player['攻击'] = userinfo.atk
    player['真元'] = userinfo.mp
    player['exp'] = userinfo.exp
    
    bossinfo = group_boss[group_id][boss_num - 1]
    battle_flag[group_id] = True
    result, victor, bossinfo_new, get_stone = await Boss_fight(player, bossinfo, bot_id=bot.self_id)
    # await send_forward_msg(bot, event, 'Boss战', bot.self_id, result)
    try:
        await send_forward_msg_list(bot, event, result)
    except ActionFailed:
        battle_flag[group_id] = False
        msg = "Boss战消息发送错误，请检查日志！"
        await battle.finish(msg)
        
    if victor == bossinfo['name']:
        group_boss[group_id][boss_num - 1] = bossinfo_new
        XiuxianDateManage().update_ls(user_id, get_stone, 1)
        battle_flag[group_id] = False
        await battle.finish(f"道友不敌{bossinfo['name']}，重伤逃遁，临逃前收获灵石{get_stone}枚")
    elif victor == player['道号']:
        group_boss[group_id].remove(group_boss[group_id][boss_num - 1])
        XiuxianDateManage().update_ls(user_id, get_stone, 1)
        battle_flag[group_id] = False
        await battle.finish(f"恭喜道友击败{bossinfo['name']}，收获灵石{get_stone}枚")

@boss_info.handle()
async def _(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    await data_check_conf(bot, event)
    group_id = event.group_id
    isInGroup = isInGroups(event)
    if not isInGroup:#不在配置表内
        await boss_info.finish(f'本群尚未开启世界Boss，请联系管理员开启!')
    
    try:
        bosss = group_boss[group_id]
    except:
        await boss_info.finish(f'本群尚未生成世界Boss，请等待世界boss刷新!')
        
    msg = args.extract_plain_text().strip()
    boss_num = re.findall("\d+", msg)  # boss编号

    if bosss == []:
        await boss_info.finish(f'本群尚未生成世界Boss，请等待世界boss刷新!')
    
    Flag = False#True查对应Boss
    if boss_num:
        boss_num = int(boss_num[0])
        index = len(group_boss[group_id])
        if not (0 < boss_num <= index):
            await boss_info.finish(f'请输入正确的世界Boss编号！')
            
        Flag = True
    
    bossmsgs = ""
    if Flag:#查单个Boss信息
        boss = group_boss[group_id][boss_num - 1]
        bossmsgs = f'''
世界Boss：{boss['name']}
境界：{boss['jj']}
剩余血量：{boss['气血']}
攻击：{boss['攻击']}
携带灵石：{boss['stone']}
        '''
        await boss_info.finish(bossmsgs)
    else:
        i = 1
        for boss in bosss:
            bossmsgs += f"编号{i}、{boss['jj']}Boss:{boss['name']} \n"
            i += 1
        await boss_info.finish(bossmsgs)

@create.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    await data_check_conf(bot, event)
    group_id = event.group_id
    isInGroup = isInGroups(event)
    if not isInGroup:#不在配置表内
        await create.finish(f'本群尚未开启世界Boss，请联系管理员开启!')
    
    bossinfo = createboss()
    try:
        group_boss[group_id]
    except:
        group_boss[group_id] = []
        
    if len(group_boss[group_id]) >= config['Boss个数上限']:
        await create.finish(f"本群世界Boss已达到上限{config['Boss个数上限']}个，无法继续生成")
    group_boss[group_id].append(bossinfo)
    await create.finish(f"已生成{bossinfo['jj']}Boss:{bossinfo['name']}，诸位道友请击败Boss获得奖励吧！")



@set_group_boss.handle()
async def _(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    await data_check_conf(bot, event)
    mode = args.extract_plain_text().strip()
    group_id = event.group_id
    isInGroup = isInGroups(event) #True在，False不在

    if mode == '开启':
        if isInGroup:
            await set_group_boss.finish(f'本群已开启世界Boss，请勿重复开启!')
        else:
            config['open'].append(group_id)
            savef(config)
            await set_group_boss.finish(f'已开启本群世界Boss!')

    elif mode == '关闭':
        if isInGroup:
            config['open'].remove(group_id)
            savef(config)
            await set_group_boss.finish(f'已关闭本群世界Boss!')
        else:
            await set_group_boss.finish(f'本群未开启世界Boss!')
    
    elif mode == '':
        await set_group_boss.finish(__boss_help__)
    else:
        await set_group_boss.finish(f'请输入正确的指令：世界boss开启或关闭!')


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


def isInGroups(event: GroupMessageEvent):
    return event.group_id in groups
