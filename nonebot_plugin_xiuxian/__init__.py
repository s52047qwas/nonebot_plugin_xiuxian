import random
import re
from datetime import datetime

from .help import *
from nonebot import get_driver
from nonebot import require
from nonebot.adapters.onebot.v11 import (
    PRIVATE_FRIEND,
    Bot,
    GROUP,
    Message,
    MessageEvent,
    GroupMessageEvent,
)
from nonebot.log import logger
from typing import Any, Tuple
from nonebot.params import CommandArg, RegexGroup

from .command import *
from .cd_manager import add_cd, check_cd, cd_msg
from .data_source import jsondata
from .xiuxian2_handle import XiuxianDateManage, XiuxianJsonDate, OtherSet
from .xiuxian_config import XiuConfig, JsonConfig
from .xiuxian_opertion import do_is_work

# 定时任务
scheduler = require("nonebot_plugin_apscheduler").scheduler

driver = get_driver()
work = {}  # 悬赏令信息记录
sect_out_check = {}  # 退出宗门或踢出宗门信息记录
sql_message = XiuxianDateManage()  # sql类


@command.run_xiuxian.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    """加入修仙"""
    user_id = event.get_user_id()
    user_name = (
        event.sender.card if event.sender.card else event.sender.nickname
    )  # 获取为用户名
    root, root_type = XiuxianJsonDate().linggen_get()  # 获取灵根，灵根类型

    rate = sql_message.get_root_rate(root_type)  # 灵根倍率
    power = 100 * float(rate)  # 战力=境界的power字段 * 灵根的rate字段
    create_time = str(datetime.now())

    msg = sql_message.create_user(
        user_id, root, root_type, int(power), create_time, user_name
    )
    await run_xiuxian.finish(msg, at_sender=True)


@command.xiuxian_message.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    """我的修仙信息"""
    try:
        user_id, group_id, mess = await data_check(bot, event)
    except MsgError:
        return

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

    msg = f"""{user_name}道友的信息
灵根为：{mess.root}({mess.root_type}+{int(level_rate * 100)}%)
当前境界：{mess.level}(境界+{int(realm_rate * 100)}%)
当前灵石：{mess.stone}
当前修为：{mess.exp}(修炼效率+{int((level_rate * realm_rate) * 100)}%)
突破状态：{get_exp}
你的战力为：{int(mess.exp * level_rate * realm_rate)}"""

    await run_xiuxian.finish(msg, at_sender=True)


@sign_in.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    """修仙签到"""
    try:
        user_id, group_id, mess = await data_check(bot, event)
    except MsgError:
        return

    result = sql_message.get_sign(user_id)
    sql_message.update_power2(user_id)
    await sign_in.send(result, at_sender=True)


@command.help_in.handle()
async def _():
    """修仙帮助"""
    msg = help.__xiuxian_notes__
    await help_in.send(msg, at_sender=True)


@command.dufang.handle()
async def _(bot: Bot, event: MessageEvent, args: Tuple[Any, ...] = RegexGroup()):
    try:
        user_id, group_id, mess = await data_check(bot, event)
    except MsgError:
        return

    if cd := check_cd(event):
        # 如果 CD 还没到 则直接结束
        await dufang.finish(cd_msg(cd), at_sender=True)

    user_message = sql_message.get_user_message(user_id)

    add_cd(event, XiuConfig().dufang_cd)

    if args[2] is None:
        await dufang.finish(f"请输入正确的指令，例如金银阁10大、金银阁10猜3")

    price = args[1]  # 300
    mode = args[2]  # 大、小、猜
    mode_num = 0
    if mode == '猜':
        mode_num = args[3]  # 猜的数值
        if str(mode_num) not in ['1', '2', '3', '4', '5', '6']:
            await dufang.finish(f"请输入正确的指令，例如金银阁10大、金银阁10猜3")

    price_num = int(price)
    if int(user_message.stone) < int(price_num):
        await dufang.finish("道友的金额不足，请重新输入！")

    value = random.randint(1, 6)
    msg = Message("[CQ:dice,value={}]".format(value))

    if value >= 4 and str(mode) == "大":
        sql_message.update_ls(user_id, price_num, 1)
        await dufang.send(msg)
        await dufang.finish(
            "最终结果为{}，你猜对了，收获灵石{}块".format(value, price_num), at_sender=True
        )
    elif value <= 3 and str(mode) == "小":
        sql_message.update_ls(user_id, price_num, 1)
        await dufang.send(msg)
        await dufang.finish(
            "最终结果为{}，你猜对了，收获灵石{}块".format(value, price_num), at_sender=True
        )
    elif str(value) == str(mode_num) and str(mode) == "猜":
        sql_message.update_ls(user_id, price_num * 5, 1)
        await dufang.send(msg)
        await dufang.finish(
            "最终结果为{}，你猜对了，收获灵石{}块".format(value, price_num * 5), at_sender=True
        )
    else:
        sql_message.update_ls(user_id, price_num, 2)
        await dufang.send(msg)
        await dufang.finish(
            "最终结果为{}，你猜错了，损失灵石{}块".format(value, price_num), at_sender=True
        )


@command.restart.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    """重置灵根信息"""
    try:
        user_id, group_id, mess = await data_check(bot, event)
    except MsgError:
        return

    name, root_type = XiuxianJsonDate().linggen_get()
    result = sql_message.ramaker(name, root_type, user_id)
    sql_message.update_power2(user_id)  # 更新战力
    await restart.send(message=result, at_sender=True)


