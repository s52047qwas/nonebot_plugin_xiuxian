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
from ..cd_manager import add_cd, check_cd, cd_msg
from .infoconfig import get_config
from ..utils import data_check_conf
from ..read_buff import UserBuffDate

config = get_config()

def format_number(number: int) -> str:
    if number >= 1000000000000:
        return str(round(number / 1000000000000, 1)) + "万亿"
    elif number >= 100000000:
        return str(round(number / 100000000, 1)) + "亿"
    elif number >= 10000:
        return str(round(number / 10000, 1)) + "万"
    elif number <= -1000000000000:
        return str(round(number / 1000000000000, 1)) + "万亿"
    elif number <= -100000000:
        return str(round(number / 100000000, 1)) + "亿"
    elif number <= -10000:
        return str(round(number / 10000, 1)) + "万"
    else:
        return str(number)

xiuxian_message = on_command("我的修仙信息", aliases={"我的存档"}, priority=5)


sql_message = XiuxianDateManage()  # sql类

@xiuxian_message.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    """我的修仙信息"""
    await data_check_conf(bot, event)

    if cd := check_cd(event, '查询信息'):
        # 如果 CD 还没到 则直接结束
        await xiuxian_message.finish(cd_msg(cd), at_sender=True)
        
    
    try:
        user_id, group_id, mess = await data_check(bot, event)
    except MsgError:
        return
    add_cd(event, config['查询CD'], '查询信息')
    mess = sql_message.get_user_real_info(user_id)
    user_name = mess.user_name
    user_num = mess.id
    rank = sql_message.get_exp_rank(user_id)
    user_rank = int(rank[0])
    stone = sql_message.get_stone_rank(user_id)
    user_stone = int(stone[0])
    if user_name:
        pass
    else:
        user_name = "无名氏(发送改名+道号更新)"
    level_rate = sql_message.get_root_rate(mess.root_type)  # 灵根倍率
    realm_rate = jsondata.level_data()[mess.level]["spend"]  # 境界倍率
    sect_id = mess.sect_id
    if sect_id:
        sect_info = sql_message.get_sect_info(sect_id)
        sectmsg = sect_info.sect_name
        sectzw = jsondata.sect_config_data()[f"{mess.sect_position}"]["title"]
    else:
        sectmsg = '无宗门'
        sectzw = '无'

    # 判断突破的修为
    list_all = len(OtherSet().level) - 1
    now_index = OtherSet().level.index(mess.level)
    if list_all == now_index:
        exp_meg = "位面至高"
    else:
        is_updata_level = OtherSet().level[now_index + 1]
        need_exp = sql_message.get_level_power(is_updata_level)
        get_exp = need_exp - mess.exp
        if get_exp > 0:
            if get_exp > 10000:
                get_exp = int(divmod(get_exp, 10000)[0])
                exp_meg = "还需{}万修为可突破！".format(get_exp)
            else:
                exp_meg = "还需{}修为可突破！".format(get_exp)
        else:
            exp_meg = "可突破！"
    
    user_buff_data = UserBuffDate(user_id)
    user_main_buff_date = user_buff_data.get_user_main_buff_data()
    user_sec_buff_date = user_buff_data.get_user_sec_buff_data()
    user_weapon_data = user_buff_data.get_user_weapon_data()
    user_armor_data = user_buff_data.get_user_armor_buff_data()
    main_buff_name = '无'
    sec_buff_name = '无'
    weapon_name = '无'
    armor_name = '无'
    if user_main_buff_date != None:
        main_buff_name = f"{user_main_buff_date['name']}({user_main_buff_date['level']})"
    if user_sec_buff_date != None:
        sec_buff_name = f"{user_sec_buff_date['name']}({user_sec_buff_date['level']})"
    if user_weapon_data != None:
        weapon_name = f"{user_weapon_data['name']}({user_weapon_data['level']})"
    if user_armor_data != None:
        armor_name = f"{user_armor_data['name']}({user_armor_data['level']})"

    DETAIL_MAP = {
    '道号': f'{user_name}',
    '境界': f'{mess.level}',
    '修为': f'{mess.exp}',
    '灵石': f'{mess.stone}',
    '战力': f'{int(mess.exp * level_rate * realm_rate)}',
    '灵根': f'{mess.root}({mess.root_type}+{int(level_rate * 100)}%)',
    '突破状态': f'{exp_meg}概率：{jsondata.level_rate_data()[mess.level] + int(mess.level_up_rate)}%',
    '攻击力': f'{mess.atk}，攻修等级{mess.atkpractice}级',
    '所在宗门':sectmsg,
    '宗门职位':sectzw,
    '主修功法':main_buff_name,
    '副修神通':sec_buff_name,
    "法器":weapon_name,
    "防具":armor_name,
    '注册位数': f'道友是踏入修仙世界的第{int(user_num)}人',
    '修为排行': f'道友的修为排在第{int(user_rank)}位',
    '灵石排行': f'道友的灵石排在第{int(user_stone)}位',
    }
    if config['是否开启图片信息']:
        img_res = await draw_user_info_img(user_id, DETAIL_MAP)
        await xiuxian_message.finish(MessageSegment.image(img_res))
    else:
        try:
            msg = f"""{user_name}道友的信息
灵根为：{mess.root}({mess.root_type}+{int(level_rate * 100)}%)
当前境界：{mess.level}(境界+{int(realm_rate * 100)}%)
当前灵石：{format_number(mess.stone)}
当前修为：{format_number(mess.exp)}(修炼效率+{int((level_rate * realm_rate) * 100)}%)
当前主修功法为：{user_main_buff_date['name']}({user_main_buff_date['level']})
当前副修神通为：{user_sec_buff_date['name']}({user_sec_buff_date['level']})
你的战力为：{format_number(int(mess.exp * level_rate * realm_rate))}
你的攻击力为{format_number(mess.atk)}，攻修等级{mess.atkpractice}级
你是踏入修仙世界的第{int(user_num)}人
你的修为排在第{int(user_rank)}位
你的灵石排在第{int(user_stone)}位"""
            await xiuxian_message.finish(msg, at_sender=True)
        except TypeError:
            msg = f"""{user_name}道友的信息
灵根为：{mess.root}({mess.root_type}+{int(level_rate * 100)}%)
当前境界：{mess.level}(境界+{int(realm_rate * 100)}%)
当前灵石：{format_number(mess.stone)}
当前修为：{format_number(mess.exp)}(修炼效率+{int((level_rate * realm_rate) * 100)}%)
你的战力为：{format_number(int(mess.exp * level_rate * realm_rate))}
你的攻击力为{format_number(mess.atk)}，攻修等级{mess.atkpractice}级
你是踏入修仙世界的第{int(user_num)}人
你的修为排在第{int(user_rank)}位
你的灵石排在第{int(user_stone)}位"""
            await xiuxian_message.finish(msg, at_sender=True)

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




