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
    ActionFailed,
    MessageSegment

)
from nonebot.permission import SUPERUSER
from nonebot.log import logger
from ..xiuxian2_handle import XiuxianDateManage
from ..xiuxian_config import USERRANK, XiuConfig
from .makeboss import createboss
from .bossconfig import get_config, savef
from ..player_fight import Boss_fight
from ..item_json import Items
from ..utils import data_check_conf, send_forward_msg_list, check_user, send_forward_msg, get_msg_pic
from ..read_buff import UserBuffDate
from pathlib import Path
import json
import os
from nonebot_plugin_guild_patch import (
    GUILD,
    GUILD_OWNER,
    GUILD_ADMIN,
    GUILD_SUPERUSER,
    GuildMessageEvent
)

config = get_config()
# 定时任务
set_boss = require("nonebot_plugin_apscheduler").scheduler

create = on_command("生成世界boss", aliases={"生成世界Boss", "生成世界BOSS"}, priority=5, permission= GROUP | GUILD and (SUPERUSER | GUILD_SUPERUSER))
boss_info = on_command("查询世界boss", aliases={"查询世界Boss", "查询世界BOSS"}, priority=5, permission= GROUP | GUILD)
set_group_boss = on_command("世界boss", aliases={"世界Boss", "世界BOSS"}, priority=5, permission= GROUP | GUILD and (SUPERUSER | GROUP_ADMIN | GROUP_OWNER | GUILD_SUPERUSER | GUILD_ADMIN | GUILD_OWNER))
battle = on_command("讨伐boss", aliases={"讨伐世界boss", "讨伐Boss", "讨伐BOSS", "讨伐世界Boss","讨伐世界BOSS"}, priority=5, permission= GROUP | GUILD)
boss_help = on_command("世界boss帮助", aliases={"世界Boss帮助", "世界BOSS帮助"}, priority=4, block=True)
boss_delete = on_command("天罚boss", aliases={"天罚世界boss", "天罚Boss", "天罚BOSS", "天罚世界Boss","天罚世界BOSS"}, priority=5, permission= GROUP | GUILD and (SUPERUSER | GROUP_ADMIN | GROUP_OWNER | GUILD_SUPERUSER | GUILD_ADMIN | GUILD_OWNER))
boss_delete_all = on_command("天罚所有boss", aliases={"天罚所有世界boss", "天罚所有Boss", "天罚所有BOSS", "天罚所有世界Boss","天罚所有世界BOSS"}, priority=5, permission= GROUP | GUILD and (SUPERUSER | GROUP_ADMIN | GROUP_OWNER | GUILD_SUPERUSER | GUILD_ADMIN | GUILD_OWNER))
boss_integral_info = on_command("世界积分查看", priority=5, permission= GROUP | GUILD)
boss_integral_use = on_command("世界积分兑换", priority=5, permission= GROUP | GUILD)


boss_time = config["Boss生成时间参数"]
__boss_help__ = f"""
世界Boss帮助信息:
指令：
1、生成世界boss、生成世界boss+数量：生成一只随机大境界的世界Boss、生成指定数量的世界boss,超管权限
2、查询世界boss：查询本群全部世界Boss，可加Boss编号查询对应Boss信息
3、世界boss开启、关闭：开启后才可以生成世界Boss，管理员权限
4、讨伐boss、讨伐世界boss：讨伐世界Boss，必须加Boss编号
5、世界boss帮助、世界boss：获取世界Boss帮助信息
6、天罚boss、天罚世界boss：删除世界Boss，必须加Boss编号,管理员权限
7、天罚所有boss、天罚所有世界boss：删除所有的世界Boss,管理员权限
9、世界积分查看：查看自己的世界积分，和世界积分兑换商品
0、世界积分兑换+编号：兑换对应的商品
非指令：
1、拥有定时任务：每{str(boss_time['hours']) + '小时' if boss_time['hours'] != 0 else ''}{str(boss_time['minutes']) + '分钟' if boss_time['minutes'] != 0 else ''}生成一只随机大境界的世界Boss
""".strip()

