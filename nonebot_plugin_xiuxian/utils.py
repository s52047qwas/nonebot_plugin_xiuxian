from .xiuxian2_handle import XiuxianDateManage
from nonebot.adapters.onebot.v11 import (
    Bot,
    MessageEvent,
    GroupMessageEvent,
)

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

def check_user(event: GroupMessageEvent):
    """
    判断用户信息是否存在
    :返回参数:
      * `isUser: 是否存在
      * `user_info: 用户
      * `msg: 消息体
    """
    
    isUser = False
    user_id = event.get_user_id()
    user_info = XiuxianDateManage().get_user_message(user_id)
    if user_info is None:
        msg = "修仙界没有道友的信息，请输入【我要修仙】加入！"
    else:
        isUser = True
        msg = ''
    
    return isUser, user_info, msg

async def send_forward_msg(
    bot: Bot,
    event: MessageEvent,
    name: str,  # 转发的用户名称
    uin: str,  # qq
    msgs: list  # 转发内容
):
    """合并消息转发"""
    def to_json(msg):
        return {"type": "node", "data": {"name": name, "uin": uin, "content": msg}}

    messages = [to_json(msg) for msg in msgs]
    if isinstance(event, GroupMessageEvent):
        await bot.call_api(
            "send_group_forward_msg", group_id=event.group_id, messages=messages
        )
    else:
        await bot.call_api(
            "send_private_forward_msg", user_id=event.user_id, messages=messages
        )