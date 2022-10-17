from random import choice
from typing import Dict, Any

from nonebot import get_driver
from nonebot.log import logger
from nonebot.adapters.onebot.v11 import MessageEvent
from .xiuxian2_handle import XiuxianDateManage

driver = get_driver()
cdtype :Dict[str, int] = {}
cd_data :Dict[str, Any] = {}


cdmsg = [
    '你急啥呢？{cd_msg}后再来吧',
    'CD:{cd_msg}',
    '{cd_msg}后再来哦',
    
]

def check_cd(event: MessageEvent, cdtype: str) -> int:
    """
    :说明: `check_cd`
        * 检查是否达到CD时间\n
        * 如果达到则返回 `0`\n
        * 如果未达到则返回 `剩余CD时间`
    :参数:
      * `event: MessageEvent`: 事件对象
      * `cdtype: str`: cd类型
    :返回:
      - `int`: 剩余时间
    """
    uid = event.get_user_id()
    # cd = 设置的到期时间 - 当前时间
    try:
        cd: int = cd_data[uid][cdtype] - event.time
        logger.debug(f"{uid} 还剩: {cd}")
    except KeyError:
        cd = -1
    if cd < 0:
        return 0
    else:
        return cd
    
    
def add_cd(event: MessageEvent, config_time, cdtype, times: int = 1):
    """
    :说明: `add_cd`
    > 添加cd, 到期时间 = 当前时间 + 设定的CD * 倍数
    :参数:
      * `event: MessageEvent`: 事件
      * `times: int`: 倍数, 默认为 `1`
    """
    cd_data[event.get_user_id()] = {}
    cd_data[event.get_user_id()][cdtype] = event.time + times * config_time
    logger.debug("查询CD: {}".format(cd_data))
    
def check_user_type(user_id, need_type):
    """
    :说明: `check_user_type`
    > 匹配用户状态，返回是否状态一致
    :返回参数:
      * `isType: 是否一致
      * `msg: 消息体
    """
    isType = False
    user_cd_message = XiuxianDateManage().get_user_cd(user_id)
    if user_cd_message == None:
        user_type = 0
    else:
        user_type = user_cd_message.type
    
    if user_type == need_type:#状态一致
        isType = True
        msg = ''
        return isType, msg
    
    if need_type == 1:
        msg = "道友现在在闭关呢，小心走火入魔！"
        return isType, msg
    elif need_type == 2:
        msg = "道友现在在做悬赏令呢，小心走火入魔！"
        return isType, msg
    
def cd_msg(time_last) -> str:
    """获取CD提示信息"""
    hours, minutes, seconds = 0, 0, 0
    if time_last >= 60:
        minutes, seconds = divmod(time_last, 60)
        hours, minutes = divmod(minutes, 60)
    else:
        seconds = time_last
    cd_msg = f"{str(hours) + '小时' if hours else ''}{str(minutes) + '分钟' if minutes else ''}{str(seconds) + '秒' if seconds else ''}"

    return choice(cdmsg).format(cd_msg=cd_msg)