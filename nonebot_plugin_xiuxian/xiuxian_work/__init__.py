from typing import Any, Tuple, Dict
from nonebot import on_regex, require, on_command
from nonebot.params import RegexGroup, CommandArg

from nonebot.adapters.onebot.v11 import (
    Bot,
    MessageEvent,
    PRIVATE_FRIEND,
    GROUP,
    GroupMessageEvent,
    MessageSegment,
    Message
)
from ..xiuxian2_handle import XiuxianDateManage
from .work_handle import workhandle
from datetime import datetime
from ..xiuxian_opertion import do_is_work
from ..cd_manager import add_cd, check_cd, cd_msg
from ..utils import data_check_conf, check_user, send_forward_msg, check_user_type, send_forward_msg_list, get_msg_pic, pic_msg_format
from nonebot.log import logger
from .reward_data_source import PLAYERSDATA
import os
from ..item_json import Items
from ..xiuxian_config import USERRANK, XiuConfig
from ..exp_util import get_exp_rate, user_get_exp_max
# 定时任务
resetrefreshnum = require("nonebot_plugin_apscheduler").scheduler


work = {}  # 悬赏令信息记录
refreshnum : Dict[str, int] = {} #用户悬赏令刷新次数记录
sql_message = XiuxianDateManage()  # sql类
items = Items()
lscost = 3000#刷新灵石消耗
count = 5#免费次数


# 重置悬赏令刷新次数
@resetrefreshnum.scheduled_job("cron",hour=0,minute=0)
async def _():
    global refreshnum
    refreshnum = {}
    logger.info("用户悬赏令刷新次数重置成功")

do_work = on_regex(
    r"^(江湖好手|练气境|筑基境|结丹境|元婴境|化神境|炼虚境|合体境|大乘境|渡劫境)?(悬赏令)+(刷新|终止|结算|接取|帮助)?(\d+)?",
    priority=5,
    permission=PRIVATE_FRIEND | GROUP,
)
__work_help__ = f"""
悬赏令帮助信息:
指令：
1、对应境界+悬赏令：获取对应等级的悬赏令，不加境界默认当前境界
2、对应境界+悬赏令刷新：刷新当前悬赏令，不加境界默认当前境界，每次刷新需要{lscost}灵石，每日免费{count}次
境界可选：江湖好手、练气境、筑基境、结丹境、元婴境、化神境、炼虚境、合体境、大乘境、渡劫境
3、悬赏令终止：终止当前悬赏令任务
4、悬赏令结算：结算悬赏奖励
5、悬赏令接取+编号：接取对应的悬赏令
注：执行悬赏令期间，会根据时间获取一定修为
""".strip()
        
