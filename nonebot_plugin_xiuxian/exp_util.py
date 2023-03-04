import logging
from .item_json import Items
from .xiuxian2_handle import XiuxianDateManage, OtherSet
from .read_buff import UserBuffDate
from .xiuxian_config import XiuConfig
from .data_source import jsondata
from nonebot.log import logger
items = Items()
sql_message = XiuxianDateManage()

## 获取每分钟获得经验
def get_exp_rate(user_id, is_close: bool):
    user_mes = sql_message.get_user_message(user_id)  # 获取用户信息
    level = user_mes.level
    level_rate = sql_message.get_root_rate(user_mes.root_type)  # 灵根倍率
    realm_rate = jsondata.level_data()[level]["spend"]  # 境界倍率
    user_buff_data = UserBuffDate(user_id)
    mainbuffdata = user_buff_data.get_user_main_buff_data()
    mainbuffratebuff = mainbuffdata['ratebuff'] if mainbuffdata != None else 0  # 功法修炼倍率
    is_close_flag = 0
    if is_close:
        is_close_flag = 1
    exp = int(
         XiuConfig().closing_exp * (
                    (level_rate * realm_rate * (1 + mainbuffratebuff)) + is_close_flag * int(user_buff_data.BuffInfo.blessed_spot))
        # 基础闭关经验 * (灵根倍率 * 境界倍率 * (1 + 功法倍率) + (是否闭关 * 洞天福地加成倍率) )
    )  # 本次闭关获取的修为
    return exp


def user_get_exp_max(user_id):
    user_mes = sql_message.get_user_message(user_id)  # 获取用户信息
    level = user_mes.level
    use_exp = user_mes.exp
    max_exp = (
            int(OtherSet().set_closing_type(level)) * XiuConfig().closing_exp_upper_limit
    )  # 获取下个境界需要的修为 * 1.5为闭关上限
    user_get_exp_max = int(max_exp) - use_exp

    if user_get_exp_max < 0:
        # 校验当当前修为超出上限的问题，不可为负数
        user_get_exp_max = 0

    return user_get_exp_max