@command.rank.handle()
async def _(event: GroupMessageEvent):
    """排行榜"""
    message = str(event.message)

    rank_msg = r'[\u4e00-\u9fa5]+'
    message = re.findall(rank_msg, message)
    if message:
        message = message[0]

    if message == "排行榜" or message == "修仙排行榜" or message == "境界排行榜":
        p_rank = sql_message.realm_top()
        await rank.finish(message=p_rank)
    elif message == "灵石排行榜":
        a_rank = sql_message.stone_top()
        await rank.finish(message=a_rank)
    elif message == "战力排行榜":
        a_rank = sql_message.power_top()
        await rank.finish(message=a_rank)
    elif message in ["宗门排行榜", "宗门建设度排行榜"]:
        s_rank, _ = sql_message.scale_top()
        await rank.finish(message=s_rank)


# 重置每日签到
@scheduler.scheduled_job(
    "cron",
    hour=0,
    minute=0,
)
async def _():
    sql_message.singh_remake()
    logger.info("每日修仙签到重置成功！")


@command.time_mes.handle()
async def _(event: GroupMessageEvent):
    """押注超时校验"""
    msg = event.message
    if str(msg) == "金银阁":
        await time_mes.finish(f"指令已更新，例：金银阁10大、金银阁10猜3")


