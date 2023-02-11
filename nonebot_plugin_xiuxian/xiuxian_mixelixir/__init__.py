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
    MessageSegment
)
from nonebot.permission import SUPERUSER
from ..xiuxian2_handle import XiuxianDateManage
from datetime import datetime
from ..xiuxian_opertion import do_is_work
from ..cd_manager import add_cd, check_cd, cd_msg
from nonebot.log import logger
from ..utils import data_check_conf, check_user, send_forward_msg, get_msg_pic, pic_msg_format
from ..item_json import Items
from .mixelixirutil import get_mix_elixir_msg, tiaohe, check_mix
from ..read_buff import get_player_info, save_player_info
from ..xiuxian_config import USERRANK, XiuConfig
from datetime import datetime
import random
import re

sql_message = XiuxianDateManage()  # sql类
items = Items()
from .mix_elixir_config import MIXELIXIRCONFIG

mix_elixir = on_command("炼丹", priority=5, permission=GROUP)
elixir_help = on_command("炼丹帮助", priority=5, permission=GROUP)
mix_elixir_help = on_command("炼丹配方帮助", priority=5, permission=GROUP)
yaocai_get = on_command("灵田收取", aliases={"灵田结算"}, priority=5, permission=GROUP)
my_mix_elixir_info = on_command("我的炼丹信息", priority=5, permission=GROUP)
mix_elixir_sqdj_up = on_command("升级收取等级", priority=5, permission=GROUP)
mix_elixir_dykh_up = on_command("升级丹药控火", priority=5, permission=GROUP)
mix_elixir_nyx_up = on_command("升级丹药耐药性", priority=5, permission=GROUP)

__elixir_help__ = f"""
炼丹帮助信息:
指令：
1、炼丹：会检测背包内的药材，自动生成配方
2、炼丹帮助：获取本帮助信息
3、炼丹配方帮助：获取炼丹配方帮助
4、灵田收取、灵田结算：收取洞天福地里灵田的药材
5、我的炼丹信息：查询自己的炼丹信息
6、升级收取等级：每一个等级会增加灵田收取的数量
7、升级丹药控火：每一个等级会增加炼丹的产出数量
"""