@do_work.handle()
async def _(bot: Bot, event: GroupMessageEvent, args: Tuple[Any, ...] = RegexGroup()):
    await data_check_conf(bot, event)
    isUser, user_info, msg = check_user(event)
    if not isUser:
        if XiuConfig().img:
            msg = await pic_msg_format(msg, event)
            pic = await get_msg_pic(msg)
            await do_work.finish(MessageSegment.image(pic))
        else:
            await do_work.finish(msg, at_sender=True)
    user_id = user_info.user_id
    user_cd_message = sql_message.get_user_cd(user_id)
    if not os.path.exists(PLAYERSDATA / str(user_id) / "workinfo.json") and user_cd_message.type == 2:
        sql_message.do_work(user_id, 0)
        msg = f"悬赏令已更新，已重置道友的状态！"
        if XiuConfig().img:
            msg = await pic_msg_format(msg, event)
            pic = await get_msg_pic(msg)
            await do_work.finish(MessageSegment.image(pic))
        else:
            await do_work.finish(msg, at_sender=True)
    work_level = args[0] #境界
    mode = args[2]#刷新、终止、结算、接取
    if work_level == None:
        user_level = user_info.level
        if USERRANK[user_info.level] <= 22:
            msg = f"道友的境界过高，悬赏令已经不能满足道友了，请尝试获取低境界的悬赏令"
            if XiuConfig().img:
                msg = await pic_msg_format(msg, event)
                pic = await get_msg_pic(msg)
                await do_work.finish(MessageSegment.image(pic))
            else:
                await do_work.finish(msg, at_sender=True)
    else:
        user_level = work_level
    work_list = []
    if mode == None:#接取逻辑
        try:
            if work[user_id]:
                if (datetime.now() - work[user_id].time).seconds // 60 >= 60:
                    work_msg = workhandle().do_work(0, level=user_level, exp=user_info.exp, user_id=user_info.user_id)

                    n = 1
                    work_msg_f = f"☆------道友的个人悬赏令------☆\n"
                    for i in work_msg:
                        work_list.append([i[0], i[3]])
                        work_msg_f += f"{n}、{get_work_msg(i)}"
                        n += 1
                    work_msg_f += "(悬赏令每小时更新一次)"
                    work[user_id].msg = work_msg_f
                    work[user_id].world = work_list
                    work[user_id].time = datetime.now()
                    msg = work[user_id].msg
                    if XiuConfig().img:
                        msg = await pic_msg_format(msg, event)
                        pic = await get_msg_pic(msg)
                        await do_work.finish(MessageSegment.image(pic))
                    else:
                        await do_work.finish(msg, at_sender=True)
                else:
                    msg = work[user_id].msg
                    if XiuConfig().img:
                        msg = await pic_msg_format(msg, event)
                        pic = await get_msg_pic(msg)
                        await do_work.finish(MessageSegment.image(pic))
                    else:
                        await do_work.finish(msg, at_sender=True)
        except KeyError:
            pass
        
        
        if user_cd_message is None or user_cd_message.type == 0:
            work_msg = workhandle().do_work(0, level=user_level, exp=user_info.exp, user_id=user_info.user_id)
            n = 1
            work_msg_f = f"☆------道友的个人悬赏令------☆\n"
            for i in work_msg:
                work_list.append([i[0], i[3]])
                work_msg_f += f"{n}、{get_work_msg(i)}"
                n += 1
            work_msg_f += f"(悬赏令每小时更新一次)"
            work[user_id] = do_is_work(user_id)
            work[user_id].time = datetime.now()
            work[user_id].msg = work_msg_f
            work[user_id].world = work_list
            msg = work_msg_f
            if XiuConfig().img:
                msg = await pic_msg_format(msg, event)
                pic = await get_msg_pic(msg)
                await do_work.finish(MessageSegment.image(pic))
            else:
                await do_work.finish(msg, at_sender=True)
        
        elif user_cd_message.type == 1:
            msg = "已经在闭关中，请输入【出关】结束后才能获取悬赏令！"
            if XiuConfig().img:
                msg = await pic_msg_format(msg, event)
                pic = await get_msg_pic(msg)
                await do_work.finish(MessageSegment.image(pic))
            else:
                await do_work.finish(msg, at_sender=True)
            
        elif user_cd_message.type == 2:
            work_time = datetime.strptime(
                user_cd_message.create_time, "%Y-%m-%d %H:%M:%S.%f"
            )
            exp_time = (datetime.now() - work_time).seconds // 60  # 闭关时长计算
            time2 = workhandle().do_work(key=1, name=user_cd_message.scheduled_time, user_id=user_info.user_id)
            if exp_time < time2:
                msg = f"进行中的悬赏令【{user_cd_message.scheduled_time}】，预计{time2 - exp_time}分钟后可结束"
                if XiuConfig().img:
                    msg = await pic_msg_format(msg, event)
                    pic = await get_msg_pic(msg)
                    await do_work.finish(MessageSegment.image(pic))
                else:
                    await do_work.finish(msg, at_sender=True)
            else:
                msg = f"进行中的悬赏令【{user_cd_message.scheduled_time}】，已结束，请输入【悬赏令结算】结算任务信息！"
                if XiuConfig().img:
                    msg = await pic_msg_format(msg, event)
                    pic = await get_msg_pic(msg)
                    await do_work.finish(MessageSegment.image(pic))
                else:
                    await do_work.finish(msg, at_sender=True)
                    
        elif user_cd_message.type == 3:
            msg = f"道友现在正在秘境中，分身乏术！"
            if XiuConfig().img:
                msg = await pic_msg_format(msg, event)
                pic = await get_msg_pic(msg)
                await do_work.finish(MessageSegment.image(pic))
            else:
                await do_work.finish(msg, at_sender=True)

    elif mode == "刷新":#刷新逻辑
        if user_cd_message.type == 2:
            work_time = datetime.strptime(
                user_cd_message.create_time, "%Y-%m-%d %H:%M:%S.%f"
            )
            exp_time = (datetime.now() - work_time).seconds // 60
            time2 = workhandle().do_work(key=1, name=user_cd_message.scheduled_time, user_id=user_info.user_id)
            if exp_time < time2:
                msg = f"进行中的悬赏令【{user_cd_message.scheduled_time}】，预计{time2 - exp_time}分钟后可结束"
                if XiuConfig().img:
                    msg = await pic_msg_format(msg, event)
                    pic = await get_msg_pic(msg)
                    await do_work.finish(MessageSegment.image(pic))
                else:
                    await do_work.finish(msg, at_sender=True)
            else:
                msg = f"进行中的悬赏令【{user_cd_message.scheduled_time}】，已结束，请输入【悬赏令结算】结算任务信息！"
                if XiuConfig().img:
                    msg = await pic_msg_format(msg, event)
                    pic = await get_msg_pic(msg)
                    await do_work.finish(MessageSegment.image(pic))
                else:
                    await do_work.finish(msg, at_sender=True)
        try:
            work[user_id]
        except KeyError:
            msg = f"道友还没有获取过悬赏令！"
            if XiuConfig().img:
                msg = await pic_msg_format(msg, event)
                pic = await get_msg_pic(msg)
                await do_work.finish(MessageSegment.image(pic))
            else:
                await do_work.finish(msg, at_sender=True)
            
        try:
            usernums = refreshnum[user_id]
        except KeyError:
            usernums = 0
        cost_bool = False
        freenum = count - usernums - 1
        if freenum < 0:
            freenum = 0
            cost_bool = True
            if int(user_info.stone) < lscost:
                msg = f"道友的灵石不足以刷新，每次刷新消耗灵石：{lscost}枚"
                if XiuConfig().img:
                    msg = await pic_msg_format(msg, event)
                    pic = await get_msg_pic(msg)
                    await do_work.finish(MessageSegment.image(pic))
                else:
                    await do_work.finish(msg, at_sender=True)
            
        work_msg = workhandle().do_work(0, level=user_level, exp=user_info.exp, user_id=user_id)
        n = 1
        work_list = []
        work_msg_f = f"☆------道友的个人悬赏令------☆\n"
        for i in work_msg:
            work_list.append([i[0], i[3]])
            work_msg_f += f"{n}、{get_work_msg(i)}"
            n += 1
        work_msg_f += f"(悬赏令每小时更新一次,悬赏令每日免费刷新次数：{count}，超过{count}次后，每次刷新消耗{lscost}灵石,今日可免费刷新次数：{freenum}次)"
        work[user_id] = do_is_work(user_id)
        work[user_id].time = datetime.now()
        work[user_id].msg = work_msg_f
        work[user_id].world = work_list
        
        refreshnum[user_id] = usernums + 1
        if cost_bool:
            sql_message.update_ls(user_id, lscost, 2)
        msg = work_msg_f
        if XiuConfig().img:
            msg = await pic_msg_format(msg, event)
            pic = await get_msg_pic(msg)
            await do_work.finish(MessageSegment.image(pic))
        else:
            await do_work.finish(msg, at_sender=True)

    elif mode == "终止":
        is_type, msg = check_user_type(user_id, 2)#需要在悬赏令中的用户
        if is_type:
            exps = int(user_info.exp * 0.001)
            sql_message.update_j_exp(user_id, exps)
            sql_message.do_work(user_id, 0)
            msg = f"道友不讲诚信，被打了一顿修为减少{exps},悬赏令已终止！"
            if XiuConfig().img:
                msg = await pic_msg_format(msg, event)
                pic = await get_msg_pic(msg)
                await do_work.finish(MessageSegment.image(pic))
            else:
                await do_work.finish(msg, at_sender=True)
        else:
            if XiuConfig().img:
                msg = await pic_msg_format(msg, event)
                pic = await get_msg_pic(msg)
                await do_work.finish(MessageSegment.image(pic))
            else:
                await do_work.finish(msg, at_sender=True)
    
    elif mode == "结算":
        is_type, msg = check_user_type(user_id, 2)#需要在悬赏令中的用户
        if is_type:
            user_cd_message = sql_message.get_user_cd(user_id)
            work_time = datetime.strptime(
                user_cd_message.create_time, "%Y-%m-%d %H:%M:%S.%f"
            )
            exp_time = (datetime.now() - work_time).seconds // 60  # 时长计算
            time2 = workhandle().do_work(
                # key=1, name=user_cd_message.scheduled_time  修改点
                key=1, name=user_cd_message.scheduled_time, level=user_info.level, exp=user_info.exp, user_id=user_info.user_id
            )
            if exp_time < time2:
                msg = f"进行中的悬赏令【{user_cd_message.scheduled_time}】，预计{time2 - exp_time}分钟后可结束"
                if XiuConfig().img:
                    msg = await pic_msg_format(msg, event)
                    pic = await get_msg_pic(msg)
                    await do_work.finish(MessageSegment.image(pic))
                else:
                    await do_work.finish(msg, at_sender=True)
            else:
                msg, give_stone, s_o_f, item_id, big_suc = workhandle().do_work(2, work_list= user_cd_message.scheduled_time,
                                            level=user_info.level, exp=user_info.exp, user_id=user_info.user_id)
                item_flag = False
                exp_rate = get_exp_rate(user_info.user_id, False)
                give_exp = int(exp_rate * exp_time * 0.5)
                exp_max = user_get_exp_max(user_info.user_id)
                if give_exp > exp_max:
                    give_exp = exp_max
                if item_id != 0:
                    item_flag = True
                    item_info = items.get_data_by_item_id(item_id)
                    item_msg = f"{item_info['level']}：{item_info['name']}"
                if big_suc: #大成功
                    give_exp = int(give_exp * 1.5)
                    sql_message.update_ls(user_id, give_stone * 2, 1)
                    sql_message.update_exp(user_id,give_exp)
                    sql_message.update_power2(user_id)  # 更新战力
                    sql_message.do_work(user_id, 0)
                    msg = f"悬赏令结算，{msg}获得报酬{give_stone * 2}枚灵石，获得修为{give_exp}"
                    #todo 战利品结算sql
                    if item_flag:
                        sql_message.send_back(user_id, item_id, item_info['name'], item_info['type'], 1)
                        msg += f"，额外获得奖励：{item_msg}！"
                    else:
                        msg += "！"
                    if XiuConfig().img:
                        msg = await pic_msg_format(msg, event)
                        pic = await get_msg_pic(msg)
                        await do_work.finish(MessageSegment.image(pic))
                    else:
                        await do_work.finish(msg, at_sender=True)

                    
                else: 
                    sql_message.update_ls(user_id, give_stone, 1)
                    sql_message.update_exp(user_id, give_exp)
                    sql_message.update_power2(user_id)  # 更新战力

                    sql_message.do_work(user_id, 0)
                    msg = f"悬赏令结算，{msg}获得报酬{give_stone}枚灵石，获得修为{give_exp}"
                    if s_o_f:#普通成功
                        if item_flag:
                            sql_message.send_back(user_id, item_id, item_info['name'], item_info['type'], 1)
                            msg += f"，额外获得奖励：{item_msg}！"
                        else:
                            msg += "！"
                        if XiuConfig().img:
                            msg = await pic_msg_format(msg, event)
                            pic = await get_msg_pic(msg)
                            await do_work.finish(MessageSegment.image(pic))
                        else:
                            await do_work.finish(msg, at_sender=True)
                    else:#失败
                        msg += "！"
                        if XiuConfig().img:
                            msg = await pic_msg_format(msg, event)
                            pic = await get_msg_pic(msg)
                            await do_work.finish(MessageSegment.image(pic))
                        else:
                            await do_work.finish(msg, at_sender=True)
                        
        else:
            if XiuConfig().img:
                msg = await pic_msg_format(msg, event)
                pic = await get_msg_pic(msg)
                await do_work.finish(MessageSegment.image(pic))
            else:
                await do_work.finish(msg, at_sender=True)
            
    elif mode == "接取":
        num = args[3]
        is_type, msg = check_user_type(user_id, 0)#需要无状态的用户
        if is_type:#接取逻辑
            if num == None or str(num) not in ['1', '2', '3']:
                msg = '请输入正确的任务序号'
                if XiuConfig().img:
                    msg = await pic_msg_format(msg, event)
                    pic = await get_msg_pic(msg)
                    await do_work.finish(MessageSegment.image(pic))
                else:
                    await do_work.finish(msg, at_sender=True)
            
            try:
                if work[user_id]:
                    work_num = int(num)  ##任务序号
                try:
                    get_work = work[user_id].world[work_num - 1]
                    sql_message.do_work(user_id, 2, get_work[0])
                    del work[user_id]
                    msg = f"接取任务【{get_work[0]}】成功"
                    if XiuConfig().img:
                        msg = await pic_msg_format(msg, event)
                        pic = await get_msg_pic(msg)
                        await do_work.finish(MessageSegment.image(pic))
                    else:
                        await do_work.finish(msg, at_sender=True)
                except IndexError:
                    msg = "没有这样的任务"
                    if XiuConfig().img:
                        msg = await pic_msg_format(msg, event)
                        pic = await get_msg_pic(msg)
                        await do_work.finish(MessageSegment.image(pic))
                    else:
                        await do_work.finish(msg, at_sender=True)

            except KeyError:
                msg = "没有查到你的悬赏令信息呢！"
                if XiuConfig().img:
                    msg = await pic_msg_format(msg, event)
                    pic = await get_msg_pic(msg)
                    await do_work.finish(MessageSegment.image(pic))
                else:
                    await do_work.finish(msg, at_sender=True)
                        
        else:
            if XiuConfig().img:
                msg = await pic_msg_format(msg, event)
                pic = await get_msg_pic(msg)
                await do_work.finish(MessageSegment.image(pic))
            else:
                await do_work.finish(msg, at_sender=True)
    elif mode == "帮助":
        msg = __work_help__
        if XiuConfig().img:
            msg = await pic_msg_format(msg, event)
            pic = await get_msg_pic(msg)
            await do_work.finish(MessageSegment.image(pic))
        else:
            await do_work.finish(msg, at_sender=True)
            
def get_work_msg(work):
    msg = f"{work[0]},完成机率{work[1]},基础报酬{work[2]}灵石,预计需{work[3]}分钟{work[4]}\n"
    return msg