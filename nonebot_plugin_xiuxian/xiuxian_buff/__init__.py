from nonebot.adapters.onebot.v11 import (
    PRIVATE_FRIEND,
    Bot,
    GROUP,
    Message,
    MessageEvent,
    GroupMessageEvent,
)
from datetime import datetime
from nonebot import get_bot, on_command, on_regex, require
from ..xiuxian2_handle import XiuxianDateManage, XiuxianJsonDate, OtherSet
from ..xiuxian_config import XiuConfig, JsonConfig
from ..utils import check_user
from ..data_source import jsondata
from ..read_buff import BuffJsonDate, UserBuffDate, get_main_info_msg, get_user_buff
from nonebot.permission import SUPERUSER
from nonebot.params import CommandArg, RegexGroup
from ..player_fight import Player_fight
from ..utils import send_forward_msg

buffinfo = on_command("我的功法", priority=5)
out_closing = on_command("出关", aliases={"灵石出关"}, priority=5)
mind_state = on_command("我的状态", priority=5)
qc = on_command("切磋", priority=5)
sql_message = XiuxianDateManage()  # sql类

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


@out_closing.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    """出关"""
    user_type = 0  # 状态0为无事件
    isUser, user_info, msg = check_user(event)
    if not isUser:
        await out_closing.finish(msg)
    user_id = user_info.user_id
    user_mes = sql_message.get_user_message(user_id)  # 获取用户信息
    level = user_mes.level
    use_exp = user_mes.exp
    hp_speed = 15
    mp_speed = 15

    max_exp = (
            int(OtherSet().set_closing_type(level)) * XiuConfig().closing_exp_upper_limit
    )  # 获取下个境界需要的修为 * 1.5为闭关上限
    user_get_exp_max = int(max_exp) - use_exp

    if user_get_exp_max < 0:
        # 校验当当前修为超出上限的问题，不可为负数
        user_get_exp_max = 0

    now_time = datetime.now()
    user_cd_message = sql_message.get_user_cd(user_id)

    if user_cd_message is None:
        # 不存在用户信息
        await out_closing.finish("没有查到道友的信息，修炼发送【闭关】，进入修炼状态！", at_sender=True)

    elif user_cd_message.type == 0:
        # 用户状态为0
        await out_closing.finish("道友现在什么都没干呢~", at_sender=True)

    elif user_cd_message.type == 1:
        # 用户状态为1
        in_closing_time = datetime.strptime(
            user_cd_message.create_time, "%Y-%m-%d %H:%M:%S.%f"
        )  # 进入闭关的时间
        exp_time = (
                OtherSet().date_diff(now_time, in_closing_time) // 60
        )  # 闭关时长计算(分钟) = second // 60
        level_rate = sql_message.get_root_rate(user_mes.root_type)  # 灵根倍率
        realm_rate = jsondata.level_data()[level]["spend"]  # 境界倍率
        mainbuffdata = UserBuffDate(user_id).get_user_main_buff_data()
        mainbuffratebuff = mainbuffdata['ratebuff'] if mainbuffdata != None else 0#功法修炼倍率
        exp = int(
            exp_time * XiuConfig().closing_exp * level_rate * realm_rate * (1 + mainbuffratebuff)
        )  # 本次闭关获取的修为

        if exp >= user_get_exp_max:
            # 用户获取的修为到达上限
            sql_message.in_closing(user_id, user_type)
            sql_message.update_exp(user_id, user_get_exp_max)
            sql_message.update_power2(user_id)  # 更新战力

            result_msg, result_hp_mp = OtherSet().send_hp_mp(user_id, int(exp * hp_speed), int(exp*mp_speed))
            sql_message.update_user_attribute(user_id, result_hp_mp[0], result_hp_mp[1], int(result_hp_mp[2] / 10))
            await out_closing.finish(
                "闭关结束，本次闭关到达上限，共增加修为：{}{}{}".format(user_get_exp_max, result_msg[0], result_msg[1]), at_sender=True
            )
        else:
            # 用户获取的修为没有到达上限

            if str(event.message) == "灵石出关":
                user_stone = user_mes.stone  # 用户灵石数
                if exp <= user_stone:
                    exp = exp * 2
                    sql_message.in_closing(user_id, user_type)
                    sql_message.update_exp(user_id, exp)
                    sql_message.update_ls(user_id, int(exp / 2), 2)
                    sql_message.update_power2(user_id)  # 更新战力

                    result_msg, result_hp_mp = OtherSet().send_hp_mp(user_id, int(exp * hp_speed), int(exp * mp_speed))
                    sql_message.update_user_attribute(user_id, result_hp_mp[0], result_hp_mp[1],
                                                      int(result_hp_mp[2] / 10))
                    await out_closing.finish(
                        "闭关结束，共闭关{}分钟，本次闭关增加修为：{}，消耗灵石{}枚{}{}".format(exp_time, exp, int(exp / 2),
                                                                      result_msg[0], result_msg[1]), at_sender=True
                    )
                else:
                    exp = exp + user_stone
                    sql_message.in_closing(user_id, user_type)
                    sql_message.update_exp(user_id, exp)
                    sql_message.update_ls(user_id, user_stone, 2)
                    sql_message.update_power2(user_id)  # 更新战力
                    result_msg, result_hp_mp = OtherSet().send_hp_mp(user_id, int(exp * hp_speed), int(exp * mp_speed))
                    sql_message.update_user_attribute(user_id, result_hp_mp[0], result_hp_mp[1],
                                                      int(result_hp_mp[2] / 10))
                    await out_closing.finish(
                        "闭关结束，共闭关{}分钟，本次闭关增加修为：{}，消耗灵石{}枚{}{}".format(exp_time, exp, user_stone,
                                                                  result_msg[0], result_msg[1]), at_sender=True
                    )
            else:
                sql_message.in_closing(user_id, user_type)
                sql_message.update_exp(user_id, exp)
                sql_message.update_power2(user_id)  # 更新战力
                result_msg, result_hp_mp = OtherSet().send_hp_mp(user_id, int(exp * hp_speed), int(exp * mp_speed))
                sql_message.update_user_attribute(user_id, result_hp_mp[0], result_hp_mp[1], int(result_hp_mp[2] / 10))
                await out_closing.finish(
                    "闭关结束，共闭关{}分钟，本次闭关增加修为：{}{}{}".format(exp_time, exp, result_msg[0],
                                                          result_msg[1]), at_sender=True
                )

    elif user_cd_message.type == 2:
        await out_closing.finish("悬赏令事件进行中，请输入【悬赏令结算】结束！", at_sender=True)