group_boss = {}
groups = config['open']
battle_flag = {}
sql_message = XiuxianDateManage()  # sql类

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
            if XiuConfig().img:
                pic = await get_msg_pic(msg)#
                await bot.send_group_msg(group_id=int(g), message=MessageSegment.image(pic))
            else:
                await bot.send_group_msg(group_id=int(g), message=msg)
            logger.info('已生成世界boss')
        
        
@boss_help.handle()
async def _(bot: Bot, event: MessageEvent):
    await data_check_conf(bot, event)
    msg = __boss_help__
    pic = await get_msg_pic(msg)#
    await boss_help.finish(MessageSegment.image(pic), at_sender=True)

@boss_delete.handle()
async def _(bot: Bot, event: MessageEvent, args: Message = CommandArg()):
    await data_check_conf(bot, event)
    msg = args.extract_plain_text().strip()
    user_id, group_id, mess = await data_check(bot, event)
    boss_num = re.findall("\d+", msg)  # boss编号
    
    isInGroup = isInGroups(event)
    if not isInGroup:#不在配置表内
        msg = f'本群尚未开启世界Boss，请联系管理员开启!'
        if XiuConfig().img:
            pic = await get_msg_pic(msg)
            await boss_delete.finish(MessageSegment.image(pic), at_sender=True)
        else:
            await boss_delete.finish(msg, at_sender=True)
    
    if boss_num:
        boss_num = int(boss_num[0])
    else:
        msg = f'请输入正确的世界Boss编号！'
        if XiuConfig().img:
            pic = await get_msg_pic(msg)
            await boss_delete.finish(MessageSegment.image(pic), at_sender=True)
        else:
            await boss_delete.finish(msg, at_sender=True)
    
    try:
        bosss = group_boss[group_id]
    except:
        msg = f'本群尚未生成世界Boss，请等待世界boss刷新!'
        if XiuConfig().img:
            pic = await get_msg_pic(msg)
            await boss_delete.finish(MessageSegment.image(pic), at_sender=True)
        else:
            await boss_delete.finish(msg, at_sender=True)
    
    if bosss == []:
        msg = f'本群尚未生成世界Boss，请等待世界boss刷新!'
        if XiuConfig().img:
            pic = await get_msg_pic(msg)
            await boss_delete.finish(MessageSegment.image(pic), at_sender=True)
        else:
            await boss_delete.finish(msg, at_sender=True)
    
    index = len(group_boss[group_id])
    
    if not (0 < boss_num <= index):
        msg = f'请输入正确的世界Boss编号！'
        if XiuConfig().img:
            pic = await get_msg_pic(msg)
            await boss_delete.finish(MessageSegment.image(pic), at_sender=True)
        else:
            await boss_delete.finish(msg, at_sender=True)
    
    group_boss[group_id].remove(group_boss[group_id][boss_num - 1])
    msg = f"该世界Boss被突然从天而降的神雷劈中，烟消云散了"
    if XiuConfig().img:
        pic = await get_msg_pic(msg)
        await boss_delete.finish(MessageSegment.image(pic), at_sender=True)
    else:
        await boss_delete.finish(msg, at_sender=True)



@boss_delete_all.handle()
async def _(bot: Bot, event: MessageEvent, args: Message = CommandArg()):
    await data_check_conf(bot, event)
    user_id, group_id, mess = await data_check(bot, event)
    
    isInGroup = isInGroups(event)
    if not isInGroup:#不在配置表内
        msg = f'本群尚未开启世界Boss，请联系管理员开启!'
        if XiuConfig().img:
            pic = await get_msg_pic(msg)
            await boss_delete_all.finish(MessageSegment.image(pic), at_sender=True)
        else:
            await boss_delete_all.finish(msg, at_sender=True)
    
    try:
        bosss = group_boss[group_id]
    except:
        msg = f'本群尚未生成世界Boss，请等待世界boss刷新!'
        if XiuConfig().img:
            pic = await get_msg_pic(msg)
            await boss_delete_all.finish(MessageSegment.image(pic), at_sender=True)
        else:
            await boss_delete_all.finish(msg, at_sender=True)
    
    if bosss == []:
        msg = f'本群尚未生成世界Boss，请等待世界boss刷新!'
        if XiuConfig().img:
            pic = await get_msg_pic(msg)
            await boss_delete_all.finish(MessageSegment.image(pic), at_sender=True)
        else:
            await boss_delete_all.finish(msg, at_sender=True)
    
    group_boss[group_id] = []
    msg = f"所有的世界Boss都烟消云散了~~"
    if XiuConfig().img:
        pic = await get_msg_pic(msg)
        await boss_delete_all.finish(MessageSegment.image(pic), at_sender=True)
    else:
        await boss_delete_all.finish(msg, at_sender=True)

