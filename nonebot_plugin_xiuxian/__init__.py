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
    MessageSegment,
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
from .read_buff import UserBuffDate
from .utils import Txt2Img, data_check_conf



# 定时任务
scheduler = require("nonebot_plugin_apscheduler").scheduler

driver = get_driver()
work = {}  # 悬赏令信息记录
sect_out_check = {}  # 退出宗门或踢出宗门信息记录
sql_message = XiuxianDateManage()  # sql类

from nonebot import load_all_plugins
src = ''
load_all_plugins(
        [
            f'{src}nonebot_plugin_xiuxian.xiuxian_boss',
            f'{src}nonebot_plugin_xiuxian.xiuxian_bank',
            f'{src}nonebot_plugin_xiuxian.xiuxian_sect',
            f'{src}nonebot_plugin_xiuxian.xiuxian_info',
            f'{src}nonebot_plugin_xiuxian.xiuxian_buff',
        ],
        [],
    )



@command.run_xiuxian.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    """加入修仙"""
    await data_check_conf(bot, event)

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


@sign_in.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    """修仙签到"""
    await data_check_conf(bot, event)

    try:
        user_id, group_id, mess = await data_check(bot, event)
    except MsgError:
        return

    result = sql_message.get_sign(user_id)
    sql_message.update_power2(user_id)
    await sign_in.send(result, at_sender=True)


@command.help_in.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    """修仙帮助"""
    await data_check_conf(bot, event)

    font_size = 30
    title = '修仙模拟器帮助信息'
    msg = help.__xiuxian_notes__
    img = Txt2Img(font_size)
    pic = img.save(title, msg)
    await help_in.send(MessageSegment.image(pic))
#     msg = help.__xiuxian_notes__
#     await help_in.send(msg, at_sender=True)


@command.dufang.handle()
async def _(bot: Bot, event: MessageEvent, args: Tuple[Any, ...] = RegexGroup()):
    await data_check_conf(bot, event)

    try:
        user_id, group_id, mess = await data_check(bot, event)
    except MsgError:
        return

    if cd := check_cd(event, '金银阁'):
        # 如果 CD 还没到 则直接结束
        await dufang.finish(cd_msg(cd), at_sender=True)

    user_message = sql_message.get_user_message(user_id)

    add_cd(event, XiuConfig().dufang_cd, '金银阁')

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
    if int(user_message.stone) < price_num:
        await dufang.finish("道友的金额不足，请重新输入！")
    elif price_num == 0:
        await dufang.finish("走开走开，0块钱也赌！")

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
    await data_check_conf(bot, event)

    try:
        user_id, group_id, mess = await data_check(bot, event)
    except MsgError:
        return

    name, root_type = XiuxianJsonDate().linggen_get()
    result = sql_message.ramaker(name, root_type, user_id)
    sql_message.update_power2(user_id)  # 更新战力
    await restart.send(message=result, at_sender=True)


@command.rank.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    """排行榜"""
    await data_check_conf(bot, event)

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
async def _(bot: Bot, event: GroupMessageEvent):
    """押注超时校验"""
    # try:
    #     user_id, group_id, mess = await data_check(bot, event)
    # except MsgError:
    #     return
    # except ConfError:
    #     return

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
    except ConfError:
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
    except ConfError:
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
    except ConfError:
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
        nowhp = user_msg.hp - (now_exp / 2) if (user_msg.hp - (now_exp / 2)) > 0 else 1
        nowmp = user_msg.mp - now_exp if (user_msg.mp - now_exp) > 0 else 1

        sql_message.update_user_hp_mp(user_id, nowhp, nowmp)  # 修为掉了，血量、真元也要掉

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

