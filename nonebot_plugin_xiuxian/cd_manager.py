from random import choice
from typing import Dict

from nonebot import get_driver
from nonebot.log import logger
from nonebot.adapters.onebot.v11 import MessageEvent, PrivateMessageEvent
from .xiuxian_config import XiuConfig

driver = get_driver()

cd_data: Dict[str, int] = {}


def check_cd(event: MessageEvent) -> int:
    """
    :说明: `check_cd`
        * 检查是否达到CD时间\n
        * 如果达到则返回 `0`\n
        * 如果未达到则返回 `剩余CD时间`
    :参数:
      * `event: MessageEvent`: 事件对象
    :返回:
      - `int`: 剩余时间
    """
    uid = event.get_user_id()
    # cd = 设置的到期时间 - 当前时间
    try:
        cd: int = cd_data[uid] - event.time
        logger.debug(f"{uid} 还剩: {cd}")
    except KeyError:
        cd = -1
    if cd < 0:
        return 0
    else:
        return cd
    
    
def add_cd(event: MessageEvent, times: int = 1):
    """
    :说明: `add_cd`
    > 添加cd, 到期时间 = 当前时间 + 设定的CD * 倍数
    :参数:
      * `event: MessageEvent`: 事件
      * `times: int`: 倍数, 默认为 `1`
    """
    cd_data[event.get_user_id()] = event.time + times * XiuConfig().dufang_cd
    logger.debug("查询CD: {}".format(cd_data))
    
def cd_msg(time_last) -> str:
    """获取CD提示信息"""
    hours, minutes, seconds = 0, 0, 0
    if time_last >= 60:
        minutes, seconds = divmod(time_last, 60)
        hours, minutes = divmod(minutes, 60)
    else:
        seconds = time_last
    cd_msg = f"{str(hours) + '小时' if hours else ''}{str(minutes) + '分钟' if minutes else ''}{str(seconds) + '秒' if seconds else ''}"

    return XiuConfig().dufang_cd_msg.format(cd_msg=cd_msg)