@battle.handle()
async def _(bot: Bot, event: MessageEvent, args: Message = CommandArg()):
    await data_check_conf(bot, event)
    try:
        isUser, userinfo, msg = check_user(event)
    except MsgError:
        return
    
    msg = args.extract_plain_text().strip()
    user_id, group_id, mess = await data_check(bot, event)
    boss_num = re.findall("\d+", msg)  # boss编号
    
    isInGroup = isInGroups(event)
    if not isInGroup:#不在配置表内
        msg = f'本群尚未开启世界Boss，请联系管理员开启!'
        if XiuConfig().img:
            pic = await get_msg_pic(msg)
            await battle.finish(MessageSegment.image(pic), at_sender=True)
        else:
            await battle.finish(msg, at_sender=True)
    
    if boss_num:
        boss_num = int(boss_num[0])
    else:
        msg = f'请输入正确的世界Boss编号！'
        if XiuConfig().img:
            pic = await get_msg_pic(msg)
            await battle.finish(MessageSegment.image(pic), at_sender=True)
        else:
            await battle.finish(msg, at_sender=True)
    
    try:
        bosss = group_boss[group_id]
    except:
        msg = f'本群尚未生成世界Boss，请等待世界boss刷新!'
        if XiuConfig().img:
            pic = await get_msg_pic(msg)
            await battle.finish(MessageSegment.image(pic), at_sender=True)
        else:
            await battle.finish(msg, at_sender=True)
    
    if bosss == []:
        msg = f'本群尚未生成世界Boss，请等待世界boss刷新!'
        if XiuConfig().img:
            pic = await get_msg_pic(msg)
            await battle.finish(MessageSegment.image(pic), at_sender=True)
        else:
            await battle.finish(msg, at_sender=True)
    
    index = len(group_boss[group_id])
    
    if not (0 < boss_num <= index):
        msg = f'请输入正确的世界Boss编号！'
        if XiuConfig().img:
            pic = await get_msg_pic(msg)
            await battle.finish(MessageSegment.image(pic), at_sender=True)
        else:
            await battle.finish(msg, at_sender=True)
        
    try:
        battle_flag[group_id]
    except:
        battle_flag[group_id] = False
    
    if battle_flag[group_id]:
        msg = f'当前有道友正在Boss战斗！'
        if XiuConfig().img:
            pic = await get_msg_pic(msg)
            await battle.finish(MessageSegment.image(pic), at_sender=True)
        else:
            await battle.finish(msg, at_sender=True)
    
    
    if userinfo.hp is None or userinfo.hp == 0:
        # 判断用户气血是否为空
        XiuxianDateManage().update_user_hp(user_id)
    
    if userinfo.hp <= userinfo.exp / 10:
        msg = "重伤未愈，动弹不得！"
        if XiuConfig().img:
            pic = await get_msg_pic(msg)
            await battle.finish(MessageSegment.image(pic), at_sender=True)
        else:
            await battle.finish(msg, at_sender=True)
        
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
    boss_rank = USERRANK[bossinfo['jj']]
    user_rank = USERRANK[userinfo.level]
    boss_old_hp = bossinfo['气血']#打之前的血量
    more_msg = ''
    battle_flag[group_id] = True
    result, victor, bossinfo_new, get_stone = await Boss_fight(player, bossinfo, bot_id=bot.self_id)
    if victor == "Boss赢了":
        group_boss[group_id][boss_num - 1] = bossinfo_new
        XiuxianDateManage().update_ls(user_id, get_stone, 1)
        #新增boss战斗积分点数
        boss_now_hp = bossinfo_new['气血']#打之后的血量
        boss_all_hp = bossinfo['总血量']#总血量
        boss_integral = int(((boss_old_hp - boss_now_hp) / boss_all_hp) * 100)
        if boss_integral < 10:#摸一下不给
            boss_integral = 0
        if boss_rank - user_rank >= 9:#超过太多不给
            boss_integral = 0
            more_msg = "道友的境界超过boss太多了！"
        user_boss_fight_info = get_user_boss_fight_info(user_id)
        user_boss_fight_info['boss_integral'] += boss_integral
        save_user_boss_fight_info(user_id, user_boss_fight_info)
        msg = f"道友不敌{bossinfo['name']}，重伤逃遁，临逃前收获灵石{get_stone}枚，{more_msg}获得世界积分：{boss_integral}点"
        battle_flag[group_id] = False
        if isinstance(event, GroupMessageEvent):
            try:
                await send_forward_msg_list(bot, event, result)
            except ActionFailed:
                msg += "\nBoss战消息发送错误，可能被风控！"
        if XiuConfig().img:
            pic = await get_msg_pic(msg)
            await battle.finish(MessageSegment.image(pic), at_sender=True)
        else:
            await battle.finish(msg, at_sender=True)
        
    elif victor == "群友赢了":
        #新增boss战斗积分点数
        boss_all_hp = bossinfo['总血量']#总血量
        boss_integral = int((boss_old_hp / boss_all_hp) * 100)
        if boss_integral < 10:#摸一下不给
            boss_integral = 0
        if boss_rank - user_rank >= 9:#超过太多不给
            boss_integral = 0
            more_msg = "道友的境界超过boss太多了！"
        group_boss[group_id].remove(group_boss[group_id][boss_num - 1])
        battle_flag[group_id] = False
        XiuxianDateManage().update_ls(user_id, get_stone, 1)
        user_boss_fight_info = get_user_boss_fight_info(user_id)
        user_boss_fight_info['boss_integral'] += boss_integral
        save_user_boss_fight_info(user_id, user_boss_fight_info)
        msg = f"恭喜道友击败{bossinfo['name']}，收获灵石{get_stone}枚，{more_msg}获得世界积分：{boss_integral}点"
        if isinstance(event, GroupMessageEvent):
            try:
                await send_forward_msg_list(bot, event, result)
            except ActionFailed:
                msg += "\nBoss战消息发送错误，可能被风控！"
        if XiuConfig().img:
            pic = await get_msg_pic(msg)
            await battle.finish(MessageSegment.image(pic), at_sender=True)
        else:
            await battle.finish(msg, at_sender=True)