@mind_state.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    """我的状态信息。"""
    isUser, user_msg, msg = check_user(event)
    if not isUser:
        await mind_state.finish(msg)
    user_id = user_msg.user_id

    if user_msg.hp is None or user_msg.hp == 0 or user_msg.hp == 0:
        sql_message.update_user_hp(user_id)
    
    level_rate = sql_message.get_root_rate(user_msg.root_type)  # 灵根倍率
    realm_rate = jsondata.level_data()[user_msg.level]["spend"]  # 境界倍率
    mainbuffdata = UserBuffDate(user_id).get_user_main_buff_data()
    mainbuffratebuff = mainbuffdata['ratebuff'] if mainbuffdata != None else 0
    mainhpbuff = mainbuffdata['hpbuff'] if mainbuffdata != None else 0
    mainmpbuff = mainbuffdata['mpbuff'] if mainbuffdata != None else 0
    user = f"""道号：{user_msg.user_name}
气血：{user_msg.hp}/{int((user_msg.exp/2) * (1 + mainhpbuff))}
真元：{user_msg.mp}/{int((user_msg.exp) * (1 + mainmpbuff))}
攻击：{user_msg.atk}
攻击修炼：{user_msg.atkpractice}级(提升攻击力{user_msg.atkpractice * 10}%)
修炼效率：{int((level_rate * realm_rate) * (1 + mainbuffratebuff)  * 100)}%
"""

    await mind_state.finish(user)


@buffinfo.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    isUser, user_info, msg = check_user(event)
    if not isUser:
        await buffinfo.finish(msg)
    user_id = user_info.user_id
    mainbuffdata = UserBuffDate(user_id).get_user_main_buff_data()
    if mainbuffdata != None:
        s, mainbuffmsg = get_main_info_msg(str(get_user_buff(user_id).main_buff))
    else:
        s, mainbuffmsg = ''
    secbuffdata = UserBuffDate(user_id).get_user_sec_buff_data()
    secbuffmsg = get_sec_msg(secbuffdata) if get_sec_msg(secbuffdata) != '无' else ''
    msg = f"""
道友的主功法：{mainbuffdata["name"] if mainbuffdata != None else '无'}
{mainbuffmsg}
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
        if secbuffdata['turncost'] == 0:
            msg = f"攻击{len(secbuffdata['atkvalue'])}次，造成{shmsg[:-1]}伤害{hpmsg}{mpmsg}，释放概率：{secbuffdata['rate']}%"
        else:
            msg = f"连续攻击{len(secbuffdata['atkvalue'])}次，造成{shmsg[:-1]}伤害{hpmsg}{mpmsg}，休息{secbuffdata['turncost']}回合，释放概率：{secbuffdata['rate']}%"
    elif secbuffdata['type'] == 2:
        msg = f"持续伤害，造成{secbuffdata['atkvalue']}倍攻击力伤害{hpmsg}{mpmsg}，持续{secbuffdata['turncost']}回合，释放概率：{secbuffdata['rate']}%"
    elif secbuffdata['type'] == 3:
        if secbuffdata['bufftype'] == 1:
            msg = f"增强自身，提高{secbuffdata['buffvalue']}倍攻击力{hpmsg}{mpmsg}，持续{secbuffdata['turncost']}回合，释放概率：{secbuffdata['rate']}%"
        elif secbuffdata['bufftype'] == 2:
            msg = f"增强自身，提高{secbuffdata['buffvalue'] * 100}%减伤率{hpmsg}{mpmsg}，持续{secbuffdata['turncost']}回合，释放概率：{secbuffdata['rate']}%"
    elif secbuffdata['type'] == 4:
        msg = f"封印对手{hpmsg}{mpmsg}，持续{secbuffdata['turncost']}回合，释放概率：{secbuffdata['rate']}%，命中成功率{secbuffdata['success']}%"

    return msg
