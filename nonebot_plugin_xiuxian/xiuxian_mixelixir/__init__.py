from typing import Any, Tuple, Dict
from types import NoneType
from nonebot import on_regex, get_bot, on_command, require
from nonebot.params import RegexGroup, EventPlainText
from nonebot.adapters.onebot.v11 import (
    Bot,
    MessageEvent,
    PRIVATE_FRIEND,
    GROUP,
    GroupMessageEvent,
)
from nonebot.permission import SUPERUSER
from ..xiuxian2_handle import XiuxianDateManage
from datetime import datetime
from ..xiuxian_opertion import do_is_work
from ..cd_manager import add_cd, check_cd, cd_msg
from nonebot.log import logger
from ..utils import data_check_conf, check_user, send_forward_msg
from ..item_json import Items
from .mixelixirutil import get_mix_elixir_msg, tiaohe, check_mix
import os
import re

sql_message = XiuxianDateManage()  # sql类
items = Items()

mix_elixir = on_command("炼丹", priority=5, permission=GROUP)

@mix_elixir.handle()
async def _mix_elixir(bot: Bot, event: GroupMessageEvent):
    await data_check_conf(bot, event)
    isUser, user_info, msg = check_user(event)
    if not isUser:
        await mix_elixir.finish(msg, at_sender=True)
    user_id = user_info.user_id
    user_back = sql_message.get_back_msg(user_id)
    if user_back == None:
        msg = "道友的背包空空如也，无法炼丹"
        await mix_elixir.finish(msg, at_sender=True)
    yaocai_dict = {}
    for back in user_back:
        if back.goods_type == "药材":
            yaocai_dict[back.goods_id] = items.get_data_by_item_id(back.goods_id)
            yaocai_dict[back.goods_id]['num'] = back.goods_num
            continue
        else:
            continue
    if yaocai_dict == {}:
        msg = f"道友的背包内没有药材，无法炼丹！"
        await mix_elixir.finish(msg, at_sender=True)
    msg = "正在匹配背包中的丹方，请等待"
    await mix_elixir.send(msg, at_sender=True)
    finall_mix_elixir_msg = await get_mix_elixir_msg(yaocai_dict)
    if finall_mix_elixir_msg == {}:
        msg = "系统未检测到丹方，道友背包内的药材不满足！"
        await mix_elixir.finish(msg, at_sender=True)
    else:
        l_msg = []
        for k, v in finall_mix_elixir_msg.items():
            goods_info = items.get_data_by_item_id(v['id'])
            msg = f"名字：{goods_info['name']}\n"
            msg += f"效果：{goods_info['desc']}\n"
            msg += f"配方：{v['配方']['配方简写']}"
            l_msg.append(msg)
        await send_forward_msg(bot, event, '炼丹', bot.self_id, l_msg)
        msg = f"请道友输入配方公式 或者 取消，若想自己合成，请参考炼丹帮助"
        await mix_elixir.pause(prompt=msg)

@mix_elixir.handle()
async def _mix_elixir(bot: Bot, event: GroupMessageEvent, mode : str = EventPlainText()):
    await data_check_conf(bot, event)
    if mode == "取消":
        msg = "本次炼丹已取消！"
        await mix_elixir.finish(msg)
    user_id = event.user_id
    pattern = r"^主药([\u4e00-\u9fa5]+)?(\d+)?药引([\u4e00-\u9fa5]+)?(\d)?(辅药)?([\u4e00-\u9fa5]+)?(\d+)?丹炉([\u4e00-\u9fa5]+)?"
    matched = re.search(pattern, mode)
    if type(matched) == NoneType:
        msg = f"请参考转发内容里的配方输入正确的配方！"
        await mix_elixir.finish(msg)
    else:
        zhuyao_name = matched.groups()[0]
        check, zhuyao_goods_id = await check_yaocai_name_in_back(user_id, zhuyao_name)
        if not check:
            msg = f"请检查药材：{zhuyao_name} 是否在背包中！"
            await mix_elixir.finish(msg)
        zhuyao_num = int(matched.groups()[1])#数量一定会有
        yaoyin_name = matched.groups()[2]
        check, yaoyin_goods_id = await check_yaocai_name_in_back(user_id, yaoyin_name)
        if not check:
            msg = f"请检查药材：{yaoyin_name} 是否在背包中！"
            await mix_elixir.finish(msg)
        yaoyin_num = int(matched.groups()[3])#数量一定会有
        fuyao_flag = False
        if matched.groups()[4] != None:#匹配到辅药
            fuyao_name = matched.groups()[5]
            if fuyao_name == None:
                msg = f"请检查辅药是否输入！"
                await mix_elixir.finish(msg)
            else:
                check, fuyao_goods_id = await check_yaocai_name_in_back(user_id, fuyao_name)
                if not check:
                    msg = f"请检查药材：{fuyao_name} 是否在背包中！"
                    await mix_elixir.finish(msg)
            fuyao_num = matched.groups()[6]
            if fuyao_num == None:
                msg = f"请输入辅药的数量！"
                await mix_elixir.finish(msg)
            else:
                #辅药的数量
                fuyao_num = int(fuyao_num)
                fuyao_flag = True
        #检测通过
        zhuyao_info = Items().get_data_by_item_id(zhuyao_goods_id)
        yaoyin_info = Items().get_data_by_item_id(yaoyin_goods_id)
        if await tiaohe(zhuyao_info, zhuyao_num, yaoyin_info, yaoyin_num):#调和失败
            msg = f"冷热调和失败！小心炸炉哦~"
            await mix_elixir.finish(msg)
        else:
            elixir_config = {}
            elixir_config[str(zhuyao_info['主药']['type'])] = zhuyao_info['主药']['power'] * zhuyao_num
            if fuyao_flag:#有辅药
                fuyao_info = Items().get_data_by_item_id(fuyao_goods_id)
                elixir_config[str(fuyao_info['辅药']['type'])] = zhuyao_info['辅药']['power'] * fuyao_num
                is_mix, id = await check_mix(elixir_config)
                if is_mix:
                    goods_info = Items().get_data_by_item_id(id)
                    msg = f"恭喜道友成功炼成丹药：{goods_info['name']}"
                    await mix_elixir.finish(msg)
                else:
                    msg = f"没有炼成丹药哦~就不扣你药材啦"
                    await mix_elixir.finish(msg)
            else:#没辅药
                is_mix, id = await check_mix(elixir_config)
                if is_mix:
                    goods_info = Items().get_data_by_item_id(id)
                    msg = f"恭喜道友成功炼成丹药：{goods_info['name']}"
                    await mix_elixir.finish(msg)
                else:
                    msg = f"没有炼成丹药哦~就不扣你药材啦"
                    await mix_elixir.finish(msg)
    
async def check_yaocai_name_in_back(user_id, yaocai_name):
    flag = False
    goods_id = 0
    user_back = sql_message.get_back_msg(user_id)
    for back in user_back:
        if back.goods_type == '药材':
            if Items().get_data_by_item_id(back.goods_id)['name'] == yaocai_name:
                flag = True
                goods_id = back.goods_id
                break
            else:
                continue
        else:
            continue
    return flag, goods_id