@boss_info.handle()
async def _(bot: Bot, event: MessageEvent, args: Message = CommandArg()):
    await data_check_conf(bot, event)
    user_id, group_id, mess = await data_check(bot, event)
    isInGroup = isInGroups(event)
    if not isInGroup:#不在配置表内
        msg = f'本群尚未开启世界Boss，请联系管理员开启!'
        if XiuConfig().img:
            pic = await get_msg_pic(msg)
            await boss_info.finish(MessageSegment.image(pic), at_sender=True)
        else:
            await boss_info.finish(msg, at_sender=True)
    
    try:
        bosss = group_boss[group_id]
    except:
        msg = f'本群尚未生成世界Boss，请等待世界boss刷新!'
        if XiuConfig().img:
            pic = await get_msg_pic(msg)
            await boss_info.finish(MessageSegment.image(pic), at_sender=True)
        else:
            await boss_info.finish(msg, at_sender=True)
        
    msg = args.extract_plain_text().strip()
    boss_num = re.findall("\d+", msg)  # boss编号

    if bosss == []:
        msg = f'本群尚未生成世界Boss，请等待世界boss刷新!'
        if XiuConfig().img:
            pic = await get_msg_pic(msg)
            await boss_info.finish(MessageSegment.image(pic), at_sender=True)
        else:
            await boss_info.finish(msg, at_sender=True)
    
    Flag = False#True查对应Boss
    if boss_num:
        boss_num = int(boss_num[0])
        index = len(group_boss[group_id])
        if not (0 < boss_num <= index):
            msg = f'请输入正确的世界Boss编号！'
            if XiuConfig().img:
                pic = await get_msg_pic(msg)
                await boss_info.finish(MessageSegment.image(pic), at_sender=True)
            else:
                await boss_info.finish(msg, at_sender=True)
            
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
        msg = bossmsgs
        if XiuConfig().img:
            pic = await get_msg_pic(msg)
            await boss_info.finish(MessageSegment.image(pic), at_sender=True)
        else:
            await boss_info.finish(msg, at_sender=True)
    else:
        i = 1
        for boss in bosss:
            bossmsgs += f"编号{i}、{boss['jj']}Boss:{boss['name']} \n"
            i += 1
        msg = bossmsgs
        if XiuConfig().img:
            pic = await get_msg_pic(msg)
            await boss_info.finish(MessageSegment.image(pic), at_sender=True)
        else:
            await boss_info.finish(msg, at_sender=True)

