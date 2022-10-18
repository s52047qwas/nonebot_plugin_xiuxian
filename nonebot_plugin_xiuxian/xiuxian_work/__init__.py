from typing import Any, Tuple, Dict
from nonebot import on_regex, require
from nonebot.params import RegexGroup
from nonebot.adapters.onebot.v11 import (
    Bot,
    MessageEvent,
    PRIVATE_FRIEND,
    GROUP,
    GroupMessageEvent,
)
from ..xiuxian2_handle import XiuxianDateManage
from .work_handle import workhandle
from datetime import datetime
from ..xiuxian_opertion import do_is_work
from ..cd_manager import add_cd, check_cd, cd_msg
from nonebot.log import logger
from .reward_data_source import PLAYERSDATA
import os

# 定时任务
resetrefreshnum = require("nonebot_plugin_apscheduler").scheduler


work = {}  # 悬赏令信息记录
refreshnum : Dict[str, int] = {} #用户悬赏令刷新次数记录
sql_message = XiuxianDateManage()  # sql类

# 重置悬赏令刷新次数
@resetrefreshnum.scheduled_job("cron",hour=0,minute=0)
async def _():
    global refreshnum
    refreshnum = {}
    logger.info("用户悬赏令刷新次数重置成功")

do_work = on_regex(
    r"(江湖好手|练气境|筑基境|结丹境|元婴境|化神境|炼虚境|合体境|大乘境|渡劫境)?(悬赏令)+(接取|结算|刷新|终止)?(\d+)?",
    priority=5,
    permission=PRIVATE_FRIEND | GROUP,
)


class MsgError(ValueError):
    pass

