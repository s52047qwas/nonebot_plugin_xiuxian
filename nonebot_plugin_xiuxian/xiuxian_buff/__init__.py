from nonebot.adapters.onebot.v11 import (
    PRIVATE_FRIEND,
    Bot,
    GROUP,
    Message,
    MessageEvent,
    GroupMessageEvent,
    MessageSegment
)
from nonebot.log import logger
from datetime import datetime
from nonebot import get_bot, on_command, on_regex, require
from ..xiuxian2_handle import XiuxianDateManage, XiuxianJsonDate, OtherSet
from ..xiuxian_config import XiuConfig, JsonConfig
from ..utils import check_user
from ..data_source import jsondata
from ..read_buff import UserBuffDate, get_main_info_msg, get_user_buff, get_sec_msg
from nonebot.permission import SUPERUSER
from nonebot.params import CommandArg, RegexGroup
from ..player_fight import Player_fight
from .two_exp_cd import two_exp_cd
from ..utils import send_forward_msg_list, data_check_conf, check_user_type, get_msg_pic, pic_msg_format
from ..cd_manager import add_cd, check_cd, cd_msg
from ..read_buff import get_player_info, save_player_info
import random

two_exp_cd_up = require("nonebot_plugin_apscheduler").scheduler

buffinfo = on_command("我的功法", priority=5)
out_closing = on_command("出关", aliases={"灵石出关"}, priority=5)
mind_state = on_command("我的状态", priority=5)
qc = on_command("切磋", priority=5)
buff_help = on_command("功法帮助", priority=5)
blessed_spot_creat = on_command("洞天福地购买", priority=5)
blessed_spot_info = on_command("洞天福地查看", priority=5)
blessed_spot_rename = on_command("洞天福地改名", priority=5)
ling_tian_up = on_command("灵田开垦", priority=5)
two_exp = on_command("双修", priority=5, permission=GROUP)

sql_message = XiuxianDateManage()  # sql类

BLESSEDSPOTCOST = 500000

__buff_help__ = f"""
功法帮助信息:
指令：
1、我的功法：查看自身功法信息
2、切磋，at对应人员，不会消耗气血
3、洞天福地购买：购买洞天福地
4、洞天福地查看：查看自己的洞天福地
5、洞天福地改名+名字：修改自己洞天福地的名字
6、灵田开垦：提升灵田的等级，提高灵田结算的药材数量
7、双修，at对应人员，每天3次
""".strip()

# 每日0点重置用户双修次数
@two_exp_cd_up.scheduled_job("cron", hour=0, minute=0)
async def two_exp_cd_up_():
    two_exp_cd.re_data()
    logger.info('双修次数已更新！')

@buff_help.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    """修仙帮助"""
    await data_check_conf(bot, event)
    msg = __buff_help__
    msg = await pic_msg_format(msg, event)
    pic = await get_msg_pic(msg)#
    await buff_help.finish(MessageSegment.image(pic), at_sender=True)