@create.handle()
async def _(bot: Bot, event: MessageEvent, args: Message = CommandArg()):
    await data_check_conf(bot, event)
    user_id, group_id, mess = await data_check(bot, event)
    isInGroup = isInGroups(event)
    if not isInGroup:#不在配置表内
        msg = f'本群尚未开启世界Boss，请联系管理员开启!'
        if XiuConfig().img:
            pic = await get_msg_pic(msg)
            await create.finish(MessageSegment.image(pic), at_sender=True)
        else:
            await create.finish(msg, at_sender=True)
    try:
        group_boss[group_id]
    except:
        group_boss[group_id] = []
    if len(group_boss[group_id]) >= config['Boss个数上限']:
        msg = f"本群世界Boss已达到上限{config['Boss个数上限']}个，无法继续生成"
        if XiuConfig().img:
            pic = await get_msg_pic(msg)
            await create.finish(MessageSegment.image(pic), at_sender=True)
        else:
            await create.finish(msg, at_sender=True)
    args = args.extract_plain_text().strip()
    num = re.findall("\d+", args)  
    if num:
        num = int(num[0]) #数量
        i = 0
        while(i < num):
            bossinfo = createboss()
            group_boss[group_id].append(bossinfo)
            i += 1
            if len(group_boss[group_id]) >= config['Boss个数上限']:
                break
        msg = f"已生成{i}个世界boss，请发送 查询世界boss 来查看boss"
        if XiuConfig().img:
            pic = await get_msg_pic(msg)
            await create.finish(MessageSegment.image(pic), at_sender=True)
        else:
            await create.finish(msg, at_sender=True)
    else:
        bossinfo = createboss()
        group_boss[group_id].append(bossinfo)
        msg = f"已生成{bossinfo['jj']}Boss:{bossinfo['name']}，诸位道友请击败Boss获得奖励吧！"
        if XiuConfig().img:
            pic = await get_msg_pic(msg)
            await create.finish(MessageSegment.image(pic), at_sender=True)
        else:
            await create.finish(msg, at_sender=True)



@set_group_boss.handle()
async def _(bot: Bot, event: MessageEvent, args: Message = CommandArg()):
    await data_check_conf(bot, event)
    mode = args.extract_plain_text().strip()
    user_id, group_id, mess = await data_check(bot, event)
    isInGroup = isInGroups(event) #True在，False不在
    print("群号配置:",isInGroup)
    print("群号:",group_id)
    print("已开启群聊:",groups)

    if mode == '开启':
        if isInGroup:
            msg = f'本群已开启世界Boss，请勿重复开启!'
            if XiuConfig().img:
                pic = await get_msg_pic(msg)
                await set_group_boss.finish(MessageSegment.image(pic), at_sender=True)
            else:
                await set_group_boss.finish(msg, at_sender=True)
        else:
            config['open'].append(group_id)
            savef(config)
            msg = f'已开启本群世界Boss!'
            if XiuConfig().img:
                pic = await get_msg_pic(msg)
                await set_group_boss.finish(MessageSegment.image(pic), at_sender=True)
            else:
                await set_group_boss.finish(msg, at_sender=True)

    elif mode == '关闭':
        if isInGroup:
            config['open'].remove(group_id)
            savef(config)
            msg = f'已关闭本群世界Boss!'
            if XiuConfig().img:
                pic = await get_msg_pic(msg)
                await set_group_boss.finish(MessageSegment.image(pic), at_sender=True)
            else:
                await set_group_boss.finish(msg, at_sender=True)
        else:
            msg = f'本群未开启世界Boss!'
            if XiuConfig().img:
                pic = await get_msg_pic(msg)
                await set_group_boss.finish(MessageSegment.image(pic), at_sender=True)
            else:
                await set_group_boss.finish(msg, at_sender=True)
    
    elif mode == '':
        msg = __boss_help__
        if XiuConfig().img:
            pic = await get_msg_pic(msg)
            await set_group_boss.finish(MessageSegment.image(pic), at_sender=True)
        else:
            await set_group_boss.finish(msg, at_sender=True)
    else:
        msg = f'请输入正确的指令：世界boss开启或关闭!'
        if XiuConfig().img:
            pic = await get_msg_pic(msg)
            await set_group_boss.finish(MessageSegment.image(pic), at_sender=True)
        else:
            await set_group_boss.finish(msg, at_sender=True)


