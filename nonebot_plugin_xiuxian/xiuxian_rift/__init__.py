from nonebot import get_bot, on_command, require
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import (
    Bot,
    MessageEvent,
    GROUP,
    Message,
    GroupMessageEvent,
    GROUP_ADMIN,
    GROUP_OWNER,
    MessageSegment
)
from .old_rift_info import old_rift_info
from nonebot.permission import SUPERUSER
from nonebot.log import logger
from ..xiuxian2_handle import XiuxianDateManage
from ..utils import data_check_conf, check_user, send_forward_msg, check_user_type, send_forward_msg_list, get_msg_pic, pic_msg_format
from .riftconfig import get_config, savef
from .jsondata import save_rift_data, read_rift_data
from .riftmake import Rift, get_rift_type, get_story_type, NONEMSG, get_battle_type, get_dxsj_info, get_boss_battle_info, get_treasure_info
import random
from datetime import datetime
from ..xiuxian_config import XiuConfig
from nonebot import get_driver

driver = get_driver()
config = get_config()
sql_message = XiuxianDateManage()  # sql类

# 定时任务
set_rift = require("nonebot_plugin_apscheduler").scheduler
set_group_rift = on_command("群秘境", priority=5, permission= GROUP and (SUPERUSER | GROUP_ADMIN | GROUP_OWNER))
explore_rift = on_command("探索秘境", priority=5, permission= GROUP)
rift_help = on_command("秘境帮助", priority=5, permission= GROUP)
create_rift = on_command("生成秘境", priority=5, permission= GROUP and (SUPERUSER))
complete_rift = on_command("秘境结算", aliases={"结算秘境"}, priority=5, permission= GROUP)
break_rift = on_command("秘境探索终止", aliases={"终止探索秘境"}, priority=5, permission= GROUP)

__rift_help__ = f"""
秘境帮助信息:
指令：
1、群秘境开启、关闭：开启本群的秘境生成，管理员权限
2、生成秘境：生成一个随机秘境，超管权限
3、探索秘境：探索秘境获取随机奖励
4、秘境结算、结算秘境：结算秘境奖励
5、秘境探索终止、终止探索秘境：终止秘境事件
6、秘境帮助：获取秘境帮助信息
非指令：
1、每日18点30分生成一个随机等级的秘境
""".strip()

group_rift = {} #dict
groups = config['open'] #list

@driver.on_startup
async def read_rift_():
    global group_rift
    group_rift.update(old_rift_info.read_rift_info())
    print(group_rift)
    logger.info("历史rift数据读取成功")


@driver.on_shutdown
async def save_rift_():
    global group_rift
    old_rift_info.save_rift(group_rift)
    logger.info("rift数据已保存")


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
            rift.time = config['rift'][rift.name]['time']
            group_rift[group_id] = rift
            msg = f"野生的{rift.name}已开启！可探索次数：{rift.count}次，请诸位道友发送 探索秘境 来加入吧！"
            try:
                if XiuConfig().img:
                    pic = await get_msg_pic(msg)
                    await bot.send_group_msg(group_id=int(group_id), message=MessageSegment.image(pic))
                else:
                    await bot.send_group_msg(group_id=int(group_id), message=msg)
            except Exception as e:
                logger.error(f"群秘境生成推送失败：{e}")
@rift_help.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    await data_check_conf(bot, event)
    msg = __rift_help__
    pic = await get_msg_pic(msg)#
    await rift_help.finish(MessageSegment.image(pic))

