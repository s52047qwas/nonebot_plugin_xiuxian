from nonebot.adapters.onebot.v11 import (
    PRIVATE_FRIEND,
    Bot,
    GROUP,
    Message,
    MessageEvent,
    GroupMessageEvent,
)
from nonebot import get_bot, on_command, on_regex, require
from ..xiuxian2_handle import XiuxianDateManage
from ..utils import check_user
from ..read_buff import BuffJsonDate, UserBuffDate
from nonebot.permission import SUPERUSER
from nonebot.params import CommandArg, RegexGroup
from ..player_fight import Player_fight
from ..utils import send_forward_msg

buffinfo = on_command("我的buff", aliases={"我的Buff", "我的BUFF"}, priority=5)

qc = on_command("切磋", permission=SUPERUSER, priority=5)


@qc.handle()
async def _(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    """重置用户状态。
    单用户：重置状态@xxx
    多用户：重置状态"""
    give_qq = None  # 艾特的时候存到这里
    for arg in args:
        if arg.type == "at":
            give_qq = arg.data.get("qq", "")

    if give_qq:
        player1 = {"user_id": None, "道号": None, "气血": None,
                   "攻击": None, "真元": None, '会心': None, '防御': 0, 'exp': 0}
        player2 = {"user_id": None, "道号": None, "气血": None,
                   "攻击": None, "真元": None, '会心': None, '防御': 0, 'exp': 0}
        user1 = XiuxianDateManage().get_user_message(event.get_user_id())
        user2 = XiuxianDateManage().get_user_message(give_qq)
        player1['user_id'] = user1.user_id
        player1['道号'] = user1.user_name
        player1['气血'] = user1.hp
        player1['攻击'] = user1.atk
        player1['真元'] = user1.mp
        player1['会心'] = 1
        player1['exp'] = user1.exp

        player2['user_id'] = user2.user_id
        player2['道号'] = user2.user_name
        player2['气血'] = user2.hp
        player2['攻击'] = user2.atk
        player2['真元'] = user2.mp
        player2['会心'] = 1
        player2['exp'] = user2.exp
        
        print('开始切磋')
        result, victor = Player_fight(player1, player2, 1)
        await send_forward_msg(bot, event, '决斗场', bot.self_id, result)
        await qc.finish(f"获胜的是{victor}")


Buffjsondata = BuffJsonDate()


@buffinfo.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    isUser, user_info, msg = check_user(event)
    if not isUser:
        await buffinfo.finish(msg)
    user_id = user_info.user_id
    mainbuffdata = UserBuffDate(user_id).get_user_main_buff_data()
    secbuffdata = UserBuffDate(user_id).get_user_sec_buff_data()
    secbuffmsg = get_sec_msg(secbuffdata) if get_sec_msg(
        secbuffdata) != '无' else ''
    msg = f"""
道友的主功法：{mainbuffdata["name"] if mainbuffdata != None else '无'}
道友的神通：{secbuffdata["name"] if secbuffdata != None else '无'}
{secbuffmsg}
"""
    await buffinfo.finish(msg)


def get_sec_msg(secbuffdata):
    if secbuffdata == None:
        msg = "无"
        return msg
    hpmsg = f"，消耗当前血量{int(secbuffdata['hpcost'] * 100)}%" if secbuffdata['hpcost'] != 0 else ''
    mpmsg = f"，消耗真元{int(secbuffdata['mpcost'] * 100)}%" if secbuffdata['mpcost'] != 0 else ''

    if secbuffdata['type'] == 1:
        shmsg = ''
        for value in secbuffdata['atkvalue']:
            shmsg += f"{value}倍、"

        msg = f"连续攻击{len(secbuffdata['atkvalue'])}次，造成{shmsg[:-1]}伤害{hpmsg}{mpmsg}，休息{secbuffdata['turncost']}回合"
    elif secbuffdata['type'] == 2:
        msg = f"持续伤害，造成{secbuffdata['atkvalue']}倍攻击力伤害{hpmsg}{mpmsg}，持续{secbuffdata['turncost']}回合"
    elif secbuffdata['type'] == 3:
        if secbuffdata['bufftype'] == 1:
            msg = f"增强自身，提高{secbuffdata['buffvalue']}倍攻击力{hpmsg}{mpmsg}，持续{secbuffdata['turncost']}回合"
        elif secbuffdata['bufftype'] == 2:
            msg = f"增强自身，提高{secbuffdata['buffvalue'] * 100}%减伤率{hpmsg}{mpmsg}，持续{secbuffdata['turncost']}回合"

    return msg