__mix_elixir_help__ = f"""
炼丹配方信息
1、炼丹需要主药、药引、辅药
2、主药和药引控制炼丹时的冷热调和，冷热失和则炼不出丹药
3、草药的类型控制产出丹药的类型
"""
@mix_elixir_sqdj_up.handle()
async def _(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    """收取等级升级"""
    await data_check_conf(bot, event)
    isUser, user_info, msg = check_user(event)
    if not isUser:
        if XiuConfig().img:
            msg = await pic_msg_format(msg, event)
            pic = await get_msg_pic(msg)
            await mix_elixir_sqdj_up.finish(MessageSegment.image(pic))
        else:
            await mix_elixir_sqdj_up.finish(msg, at_sender=True)
    user_id = user_info.user_id
    if int(user_info.blessed_spot_flag) == 0:
        msg = f"道友还没有洞天福地呢，请发送洞天福地购买吧~"
        if XiuConfig().img:
            msg = await pic_msg_format(msg, event)
            pic = await get_msg_pic(msg)
            await mix_elixir_sqdj_up.finish(MessageSegment.image(pic))
        else:
            await mix_elixir_sqdj_up.finish(msg, at_sender=True)
    SQDJCONFIG = MIXELIXIRCONFIG['收取等级']
    mix_elixir_info = get_player_info(user_id, "mix_elixir_info")
    now_level = mix_elixir_info['收取等级']
    if now_level >= len(SQDJCONFIG):
        msg = f"道友的收取等级已达到最高等级，无法升级了"
        if XiuConfig().img:
            msg = await pic_msg_format(msg, event)
            pic = await get_msg_pic(msg)
            await mix_elixir_sqdj_up.finish(MessageSegment.image(pic))
        else:
            await mix_elixir_sqdj_up.finish(msg, at_sender=True)
    next_level_cost = SQDJCONFIG[str(now_level + 1)]['level_up_cost']
    if mix_elixir_info['炼丹经验'] < next_level_cost:
        msg = f"下一个收取等级所需要的炼丹经验为{next_level_cost}点，道友请炼制更多的丹药再来升级吧~"
        if XiuConfig().img:
            msg = await pic_msg_format(msg, event)
            pic = await get_msg_pic(msg)
            await mix_elixir_sqdj_up.finish(MessageSegment.image(pic))
        else:
            await mix_elixir_sqdj_up.finish(msg, at_sender=True)
    mix_elixir_info['炼丹经验'] = mix_elixir_info['炼丹经验'] - next_level_cost
    mix_elixir_info['收取等级'] = now_level + 1
    save_player_info(user_id, mix_elixir_info, 'mix_elixir_info')
    msg = f"道友的收取等级目前为：{mix_elixir_info['收取等级']}级，可以使灵田收获的药材增加{mix_elixir_info['收取等级']}个！"
    if XiuConfig().img:
        msg = await pic_msg_format(msg, event)
        pic = await get_msg_pic(msg)
        await mix_elixir_sqdj_up.finish(MessageSegment.image(pic))
    else:
        await mix_elixir_sqdj_up.finish(msg, at_sender=True)
    
@mix_elixir_dykh_up.handle()
async def _(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    """丹药控火升级"""
    await data_check_conf(bot, event)
    isUser, user_info, msg = check_user(event)
    if not isUser:
        if XiuConfig().img:
            msg = await pic_msg_format(msg, event)
            pic = await get_msg_pic(msg)
            await mix_elixir_dykh_up.finish(MessageSegment.image(pic))
        else:
            await mix_elixir_dykh_up.finish(msg, at_sender=True)
    user_id = user_info.user_id
    DYKHCONFIG = MIXELIXIRCONFIG['丹药控火']
    mix_elixir_info = get_player_info(user_id, "mix_elixir_info")
    now_level = mix_elixir_info['丹药控火']
    if now_level >= len(DYKHCONFIG):
        msg = f"道友的丹药控火等级已达到最高等级，无法升级了"
        if XiuConfig().img:
            msg = await pic_msg_format(msg, event)
            pic = await get_msg_pic(msg)
            await mix_elixir_dykh_up.finish(MessageSegment.image(pic))
        else:
            await mix_elixir_dykh_up.finish(msg, at_sender=True)
    next_level_cost = DYKHCONFIG[str(now_level + 1)]['level_up_cost']
    if mix_elixir_info['炼丹经验'] < next_level_cost:
        msg = f"下一个丹药控火等级所需要的炼丹经验为{next_level_cost}点，道友请炼制更多的丹药再来升级吧~"
        if XiuConfig().img:
            msg = await pic_msg_format(msg, event)
            pic = await get_msg_pic(msg)
            await mix_elixir_dykh_up.finish(MessageSegment.image(pic))
        else:
            await mix_elixir_dykh_up.finish(msg, at_sender=True)
    mix_elixir_info['炼丹经验'] = mix_elixir_info['炼丹经验'] - next_level_cost
    mix_elixir_info['丹药控火'] = now_level + 1
    save_player_info(user_id, mix_elixir_info, 'mix_elixir_info')
    msg = f"道友的丹药控火等级目前为：{mix_elixir_info['丹药控火']}级，可以使炼丹收获的丹药增加{mix_elixir_info['丹药控火']}个！"
    if XiuConfig().img:
        msg = await pic_msg_format(msg, event)
        pic = await get_msg_pic(msg)
        await mix_elixir_dykh_up.finish(MessageSegment.image(pic))
    else:
        await mix_elixir_dykh_up.finish(msg, at_sender=True)

@mix_elixir_nyx_up.handle()
async def _(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    """丹药耐药性升级"""
    await data_check_conf(bot, event)
    isUser, user_info, msg = check_user(event)
    if not isUser:
        if XiuConfig().img:
            msg = await pic_msg_format(msg, event)
            pic = await get_msg_pic(msg)
            await mix_elixir_nyx_up.finish(MessageSegment.image(pic))
        else:
            await mix_elixir_nyx_up.finish(msg, at_sender=True)
    msg = f"丹药耐药性的升级目前未开放！"
    if XiuConfig().img:
        msg = await pic_msg_format(msg, event)
        pic = await get_msg_pic(msg)
        await mix_elixir_nyx_up.finish(MessageSegment.image(pic))
    else:
        await mix_elixir_nyx_up.finish(msg, at_sender=True)

@yaocai_get.handle()
async def _(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    """灵田收取"""
    await data_check_conf(bot, event)
    isUser, user_info, msg = check_user(event)
    if not isUser:
        if XiuConfig().img:
            msg = await pic_msg_format(msg, event)
            pic = await get_msg_pic(msg)
            await yaocai_get.finish(MessageSegment.image(pic))
        else:
            await yaocai_get.finish(msg, at_sender=True)
    user_id = user_info.user_id
    if int(user_info.blessed_spot_flag) == 0:
        msg = f"道友还没有洞天福地呢，请发送洞天福地购买吧~"
        if XiuConfig().img:
            msg = await pic_msg_format(msg, event)
            pic = await get_msg_pic(msg)
            await yaocai_get.finish(MessageSegment.image(pic))
        else:
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
            num = mix_elixir_info['灵田数量'] + mix_elixir_info['收取等级']
            msg = ''
            if yaocai_id_list == []:
                sql_message.send_back(user_info.user_id, 3001, '恒心草', '药材', num)#没有合适的，保底
                msg += f"道友成功收获药材：恒心草 {num} 个！\n"
            else:
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
            if XiuConfig().img:
                msg = await pic_msg_format(msg, event)
                pic = await get_msg_pic(msg)
                await yaocai_get.finish(MessageSegment.image(pic))
            else:
                await yaocai_get.finish(msg, at_sender=True)
        else:
            msg = f"道友的灵田还不能收取，下次收取时间为：{round(GETCONFIG['time_cost'] * (1 - (GETCONFIG['加速基数'] * mix_elixir_info['药材速度'])), 2) - timedeff}小时之后"
            if XiuConfig().img:
                msg = await pic_msg_format(msg, event)
                pic = await get_msg_pic(msg)
                await yaocai_get.finish(MessageSegment.image(pic))
            else:
                await yaocai_get.finish(msg, at_sender=True)

@my_mix_elixir_info.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    await data_check_conf(bot, event)
    isUser, user_info, msg = check_user(event)
    if not isUser:
        if XiuConfig().img:
            msg = await pic_msg_format(msg, event)
            pic = await get_msg_pic(msg)
            await my_mix_elixir_info.finish(MessageSegment.image(pic))
        else:
            await my_mix_elixir_info.finish(msg, at_sender=True)
    user_id = user_info.user_id
    mix_elixir_info = get_player_info(user_id, 'mix_elixir_info')
    l_msg = []
    l_msg.append(f"☆------道友的炼丹信息------☆")
    msg = f"药材收取等级：{mix_elixir_info['收取等级']}\n"
    msg += f"丹药控火等级：{mix_elixir_info['丹药控火']}\n"
    msg += f"丹药耐药性等级：{mix_elixir_info['丹药耐药性']}\n"
    msg += f"炼丹经验：{mix_elixir_info['炼丹经验']}\n"
    l_msg.append(msg)
    if mix_elixir_info['炼丹记录'] != {}:
        l_msg.append(f"☆------道友的炼丹记录------☆")
        i = 1
        for k, v in mix_elixir_info['炼丹记录'].items():
            msg = f"编号：{i}，{v['name']}，炼成次数：{v['num']}次"
            l_msg.append(msg)
            i += 1
    await send_forward_msg(bot, event, '炼丹信息', bot.self_id, l_msg)
    await my_mix_elixir_info.finish()

@elixir_help.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    await data_check_conf(bot, event)
    pic = await get_msg_pic(__elixir_help__)#
    await elixir_help.finish(MessageSegment.image(pic))

@mix_elixir_help.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    await data_check_conf(bot, event)
    pic = await get_msg_pic(__mix_elixir_help__)#
    await mix_elixir_help.finish(MessageSegment.image(pic))

user_ldl_dict = {}
user_ldl_flag = {}

@mix_elixir.handle()
async def _mix_elixir(bot: Bot, event: GroupMessageEvent):
    await data_check_conf(bot, event)
    isUser, user_info, msg = check_user(event)
    if not isUser:
        if XiuConfig().img:
            msg = await pic_msg_format(msg, event)
            pic = await get_msg_pic(msg)
            await mix_elixir.finish(MessageSegment.image(pic))
        else:
            await mix_elixir.finish(msg, at_sender=True)
    user_id = user_info.user_id
    user_back = sql_message.get_back_msg(user_id)
    if user_back == None:
        msg = "道友的背包空空如也，无法炼丹"
        if XiuConfig().img:
            msg = await pic_msg_format(msg, event)
            pic = await get_msg_pic(msg)
            await mix_elixir.finish(MessageSegment.image(pic))
        else:
            await mix_elixir.finish(msg, at_sender=True)
    yaocai_dict = {}
    for back in user_back:
        if back.goods_type == "药材":
            yaocai_dict[back.goods_id] = items.get_data_by_item_id(back.goods_id)
            yaocai_dict[back.goods_id]['num'] = back.goods_num
            continue
        if back.goods_type == "炼丹炉":
            global user_ldl_dict, user_ldl_flag
            user_ldl_dict[user_id] = {}
            user_ldl_dict[user_id][back.goods_id] = back.goods_id
            user_ldl_dict[user_id][back.goods_id] = back.goods_name
            user_ldl_flag[user_id] = True
            continue
        else:
            continue
    if yaocai_dict == {}:
        msg = f"道友的背包内没有药材，无法炼丹！"
        if XiuConfig().img:
            msg = await pic_msg_format(msg, event)
            pic = await get_msg_pic(msg)
            await mix_elixir.finish(MessageSegment.image(pic))
        else:
            await mix_elixir.finish(msg, at_sender=True)
    try:
        user_ldl_flag[user_id]
    except KeyError:
        msg = f"道友背包内没有炼丹炉，无法炼丹！"
        if XiuConfig().img:
            msg = await pic_msg_format(msg, event)
            pic = await get_msg_pic(msg)
            await mix_elixir.finish(MessageSegment.image(pic))
        else:
            await mix_elixir.finish(msg, at_sender=True)
    msg = "正在匹配背包中的丹方，请等待"
    if XiuConfig().img:
        msg = await pic_msg_format(msg, event)
        pic = await get_msg_pic(msg)
        await mix_elixir.send(MessageSegment.image(pic))
    else:
        await mix_elixir.send(msg, at_sender=True)
    finall_mix_elixir_msg = await get_mix_elixir_msg(yaocai_dict)
    if finall_mix_elixir_msg == {}:
        msg = "系统未检测到丹方，道友背包内的药材不满足！"
        if XiuConfig().img:
            msg = await pic_msg_format(msg, event)
            pic = await get_msg_pic(msg)
            await mix_elixir.finish(MessageSegment.image(pic))
        else:
            await mix_elixir.finish(msg, at_sender=True)
    else:
        ldl_name = sorted(user_ldl_dict[user_id].items(), key= lambda x:x[0], reverse=False)[0][1]
        l_msg = []
        for k, v in finall_mix_elixir_msg.items():
            goods_info = items.get_data_by_item_id(v['id'])
            msg = f"名字：{goods_info['name']}\n"
            msg += f"效果：{goods_info['desc']}\n"
            msg += f"配方：{v['配方']['配方简写']}丹炉{ldl_name}\n"
            msg += f"☆------药材清单------☆\n"
            msg += f"主药：{v['配方']['主药']}，{v['配方']['主药_level']}，数量：{v['配方']['主药_num']}\n"
            msg += f"药引：{v['配方']['药引']}，{v['配方']['药引_level']}，数量：{v['配方']['药引_num']}\n"
            if v['配方']['辅药_num'] != 0:
                msg += f"辅药：{v['配方']['辅药']}，{v['配方']['辅药_level']}，数量：{v['配方']['辅药_num']}\n"
            l_msg.append(msg)
        if len(l_msg) > 51:
            l_msg = l_msg[:50]
        await send_forward_msg(bot, event, '配方', bot.self_id, l_msg)
        msg = f"请道友输入配方公式 或者 取消，若想自己合成，请参考炼丹配方帮助"
        if XiuConfig().img:
            msg = await pic_msg_format(msg, event)
            pic = await get_msg_pic(msg)
            await mix_elixir.pause(prompt=MessageSegment.image(pic))
        else:
            await mix_elixir.pause(prompt=msg, at_sender=True)

@mix_elixir.handle()
async def _mix_elixir(bot: Bot, event: GroupMessageEvent, mode : str = EventPlainText()):
    await data_check_conf(bot, event)
    if mode == "取消":
        msg = "本次炼丹已取消！"
        if XiuConfig().img:
            msg = await pic_msg_format(msg, event)
            pic = await get_msg_pic(msg)
            await mix_elixir.finish(MessageSegment.image(pic))
        else:
            await mix_elixir.finish(msg, at_sender=True)
    user_id = event.user_id
    pattern = r"主药([\u4e00-\u9fa5]+)(\d+)药引([\u4e00-\u9fa5]+)(\d+)辅药([\u4e00-\u9fa5]+)(\d+)丹炉([\u4e00-\u9fa5]+)+"
    matched = re.search(pattern, mode)
    if matched == None:
        msg = f"请参考转发内容里的配方输入正确的配方！"
        if XiuConfig().img:
            msg = await pic_msg_format(msg, event)
            pic = await get_msg_pic(msg)
            await mix_elixir.reject(prompt=MessageSegment.image(pic))
        else:
            await mix_elixir.reject(prompt=msg, at_sender=True)
    else:
        zhuyao_name = matched.groups()[0]
        zhuyao_num = int(matched.groups()[1])#数量一定会有
        check, zhuyao_goods_id = await check_yaocai_name_in_back(user_id, zhuyao_name, zhuyao_num)
        if not check:
            msg = f"请检查药材：{zhuyao_name} 是否在背包中，或者数量是否足够！"
            if XiuConfig().img:
                msg = await pic_msg_format(msg, event)
                pic = await get_msg_pic(msg)
                await mix_elixir.reject(prompt=MessageSegment.image(pic))
            else:
                await mix_elixir.reject(prompt=msg, at_sender=True)
        yaoyin_name = matched.groups()[2]
        yaoyin_num = int(matched.groups()[3])#数量一定会有
        check, yaoyin_goods_id = await check_yaocai_name_in_back(user_id, yaoyin_name, yaoyin_num)
        if not check:
            msg = f"请检查药材：{yaoyin_name} 是否在背包中，或者数量是否足够！"
            if XiuConfig().img:
                msg = await pic_msg_format(msg, event)
                pic = await get_msg_pic(msg)
                await mix_elixir.reject(prompt=MessageSegment.image(pic))
            else:
                await mix_elixir.reject(prompt=msg, at_sender=True)
        fuyao_name = matched.groups()[4]
        fuyao_num = int(matched.groups()[5])
        check, fuyao_goods_id = await check_yaocai_name_in_back(user_id, fuyao_name, fuyao_num)
        if not check:
            msg = f"请检查药材：{fuyao_name} 是否在背包中，或者数量是否足够！"
            if XiuConfig().img:
                msg = await pic_msg_format(msg, event)
                pic = await get_msg_pic(msg)
                await mix_elixir.reject(prompt=MessageSegment.image(pic))
            else:
                await mix_elixir.reject(prompt=msg, at_sender=True)
        if zhuyao_name == fuyao_name:
            check, fuyao_goods_id = await check_yaocai_name_in_back(user_id, fuyao_name, fuyao_num + zhuyao_num)
            if not check:
                msg = f"请检查药材：{zhuyao_name} 是否在背包中，或者数量是否足够！"
                if XiuConfig().img:
                    msg = await pic_msg_format(msg, event)
                    pic = await get_msg_pic(msg)
                    await mix_elixir.reject(prompt=MessageSegment.image(pic))
                else:
                    await mix_elixir.reject(prompt=msg, at_sender=True)
        if yaoyin_name == fuyao_name:
            check, fuyao_goods_id = await check_yaocai_name_in_back(user_id, fuyao_name, fuyao_num + yaoyin_num)
            if not check:
                msg = f"请检查药材：{yaoyin_name} 是否在背包中，或者数量是否足够！"
                if XiuConfig().img:
                    msg = await pic_msg_format(msg, event)
                    pic = await get_msg_pic(msg)
                    await mix_elixir.reject(prompt=MessageSegment.image(pic))
                else:
                    await mix_elixir.reject(prompt=msg, at_sender=True)
                
        ldl_name = matched.groups()[6]
        check, ldl_info = await check_ldl_name_in_back(user_id, ldl_name)
        if not check:
            msg = f"请检查炼丹炉：{ldl_name} 是否在背包中！"
            if XiuConfig().img:
                msg = await pic_msg_format(msg, event)
                pic = await get_msg_pic(msg)
                await mix_elixir.reject(prompt=MessageSegment.image(pic))
            else:
                await mix_elixir.reject(prompt=msg, at_sender=True)
        #检测通过
        zhuyao_info = Items().get_data_by_item_id(zhuyao_goods_id)
        yaoyin_info = Items().get_data_by_item_id(yaoyin_goods_id)
        if await tiaohe(zhuyao_info, zhuyao_num, yaoyin_info, yaoyin_num):#调和失败
            msg = f"冷热调和失败！小心炸炉哦~"
            if XiuConfig().img:
                msg = await pic_msg_format(msg, event)
                pic = await get_msg_pic(msg)
                await mix_elixir.finish(MessageSegment.image(pic))
            else:
                await mix_elixir.finish(msg, at_sender=True)
        else:
            elixir_config = {}
            elixir_config[str(zhuyao_info['主药']['type'])] = zhuyao_info['主药']['power'] * zhuyao_num
            fuyao_info = Items().get_data_by_item_id(fuyao_goods_id)
            elixir_config[str(fuyao_info['辅药']['type'])] = fuyao_info['辅药']['power'] * fuyao_num
            is_mix, id = await check_mix(elixir_config)
            if is_mix:
                mix_elixir_info = get_player_info(user_id, 'mix_elixir_info')
                goods_info = Items().get_data_by_item_id(id)
                num = 1 + ldl_info['buff'] + mix_elixir_info['丹药控火']
                msg = f"恭喜道友成功炼成丹药：{goods_info['name']}{num}枚"
                #背包sql
                sql_message.send_back(user_id, id, goods_info['name'], "丹药", num)
                sql_message.update_back_j(user_id, zhuyao_goods_id, zhuyao_num)
                sql_message.update_back_j(user_id, fuyao_goods_id, fuyao_num)
                sql_message.update_back_j(user_id, yaoyin_goods_id, yaoyin_num)
                try:
                    mix_elixir_info['炼丹记录'][id]
                    now_num = mix_elixir_info['炼丹记录'][id]['num']
                    if now_num >= goods_info['mix_all']:
                        msg += f"该丹药道友已炼制{now_num}次，无法获得炼丹经验了~"
                    elif now_num + num >= goods_info['mix_all']:
                        exp_num = goods_info['mix_all'] - now_num
                        mix_elixir_info['炼丹经验'] += goods_info['mix_exp'] * exp_num
                        msg += f"获得炼丹经验{goods_info['mix_exp'] * exp_num}点"
                    else:
                        mix_elixir_info['炼丹经验'] += goods_info['mix_exp'] * num
                        msg += f"获得炼丹经验{goods_info['mix_exp'] * num}点"
                    mix_elixir_info['炼丹记录'][id]['num'] += num
                except:
                    mix_elixir_info['炼丹记录'][id] = {}
                    mix_elixir_info['炼丹记录'][id]['name'] = goods_info['name']
                    mix_elixir_info['炼丹记录'][id]['num'] = num
                    mix_elixir_info['炼丹经验'] += goods_info['mix_exp'] * num
                    msg += f"获得炼丹经验{goods_info['mix_exp'] * num}点"
                save_player_info(user_id, mix_elixir_info, 'mix_elixir_info')
                
                if XiuConfig().img:
                    msg = await pic_msg_format(msg, event)
                    pic = await get_msg_pic(msg)
                    await mix_elixir.finish(MessageSegment.image(pic))
                else:
                    await mix_elixir.finish(msg, at_sender=True)
            else:
                msg = f"没有炼成丹药哦~就不扣你药材啦"
                if XiuConfig().img:
                    msg = await pic_msg_format(msg, event)
                    pic = await get_msg_pic(msg)
                    await mix_elixir.finish(MessageSegment.image(pic))
                else:
                    await mix_elixir.finish(msg, at_sender=True)
    
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

async def check_ldl_name_in_back(user_id, ldl_name):
    flag = False
    goods_info = {}
    user_back = sql_message.get_back_msg(user_id)
    for back in user_back:
        if back.goods_type == '炼丹炉':
            if back.goods_name == ldl_name:
                flag = True
                goods_info = Items().get_data_by_item_id(back.goods_id)
                break
            else:
                continue
        else:
            continue
    return flag, goods_info