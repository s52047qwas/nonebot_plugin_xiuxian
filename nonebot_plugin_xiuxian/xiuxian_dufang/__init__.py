from nonebot import on_regex
from nonebot.adapters.onebot.v11 import (
    PRIVATE_FRIEND,
    Bot,
    Event,
    GROUP,
    GROUP_ADMIN,
    GROUP_OWNER,
    Message,
    MessageEvent,
    GroupMessageEvent,
    MessageSegment,
)
import re
from re import I
from ..xiuxian2_handle import XiuxianDateManage
from datetime import datetime
import random
from ..xiuxian_opertion import gamebingo
from nonebot.params import State
from nonebot.typing import T_State

dufang = on_regex(
    r"(金银阁)\s?(\d+)\s?([大|小|猜])?\s?(\d+)?",
    flags=I,
    permission=PRIVATE_FRIEND | GROUP,
)

race = {}  # 押注信息记录
sql_message = XiuxianDateManage()  # sql类

@dufang.handle()
async def _(bot: Bot, event: MessageEvent, state: T_State = State()):
    
    global race

    user_id = event.get_user_id()
    group_id = await get_group_id(event.get_session_id())
    user_message = sql_message.get_user_message(user_id)
    
    try:
        if race[group_id].start == 1 and race[group_id].player[0] != user_id:
            await dufang.finish(f"已有其他道友进行中")
            
    except KeyError:
        pass
    
    args = list(state["_matched_groups"])
    
    if args[2] == None:
        await dufang.finish(f"请输入正确的指令，例如金银阁10大、金银阁10猜3")
    
    price = args[1]#300
    mode = args[2]#大、小、猜
    mode_num = 0
    if mode == '猜':
        mode_num = args[3]#猜的数值
    
    
    race[group_id] = gamebingo()
    race[group_id].start_change(1)
    race[group_id].add_player(user_id)
    race[group_id].time = datetime.now()
    
    price_num = int(price)
    if int(user_message.stone) < int(price_num):
        await dufang.finish("道友的金额不足，请重新输入！")
    
    race[group_id].add_price(int(price_num))
    value = random.randint(1, 6)
    msg = Message("[CQ:dice,value={}]".format(value))
    
    if value >= 4 and str(mode) == "大":
        del race[group_id]
        sql_message.update_ls(user_id, price_num, 1)
        await dufang.send(msg)
        await dufang.finish(
            "最终结果为{}，你猜对了，收获灵石{}块".format(value, price_num), at_sender=True
        )
    elif value <= 3 and str(mode) == "小":
        del race[group_id]
        sql_message.update_ls(user_id, price_num, 1)
        await dufang.send(msg)
        await dufang.finish(
            "最终结果为{}，你猜对了，收获灵石{}块".format(value, price_num), at_sender=True
        )
    elif str(value) == str(mode_num) and str(mode) == "猜":
        del race[group_id]
        sql_message.update_ls(user_id, price_num * 6, 1)
        await dufang.send(msg)
        await dufang.finish(
            "最终结果为{}，你猜对了，收获灵石{}块".format(value, price_num * 6), at_sender=True
        )
    else:
        del race[group_id]
        sql_message.update_ls(user_id, price_num, 2)
        await dufang.send(msg)
        await dufang.finish(
            "最终结果为{}，你猜错了，损失灵石{}块".format(value, price_num), at_sender=True
        )   

async def get_group_id(session_id):
    """获取group_id"""
    res = re.findall("_(.*)_", session_id)
    group_id = res[0]
    return group_id