@blessed_spot_creat.handle()
async def _(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    """洞天福地开启"""
    await data_check_conf(bot, event)
    isUser, user_info, msg = check_user(event)
    if not isUser:
        if XiuConfig().img:
            msg = await pic_msg_format(msg, event)
            pic = await get_msg_pic(msg)
            await blessed_spot_creat.finish(MessageSegment.image(pic))
        else:
            await blessed_spot_creat.finish(msg, at_sender=True)
    user_id = user_info.user_id
    if int(user_info.blessed_spot_flag) != 0:
        msg = f"道友已经拥有洞天福地了，请发送洞天福地查看吧~"
        if XiuConfig().img:
            msg = await pic_msg_format(msg, event)
            pic = await get_msg_pic(msg)
            await blessed_spot_creat.finish(MessageSegment.image(pic))
        else:
            await blessed_spot_creat.finish(msg, at_sender=True)
    if user_info.stone < BLESSEDSPOTCOST:
        msg = f"道友的灵石不足{BLESSEDSPOTCOST}枚，无法购买洞天福地"
        if XiuConfig().img:
            msg = await pic_msg_format(msg, event)
            pic = await get_msg_pic(msg)
            await blessed_spot_creat.finish(MessageSegment.image(pic))
        else:
            await blessed_spot_creat.finish(msg, at_sender=True)
    else:
        sql_message.update_ls(user_id, BLESSEDSPOTCOST, 2)
        sql_message.update_user_blessed_spot_flag(user_id)
        mix_elixir_info = get_player_info(user_id, "mix_elixir_info")
        mix_elixir_info['收取时间'] = str(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        save_player_info(user_id, mix_elixir_info, 'mix_elixir_info')
        msg = f"恭喜道友拥有了自己的洞天福地，请收集聚灵旗来提升洞天福地的等级吧~"
        if XiuConfig().img:
            msg = await pic_msg_format(msg, event)
            pic = await get_msg_pic(msg)
            await blessed_spot_creat.finish(MessageSegment.image(pic))
        else:
            await blessed_spot_creat.finish(msg, at_sender=True)

@blessed_spot_info.handle()
async def _(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    """洞天福地信息"""
    await data_check_conf(bot, event)
    isUser, user_info, msg = check_user(event)
    if not isUser:
        if XiuConfig().img:
            msg = await pic_msg_format(msg, event)
            pic = await get_msg_pic(msg)
            await blessed_spot_info.finish(MessageSegment.image(pic))
        else:
            await blessed_spot_info.finish(msg, at_sender=True)
    user_id = user_info.user_id
    if int(user_info.blessed_spot_flag) == 0:
        msg = f"道友还没有洞天福地呢，请发送洞天福地购买吧~"
        if XiuConfig().img:
            msg = await pic_msg_format(msg, event)
            pic = await get_msg_pic(msg)
            await blessed_spot_info.finish(MessageSegment.image(pic))
        else:
            await blessed_spot_info.finish(msg, at_sender=True)
    msg = f'\n道友的洞天福地：\n'
    user_buff_data = UserBuffDate(user_id).BuffInfo
    if user_info.blessed_spot_name == 0:
        blessed_spot_name = "尚未命名"
    else:
        blessed_spot_name = user_info.blessed_spot_name
    mix_elixir_info = get_player_info(user_id, "mix_elixir_info")
    msg += f"名字：{blessed_spot_name}\n"
    msg += f"修炼速度：增加{int(user_buff_data.blessed_spot) * 100}%\n"
    msg += f"灵田数量：{mix_elixir_info['灵田数量']}"
    if XiuConfig().img:
        msg = await pic_msg_format(msg, event)
        pic = await get_msg_pic(msg)
        await blessed_spot_info.finish(MessageSegment.image(pic))
    else:
        await blessed_spot_info.finish(msg, at_sender=True)
    
@ling_tian_up.handle()
async def _(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    """洞天福地灵田升级"""
    await data_check_conf(bot, event)
    isUser, user_info, msg = check_user(event)
    if not isUser:
        if XiuConfig().img:
            msg = await pic_msg_format(msg, event)
            pic = await get_msg_pic(msg)
            await ling_tian_up.finish(MessageSegment.image(pic))
        else:
            await ling_tian_up.finish(msg, at_sender=True)
    user_id = user_info.user_id
    if int(user_info.blessed_spot_flag) == 0:
        msg = f"道友还没有洞天福地呢，请发送洞天福地购买吧~"
        if XiuConfig().img:
            msg = await pic_msg_format(msg, event)
            pic = await get_msg_pic(msg)
            await ling_tian_up.finish(MessageSegment.image(pic))
        else:
            await ling_tian_up.finish(msg, at_sender=True)
    LINGTIANCONFIG = {
        "1":{
            "level_up_cost":500000
        },
        "2":{
            "level_up_cost":1000000
        },
        "3":{
            "level_up_cost":2000000
        },
        "4":{
            "level_up_cost":3000000
        },
        "5":{
            "level_up_cost":4000000
        }
    }
    mix_elixir_info = get_player_info(user_id, "mix_elixir_info")
    now_num = mix_elixir_info['灵田数量']
    if now_num == len(LINGTIANCONFIG) + 1:
        msg = f"道友的灵田已全部开垦完毕，无法继续开垦了！"
    else:
        cost = LINGTIANCONFIG[str(now_num)]['level_up_cost']
        if int(user_info.stone) < cost:
            msg = f"本次开垦需要灵石：{cost}，道友的灵石不足！"
        else:
            msg = f"道友成功消耗灵石：{cost}，灵田数量+1，目前数量：{now_num + 1}"
            mix_elixir_info['灵田数量'] = now_num + 1
            save_player_info(user_id, mix_elixir_info, 'mix_elixir_info')
            sql_message.update_ls(user_id, cost, 2)
    if XiuConfig().img:
        msg = await pic_msg_format(msg, event)
        pic = await get_msg_pic(msg)
        await ling_tian_up.finish(MessageSegment.image(pic))
    else:
        await ling_tian_up.finish(msg, at_sender=True)

@blessed_spot_rename.handle()
async def _(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    """洞天福地改名"""
    await data_check_conf(bot, event)
    isUser, user_info, msg = check_user(event)
    if not isUser:
        if XiuConfig().img:
            msg = await pic_msg_format(msg, event)
            pic = await get_msg_pic(msg)
            await blessed_spot_rename.finish(MessageSegment.image(pic))
        else:
            await blessed_spot_rename.finish(msg, at_sender=True)
    user_id = user_info.user_id
    if int(user_info.blessed_spot_flag) == 0:
        msg = f"道友还没有洞天福地呢，请发送洞天福地购买吧~"
        if XiuConfig().img:
            msg = await pic_msg_format(msg, event)
            pic = await get_msg_pic(msg)
            await blessed_spot_rename.finish(MessageSegment.image(pic))
        else:
            await blessed_spot_rename.finish(msg, at_sender=True)
    arg = args.extract_plain_text().strip()
    arg = str(arg)
    if arg == "":
        msg = "请输入洞天福地的名字！"
        if XiuConfig().img:
            msg = await pic_msg_format(msg, event)
            pic = await get_msg_pic(msg)
            await blessed_spot_rename.finish(MessageSegment.image(pic))
        else:
            await blessed_spot_rename.finish(msg, at_sender=True)
    if len(arg) > 9:
        msg = f"洞天福地的名字不可大于9位，请重新命名"
    else:
        msg = f"道友的洞天福地成功改名为：{arg}"
        sql_message.update_user_blessed_spot_name(user_id, arg)
    if XiuConfig().img:
        msg = await pic_msg_format(msg, event)
        pic = await get_msg_pic(msg)
        await blessed_spot_rename.finish(MessageSegment.image(pic))
    else:
        await blessed_spot_rename.finish(msg, at_sender=True)
    

@qc.handle()
async def _(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    """切磋，不会掉血"""
    await data_check_conf(bot, event)
    isUser, user_info, msg = check_user(event)
    if not isUser:
        if XiuConfig().img:
            msg = await pic_msg_format(msg, event)
            pic = await get_msg_pic(msg)
            await qc.finish(MessageSegment.image(pic))
        else:
            await qc.finish(msg, at_sender=True)
    user_id = user_info.user_id
    
    give_qq = None  # 艾特的时候存到这里
    for arg in args:
        if arg.type == "at":
            give_qq = arg.data.get("qq", "")
    if give_qq:
        if give_qq == str(user_id):
            msg = "道友不会左右互搏之术！"
            if XiuConfig().img:
                msg = await pic_msg_format(msg, event)
                pic = await get_msg_pic(msg)
                await qc.finish(MessageSegment.image(pic))
            else:
                await qc.finish(msg, at_sender=True)
                
        if cd := check_cd(event, '切磋'):
            # 如果 CD 还没到 则直接结束
            msg = cd_msg(cd)
            if XiuConfig().img:
                msg = await pic_msg_format(msg, event)
                pic = await get_msg_pic(msg)
                await qc.finish(MessageSegment.image(pic))
            else:
                await qc.finish(msg, at_sender=True)
        player1 = {"user_id": None, "道号": None, "气血": None,
                   "攻击": None, "真元": None, '会心': None, '防御': 0, 'exp': 0}
        player2 = {"user_id": None, "道号": None, "气血": None,
                   "攻击": None, "真元": None, '会心': None, '防御': 0, 'exp': 0}
        user1 = sql_message.get_user_real_info(user_id)
        user1_weapon_data = UserBuffDate(user_id).get_user_weapon_data()
        if user1_weapon_data != None:
            player1['会心'] = int(user1_weapon_data['crit_buff'] * 100)
        else:
            player1['会心'] = 1

        user2 = sql_message.get_user_real_info(give_qq)
        user2_weapon_data = UserBuffDate(give_qq).get_user_weapon_data()
        if user2_weapon_data != None:
            player2['会心'] = int(user2_weapon_data['crit_buff'] * 100)
        else:
            player2['会心'] = 1
        player1['user_id'] = user1.user_id
        player1['道号'] = user1.user_name
        player1['气血'] = user1.hp
        player1['攻击'] = user1.atk
        player1['真元'] = user1.mp
        player1['exp'] = user1.exp

        player2['user_id'] = user2.user_id
        player2['道号'] = user2.user_name
        player2['气血'] = user2.hp
        player2['攻击'] = user2.atk
        player2['真元'] = user2.mp
        player2['exp'] = user2.exp
        
        result, victor = Player_fight(player1, player2, 1, bot.self_id)
        add_cd(event, 300, '切磋')
        # await send_forward_msg(bot, event, '决斗场', bot.self_id, result)
        await send_forward_msg_list(bot, event, result)
        msg = f"获胜的是{victor}"
        if XiuConfig().img:
            msg = await pic_msg_format(msg, event)
            pic = await get_msg_pic(msg)
            await qc.finish(MessageSegment.image(pic))
        else:
            await qc.finish(msg, at_sender=True)
    else:
        msg = "没有对方的信息！"
        if XiuConfig().img:
            msg = await pic_msg_format(msg, event)
            pic = await get_msg_pic(msg)
            await qc.finish(MessageSegment.image(pic))
        else:
            await qc.finish(msg, at_sender=True)

@out_closing.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    """出关"""
    await data_check_conf(bot, event)
    user_type = 0  # 状态0为无事件
    isUser, user_info, msg = check_user(event)
    if not isUser:
        if XiuConfig().img:
            msg = await pic_msg_format(msg, event)
            pic = await get_msg_pic(msg)
            await out_closing.finish(MessageSegment.image(pic))
        else:
            await out_closing.finish(msg, at_sender=True)
    user_id = user_info.user_id
    user_mes = sql_message.get_user_message(user_id)  # 获取用户信息
    level = user_mes.level
    use_exp = user_mes.exp
    hp_speed = 25
    mp_speed = 50

    max_exp = (
            int(OtherSet().set_closing_type(level)) * XiuConfig().closing_exp_upper_limit
    )  # 获取下个境界需要的修为 * 1.5为闭关上限
    user_get_exp_max = int(max_exp) - use_exp

    if user_get_exp_max < 0:
        # 校验当当前修为超出上限的问题，不可为负数
        user_get_exp_max = 0

    now_time = datetime.now()
    user_cd_message = sql_message.get_user_cd(user_id)
    is_type, msg = check_user_type(user_id, 1)
    if not is_type:
        if XiuConfig().img:
            msg = await pic_msg_format(msg, event)
            pic = await get_msg_pic(msg)
            await out_closing.finish(MessageSegment.image(pic))
        else:
            await out_closing.finish(msg, at_sender=True)
    else:
        # 用户状态为1
        in_closing_time = datetime.strptime(
            user_cd_message.create_time, "%Y-%m-%d %H:%M:%S.%f"
        )  # 进入闭关的时间
        exp_time = (
                OtherSet().date_diff(now_time, in_closing_time) // 60
        )  # 闭关时长计算(分钟) = second // 60
        level_rate = sql_message.get_root_rate(user_mes.root_type)  # 灵根倍率
        realm_rate = jsondata.level_data()[level]["spend"]  # 境界倍率
        user_buff_data = UserBuffDate(user_id)
        mainbuffdata = user_buff_data.get_user_main_buff_data()
        mainbuffratebuff = mainbuffdata['ratebuff'] if mainbuffdata != None else 0#功法修炼倍率
        exp = int(
            (exp_time * XiuConfig().closing_exp) * ((level_rate * realm_rate * (1 + mainbuffratebuff)) + int(user_buff_data.BuffInfo.blessed_spot))#洞天福地为加法
        )  # 本次闭关获取的修为

        if exp >= user_get_exp_max:
            # 用户获取的修为到达上限
            sql_message.in_closing(user_id, user_type)
            sql_message.update_exp(user_id, user_get_exp_max)
            sql_message.update_power2(user_id)  # 更新战力

            result_msg, result_hp_mp = OtherSet().send_hp_mp(user_id, int(exp * hp_speed), int(exp*mp_speed))
            sql_message.update_user_attribute(user_id, result_hp_mp[0], result_hp_mp[1], int(result_hp_mp[2] / 10))
            msg = "闭关结束，本次闭关到达上限，共增加修为：{}{}{}".format(user_get_exp_max, result_msg[0], result_msg[1])
            if XiuConfig().img:
                msg = await pic_msg_format(msg, event)
                pic = await get_msg_pic(msg)
                await out_closing.finish(MessageSegment.image(pic))
            else:
                await out_closing.finish(msg, at_sender=True)
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
                    msg = "闭关结束，共闭关{}分钟，本次闭关增加修为：{}，消耗灵石{}枚{}{}".format(exp_time, exp, int(exp / 2),
                                                                      result_msg[0], result_msg[1])
                    if XiuConfig().img:
                        msg = await pic_msg_format(msg, event)
                        pic = await get_msg_pic(msg)
                        await out_closing.finish(MessageSegment.image(pic))
                    else:
                        await out_closing.finish(msg, at_sender=True)
                else:
                    exp = exp + user_stone
                    sql_message.in_closing(user_id, user_type)
                    sql_message.update_exp(user_id, exp)
                    sql_message.update_ls(user_id, user_stone, 2)
                    sql_message.update_power2(user_id)  # 更新战力
                    result_msg, result_hp_mp = OtherSet().send_hp_mp(user_id, int(exp * hp_speed), int(exp * mp_speed))
                    sql_message.update_user_attribute(user_id, result_hp_mp[0], result_hp_mp[1],
                                                      int(result_hp_mp[2] / 10))
                    msg = "闭关结束，共闭关{}分钟，本次闭关增加修为：{}，消耗灵石{}枚{}{}".format(exp_time, exp, user_stone,
                                                                  result_msg[0], result_msg[1])
                    if XiuConfig().img:
                        msg = await pic_msg_format(msg, event)
                        pic = await get_msg_pic(msg)
                        await out_closing.finish(MessageSegment.image(pic))
                    else:
                        await out_closing.finish(msg, at_sender=True)
            else:
                sql_message.in_closing(user_id, user_type)
                sql_message.update_exp(user_id, exp)
                sql_message.update_power2(user_id)  # 更新战力
                result_msg, result_hp_mp = OtherSet().send_hp_mp(user_id, int(exp * hp_speed), int(exp * mp_speed))
                sql_message.update_user_attribute(user_id, result_hp_mp[0], result_hp_mp[1], int(result_hp_mp[2] / 10))
                msg = "闭关结束，共闭关{}分钟，本次闭关增加修为：{}{}{}".format(exp_time, exp, result_msg[0],
                                                          result_msg[1])
                if XiuConfig().img:
                    msg = await pic_msg_format(msg, event)
                    pic = await get_msg_pic(msg)
                    await out_closing.finish(MessageSegment.image(pic))
                else:
                    await out_closing.finish(msg, at_sender=True)

@mind_state.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    """我的状态信息。"""
    await data_check_conf(bot, event)
    isUser, user_msg, msg = check_user(event)
    if not isUser:
        if XiuConfig().img:
            msg = await pic_msg_format(msg, event)
            pic = await get_msg_pic(msg)
            await mind_state.finish(MessageSegment.image(pic))
        else:
            await mind_state.finish(msg, at_sender=True)
    user_id = user_msg.user_id


    if user_msg.hp is None or user_msg.hp == 0 or user_msg.hp == 0:
        sql_message.update_user_hp(user_id)
    user_msg = sql_message.get_user_real_info(user_id)
    
    level_rate = sql_message.get_root_rate(user_msg.root_type)  # 灵根倍率
    realm_rate = jsondata.level_data()[user_msg.level]["spend"]  # 境界倍率
    user_buff_data = UserBuffDate(user_id)
    main_buff_data = user_buff_data.get_user_main_buff_data()
    user_weapon_data = user_buff_data.get_user_weapon_data()
    if user_weapon_data != None:
        crit_buff = int(user_weapon_data['crit_buff'] * 100)
    else:
        crit_buff = 1
    
    user_armor_data = user_buff_data.get_user_armor_buff_data()
    if user_armor_data != None:
        def_buff = int(user_armor_data['def_buff'] * 100)
    else:
        def_buff = 0

    main_buff_rate_buff = main_buff_data['ratebuff'] if main_buff_data != None else 0
    main_hp_buff = main_buff_data['hpbuff'] if main_buff_data != None else 0
    main_mp_buff = main_buff_data['mpbuff'] if main_buff_data != None else 0
    user = f"""道号：{user_msg.user_name}
气血：{user_msg.hp}/{int((user_msg.exp/2) * (1 + main_hp_buff))}
真元：{user_msg.mp}/{int((user_msg.exp) * (1 + main_mp_buff))}
攻击：{user_msg.atk}
攻击修炼：{user_msg.atkpractice}级(提升攻击力{user_msg.atkpractice * 4}%)
修炼效率：{int(((level_rate * realm_rate) * (1 + main_buff_rate_buff) + int(user_buff_data.BuffInfo.blessed_spot))  * 100)}%
会心：{crit_buff}%
减伤率：{def_buff}%
"""
    if XiuConfig().img:
        msg = await pic_msg_format(msg, event)
        pic = await get_msg_pic(user)
        await mind_state.finish(MessageSegment.image(pic))
    else:
        await mind_state.finish(user, at_sender=True)


@buffinfo.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    await data_check_conf(bot, event)

    isUser, user_info, msg = check_user(event)
    if not isUser:
        if XiuConfig().img:
            msg = await pic_msg_format(msg, event)
            pic = await get_msg_pic(msg)
            await buffinfo.finish(MessageSegment.image(pic))
        else:
            await buffinfo.finish(msg, at_sender=True)
    user_id = user_info.user_id
    mainbuffdata = UserBuffDate(user_id).get_user_main_buff_data()
    if mainbuffdata != None:
        s, mainbuffmsg = get_main_info_msg(str(get_user_buff(user_id).main_buff))
    else:
        mainbuffmsg = ''
    secbuffdata = UserBuffDate(user_id).get_user_sec_buff_data()
    secbuffmsg = get_sec_msg(secbuffdata) if get_sec_msg(secbuffdata) != '无' else ''
    msg = f"""
道友的主功法：{mainbuffdata["name"] if mainbuffdata != None else '无'}
{mainbuffmsg}
道友的神通：{secbuffdata["name"] if secbuffdata != None else '无'}
{secbuffmsg}
"""
    if XiuConfig().img:
        msg = await pic_msg_format(msg, event)
        pic = await get_msg_pic(msg)
        await buffinfo.finish(MessageSegment.image(pic))
    else:
        await buffinfo.finish(msg, at_sender=True)


two_exp_limit = 3


@two_exp.handle()
async def two_exp_(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    """双修"""
    send_group_id = event.group_id
    global two_exp_limit
    isUser, user_1, msg = check_user(event)
    if not isUser:
        if XiuConfig().img:
            pic = await get_msg_pic(f"@{event.sender.nickname}\n" + msg)
            await bot.send_group_msg(group_id=int(send_group_id), message=MessageSegment.image(pic))
        else:
            await bot.send_group_msg(group_id=int(send_group_id), message=msg)
        await two_exp.finish()

    two_qq = None  # 艾特的时候存到这里
    for arg in args:
        if arg.type == "at":
            two_qq = arg.data.get("qq", "")
    if two_qq is None:
        msg = "请at你的道侣,与其一起双修！"
        if XiuConfig().img:
            pic = await get_msg_pic(f"@{event.sender.nickname}\n" + msg)
            await bot.send_group_msg(group_id=int(send_group_id), message=MessageSegment.image(pic))
        else:
            await bot.send_group_msg(group_id=int(send_group_id), message=msg)
        await two_exp.finish()

    user_2 = sql_message.get_user_message(two_qq)
    if int(user_1.user_id) == int(two_qq):
        msg = "道友无法与自己双修！"
        if XiuConfig().img:
            pic = await get_msg_pic(f"@{event.sender.nickname}\n" + msg)
            await bot.send_group_msg(group_id=int(send_group_id), message=MessageSegment.image(pic))
        else:
            await bot.send_group_msg(group_id=int(send_group_id), message=msg)
        await two_exp.finish()
    if user_2:
        exp_1 = user_1.exp
        exp_2 = user_2.exp
        if exp_2 > exp_1:
            msg = "修仙大能看了看你，不屑一顾，扬长而去！"
            if XiuConfig().img:
                pic = await get_msg_pic(f"@{event.sender.nickname}\n" + msg)
                await bot.send_group_msg(group_id=int(send_group_id), message=MessageSegment.image(pic))
            else:
                await bot.send_group_msg(group_id=int(send_group_id), message=msg)
            await two_exp.finish()
        else:
            limt_1 = two_exp_cd.find_user(user_1.user_id)
            limt_2 = two_exp_cd.find_user(user_2.user_id)
            # 加入传承
            if limt_1 >= two_exp_limit:
                msg = "道友今天双修次数已经到达上限！"
                if XiuConfig().img:
                    pic = await get_msg_pic(f"@{event.sender.nickname}\n" + msg)
                    await bot.send_group_msg(group_id=int(send_group_id), message=MessageSegment.image(pic))
                else:
                    await bot.send_group_msg(group_id=int(send_group_id), message=msg)
                await two_exp.finish()
            if limt_2 >= two_exp_limit:
                msg = "对方今天双修次数已经到达上限！"
                if XiuConfig().img:
                    pic = await get_msg_pic(f"@{event.sender.nickname}\n" + msg)
                    await bot.send_group_msg(group_id=int(send_group_id), message=MessageSegment.image(pic))
                else:
                    await bot.send_group_msg(group_id=int(send_group_id), message=msg)
                await two_exp.finish()
            max_exp_1 = (
                    int(OtherSet().set_closing_type(user_1.level)) * XiuConfig().closing_exp_upper_limit
            )  # 获取下个境界需要的修为 * 1.5为闭关上限
            max_exp_2 = (
                    int(OtherSet().set_closing_type(user_2.level)) * XiuConfig().closing_exp_upper_limit
            )
            user_get_exp_max_1 = int(max_exp_1) - user_1.exp
            user_get_exp_max_2 = int(max_exp_2) - user_2.exp

            if user_get_exp_max_1 < 0:
                user_get_exp_max_1 = 0
            if user_get_exp_max_2 < 0:
                user_get_exp_max_2 = 0
            msg = ""
            msg += f"{user_1.user_name}与{user_2.user_name}情投意合，神魂交融，于某地一起修炼了一晚。"
            if random.randint(1, 100) in [13, 14, 52, 10, 66]:
                exp = int((exp_1 + exp_2) * 0.0045)
                if exp >= user_get_exp_max_1:
                    sql_message.update_exp(user_1.user_id, user_get_exp_max_1)
                    msg += f"{user_1.user_name}修为到达上限，增加修为{user_get_exp_max_1}。"
                else:
                    sql_message.update_exp(user_1.user_id, exp)
                    msg += f"{user_1.user_name}增加修为{exp}。"
                sql_message.update_power2(user_1.user_id)

                if exp >= user_get_exp_max_2:
                    sql_message.update_exp(user_2.user_id, user_get_exp_max_2)
                    msg += f"{user_2.user_name}修为到达上限，增加修为{user_get_exp_max_2}。"
                else:
                    sql_message.update_exp(user_2.user_id, exp)
                    msg += f"{user_2.user_name}增加修为{exp}。"
                sql_message.update_power2(user_2.user_id)
                sql_message.update_levelrate(user_1.user_id, user_1.level_up_rate + 2)
                sql_message.update_levelrate(user_2.user_id, user_2.level_up_rate + 2)
                two_exp_cd.add_user(user_1.user_id)
                two_exp_cd.add_user(user_2.user_id)
                msg += f"离开时双方互相留法宝为对方护道，双方各增加突破概率2%。"
                if XiuConfig().img:
                    pic = await get_msg_pic(f"@{event.sender.nickname}\n" + msg)
                    await bot.send_group_msg(group_id=int(send_group_id), message=MessageSegment.image(pic))
                else:
                    await bot.send_group_msg(group_id=int(send_group_id), message=msg)
                await two_exp.finish()
            else:
                exp = int((exp_1 + exp_2) * 0.0045)
                if exp >= user_get_exp_max_1:
                    sql_message.update_exp(user_1.user_id, user_get_exp_max_1)
                    msg += f"{user_1.user_name}修为到达上限，增加修为{user_get_exp_max_1}。"
                else:
                    sql_message.update_exp(user_1.user_id, exp)
                    msg += f"{user_1.user_name}增加修为{exp}。"
                sql_message.update_power2(user_1.user_id)

                if exp >= user_get_exp_max_2:
                    sql_message.update_exp(user_2.user_id, user_get_exp_max_2)
                    msg += f"{user_2.user_name}修为到达上限，增加修为{user_get_exp_max_2}。"
                else:
                    sql_message.update_exp(user_2.user_id, exp)
                    msg += f"{user_2.user_name}增加修为{exp}。"
                sql_message.update_power2(user_2.user_id)
                two_exp_cd.add_user(user_1.user_id)
                two_exp_cd.add_user(user_2.user_id)
                if XiuConfig().img:
                    pic = await get_msg_pic(f"@{event.sender.nickname}\n" + msg)
                    await bot.send_group_msg(group_id=int(send_group_id), message=MessageSegment.image(pic))
                else:
                    await bot.send_group_msg(group_id=int(send_group_id), message=msg)
                await two_exp.finish()
    else:
        msg = "修仙者应一心向道，务要留恋凡人！"
        if XiuConfig().img:
            pic = await get_msg_pic(f"@{event.sender.nickname}\n" + msg)
            await bot.send_group_msg(group_id=int(send_group_id), message=MessageSegment.image(pic))
        else:
            await bot.send_group_msg(group_id=int(send_group_id), message=msg)
        await two_exp.finish()