@boss_integral_info.handle()
async def _(bot: Bot, event: MessageEvent, args: Message = CommandArg()):
    await data_check_conf(bot, event)

    try:
        user_id, group_id, mess = await data_check(bot, event)
    except MsgError:
        return

    isInGroup = isInGroups(event)
    if not isInGroup:#不在配置表内
        msg = f'本群尚未开启世界Boss，请联系管理员开启!'
        if XiuConfig().img:
            pic = await get_msg_pic(msg)
            await boss_integral_info.finish(MessageSegment.image(pic), at_sender=True)
        else:
            await boss_integral_info.finish(msg, at_sender=True)
    
    user_boss_fight_info = get_user_boss_fight_info(user_id)
    boss_integral_shop = config['世界积分商品']
    l_msg = []
    l_msg.append(f"道友目前拥有的世界积分：{user_boss_fight_info['boss_integral']}点")
    if boss_integral_shop != {}:
        for k, v in boss_integral_shop.items():
            msg = f"编号:{k}\n"
            msg += f"描述：{v['desc']}\n"
            msg += f"所需世界积分：{v['cost']}点"
            l_msg.append(msg)
    else:
        l_msg.append(f"世界积分商店内空空如也！")
    if isinstance(event, GroupMessageEvent):
        await send_forward_msg(bot, event, '世界积分商店', bot.self_id, l_msg)
        await boss_integral_info.finish()
    elif isinstance(event, GuildMessageEvent):
        msg = ' '.join(l_msg)
        if XiuConfig().img:
            pic = await get_msg_pic(msg)
            await boss_integral_info.finish(MessageSegment.image(pic), at_sender=True)
        else:
            await boss_integral_info.finish(msg, at_sender=True)
        
@boss_integral_use.handle()
async def _(bot: Bot, event: MessageEvent, args: Message = CommandArg()):
    await data_check_conf(bot, event)
    try:
        user_id, group_id, mess = await data_check(bot, event)
    except MsgError:
        return
    msg = args.extract_plain_text().strip()
    shop_num = re.findall("\d+", msg)  # boss编号
    
    isInGroup = isInGroups(event)
    if not isInGroup:#不在配置表内
        msg = f'本群尚未开启世界Boss，请联系管理员开启!'
        if XiuConfig().img:
            pic = await get_msg_pic(msg)
            await boss_integral_use.finish(MessageSegment.image(pic), at_sender=True)
        else:
            await boss_integral_use.finish(msg, at_sender=True)
    
    if shop_num:
        shop_num = int(shop_num[0])
    else:
        msg = f'请输入正确的商品编号！'
        if XiuConfig().img:
            pic = await get_msg_pic(msg)
            await boss_integral_use.finish(MessageSegment.image(pic), at_sender=True)
        else:
            await boss_integral_use.finish(msg, at_sender=True)
    
    boss_integral_shop = config['世界积分商品']
    is_in = False
    if boss_integral_shop != {}:
        for k, v in boss_integral_shop.items():
            if shop_num == int(k):
                is_in = True
                cost = v['cost']
                shop_id = v['id']
                break
            else:
                continue
    else:
        msg = f"世界积分商店内空空如也！"
        if XiuConfig().img:
            pic = await get_msg_pic(msg)
            await boss_integral_use.finish(MessageSegment.image(pic), at_sender=True)
        else:
            await boss_integral_use.finish(msg, at_sender=True)
    if is_in:
        user_boss_fight_info = get_user_boss_fight_info(user_id)
        if user_boss_fight_info['boss_integral'] < cost:
            msg = f"道友的世界积分不满足兑换条件呢"
            if XiuConfig().img:
                pic = await get_msg_pic(msg)
                await boss_integral_use.finish(MessageSegment.image(pic), at_sender=True)
            else:
                await boss_integral_use.finish(msg, at_sender=True)
        else:
            user_boss_fight_info['boss_integral'] -= cost
            save_user_boss_fight_info(user_id, user_boss_fight_info)
            item_info = Items().get_data_by_item_id(shop_id)
            sql_message.send_back(user_id, shop_id, item_info['name'], item_info['type'], 1)
            msg = f"道友成功兑换获得：{item_info['name']}"
            if XiuConfig().img:
                pic = await get_msg_pic(msg)
                await boss_integral_use.finish(MessageSegment.image(pic), at_sender=True)
            else:
                await boss_integral_use.finish(msg, at_sender=True)
    else:
        msg = f"该编号不在商品列表内哦，请检查后再兑换"
        if XiuConfig().img:
            pic = await get_msg_pic(msg)
            await boss_integral_use.finish(MessageSegment.image(pic), at_sender=True)
        else:
            await boss_integral_use.finish(msg, at_sender=True)

