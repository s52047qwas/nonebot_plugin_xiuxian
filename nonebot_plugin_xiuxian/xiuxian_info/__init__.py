import re
from nonebot import on_command
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

from ..xiuxian2_handle import XiuxianDateManage, OtherSet
from ..data_source import jsondata
from .draw_user_info import draw_user_info_img
from .cd_manager import add_cd, check_cd, cd_msg




xiuxian_message = on_command("我的修仙信息", aliases={"我的存档"}, priority=5)


sql_message = XiuxianDateManage()  # sql类

@xiuxian_message.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    """我的修仙信息"""
    
    if cd := check_cd(event):
        # 如果 CD 还没到 则直接结束
        await xiuxian_message.finish(cd_msg(cd), at_sender=True)
        
    
    try:
        user_id, group_id, mess = await data_check(bot, event)
    except MsgError:
        return
    add_cd(event)
    user_name = mess.user_name
    if user_name:
        pass
    else:
        user_name = "无名氏(发送改名+道号更新)"
    level_rate = sql_message.get_root_rate(mess.root_type)  # 灵根倍率
    realm_rate = jsondata.level_data()[mess.level]["spend"]  # 境界倍率

    # 判断突破的修为
    list_all = len(OtherSet().level) - 1
    now_index = OtherSet().level.index(mess.level)
    if list_all == now_index:
        get_exp = "位面至高"
    else:
        is_updata_level = OtherSet().level[now_index + 1]
        need_exp = sql_message.get_level_power(is_updata_level)
        if need_exp - mess.exp > 0:
            get_exp = "还需{}修为可突破".format(need_exp - mess.exp)
        else:
            get_exp = "可突破！"

    DETAIL_MAP = {
    '道号': f'{user_name}',
    '境界': f'{mess.level}',
    '修为': f'{mess.exp}',
    '灵石': f'{mess.stone}',
    '战力': f'{int(mess.exp * level_rate * realm_rate)}',
    '灵根': f'{mess.root}({mess.root_type}+{int(level_rate * 100)}%)',
    '突破状态': f'{get_exp}'
    }
    
    
    img_res = await draw_user_info_img(user_id, DETAIL_MAP)


    await xiuxian_message.finish(MessageSegment.image(img_res), at_sender=True)
    
    
    
async def data_check(bot, event):
    user_qq = event.get_user_id()
    group_id = await get_group_id(event.get_session_id())
    msg = sql_message.get_user_message(user_qq)

    if msg:
        pass
    else:
        await bot.send(event=event, message=f"没有您的信息，输入【我要修仙】加入！")
        raise MsgError

    return user_qq, group_id, msg

async def get_group_id(session_id):
    """获取group_id"""
    res = re.findall("_(.*)_", session_id)
    group_id = res[0]
    return group_id

class MsgError(ValueError):
    pass