@do_work.handle()
async def _(bot: Bot, event: GroupMessageEvent, args: Tuple[Any, ...] = RegexGroup()):
    level = args[0] #境界
    mode = args[2] #接取、结算、刷新、终止
    num = args[3] #1、2、3
    
    global work
    work_list = []
    user_id = event.get_user_id()
    
    if sql_message.get_user_message(user_id) is None:
        await do_work.finish("修仙界没有道友的信息，请输入【我要修仙】加入！")
        
    user_cd_message = sql_message.get_user_cd(user_id)
    userinfo = sql_message.get_user_message(user_id)

    if not os.path.exists(PLAYERSDATA / str(user_id) / "workinfo.json") and user_cd_message.type == 2:
        sql_message.do_work(user_id, 0)
        await do_work.finish(f"悬赏令已更新，已重置道友的状态！")

    userlevel = ''
    if level == None:
        if userinfo.level == '江湖好手':
            userlevel = '江湖好手'
        else:
            userlevel = userinfo.level[:3]#取境界前3位，补全初期、中期、圆满任务可不取
    else:
        if level == '江湖好手':
            userlevel = '江湖好手'
        else:
            userlevel = level[:3]#取境界前3位，补全初期、中期、圆满任务可不取
    
    if mode != None:#有mode
        if mode == '接取':
            if user_cd_message.type == 1:
                await do_work.finish("道友现在在闭关呢，小心走火入魔！", at_sender=True)
                
            if num == None or str(num) not in ['1', '2', '3']:
                await do_work.finish('请输入正确的任务序号')
                
            try:
                if work[user_id]:
                    work_num = int(num)  ##任务序号
                try:
                    get_work = work[user_id].world[work_num - 1]
                    sql_message.do_work(user_id, 2, get_work[0])
                    del work[user_id]
                    await do_work.finish(f"接取任务【{get_work[0]}】成功")
                except IndexError:
                    await do_work.finish("没有这样的任务")

            except KeyError:
                await do_work.finish("没有查到你的悬赏令信息呢！")
                
        if mode == '结算':
            if user_cd_message is None or user_cd_message.type == 0:
                await do_work.finish("没有查到你的悬赏令信息呢！输入【悬赏令】获取！")

            elif user_cd_message.type == 1:
                await do_work.finish("道友现在在闭关呢，小心走火入魔！", at_sender=True)

            elif user_cd_message.type == 2:
                work_time = datetime.strptime(
                    user_cd_message.create_time, "%Y-%m-%d %H:%M:%S.%f"
                )
                exp_time = (datetime.now() - work_time).seconds // 60  # 时长计算
                time2 = workhandle().do_work(
                    # key=1, name=user_cd_message.scheduled_time  修改点
                    key=1, name=user_cd_message.scheduled_time, level=userlevel, exp=userinfo.exp, user_id=userinfo.user_id
                )
                if exp_time < time2:
                    await do_work.finish(
                        f"进行中的悬赏令【{user_cd_message.scheduled_time}】，预计{time2 - exp_time}分钟后可结束",
                        at_sender=True,
                    )
                else:
                    work_sf = workhandle().do_work(2, work_list= user_cd_message.scheduled_time, level=userlevel, exp=userinfo.exp, user_id=userinfo.user_id)
                    if work_sf[3]: #大成功
                        sql_message.update_ls(user_id, work_sf[1] * 2, 1)
                        sql_message.do_work(user_id, 0)
                        #todo 战利品结算sql
                        await do_work.finish(f"悬赏令结算，{work_sf[0]},最终获得报酬{work_sf[1] * 2}枚灵石,额外获得战利品{work_sf[2]}!")
                        
                    else: #普通结算
                        sql_message.update_ls(user_id, work_sf[1], 1)
                        sql_message.do_work(user_id, 0)
                        await do_work.finish(f"悬赏令结算，{work_sf[0]},最终获得报酬{work_sf[1]}枚灵石！")
                        
        if mode == '刷新':
            if user_cd_message.type == 1:
                await do_work.finish("道友现在在闭关呢，小心走火入魔！", at_sender=True)
                
            elif user_cd_message.type == 2:
                work_time = datetime.strptime(
                user_cd_message.create_time, "%Y-%m-%d %H:%M:%S.%f"
            )
                exp_time = (datetime.now() - work_time).seconds // 60  # 闭关时长计算
                time2 = workhandle().do_work(key=1, name=user_cd_message.scheduled_time, user_id=userinfo.user_id)
                if exp_time < time2:
                    await do_work.finish(
                        f"进行中的悬赏令【{user_cd_message.scheduled_time}】，预计{time2 - exp_time}分钟后可结束",
                        at_sender=True,
                    )
                else:
                    await do_work.finish(
                        f"进行中的悬赏令【{user_cd_message.scheduled_time}】，已结束，请输入【悬赏令结算】结算任务信息！",
                        at_sender=True,
                    )
                    
            lscost = 100
            if int(userinfo.stone) < lscost:    
                await do_work.finish(f"道友的灵石不足以刷新，每次刷新消耗灵石：{lscost}枚")
                
            try:
                usernums = refreshnum[user_id]
            except KeyError:
                usernums = 0
                
            count = 5
            freenum = count - usernums
            if freenum < 0:
                freenum = 0
             
            work_msg = workhandle().do_work(0, level=userlevel, exp=userinfo.exp, user_id=userinfo.user_id)
            n = 1
            work_msg_f = f"""     ✨道友的个人悬赏令✨"""
            for i in work_msg:
                work_list.append([i[0], i[3]])
                work_msg_f += f"""
    {n}、{i[0]},完成机率{i[1]},基础报酬{i[2]}灵石,预计需{i[3]}分钟,可能获取额外物品：{i[4]}!"""
                n += 1
            work_msg_f += f"\n(悬赏令每小时更新一次,悬赏令每日免费刷新次数：{count}，超过{count}次后，每次刷新消耗{lscost}灵石,今日可免费刷新次数：{freenum}次)"
            work[user_id] = do_is_work(user_id)
            work[user_id].time = datetime.now()
            work[user_id].msg = work_msg_f
            work[user_id].world = work_list
            
            refreshnum[user_id] = usernums + 1
            sql_message.update_ls(user_id, lscost, 2)
            
            await do_work.finish(work_msg_f)
        
        if mode == '终止':
            if user_cd_message.type == 1:
                await do_work.finish("道友现在在闭关呢，终止什么！", at_sender=True)
            elif user_cd_message is None or user_cd_message.type == 0:
                await do_work.finish("没有查到你的悬赏令信息呢！输入【悬赏令】获取！", at_sender=True)
            elif user_cd_message.type == 2:
                exps = int(userinfo.exp * 0.001)
                sql_message.update_j_exp(user_id, exps)
                sql_message.do_work(user_id, 0)
                await do_work.finish(f"道友不讲诚信，被打了一顿修为减少{exps},悬赏令已终止！", at_sender=True)
                
            
            
    else:#没有mode，判断悬赏令接取逻辑
        try:
            if work[user_id]:
                if (datetime.now() - work[user_id].time).seconds // 60 >= 60:
                    work_msg = workhandle().do_work(0, level=userlevel, exp=userinfo.exp, user_id=userinfo.user_id)

                    n = 1
                    work_msg_f = f"""     ✨道友的个人悬赏令✨"""
                    for i in work_msg:
                        work_list.append([i[0], i[3]])
                        work_msg_f += f"""
{n}、{i[0]},完成机率{i[1]},基础报酬{i[2]}灵石,预计需{i[3]}分钟,可能获取额外{i[4]}!"""
                        n += 1
                    work_msg_f += "\n(悬赏令每小时更新一次)"
                    work[user_id].msg = work_msg_f
                    work[user_id].world = work_list
                    await do_work.finish(work[user_id].msg)
                else:
                    await do_work.finish(work[user_id].msg)
        except KeyError:
            pass
        
        if user_cd_message is None or user_cd_message.type == 0:
            work_msg = workhandle().do_work(0, level=userlevel, exp=userinfo.exp, user_id=userinfo.user_id)
            n = 1
            work_msg_f = f"""     ✨道友的个人悬赏令✨"""
            for i in work_msg:
                work_list.append([i[0], i[3]])
                work_msg_f += f"""
    {n}、{i[0]},完成机率{i[1]},基础报酬{i[2]}灵石,预计需{i[3]}分钟,可能获取额外物品：{i[4]}!"""
                n += 1
            work_msg_f += f"\n(悬赏令每小时更新一次)"
            work[user_id] = do_is_work(user_id)
            work[user_id].time = datetime.now()
            work[user_id].msg = work_msg_f
            work[user_id].world = work_list
            await do_work.finish(work_msg_f)
        
        elif user_cd_message.type == 1:
            await do_work.finish("已经在闭关中，请输入【出关】结束后才能获取悬赏令！", at_sender=True)
            
        elif user_cd_message.type == 2:
            work_time = datetime.strptime(
                user_cd_message.create_time, "%Y-%m-%d %H:%M:%S.%f"
            )
            exp_time = (datetime.now() - work_time).seconds // 60  # 闭关时长计算
            time2 = workhandle().do_work(key=1, name=user_cd_message.scheduled_time, user_id=userinfo.user_id)
            if exp_time < time2:
                await do_work.finish(
                    f"进行中的悬赏令【{user_cd_message.scheduled_time}】，预计{time2 - exp_time}分钟后可结束",
                    at_sender=True,
                )
            else:
                await do_work.finish(
                    f"进行中的悬赏令【{user_cd_message.scheduled_time}】，已结束，请输入【悬赏令结算】结算任务信息！",
                    at_sender=True,
                )