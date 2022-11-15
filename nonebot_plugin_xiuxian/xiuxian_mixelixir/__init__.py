from typing import Any, Tuple, Dict
from nonebot import on_regex, get_bot, on_command, require
from nonebot.params import RegexGroup, EventPlainText, CommandArg
from nonebot.adapters.onebot.v11 import (
    Bot,
    MessageEvent,
    PRIVATE_FRIEND,
    GROUP,
    Message,
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
from ..read_buff import get_player_info, save_player_info
from ..xiuxian_config import USERRANK
from datetime import datetime
import random
import re

sql_message = XiuxianDateManage()  # sql类
items = Items()

mix_elixir = on_command("炼丹", priority=5, permission=GROUP)
elixir_help = on_command("炼丹帮助", priority=5, permission=GROUP)
mix_elixir_help = on_command("炼丹配方帮助", priority=5, permission=GROUP)
yaocai_get = on_command("灵田收取", aliases={"灵田结算"}, priority=5, permission=GROUP)
__elixir_help__ = f"""
炼丹帮助信息:
指令：
1、炼丹：会检测背包内的药材，自动生成配方
2、炼丹帮助：获取本帮助信息
3、炼丹配方帮助：获取炼丹配方帮助
4、灵田收取、灵田结算：收取洞天福地里灵田的药材
"""

__mix_elixir_help__ = f"""
炼丹配方信息
1、炼丹需要主药、药引、辅药
2、主药和药引控制炼丹时的冷热调和，冷热失和则炼不出丹药
3、草药的类型控制产出丹药的类型
"""

@yaocai_get.handle()
async def _(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    """灵田收取"""
    await data_check_conf(bot, event)
    isUser, user_info, msg = check_user(event)
    if not isUser:
        await yaocai_get.finish(msg, at_sender=True)
    user_id = user_info.user_id
    if int(user_info.blessed_spot_flag) == 0:
        msg = f"道友还没有洞天福地呢，请发送洞天福地购买吧~"
        await yaocai_get.finish(msg, at_sender=True)
    mix_elixir_info = get_player_info(user_id, "mix_elixir_info")
    GETCONFIG = {
        "time_cost":48,#单位小时
        "加速基数":0.05
    }
    last_time = mix_elixir_info['收取时间']
    if last_time != 0:
        nowtime = datetime.now().strftime('%Y-%m-%d %H:%M:%S') #str
        timedeff = round((datetime.strptime(nowtime, '%Y-%m-%d %H:%M:%S') - datetime.strptime(last_time, '%Y-%m-%d %H:%M:%S')).total_seconds() / 3600, 2)
        if timedeff >= round(GETCONFIG['time_cost'] * (1 - (GETCONFIG['加速基数'] * mix_elixir_info['药材速度'])), 2) :
            yaocai_id_list = items.get_random_id_list_by_rank_and_item_type(USERRANK[user_info.level], ['药材'])
            num = mix_elixir_info['灵田数量']
            i = 1
            give_dict = {}
            while i <= num:
                id = random.choice(yaocai_id_list)
                try:
                    give_dict[id] += 1
                    i += 1
                except:
                    give_dict[id] = 1
                    i += 1
            for k, v in give_dict.items():
                goods_info = items.get_data_by_item_id(k)
                msg += f"道友成功收获药材：{goods_info['name']} {v} 个！\n"
                sql_message.send_back(user_info.user_id, k, goods_info['name'], '药材', v)
            mix_elixir_info['收取时间'] = nowtime
            save_player_info(user_id, mix_elixir_info, "mix_elixir_info")
            await yaocai_get.finish(msg, at_sender=True)
        else:
            msg = f"道友的灵田还不能收取，下次收取时间为：{round(GETCONFIG['time_cost'] * (1 - (GETCONFIG['加速基数'] * mix_elixir_info['药材速度'])), 2) - timedeff}小时之后"
            await yaocai_get.finish(msg, at_sender=True)
    else:#第一次创建
        mix_elixir_info['收取时间'] = str(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        save_player_info(user_id, mix_elixir_info, 'mix_elixir_info')
        msg = f"道友的灵田还不能收取，下次收取时间为：{GETCONFIG['time_cost']}小时之后"
        await yaocai_get.finish(msg, at_sender=True)


@elixir_help.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    await data_check_conf(bot, event)
    await elixir_help.finish(__elixir_help__)

@mix_elixir_help.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    await data_check_conf(bot, event)
    await mix_elixir_help.finish(__mix_elixir_help__)

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
            msg += f"配方：{v['配方']['配方简写']}\n"
            msg += f"☆------药材清单------☆\n"
            msg += f"主药：{v['配方']['主药']}，{v['配方']['主药_level']}，数量：{v['配方']['主药_num']}\n"
            msg += f"药引：{v['配方']['药引']}，{v['配方']['药引_level']}，数量：{v['配方']['药引_num']}\n"
            if v['配方']['辅药_num'] != 0:
                msg += f"辅药：{v['配方']['辅药']}，{v['配方']['辅药_level']}，数量：{v['配方']['辅药_num']}\n"
            l_msg.append(msg)
        await send_forward_msg(bot, event, '配方', bot.self_id, l_msg)
        msg = f"请道友输入配方公式 或者 取消，若想自己合成，请参考炼丹配方帮助"
        await mix_elixir.pause(prompt=msg)

@mix_elixir.handle()
async def _mix_elixir(bot: Bot, event: GroupMessageEvent, mode : str = EventPlainText()):
    await data_check_conf(bot, event)
    if mode == "取消":
        msg = "本次炼丹已取消！"
        await mix_elixir.finish(msg)
    user_id = event.user_id
    pattern = r"主药([\u4e00-\u9fa5]+)(\d+)药引([\u4e00-\u9fa5]+)(\d+)辅药([\u4e00-\u9fa5]+)(\d+)丹炉([\u4e00-\u9fa5]+)+"
    matched = re.search(pattern, mode)
    if matched == None:
        msg = f"请参考转发内容里的配方输入正确的配方！"
        await mix_elixir.reject(prompt=msg)
    else:
        zhuyao_name = matched.groups()[0]
        zhuyao_num = int(matched.groups()[1])#数量一定会有
        check, zhuyao_goods_id = await check_yaocai_name_in_back(user_id, zhuyao_name, zhuyao_num)
        if not check:
            msg = f"请检查药材：{zhuyao_name} 是否在背包中，或者数量是否足够！"
            await mix_elixir.reject(prompt=msg)
        yaoyin_name = matched.groups()[2]
        yaoyin_num = int(matched.groups()[3])#数量一定会有
        check, yaoyin_goods_id = await check_yaocai_name_in_back(user_id, yaoyin_name, yaoyin_num)
        if not check:
            msg = f"请检查药材：{yaoyin_name} 是否在背包中，或者数量是否足够！"
            await mix_elixir.reject(prompt=msg)
        fuyao_name = matched.groups()[4]
        fuyao_num = int(matched.groups()[5])
        check, fuyao_goods_id = await check_yaocai_name_in_back(user_id, fuyao_name, fuyao_num)
        if not check:
            msg = f"请检查药材：{fuyao_name} 是否在背包中，或者数量是否足够！"
            await mix_elixir.reject(prompt=msg)
        #检测通过
        zhuyao_info = Items().get_data_by_item_id(zhuyao_goods_id)
        yaoyin_info = Items().get_data_by_item_id(yaoyin_goods_id)
        if await tiaohe(zhuyao_info, zhuyao_num, yaoyin_info, yaoyin_num):#调和失败
            msg = f"冷热调和失败！小心炸炉哦~"
            await mix_elixir.finish(msg)
        else:
            elixir_config = {}
            elixir_config[str(zhuyao_info['主药']['type'])] = zhuyao_info['主药']['power'] * zhuyao_num
            fuyao_info = Items().get_data_by_item_id(fuyao_goods_id)
            elixir_config[str(fuyao_info['辅药']['type'])] = fuyao_info['辅药']['power'] * fuyao_num
            is_mix, id = await check_mix(elixir_config)
            if is_mix:
                goods_info = Items().get_data_by_item_id(id)
                msg = f"恭喜道友成功炼成丹药：{goods_info['name']}"
                await mix_elixir.finish(msg)
            else:
                msg = f"没有炼成丹药哦~就不扣你药材啦"
                await mix_elixir.finish(msg)
    
async def check_yaocai_name_in_back(user_id, yaocai_name, yaocai_num):
    flag = False
    goods_id = 0
    user_back = sql_message.get_back_msg(user_id)
    for back in user_back:
        if back.goods_type == '药材':
            if Items().get_data_by_item_id(back.goods_id)['name'] == yaocai_name:
                if int(back.goods_num) >= int(yaocai_num):
                    flag = True
                    goods_id = back.goods_id
                    break
            else:
                continue
        else:
            continue
    return flag, goods_id