async def get_group_id(session_id):
    """获取group_id"""
    print("session_id内容:",session_id)
    res = re.findall("_(.*)_", session_id)
    print("res内容:",res)
    group_id = int(res[0])
    print("群号:",group_id)
    return group_id

async def data_check(bot, event):
    """
    判断用户信息是否存在
    """
    if isinstance(event, GroupMessageEvent):
        user_qq = event.get_user_id()
        group_id = await get_group_id(event.get_session_id())
        print("群号:",group_id)
        msg = sql_message.get_user_message(user_qq)
        if msg:
            pass
        else:
            await bot.send(event=event, message=f"没有您的信息，输入【我要修仙】加入！")
            raise MsgError
    elif isinstance(event, GuildMessageEvent):
        tiny_id = event.get_user_id()
        group_id = f"{event.guild_id}@{event.channel_id}"
        print("群号:",group_id)
        msg = sql_message.get_user_message3(tiny_id)
        print("tiny_id", tiny_id)
        if msg:
            user_qq = msg.user_id
            pass
        else:
            await bot.send(event=event, message=f"没有您的QQ绑定信息，输入【绑定QQ+QQ号码】进行绑定后再输入【我要修仙】加入！")
            raise MsgError

    return user_qq, group_id, msg

class MsgError(ValueError):
    pass


class ConfError(ValueError):
    pass

def isInGroups(event: MessageEvent):
    if isinstance(event, GroupMessageEvent):
        print("event里面的群号",event.group_id)
        return event.group_id in groups
    elif isinstance(event, GuildMessageEvent):
        group_id = f"{event.guild_id}@{event.channel_id}"
        print("event里面的频道群号",group_id)
        return group_id in groups

PLAYERSDATA = Path() / "data" / "xiuxian" / "players"

def get_user_boss_fight_info(user_id):
    try:
        user_boss_fight_info = read_user_boss_fight_info(user_id)
    except:
        user_boss_fight_info = {}
        user_boss_fight_info['boss_integral'] = 0
        save_user_boss_fight_info(user_id, user_boss_fight_info)
    return user_boss_fight_info

def read_user_boss_fight_info(user_id):
    user_id = str(user_id)
    
    FILEPATH = PLAYERSDATA / user_id / "boss_fight_info.json"
    with open(FILEPATH, "r", encoding="UTF-8") as f:
        data = f.read()
    return json.loads(data)

def save_user_boss_fight_info(user_id, data):
    user_id = str(user_id)
    
    if not os.path.exists(PLAYERSDATA / user_id):
        print("目录不存在，创建目录")
        os.makedirs(PLAYERSDATA / user_id)
    
    FILEPATH = PLAYERSDATA / user_id / "boss_fight_info.json"
    data = json.dumps(data, ensure_ascii=False, indent=4)
    save_mode = "w" if os.path.exists(FILEPATH) else "x"
    with open(FILEPATH, mode=save_mode, encoding="UTF-8") as f:
        f.write(data)