import asyncio
from nonebot import get_bot, on_command, require
from nonebot.adapters.onebot.v11 import (
    PRIVATE_FRIEND,
    Bot,
    GROUP,
    Message,
    MessageEvent,
    GroupMessageEvent,
    MessageSegment,
    GROUP_ADMIN,
    GROUP_OWNER,
    ActionFailed
)
from nonebot.permission import SUPERUSER
from nonebot.log import logger
from nonebot.params import CommandArg, RegexGroup
from ..utils import data_check_conf, check_user, send_forward_msg, pic_msg_format, get_msg_pic
from ..xiuxian2_handle import XiuxianDateManage, OtherSet
from ..item_json import Items
from ..data_source import jsondata
from .back_util import get_user_back_msg, check_equipment_can_use, get_use_equipment_sql, get_shop_data, save_shop, get_item_msg, check_use_elixir, get_use_jlq_msg, get_item_msg_rank
from .backconfig import get_config, savef
import random
from datetime import datetime
from ..read_buff import get_weapon_info_msg, get_armor_info_msg, get_sec_msg, get_main_info_msg, get_sub_info_msg, UserBuffDate
from ..xiuxian_config import XiuConfig

items = Items()
config = get_config()
groups = config['open'] #list，群交流会使用



exercises_info = on_command("炼体查看", aliases={'查看炼体'}, priority=5)
exercises = on_command("炼体", priority=5)
exercises_help = on_command("炼体帮助", priority=5)


sql_message = XiuxianDateManage()  # sql类

__exercises_help_help__ = f"""
炼体帮助信息:
指令：
1、炼体查看、查看炼体：查看炼体状态和下一等级消耗，成功率
2、炼体：消耗灵石增加自身
3、炼体帮助：炼体帮助
""".strip()


    


@exercises_help.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    await data_check_conf(bot, event)
    msg = __exercises_help_help__
    msg = await pic_msg_format(msg, event)
    pic = await get_msg_pic(msg)#
    await exercises_help.finish(MessageSegment.image(pic))


@exercises_info.handle()
async def exercises_info(bot: Bot, event: GroupMessageEvent):
    """坊市查看"""
    await data_check_conf(bot, event)
    print(event)
    isUser, user_info, msg = check_user(event)
    if not isUser:
        if XiuConfig().img:
            msg = await pic_msg_format(msg, event)
            pic = await get_msg_pic(msg)
            await exercises_info.finish(MessageSegment.image(pic))
        else:
            await exercises_info.finish(msg, at_sender=True)




@exercises.handle()
async def exercises(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    """突破"""
    """坊市查看"""
    await data_check_conf(bot, event)
    print(event)
    isUser, user_msg, msg = check_user(event)
    if not isUser:
        if XiuConfig().img:
            msg = await pic_msg_format(msg, event)
            pic = await get_msg_pic(msg)
            await exercises_info.finish(MessageSegment.image(pic))
        else:
            await exercises_info.finish(msg, at_sender=True)

    stone = user_msg.stone  # 灵石
    # 这里你需要编写获取用户修为和灵石的逻辑，以下仅作示例
    cost_stone = XiuxianDateManage().get_level_cost(next_level_name)

    if can_breakthrough(exp, stone, cost_exp, cost_stone, user_backs):
        msg = f"突破到{next_level_name}，需要" \
              f"消耗 {OtherSet.format_number(cost_exp)} 修为，{OtherSet.format_number(cost_stone)} 灵石 " \
              f" 和 10个渡厄丹，" \
              f"成功率为100%，确定要突破吗？请回复“确定”进行突破。"
        if XiuConfig().img:
            msg = await pic_msg_format(msg, event)
            pic = await get_msg_pic(msg)
            await exercises.parse(prompt=MessageSegment.image(pic))
        else:
            await exercises.finish(prompt=msg)
    else:
        msg = "很遗憾，您的灵石不足以炼体。"
        if XiuConfig().img:
            msg = await pic_msg_format(msg, event)
            pic = await get_msg_pic(msg)
            await exercises.finish(prompt=MessageSegment.image(pic))
        else:
            await exercises.finish(prompt=msg)


@exercises.level_up.handle()
async def exercises_end(bot: Bot, event: GroupMessageEvent, mode: str = EventPlainText()):
    await data_check_conf(bot, event)
    isUser, user_info, msg = check_user(event)
    user_id, group_id, user_msg = await data_check(bot, event)

    level_name = user_msg.level  # 用户境界
    next_level_name = OtherSet().get_next_level(level_name)

    if not isUser:
        await level_up.finish()


    if mode not in ['使用', '不使用', '取消']:
        msg = "指令错误，应该为 使用、不使用或取消！"
        if XiuConfig().img:
            msg = await pic_msg_format(msg, event)
            pic = await get_msg_pic(msg)
            await level_up.reject(prompt=MessageSegment.image(pic))
        else:
            await level_up.reject(prompt=msg, at_sender=True)

    level_name = user_msg.level  # 用户境界
    exp = user_msg.exp  # 用户修为
    level_rate = jsondata.level_rate_data()[level_name]  # 对应境界突破的概率
    user_leveluprate = int(user_msg.level_up_rate)  # 用户失败次数加成

    le = OtherSet().get_type(exp, level_rate + user_leveluprate, level_name)
    user_backs = sql_message.get_back_msg(user_id)  # list(back)

    items = Items()
    elixir_name = items.get_data_by_item_id(1999)['name']


    if result == "失败":


        sql_message.update_ls(user_id, 100000,2)

        msg = "道友炼体失败,灵石减少{}，下次突破成功率增加{}%，道友不要放弃！".format(now_exp, update_rate)
        if XiuConfig().img:
            msg = await pic_msg_format(msg, event)
            pic = await get_msg_pic(msg)
            await level_up.finish(MessageSegment.image(pic))
        else:
            await level_up.finish(msg, at_sender=True)

    elif result == "成功":

        sql_message.update_ls(user_id, 100000, 2)

        # 突破成功
        sql_message.updata_exercises(user_id, )  # 更新炼体境界

        msg = "恭喜道友炼体{}成功".format(le[0])
        if XiuConfig().img:
            msg = await pic_msg_format(msg, event)
            pic = await get_msg_pic(msg)
            await level_up.finish(MessageSegment.image(pic))
        else:
            await level_up.finish(msg, at_sender=True)
    else:
        # 最高境界
        if XiuConfig().img:
            le = await pic_msg_format(le, event)
            pic = await get_msg_pic(le)
            await level_up.finish(MessageSegment.image(pic))
        else:
            await level_up.finish(le, at_sender=True)