@command.remaname.handle()
async def _(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    """修改道号"""
    try:
        user_id, group_id, mess = await data_check(bot, event)
    except MsgError:
        return

    user_name = args.extract_plain_text().strip()

    len_username = len(user_name.encode('gbk'))
    if len_username > 20:
        await remaname.finish("道号长度过长，请修改后重试！")

    mes = sql_message.update_user_name(user_id, user_name)
    await remaname.finish(mes)


@command.in_closing.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    """闭关"""
    user_type = 1  # 状态1为闭关
    try:
        user_id, group_id, mess = await data_check(bot, event)
    except MsgError:
        return

    user_cd_message = sql_message.get_user_cd(user_id)

    if user_cd_message is None:
        sql_message.in_closing(user_id, user_type)
        await in_closing.finish("进入闭关状态，如需出关，发送【出关】！", at_sender=True)

    elif user_cd_message.type == 0:
        # 状态0为未进行事件，可闭关
        sql_message.in_closing(user_id, user_type)
        await in_closing.finish("进入闭关状态，如需出关，发送【出关】！", at_sender=True)

    elif user_cd_message.type == 1:
        # 状态1为已在闭关中
        await in_closing.finish("已经在闭关中，请输入【出关】结束！", at_sender=True)

    elif user_cd_message.type == 2:
        # 状态2为已悬赏令任务进行中
        await in_closing.finish("悬赏令事件进行中，请输入【悬赏令结算】结束！", at_sender=True)


@command.out_closing.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    """出关"""
    user_type = 0  # 状态0为无事件
    try:
        user_id, group_id, mess = await data_check(bot, event)
    except MsgError:
        return

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
        exp = int(
            exp_time * XiuConfig().closing_exp * level_rate * realm_rate
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


async def get_group_id(session_id):
    """获取group_id"""
    res = re.findall("_(.*)_", session_id)
    group_id = res[0]
    return group_id


@command.level_up.handle()
async def update_level(bot: Bot, event: GroupMessageEvent):
    """突破"""
    try:
        user_id, group_id, mess = await data_check(bot, event)
    except MsgError:
        return

    if mess.hp is None:
        # 判断用户气血是否为空
        sql_message.update_user_hp(user_id)

    user_msg = sql_message.get_user_message(user_id)  # 用户信息
    user_leveluprate = int(user_msg.level_up_rate)  # 用户失败次数加成

    level_cd = user_msg.level_up_cd
    if level_cd:
        # 校验是否存在CD
        time_now = datetime.now()
        cd = OtherSet().date_diff(time_now, level_cd)  # 获取second
        if cd < XiuConfig().level_up_cd * 60:
            # 如果cd小于配置的cd，返回等待时间
            await level_up.finish(
                "目前无法突破，还需要{}分钟".format(XiuConfig().level_up_cd - (cd // 60))
            )
    else:
        pass

    level_name = user_msg.level  # 用户境界
    exp = user_msg.exp  # 用户修为
    level_rate = jsondata.level_rate_data()[level_name]  # 对应境界突破的概率

    le = OtherSet().get_type(exp, level_rate + user_leveluprate, level_name)

    if le == "失败":
        # 突破失败
        sql_message.updata_level_cd(user_id)  # 更新突破CD

        # 失败惩罚，随机扣减修为
        percentage = random.randint(
            XiuConfig().level_punishment_floor, XiuConfig().level_punishment_limit
        )
        now_exp = int(int(exp) * (percentage / 100))

        sql_message.update_j_exp(user_id, now_exp)  # 更新用户修为

        update_rate = 1 if int(level_rate * XiuConfig().level_up_probability) <= 1 else int(
            level_rate * XiuConfig().level_up_probability)  # 失败增加突破几率

        sql_message.update_levelrate(user_id, user_leveluprate + update_rate)

        await level_up.finish("道友突破失败,境界受损,修为减少{}，下次突破成功率增加{}%，道友不要放弃！".format(now_exp, update_rate))

    elif type(le) == list:
        # 突破成功
        sql_message.updata_level(user_id, le[0])  # 更新境界
        sql_message.update_power2(user_id)  # 更新战力
        sql_message.updata_level_cd(user_id)  # 更新CD
        # sql_message.update_user_attribute(user_id, )
        sql_message.update_levelrate(user_id, 0)
        sql_message.update_user_hp(user_id)  #重置用户HP，mp，atk状态
        await level_up.finish("恭喜道友突破{}成功".format(le[0]))
    else:
        # 最高境界
        await level_up.finish(le)


@command.give_stone.handle()
async def _(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    """送灵石"""
    try:
        user_id, group_id, mess = await data_check(bot, event)
    except MsgError:
        return

    user_message = sql_message.get_user_message(user_id)
    if user_message is None:
        await give_stone.finish("修仙界没有你的信息！请输入我要修仙，踏入修行")

    user_stone_num = user_message.stone
    give_qq = None  # 艾特的时候存到这里
    msg = args.extract_plain_text().strip()

    stone_num = re.findall("\d+", msg)  # 灵石数
    nick_name = re.findall("\D+", msg)  # 道号

    if stone_num:
        pass
    else:
        await give_stone.finish("请输入正确的灵石数量！")

    give_stone_num = stone_num[0]

    if int(give_stone_num) > int(user_stone_num):
        await give_stone.finish("道友的灵石不够，请重新输入！")

    for arg in args:
        if arg.type == "at":
            give_qq = arg.data.get("qq", "")

    if give_qq:
        if give_qq == user_id:
            await give_stone.finish("请不要送灵石给自己！")
        else:
            give_user = sql_message.get_user_message(give_qq)
            if give_user:
                sql_message.update_ls(user_id, give_stone_num, 2)  # 减少用户灵石
                give_stone_num2 = int(give_stone_num) * 0.03
                num = int(give_stone_num) - int(give_stone_num2)
                sql_message.update_ls(give_qq, num, 1)  # 增加用户灵石

                await give_stone.finish(
                    "共赠送{}枚灵石给{}道友！收取手续费{}枚".format(
                        give_stone_num, give_user.user_name, int(give_stone_num2)
                    )
                )
            else:
                await give_stone.finish("对方未踏入修仙界，不可赠送！")

    if nick_name:
        give_message = sql_message.get_user_message2(nick_name[0])
        if give_message:
            if give_message.user_name == user_message.user_name:
                await give_stone.finish("请不要送灵石给自己！")
            else:
                sql_message.update_ls(user_id, give_stone_num, 2)  # 减少用户灵石
                give_stone_num2 = int(give_stone_num) * 0.03
                num = int(give_stone_num) - int(give_stone_num2)
                sql_message.update_ls(give_message.user_id, num, 1)  # 增加用户灵石
                await give_stone.finish(
                    "共赠送{}枚灵石给{}道友！收取手续费{}枚".format(
                        give_stone_num, give_message.user_name, int(give_stone_num2)
                    )
                )
        else:
            await give_stone.finish("对方未踏入修仙界，不可赠送！")

    else:
        await give_stone.finish("未获取道号信息，请输入正确的道号！")


@command.do_work.handle()
async def _(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    """悬赏令"""
    global work
    user_type = 2
    work_list = []

    try:
        user_id, group_id, mess = await data_check(bot, event)
    except MsgError:
        return

    text = args.extract_plain_text().strip()

    user_cd_message = sql_message.get_user_cd(user_id)

    if "接取" in text:
        try:
            if work[user_id]:
                work_num = re.findall("\d+", text)  ##任务序号

                try:
                    get_work = work[user_id].world[int(work_num[0]) - 1]
                    sql_message.do_work(user_id, user_type, get_work[0])
                    del work[user_id]
                    await do_work.finish(f"接取任务【{get_work[0]}】成功")
                except IndexError:
                    await do_work.finish("没有这样的任务")

        except KeyError:
            await do_work.finish("没有查到你的悬赏令信息呢！")
    elif text == "结算":
        if user_cd_message is None:
            await do_work.finish("没有查到你的悬赏令信息呢！输入【悬赏令】获取！")

        elif user_cd_message.type == 0:
            await do_work.finish("没有查到你的悬赏令信息呢！输入【悬赏令】获取！")

        elif user_cd_message.type == 1:
            await do_work.finish("道友现在在闭关呢，小心走火入魔！", at_sender=True)

        elif user_cd_message.type == 2:
            work_time = datetime.strptime(
                user_cd_message.create_time, "%Y-%m-%d %H:%M:%S.%f"
            )
            exp_time = (datetime.now() - work_time).seconds // 60  # 时长计算
            time2 = XiuxianJsonDate().do_work(
                key=1, name=user_cd_message.scheduled_time
            )
            if exp_time < time2:
                await do_work.finish(
                    f"进行中的悬赏令【{user_cd_message.scheduled_time}】，预计{time2 - exp_time}分钟后可结束",
                    at_sender=True,
                )
            else:
                work_sf = XiuxianJsonDate().do_work(2, user_cd_message.scheduled_time)
                sql_message.update_ls(user_id, work_sf[1], 1)
                sql_message.do_work(user_id, 0)
                await do_work.finish(f"悬赏令结算，{work_sf[0]},最终获得报酬{work_sf[1]}枚灵石！")

    try:
        if work[user_id]:
            if (datetime.now() - work[user_id].time).seconds // 60 >= 60:
                work_msg = XiuxianJsonDate().do_work(0)

                n = 1
                work_msg_f = f"""     ✨道友的个人悬赏令✨"""
                for i in work_msg:
                    work_list.append([i[0], i[3]])
                    work_msg_f += f"""
{n}、{i[0]}     完成机率{i[1]}   报酬{i[2]}   预计需{i[3]}分钟"""
                    n += 1
                work_msg_f += "\n(悬赏令每小时更新一次)"
                work[user_id].msg = work_msg_f
                work[user_id].world = work_list
                await do_work.finish(work[user_id].msg)
            else:
                await do_work.finish(work[user_id].msg)
    except KeyError:
        pass

    if user_cd_message is None:
        work_msg = XiuxianJsonDate().do_work(0)
        n = 1
        work_msg_f = f"""     ✨道友的个人悬赏令✨"""
        for i in work_msg:
            work_list.append([i[0], i[3]])
            work_msg_f += f"""
{n}、{i[0]}   完成机率{i[1]}  报酬{i[2]}  预计需{i[3]}分钟"""
            n += 1
        work_msg_f += f"\n(悬赏令每小时更新一次)"
        work[user_id] = do_is_work(user_id)
        work[user_id].time = datetime.now()
        work[user_id].msg = work_msg_f
        work[user_id].world = work_list
        await do_work.finish(work_msg_f)

    elif user_cd_message.type == 0:

        work_msg = XiuxianJsonDate().do_work(0)
        work_msg_f = f"""     ✨道友的个人悬赏令✨"""
        n = 1
        for i in work_msg:
            work_list.append([i[0], i[3]])
            work_msg_f += f"""
{n}、{i[0]}     完成机率{i[1]}   报酬{i[2]}  预计需{i[3]}分钟"""
            n += 1
        work_msg_f += f"\n(榜单每小时更新一次)"
        work[user_id] = do_is_work(user_id)
        work[user_id].time = datetime.now()
        work[user_id].msg = work_msg_f
        work[user_id].world = work_list
        await do_work.finish(work_msg_f)

    elif user_cd_message.type == 1:
        await do_work.finish("已经在闭关中，请输入【出关】结束后才能获取悬赏令！", at_sender=True)

    elif user_cd_message.type == 2:
        work_time = datetime.strptime(
            user_cd_message.create_time, "%Y-%m-%d %H:%M:%S.%f"
        )
        exp_time = (datetime.now() - work_time).seconds // 60  # 闭关时长计算
        time2 = XiuxianJsonDate().do_work(key=1, name=user_cd_message.scheduled_time)
        if exp_time < time2:
            await do_work.finish(
                f"进行中的悬赏令【{user_cd_message.scheduled_time}】，预计{time2 - exp_time}分钟后可结束",
                at_sender=True,
            )
        else:
            await do_work.finish(
                f"进行中的悬赏令【{user_cd_message.scheduled_time}】，已结束，请输入【悬赏令结算】结算任务信息！",
                at_sender=True,
            )


# 偷灵石
@command.steal_stone.handle()
async def _(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    try:
        user_id, group_id, user_message = await data_check(bot, event)
    except MsgError:
        return

    if cd := check_cd(event):
        # 如果 CD 还没到 则直接结束
        await steal_stone.finish(cd_msg(cd), at_sender=True)

    steal_user = None
    steal_user_stone = None

    user_stone_num = user_message.stone
    steal_qq = None  # 艾特的时候存到这里, 要偷的人
    # steal_name = None
    # msg = args.extract_plain_text().strip()

    # nick_name = re.findall("\D+", msg)  ## 道号

    coststone_num = XiuConfig().tou
    if int(coststone_num) > int(user_stone_num):
        await steal_stone.finish('道友的偷窃准备(灵石)不足，请打工之后再切格瓦拉！')

    for arg in args:
        if arg.type == "at":
            steal_qq = arg.data.get('qq', '')

    if steal_qq:
        if steal_qq == user_id:
            await steal_stone.finish("请不要偷自己刷成就！")
        else:
            steal_user = sql_message.get_user_message(steal_qq)
            steal_user_stone = steal_user.stone
    if steal_user:
        steal_success = random.randint(0, 100)
        result = OtherSet().get_power_rate(user_message.power, steal_user.power)
        if isinstance(result, int):
            if int(steal_success) > result:
                sql_message.update_ls(user_id, coststone_num, 2)  # 减少手续费
                sql_message.update_ls(steal_qq, coststone_num, 1)  # 增加被偷的人的灵石
                add_cd(event, XiuConfig().tou_cd)
                await steal_stone.finish('道友偷窃失手了，被对方发现并被派去华哥厕所义务劳工！赔款{}灵石'.format(coststone_num))


            get_stone = random.randint(XiuConfig().tou_lower_limit, XiuConfig().tou_upper_limit)

            if int(get_stone) > int(steal_user_stone):
                sql_message.update_ls(user_id, steal_user_stone, 1)  # 增加偷到的灵石
                sql_message.update_ls(steal_qq, steal_user_stone, 2)  # 减少被偷的人的灵石
                add_cd(event, XiuConfig().tou_cd)
                await steal_stone.finish(
                    "{}道友已经被榨干了~".format(steal_user.user_name))

            else:
                sql_message.update_ls(user_id, get_stone, 1)  # 增加偷到的灵石
                sql_message.update_ls(steal_qq, get_stone, 2)  # 减少被偷的人的灵石
                add_cd(event, XiuConfig().tou_cd)
                await steal_stone.finish(
                    "共偷取{}道友{}枚灵石！".format(steal_user.user_name, get_stone))

        else:
            await steal_stone.finish(result)

    else:
        await steal_stone.finish("对方未踏入修仙界，不要对杂修出手！")


# GM加灵石
@command.gm_command.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    give_qq = None  # 艾特的时候存到这里
    msg = args.extract_plain_text().strip()

    stone_num = re.findall("\d+", msg)  ## 灵石数
    nick_name = re.findall("\D+", msg)  ## 道号

    give_stone_num = stone_num[0]

    if stone_num:
        pass
    else:
        await give_stone.finish("请输入正确的灵石数量！")

    for arg in args:
        if arg.type == "at":
            give_qq = arg.data.get("qq", "")

    if give_qq:
        give_user = sql_message.get_user_message(give_qq)
        if give_user:
            sql_message.update_ls(give_qq, give_stone_num, 1)  # 增加用户灵石
            await give_stone.finish(
                "共赠送{}枚灵石给{}道友！".format(give_stone_num, give_user.user_name)
            )
        else:
            await give_stone.finish("对方未踏入修仙界，不可赠送！")
    if nick_name:
        give_message = sql_message.get_user_message2(nick_name[0])
        if give_message:
            sql_message.update_ls(give_message.user_id, give_stone_num, 1)  # 增加用户灵石
            await give_stone.finish(
                "共赠送{}枚灵石给{}道友！".format(give_stone_num, give_message.user_name)
            )
        else:
            await give_stone.finish("对方未踏入修仙界，不可赠送！")
    else:
        await give_stone.finish("未获取道号信息，请输入正确的道号！")


# editer:zyp981204
@command.my_sect.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    """查看所在宗门信息"""
    try:
        user_id, group_id, mess = await data_check(bot, event)
    except MsgError:
        return

    if mess:
        sect_id = mess.sect_id
        sect_position = mess.sect_position
        user_name = mess.user_name
        sect_info = sql_message.get_sect_info(sect_id)
        owner_idx = [k for k, v in jsondata.sect_config_data().items() if v.get("title", "") == "宗主"]
        owner_position = int(owner_idx[0]) if len(owner_idx) == 1 else 0
        if sect_id:
            _, sql_res = sql_message.scale_top()
            top_idx_list = [_[0] for _ in sql_res]
            msg = f"""{user_name}所在宗门
    宗门名讳：{sect_info.sect_name}
    宗门编号：{sect_id}
    宗   主：{sql_message.get_user_message(sect_info.sect_owner).user_name}
    道友职位：{jsondata.sect_config_data()[f"{sect_position}"]["title"]}
    宗门建设度：{sect_info.sect_scale}
    洞天福地：{sect_info.sect_fairyland if sect_info.sect_fairyland else "暂无"}
    宗门位面排名：{top_idx_list.index(sect_id) + 1}"""
            if sect_position == owner_position:
                msg += f"\n   宗门储备：{sect_info.sect_used_stone}灵石"
        else:
            msg = "一介散修，莫要再问。"
    else:
        msg = "未曾踏入修仙世界，输入 我要修仙 加入我们，看破这世间虚妄!"

    await run_xiuxian.finish(msg, at_sender=True)


@command.create_sect.handle()
async def _(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    """创建宗门，对灵石、修为等级有要求，且需要当前状态无宗门"""
    try:
        user_id, group_id, mess = await data_check(bot, event)
    except MsgError:
        return

    if mess:
        # 首先判断是否满足创建宗门的三大条件
        level = mess.level
        list_level_all = list(jsondata.level_data().keys())
        if list_level_all.index(level) < list_level_all.index(
                xiuxian_config.XiuConfig().sect_min_level) or mess.stone < xiuxian_config.XiuConfig().sect_create_cost or mess.sect_id:
            msg = f"创建宗门要求：（1）创建者境界最低要求为{xiuxian_config.XiuConfig().sect_min_level}；" \
                  f"（2）花费{xiuxian_config.XiuConfig().sect_create_cost}灵石费用；" \
                  f"（3）创建者当前处于无宗门状态。道友暂未满足所有条件，请逐一核实后，再来寻我。"
        else:
            # 切割command获取宗门名称
            sect_name = args.extract_plain_text().strip()
            if sect_name:
                # sect表新增
                sql_message.create_sect(user_id, sect_name)
                # 获取新增宗门的id（自增而非可设定）
                new_sect = sql_message.get_sect_info_by_qq(user_id)
                owner_idx = [k for k, v in jsondata.sect_config_data().items() if v.get("title", "") == "宗主"]
                owner_position = int(owner_idx[0]) if len(owner_idx) == 1 else 0
                # 设置用户信息表的宗门字段
                sql_message.update_usr_sect(user_id, new_sect.sect_id, owner_position)
                # 扣灵石
                sql_message.update_ls(user_id, xiuxian_config.XiuConfig().sect_min_level, 2)
                msg = f"恭喜{mess.user_name}道友创建宗门——{sect_name}，宗门编号为{new_sect.sect_id}。为道友贺！为仙道贺！"
            else:
                msg = f"道友确定要创建无名之宗门？还请三思。"
    else:
        msg = f"区区凡人，也想创立万世仙门，大胆！"
    await create_sect.finish(msg, at_sender=True)


@command.join_sect.handle()
async def _(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    """加入宗门，后跟宗门ID，要求加入者当前状态无宗门，入门默认为外门弟子"""
    try:
        user_id, group_id, mess = await data_check(bot, event)
    except MsgError:
        return

    if mess:
        if not mess.sect_id:
            sect_no = args.extract_plain_text().strip()
            sql_sects = sql_message.get_all_sect_id()
            sects_all = [tup[0] for tup in sql_sects]
            if not sect_no.isdigit():
                msg = f"申请加入的宗门编号解析异常，应全为数字!"
            elif int(sect_no) not in sects_all:
                msg = f"申请加入的宗门编号似乎有误，未在宗门名录上发现!"
            else:
                owner_idx = [k for k, v in jsondata.sect_config_data().items() if v.get("title", "") == "外门弟子"]
                owner_position = int(owner_idx[0]) if len(owner_idx) == 1 else 4
                sql_message.update_usr_sect(user_id, int(sect_no), owner_position)
                new_sect = sql_message.get_sect_info_by_id(int(sect_no))
                msg = f"欢迎{mess.user_name}师弟入我{new_sect.sect_name}，共参天道。"
        else:
            msg = f"守山弟子：我观道友气运中已有宗门气运加持，又何必与我为难。"
    else:
        msg = f"守山弟子：凡人，回去吧，仙途难入，莫要自误！"
    await join_sect.finish(msg, at_sender=True)


@command.sect_position_update.handle()
async def _(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    """宗门职位变更，首先确认操作者的职位是长老及以上（宗主可以变更宗主及以下，长老可以变更长老以下），然后读取变更等级及艾特目标"""
    try:
        user_id, group_id, user_message = await data_check(bot, event)
    except MsgError:
        return

    position_zhanglao = [k for k, v in jsondata.sect_config_data().items() if v.get("title", "") == "长老"]
    idx_position = int(position_zhanglao[0]) if len(position_zhanglao) == 1 else 1
    if user_message.sect_position > idx_position:
        await sect_position_update.finish(
            f"你的宗门职位为{jsondata.sect_config_data()[f'{user_message.sect_position}']['title']}，无权进行职位管理")

    give_qq = None  # 艾特的时候存到这里
    msg = args.extract_plain_text().strip()
    position_num = re.findall("\d+", msg)  # 职位品阶

    for arg in args:
        # print(args)
        if arg.type == "at":
            give_qq = arg.data.get("qq", "")
    if give_qq:
        if give_qq == user_id:
            await sect_position_update.finish("无法对自己的职位进行管理。")
        else:
            if len(position_num) > 0 and position_num[0] in list(jsondata.sect_config_data().keys()):
                give_user = sql_message.get_user_message(give_qq)
                if give_user.sect_id == user_message.sect_id and give_user.sect_position > user_message.sect_position:
                    if int(position_num[0]) > user_message.sect_position:
                        sql_message.update_usr_sect(give_user.user_id, give_user.sect_id, int(position_num[0]))
                        await sect_position_update.finish(
                            f"传{jsondata.sect_config_data()[f'{user_message.sect_position}']['title']}"
                            f"{user_message.user_name}法旨，即日起{give_user.user_name}为"
                            f"本宗{jsondata.sect_config_data()[f'{int(position_num[0])}']['title']}")
                    else:
                        await sect_position_update.finish("道友试图变更的职位品阶必须在你品阶之下")
                else:
                    await sect_position_update.finish("请确保变更目标道友与你在同一宗门，且职位品阶在你之下。")
            else:
                await sect_position_update.finish("职位品阶数字解析异常，请输入宗门职位变更帮助，查看支持的数字解析配置")
    else:
        await sect_position_update.finish(f"请按照规范进行操作，ex:宗门职位变更2@XXX，将XXX道友（需在自己管理下的宗门）的"
                                          f"变更为{jsondata.sect_config_data().get('2', {'title': '没有找到2品阶'})['title']}")


@command.sect_donate.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    """宗门捐献"""
    user_id = event.get_user_id()
    user_message = sql_message.get_user_message(user_id)
    if not user_message:
        await sect_donate.finish("修仙界没有你的信息！请输入我要修仙，踏入修行")
    if not user_message.sect_id:
        await sect_donate.finish("道友还未加入一方宗门。")
    msg = args.extract_plain_text().strip()
    donate_num = re.findall("\d+", msg)  # 捐献灵石数
    if len(donate_num) > 0:
        if int(donate_num[0]) > user_message.stone:
            await sect_donate.finish(f"道友的灵石数量小于欲捐献数量{int(donate_num[0])}，请检查")
        else:
            sql_message.update_ls(user_id, int(donate_num[0]), 2)
            sql_message.donate_update(user_message.sect_id, int(donate_num[0]))
            await sect_donate.finish(f"道友捐献灵石{int(donate_num[0])}枚，增加宗门建设度{int(donate_num[0]) * 10}，蒸蒸日上！")
    else:
        await sect_donate.finish("捐献的灵石数量解析异常")


@command.sect_out.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    """退出宗门"""
    user_id = event.get_user_id()
    user_message = sql_message.get_user_message(user_id)
    if not user_message:
        await sect_out.finish("修仙界没有你的信息！请输入我要修仙，踏入修行")
    if not user_message.sect_id:
        await sect_out.finish("道友还未加入一方宗门。")
    position_this = [k for k, v in jsondata.sect_config_data().items() if v.get("title", "") == "宗主"]
    owner_position = int(position_this[0]) if len(position_this) == 1 else 0
    if user_message.sect_position != owner_position:
        msg = args.extract_plain_text().strip()
        sect_out_id = re.findall("\d+", msg)  # 退出宗门的宗门编号
        if len(sect_out_id) > 0:
            if int(sect_out_id[0]) == user_message.sect_id:
                sql_sects = sql_message.get_all_sect_id()
                sects_all = [tup[0] for tup in sql_sects]
                if int(sect_out_id[0]) not in sects_all:
                    await sect_out.finish(f"欲退出的宗门编号{int(sect_out_id[0])}似乎有误，未在宗门名录上发现!")
                else:
                    sql_message.update_usr_sect(user_id, None, None)
                    sect_info = sql_message.get_sect_info_by_id(int(sect_out_id[0]))
                    await sect_out.finish(f"道友已退出{sect_info.sect_name}，今后就是自由散修，是福是祸，犹未可知。")
            else:
                await sect_out.finish(f"道友所在宗门编号为{user_message.sect_id}，与欲退出的宗门编号{int(sect_out_id[0])}不符")
        else:
            await sect_out.finish("欲退出的宗门编号解析异常")
    else:
        await sect_out.finish("宗主无法直接退出宗门，如确有需要，请完成宗主传位后另行尝试。")


@command.sect_kick_out.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    """踢出宗门"""
    user_id = event.get_user_id()
    user_message = sql_message.get_user_message(user_id)
    if not user_message:
        await sect_kick_out.finish("修仙界没有你的信息！请输入我要修仙，踏入修行")
    if not user_message.sect_id:
        await sect_kick_out.finish("道友还未加入一方宗门。")
    give_qq = None  # 艾特的时候存到这里
    for arg in args:
        # print(args)
        if arg.type == "at":
            give_qq = arg.data.get("qq", "")
    if give_qq:
        if give_qq == user_id:
            await sect_kick_out.finish("无法对自己的进行踢出操作，试试退出宗门？")
        else:
            give_user = sql_message.get_user_message(give_qq)
            if give_user.sect_id == user_message.sect_id:
                position_zhanglao = [k for k, v in jsondata.sect_config_data().items() if v.get("title", "") == "长老"]
                idx_position = int(position_zhanglao[0]) if len(position_zhanglao) == 1 else 1
                if user_message.sect_position <= idx_position:
                    if give_user.sect_position <= user_message.sect_position:
                        await sect_kick_out.finish(
                            f"{give_user.user_name}的宗门职务为{jsondata.sect_config_data()[f'{give_user.sect_position}']['title']}，不在你之下，无权操作。")
                    else:
                        sect_info = sql_message.get_sect_info_by_id(give_user.sect_id)
                        sql_message.update_usr_sect(give_user.user_id, None, None)
                        await sect_kick_out.finish(
                            f"传{jsondata.sect_config_data()[f'{user_message.sect_position}']['title']}"
                            f"{user_message.user_name}法旨，即日起{give_user.user_name}被"
                            f"{sect_info.sect_name}除名")
                else:
                    await sect_kick_out.finish(
                        f"你的宗门职务为{jsondata.sect_config_data()[f'{user_message.sect_position}']['title']}，只有长老及以上可执行踢出操作。")
            else:
                await sect_kick_out.finish(f"{give_user.user_name}不在你管理的宗门内，请检查。")
    else:
        await sect_kick_out.finish(f"请按照规范进行操作，ex:踢出宗门@XXX，将XXX道友（需在自己管理下的宗门）踢出宗门")


@command.sect_owner_change.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    """宗主传位"""
    user_id = event.get_user_id()
    user_message = sql_message.get_user_message(user_id)
    if not user_message:
        await sect_owner_change.finish("修仙界没有你的信息！请输入我要修仙，踏入修行")
    if not user_message.sect_id:
        await sect_owner_change.finish("道友还未加入一方宗门。")
    position_this = [k for k, v in jsondata.sect_config_data().items() if v.get("title", "") == "宗主"]
    owner_position = int(position_this[0]) if len(position_this) == 1 else 0
    if user_message.sect_position != owner_position:
        await sect_owner_change.finish("只有宗主才能进行传位。")
    give_qq = None  # 艾特的时候存到这里
    for arg in args:
        # print(args)
        if arg.type == "at":
            give_qq = arg.data.get("qq", "")
    if give_qq:
        if give_qq == user_id:
            await sect_owner_change.finish("无法对自己的进行传位操作。")
        else:
            give_user = sql_message.get_user_message(give_qq)
            if give_user.sect_id == user_message.sect_id:
                sql_message.update_usr_sect(give_user.user_id, give_user.sect_id, owner_position)
                sql_message.update_usr_sect(user_message.user_id, user_message.sect_id, owner_position + 1)
                sect_info = sql_message.get_sect_info_by_id(give_user.sect_id)
                await sect_owner_change.finish(
                    f"传老宗主{user_message.user_name}法旨，即日起{give_user.user_name}继任{sect_info.sect_name}宗主")
            else:
                await sect_owner_change.finish(f"{give_user.user_name}不在你管理的宗门内，请检查。")
    else:
        await sect_owner_change.finish(f"请按照规范进行操作，ex:宗主传位@XXX，将XXX道友（需在自己管理下的宗门）升为宗主，自己则变为宗主下一等职位。")


@command.rob_stone.handle()
async def _(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    """抢灵石
            player1 = {
            "NAME": player,
            "HP": player,
            "ATK": ATK,
            "COMBO": COMBO
        }"""
    # 验证是否开启抢灵石
    conf = JsonConfig().read_data()
    try:
        if conf['qiang']:
            pass
        else:
            await rob_stone.finish("已关闭抢灵石，请联系管理员！")
    except KeyError:
        pass

    try:
        user_id, group_id, user_msg = await data_check(bot, event)
    except MsgError:
        return

    if user_msg.hp is None or user_msg.hp == 0:
        # 判断用户气血是否为空
        sql_message.update_user_hp(user_id)

    give_qq = None  # 艾特的时候存到这里
    for arg in args:
        if arg.type == "at":
            give_qq = arg.data.get("qq", "")

    player1 = {"user_id": None, "道号": None, "气血": None, "攻击": None, "真元": None, '会心': None, '防御': 0}
    player2 = {"user_id": None, "道号": None, "气血": None, "攻击": None, "真元": None, '会心': None, '防御': 0}

    if give_qq:
        if give_qq == user_id:
            await rob_stone.finish("请不要偷自己刷成就！")

        user_2 = sql_message.get_user_message(give_qq)
        if user_2:
            if user_msg.hp is None or user_msg.hp == 0:
                #判断用户气血是否为None
                sql_message.update_user_hp(user_id)
                user_msg = sql_message.get_user_message(user_id)
            if user_2.hp is None:
                sql_message.update_user_hp(give_qq)
                user_2 = sql_message.get_user_message(give_qq)

            if user_2.hp <= user_2.exp/10:
                await rob_stone.finish("对方重伤藏匿了，无法抢劫！", at_sender=True)

            if user_msg.hp <= user_msg.exp/10:
                await rob_stone.finish("重伤未愈，动弹不得！", at_sender=True)

            player1['user_id'] = user_msg.user_id
            player1['道号'] = user_msg.user_name
            player1['气血'] = user_msg.hp
            player1['攻击'] = user_msg.atk
            player1['真元'] = user_msg.mp
            player1['会心'] = 1

            player2['user_id'] = user_2.user_id
            player2['道号'] = user_2.user_name
            player2['气血'] = user_2.hp
            player2['攻击'] = user_2.atk
            player2['真元'] = user_2.mp
            player2['会心'] = 1

            # msg1 = ""
            # msg2 = ""
            #
            # for i, v in player1.items():
            #     msg1 += "{}:{}\n".format(i, v)
            #
            # for i, v in player2.items():
            #     msg2 += "{}:{}\n".format(i, v)
            #
            # await rob_stone.send(msg1)
            # await rob_stone.send(msg2)

            result, victor = OtherSet().player_fight(player1, player2, 1)
            await send_forward_msg(bot, event, '决斗场', bot.self_id, result)
            if victor == player1['道号']:
                foe_stone = user_2.stone
                if foe_stone > 0:
                    sql_message.update_ls(user_id, int(foe_stone * 0.1), 1)
                    sql_message.update_ls(give_qq, int(foe_stone * 0.1), 2)
                    exps = int(user_2.exp * 0.005)
                    sql_message.update_exp(user_id, exps)
                    sql_message.update_j_exp(give_qq, exps/2)
                    await rob_stone.finish("大战一番，战胜对手，获取灵石{}枚，修为增加{}，对手修为减少{}".format(int(foe_stone*0.1), exps,exps/2), at_sender=True)
                else:
                    exps = int(user_2.exp * 0.005)
                    sql_message.update_exp(user_id, exps)
                    sql_message.update_j_exp(give_qq, exps/2)
                    await rob_stone.finish("大战一番，战胜对手，结果对方是个穷光蛋，修为增加{}，对手修为减少{}".format(exps,exps/2), at_sender=True)

            elif victor == player2['道号']:
                mind_stone = user_msg.stone
                if mind_stone > 0:
                    sql_message.update_ls(user_id, int(mind_stone * 0.1), 2)
                    sql_message.update_ls(give_qq, int(mind_stone * 0.1), 1)
                    exps = int(user_msg.exp * 0.005)
                    sql_message.update_j_exp(user_id, exps)
                    sql_message.update_exp(give_qq, exps/2)
                    await rob_stone.finish("大战一番，被对手反杀，损失灵石{}枚，修为减少{}，对手获取灵石{}枚，修为增加{}".format(int(mind_stone * 0.1), exps, int(mind_stone * 0.1),exps/2), at_sender=True)
                else:
                    exps = int(user_msg.exp * 0.005)
                    sql_message.update_j_exp(user_id, exps)
                    sql_message.update_exp(give_qq, exps/2)
                    await rob_stone.finish("大战一番，被对手反杀，修为减少{}，对手修为增加{}".format(exps,exps/2),
                                           at_sender=True)

            else:
                await rob_stone.finish("发生错误！")

        else:
            await rob_stone.finish("没有对方的信息！")


@command.mind_state.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    try:
        user_id, group_id, user_msg = await data_check(bot, event)
    except MsgError:
        return

    if user_msg.hp is None or user_msg.hp == 0 or user_msg.hp == 0:
        sql_message.update_user_hp(user_id)

    user = f"""道号：{user_msg.user_name}
气血：{user_msg.hp}/{int(user_msg.exp/2)}
真元：{user_msg.mp}/{int(user_msg.exp)}
攻击：{user_msg.atk}/{int(user_msg.exp/10)}"""

    await mind_state.finish(user)

@command.restate.handle()
async def _(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    give_qq = None  # 艾特的时候存到这里
    for arg in args:
        if arg.type == "at":
            give_qq = arg.data.get("qq", "")

    if give_qq:
        sql_message.restate(give_qq)
        await restate.finish('{}用户信息重置成功！'.format(give_qq), at_sender=True)
    else:
        sql_message.restate()
        await restate.finish('所有用户信息重置成功！', at_sender=True)


@command.open_robot.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    group_msg = str(event.message)
    print(group_msg)

    if "开启" in group_msg:
        JsonConfig().write_data(1)
        await open_robot.finish("抢灵石开启成功！")

    elif "关闭" in group_msg:
        JsonConfig().write_data(2)
        await open_robot.finish("抢灵石关闭成功！")

    else:
        await open_robot.finish("指令错误，请输入：开启抢灵石/关闭抢灵石")


# -----------------------------------------------------------------------------

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


async def data_check(bot, event):
    """
    判断用户信息是否存在
    """
    user_qq = event.get_user_id()
    group_id = await get_group_id(event.get_session_id())
    msg = sql_message.get_user_message(user_qq)

    if msg:
        pass
    else:
        await bot.send(event=event, message=f"没有您的信息，输入【我要修仙】加入！")
        raise MsgError

    return user_qq, group_id, msg


class MsgError(ValueError):
    pass


@driver.on_shutdown
async def close_db():
    sql_message.close_dbs()