#生成秘境
@create_rift.handle()
async def _(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    await data_check_conf(bot, event)
    group_id = event.group_id
    if group_id not in groups:
        msg = '本群尚未开启秘境，请联系管理员开启群秘境'
        if XiuConfig().img:
            msg = await pic_msg_format(msg, event)
            pic = await get_msg_pic(msg)
            await create_rift.finish(MessageSegment.image(pic))
        else:
            await create_rift.finish(msg, at_sender=True)
    
    try:
        group_rift[group_id]
        msg = f"当前已存在{group_rift[group_id].name}，秘境可探索次数：{group_rift[group_id].count}次，请诸位道友发送 探索秘境 来加入吧！"
        if XiuConfig().img:
            msg = await pic_msg_format(msg, event)
            pic = await get_msg_pic(msg)
            await create_rift.finish(MessageSegment.image(pic))
        else:
            await create_rift.finish(msg, at_sender=True)
    except KeyError:
        rift = Rift()
        rift.name = get_rift_type()
        rift.rank = config['rift'][rift.name]['rank']
        rift.count = config['rift'][rift.name]['count']
        rift.time = config['rift'][rift.name]['time']
        group_rift[group_id] = rift
        msg = f"野生的{rift.name}出现了！秘境可探索次数：{rift.count}次，请诸位道友发送 探索秘境 来加入吧！"
        if XiuConfig().img:
            msg = await pic_msg_format(msg, event)
            pic = await get_msg_pic(msg)
            await create_rift.finish(MessageSegment.image(pic))
        else:
            await create_rift.finish(msg, at_sender=True)


#探索秘境
@explore_rift.handle()
async def _(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    await data_check_conf(bot, event)

    isUser, user_info, msg = check_user(event)
    if not isUser:
        if XiuConfig().img:
            msg = await pic_msg_format(msg, event)
            pic = await get_msg_pic(msg)
            await explore_rift.finish(MessageSegment.image(pic))
        else:
            await explore_rift.finish(msg, at_sender=True)
    
    user_id = user_info.user_id
    is_type, msg = check_user_type(user_id, 0)#需要无状态的用户
    if not is_type:
        if XiuConfig().img:
            msg = await pic_msg_format(msg, event)
            pic = await get_msg_pic(msg)
            await explore_rift.finish(MessageSegment.image(pic))
        else:
            await explore_rift.finish(msg, at_sender=True)
    else:
        group_id = event.group_id
        if group_id not in groups:
            msg = '本群尚未开启秘境，请联系管理员开启群秘境'
            if XiuConfig().img:
                msg = await pic_msg_format(msg, event)
                pic = await get_msg_pic(msg)
                await explore_rift.finish(MessageSegment.image(pic))
            else:
                await explore_rift.finish(msg, at_sender=True)
        try:
            group_rift[group_id]
        except:
            msg = '野外秘境尚未生成，请道友耐心等待!'
            if XiuConfig().img:
                msg = await pic_msg_format(msg, event)
                pic = await get_msg_pic(msg)
                await explore_rift.finish(MessageSegment.image(pic))
            else:
                await explore_rift.finish(msg, at_sender=True)
        if user_id in group_rift[group_id].l_user_id:
            msg = '道友已经参加过本次秘境啦，请把机会留给更多的道友！'
            if XiuConfig().img:
                msg = await pic_msg_format(msg, event)
                pic = await get_msg_pic(msg)
                await explore_rift.finish(MessageSegment.image(pic))
            else:
                await explore_rift.finish(msg, at_sender=True)
        
        group_rift[group_id].l_user_id.append(user_id)
        group_rift[group_id].count -= 1
        msg = f"道友进入秘境：{group_rift[group_id].name}，探索需要花费时间：{group_rift[group_id].time}分钟！"
        rift_data = {}
        rift_data["name"] = group_rift[group_id].name
        rift_data["time"] = group_rift[group_id].time
        rift_data["rank"] = group_rift[group_id].rank
        
        save_rift_data(user_id, rift_data)
        sql_message.do_work(user_id, 3, rift_data["time"])
        if group_rift[group_id].count == 0:
            del group_rift[group_id]
            logger.info('群{group_id}秘境已到上限次数！')
            msg += "秘境随着道友的进入，已无法再维持更多的人，而关闭了！"
            if XiuConfig().img:
                msg = await pic_msg_format(msg, event)
                pic = await get_msg_pic(msg)
                await explore_rift.finish(MessageSegment.image(pic))
            else:
                await explore_rift.finish(msg, at_sender=True)
        if XiuConfig().img:
            msg = await pic_msg_format(msg, event)
            pic = await get_msg_pic(msg)
            await explore_rift.finish(MessageSegment.image(pic))
        else:
            await explore_rift.finish(msg, at_sender=True)
    
        
#结算秘境
@complete_rift.handle()
async def _(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    await data_check_conf(bot, event)

    isUser, user_info, msg = check_user(event)
    if not isUser:
        if XiuConfig().img:
            msg = await pic_msg_format(msg, event)
            pic = await get_msg_pic(msg)
            await complete_rift.finish(MessageSegment.image(pic))
        else:
            await complete_rift.finish(msg, at_sender=True)
    user_id = user_info.user_id

    group_id = event.group_id
    if group_id not in groups:
        msg = '本群尚未开启秘境，请联系管理员开启群秘境'
        if XiuConfig().img:
            msg = await pic_msg_format(msg, event)
            pic = await get_msg_pic(msg)
            await complete_rift.finish(MessageSegment.image(pic))
        else:
            await complete_rift.finish(msg, at_sender=True)
    
    is_type, msg = check_user_type(user_id, 3)#需要在秘境的用户
    if not is_type:
        if XiuConfig().img:
            msg = await pic_msg_format(msg, event)
            pic = await get_msg_pic(msg)
            await complete_rift.finish(MessageSegment.image(pic))
        else:
            await complete_rift.finish(msg, at_sender=True)
    else:
        try:
            rift_info = read_rift_data(user_id)
        except:
            msg = '发生未知错误！'
            sql_message.do_work(user_id, 0)
            if XiuConfig().img:
                msg = await pic_msg_format(msg, event)
                pic = await get_msg_pic(msg)
                await complete_rift.finish(MessageSegment.image(pic))
            else:
                await complete_rift.finish(msg, at_sender=True)
            
        user_cd_message = sql_message.get_user_cd(user_id)
        work_time = datetime.strptime(
            user_cd_message.create_time, "%Y-%m-%d %H:%M:%S.%f"
        )
        exp_time = (datetime.now() - work_time).seconds // 60  # 时长计算
        time2 = rift_info["time"]
        if exp_time < time2:
            msg = f"进行中的：{rift_info['name']}探索，预计{time2 - exp_time}分钟后可结束"
            if XiuConfig().img:
                msg = await pic_msg_format(msg, event)
                pic = await get_msg_pic(msg)
                await complete_rift.finish(MessageSegment.image(pic))
            else:
                await complete_rift.finish(msg, at_sender=True)
        else:#秘境结算逻辑
            sql_message.do_work(user_id, 0)
            rift_rank = rift_info["rank"] #秘境等级
            rift_type = get_story_type() #无事、宝物、战斗
            if rift_type == "无事":
                msg = random.choice(NONEMSG)
                if XiuConfig().img:
                    msg = await pic_msg_format(msg, event)
                    pic = await get_msg_pic(msg)
                    await complete_rift.finish(MessageSegment.image(pic))
                else:
                    await complete_rift.finish(msg, at_sender=True)
            elif rift_type == "战斗":
                rift_type = get_battle_type()
                if rift_type == "掉血事件":
                    msg = get_dxsj_info("掉血事件", user_info)
                    if XiuConfig().img:
                        msg = await pic_msg_format(msg, event)
                        pic = await get_msg_pic(msg)
                        await complete_rift.finish(MessageSegment.image(pic))
                    else:
                        await complete_rift.finish(msg, at_sender=True)
                elif rift_type == "Boss战斗":
                    result, msg = await get_boss_battle_info(user_info, rift_rank, bot.self_id)
                    await send_forward_msg_list(bot, event, result)
                    if XiuConfig().img:
                        msg = await pic_msg_format(msg, event)
                        pic = await get_msg_pic(msg)
                        await complete_rift.finish(MessageSegment.image(pic))
                    else:
                        await complete_rift.finish(msg, at_sender=True)
            elif rift_type == "宝物":
                msg = get_treasure_info(user_info, rift_rank)
                if XiuConfig().img:
                    msg = await pic_msg_format(msg, event)
                    pic = await get_msg_pic(msg)
                    await complete_rift.finish(MessageSegment.image(pic))
                else:
                    await complete_rift.finish(msg, at_sender=True)

#终止探索秘境
@break_rift.handle()
async def _(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    await data_check_conf(bot, event)
    isUser, user_info, msg = check_user(event)
    if not isUser:
        if XiuConfig().img:
            msg = await pic_msg_format(msg, event)
            pic = await get_msg_pic(msg)
            await break_rift.finish(MessageSegment.image(pic))
        else:
            await break_rift.finish(msg, at_sender=True)

    user_id = user_info.user_id
    group_id = event.group_id
    if group_id not in groups:
        msg = '本群尚未开启秘境，请联系管理员开启群秘境'
        if XiuConfig().img:
            msg = await pic_msg_format(msg, event)
            pic = await get_msg_pic(msg)
            await break_rift.finish(MessageSegment.image(pic))
        else:
            await break_rift.finish(msg, at_sender=True)
    
    is_type, msg = check_user_type(user_id, 3)#需要在秘境的用户
    if not is_type:
        if XiuConfig().img:
            msg = await pic_msg_format(msg, event)
            pic = await get_msg_pic(msg)
            await break_rift.finish(MessageSegment.image(pic))
        else:
            await break_rift.finish(msg, at_sender=True)
    else:
        user_id = user_info.user_id
        try:
            rift_info = read_rift_data(user_id)
        except:
            msg = '发生未知错误！'
            sql_message.do_work(user_id, 0)
            if XiuConfig().img:
                msg = await pic_msg_format(msg, event)
                pic = await get_msg_pic(msg)
                await break_rift.finish(MessageSegment.image(pic))
            else:
                await break_rift.finish(msg, at_sender=True)
        
        sql_message.do_work(user_id, 0)
        msg = f"已终止{rift_info['name']}秘境的探索！"
        if XiuConfig().img:
            msg = await pic_msg_format(msg, event)
            pic = await get_msg_pic(msg)
            await break_rift.finish(MessageSegment.image(pic))
        else:
            await break_rift.finish(msg, at_sender=True)

@set_group_rift.handle()
async def _(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    await data_check_conf(bot, event)
    mode = args.extract_plain_text().strip()
    group_id = event.group_id
    is_in_group = is_in_groups(event) #True在，False不在

    if mode == '开启':
        if is_in_group:
            msg = f'本群已开启群秘境，请勿重复开启!'
            if XiuConfig().img:
                msg = await pic_msg_format(msg, event)
                pic = await get_msg_pic(msg)
                await set_group_rift.finish(MessageSegment.image(pic))
            else:
                await set_group_rift.finish(msg, at_sender=True)
        else:
            config['open'].append(group_id)
            savef(config)
            msg = f'已开启本群秘境!'
            if XiuConfig().img:
                msg = await pic_msg_format(msg, event)
                pic = await get_msg_pic(msg)
                await set_group_rift.finish(MessageSegment.image(pic))
            else:
                await set_group_rift.finish(msg, at_sender=True)

    elif mode == '关闭':
        if is_in_group:
            config['open'].remove(group_id)
            savef(config)
            msg = f'已关闭本群秘境!'
            if XiuConfig().img:
                msg = await pic_msg_format(msg, event)
                pic = await get_msg_pic(msg)
                await set_group_rift.finish(MessageSegment.image(pic))
            else:
                await set_group_rift.finish(msg, at_sender=True)
        else:
            msg = f'本群未开启群秘境!'
            if XiuConfig().img:
                msg = await pic_msg_format(msg, event)
                pic = await get_msg_pic(msg)
                await set_group_rift.finish(MessageSegment.image(pic))
            else:
                await set_group_rift.finish(msg, at_sender=True)
    
    else:
        if XiuConfig().img:
            msg = await pic_msg_format(__rift_help__, event)
            pic = await get_msg_pic(msg)
            await set_group_rift.finish(MessageSegment.image(pic))
        else:
            await set_group_rift.finish(__rift_help__, at_sender=True)
        
def is_in_groups(event: GroupMessageEvent):
    return event.group_id in groups