@command.user_leveluprate.handle()
async def _(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    """我的突破概率"""
    try:
        user_id, group_id, mess = await data_check(bot, event)
    except MsgError:
        return
    except ConfError:
        return
    
    user_msg = sql_message.get_user_message(user_id)  # 用户信息
    leveluprate = int(user_msg.level_up_rate)  # 用户失败次数加成
    
    level_name = user_msg.level  # 用户境界
    level_rate = jsondata.level_rate_data()[level_name]  # 对应境界突破的概率
    await user_leveluprate.finish(f"道友下一次突破成功概率为{level_rate + leveluprate}%")


@command.give_stone.handle()
async def _(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    """送灵石"""
    try:
        user_id, group_id, mess = await data_check(bot, event)
    except MsgError:
        return
    except ConfError:
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
    except ConfError:
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
    except ConfError:
        return

    if cd := check_cd(event, '偷灵石'):
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
                add_cd(event, XiuConfig().tou_cd, '偷灵石')
                await steal_stone.finish('道友偷窃失手了，被对方发现并被派去华哥厕所义务劳工！赔款{}灵石'.format(coststone_num))


            get_stone = random.randint(XiuConfig().tou_lower_limit, XiuConfig().tou_upper_limit)

            if int(get_stone) > int(steal_user_stone):
                sql_message.update_ls(user_id, steal_user_stone, 1)  # 增加偷到的灵石
                sql_message.update_ls(steal_qq, steal_user_stone, 2)  # 减少被偷的人的灵石
                add_cd(event, XiuConfig().tou_cd, '偷灵石')
                await steal_stone.finish(
                    "{}道友已经被榨干了~".format(steal_user.user_name))

            else:
                sql_message.update_ls(user_id, get_stone, 1)  # 增加偷到的灵石
                sql_message.update_ls(steal_qq, get_stone, 2)  # 减少被偷的人的灵石
                add_cd(event, XiuConfig().tou_cd, '偷灵石')
                await steal_stone.finish(
                    "共偷取{}道友{}枚灵石！".format(steal_user.user_name, get_stone))

        else:
            await steal_stone.finish(result)

    else:
        await steal_stone.finish("对方未踏入修仙界，不要对杂修出手！")


# GM加灵石
@command.gm_command.handle()
async def _(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    await data_check_conf(bot, event)

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
    elif nick_name:
        give_message = sql_message.get_user_message2(nick_name[0])
        if give_message:
            sql_message.update_ls(give_message.user_id, give_stone_num, 1)  # 增加用户灵石
            await give_stone.finish(
                "共赠送{}枚灵石给{}道友！".format(give_stone_num, give_message.user_name)
            )
        else:
            await give_stone.finish("对方未踏入修仙界，不可赠送！")
    else:
        sql_message.update_ls_all(give_stone_num)
        await give_stone.finish(f"全服通告：赠送所有用户{give_stone_num}灵石,请注意查收！")


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
    except ConfError:
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




@command.restate.handle()
async def _(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    """重置用户状态。
    单用户：重置状态@xxx
    多用户：重置状态"""


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
async def _(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    """抢灵石开关配置"""

    await data_check_conf(bot, event)

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


@command.shop.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    """坊市"""
    await data_check_conf(bot, event)

    data = jsondata.shop_data()

    def sends(s):
        if s == 'hp':
            return '回复气血'
        if s == 'mp':
            return "回复法术"
        if s == "atk":
            return "攻击增加"

    msg = lambda i: f"{i['name']}\n效果：{sends(i['buff_type'])}{i['buff']}\n售价：{i['price']}\n描述：{i['desc']}"
    name = list(set(i['type'] for i in data.values()))  # 判断物品类型
    data_list = []
    for i in range(len(name)):
        data_list.append(name[i])
        for j in data.values():
            if j['type'] == name[i]:
                data_list.append(msg(j) + '\n----------')

    await send_forward_msg(bot, event, '坊市', bot.self_id, data_list)

@command.buy.handle()
async def _(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    """购物"""
    try:
        user_id, group_id, user_msg = await data_check(bot, event)
    except MsgError:
        return
    except ConfError:
        return

    goods_data = jsondata.shop_data()
    get_goods = str(args)
    logger.info(f'商品名称：{get_goods}')

    for i, v in goods_data.items():
        logger.info(f'商品列表：{v}')
        if v['name'] == get_goods:
            logger.info(f"sql字段：{user_id}, {i, get_goods}, {v['type']}, {1}, {v['desc']}")
            price = v['price']
            if user_msg.stone >= price:
                sql_message.update_ls(user_id, price, 2)
                sql_message.send_back(user_id, i, v['name'], v['type'], 1)
                await buy.finish('购买成功！', at_sender=True)
            else:
                await buy.finish('没钱还敢来买东西！！', at_sender=True)
        else:
            continue
            # await buy.finish('没有获取道商品信息！')
    await buy.finish('没有获取道商品信息', at_sender=True)


@command.mind_back.handle()
async def _(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    """我的背包"""
    try:
        user_id, group_id, user_msg = await data_check(bot, event)
    except MsgError:
        return
    except ConfError:
        return
    data = jsondata.shop_data()  # 物品json信息
    back_msg = sql_message.get_back_msg(user_id)  # 背包sql信息

    # ["user_id", "goods_id", "goods_name", "goods_type", "goods_num", "create_time", "update_time",
    #  "remake", "day_num", "all_num", "action_time", "state"]
    msg = f"{user_msg.user_name}的背包\n"
    for i in back_msg:
        msg += f"名称：{i[2]},类型：{i[3]},数量：{i[4]}," \
              f"效果：{data[str(i[1])]['desc']},售价：{data[str(i[1])]['selling']}\n"
    await mind_back.finish(msg)


@command.use.handle()
async def _(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    """使用物品
        # ["user_id", "goods_id", "goods_name", "goods_type", "goods_num", "create_time", "update_time",
    #  "remake", "day_num", "all_num", "action_time", "state"]
    """
    try:
        user_id, group_id, mess = await data_check(bot, event)
    except MsgError:
        return
    except ConfError:
        return

    await use.finish('调试中，未开启！')
    get_goods = str(args)
    data = jsondata.shop_data()  # 物品json信息
    back_msg = sql_message.get_back_msg(user_id)  # 背包sql信息

    for i in back_msg:
        if i[2] == get_goods:
            pass


@command.open_xiuxian.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    """群修仙开关配置"""
    group_msg = str(event.message)
    group_id = await get_group_id(event.get_session_id())

    if "启用" in group_msg:
        JsonConfig().write_data(3, group_id)
        await open_robot.finish("当前群聊修仙模组已启用！")

    elif "禁用" in group_msg:
        JsonConfig().write_data(4, group_id)
        await open_robot.finish("当前群聊修仙模组已禁用！")

    else:
        await open_robot.finish("指令错误!")

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
    conf_data = JsonConfig().read_data()

    try:
        if group_id in conf_data["group"]:
            print('当前存在禁用数据')
            await bot.send(event=event, message=f"本群已关闭修仙模组，请联系管理员开启！")
            raise ConfError
        else:
            pass
    except KeyError:
        pass

    if msg:
        pass
    else:
        await bot.send(event=event, message=f"没有您的信息，输入【我要修仙】加入！")
        raise MsgError

    return user_qq, group_id, msg


class MsgError(ValueError):
    pass


class ConfError(ValueError):
    pass


@driver.on_shutdown
async def close_db():
    sql_message.close_dbs()
