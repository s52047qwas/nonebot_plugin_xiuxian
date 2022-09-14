import re
from nonebot.log import logger
from nonebot import get_driver
from nonebot import on_command, require, on_message
from nonebot.params import CommandArg, RawCommand, Depends, Arg, ArgStr, RegexMatched
from nonebot.adapters.onebot.v11 import (
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
from .xiuxian2_handle import XiuxianDateManage, XiuxianJsonDate, OtherSet
from datetime import datetime
import random
from nonebot.permission import SUPERUSER
from .xiuxian_opertion import gamebingo, do_is_work, time_msg
from .xiuxian_config import XiuConfig
from .data_source import jsondata

scheduler = require("nonebot_plugin_apscheduler").scheduler

__xiuxian_version__ = "v0.0.1"
__xiuxian_notes__ = f"""
修仙模拟器帮助信息:
指令：
1、我要修仙：进入修仙模式
2、我的修仙信息：获取修仙数据
3、修仙签到：获取灵石及修为
4、重入仙途：重置灵根数据，每次{XiuConfig().remake}灵石
5、金银阁：猜大小/数字，赌灵石
6、改名xx：修改你的道号
7、突破：修为足够后，可突破境界（一定几率失败）
8、闭关、出关、灵石出关：修炼增加修为，挂机功能
9、送灵石+数量+道号或者艾特对应人
10、排行榜：修仙排行榜，灵石排行榜
11、悬赏令：获取任务单，接取任务示例：悬赏令接取1， 结算命令示例：悬赏令结算
12、偷灵石：偷灵石@xxx
-简易灵根帮助-
混沌灵根>融合灵根>超灵根>龙灵根>天灵根>变异灵根>真灵根>伪灵根
""".strip()

driver = get_driver()

run_xiuxian = on_command("我要修仙", priority=5)
xiuxian_message = on_command("我的修仙信息", aliases={"我的存档"}, priority=5)
restart = on_command("再入仙途", aliases={"重新修仙"}, priority=5)
package = on_command("我的纳戒", aliases={"升级纳戒"}, priority=5)
sign_in = on_command("修仙签到", priority=5)
dufang = on_command("#金银阁", aliases={"金银阁"}, priority=5)
dice = on_command("大", aliases={"小", "1", "2", "3", "4", "5", "6"}, priority=5)
price = on_command("押注", priority=5)
help_in = on_command("修仙帮助", priority=5)
remaker = on_command("重入仙途", priority=5)
use = on_command("#使用", priority=5)
buy = on_command("#购买", priority=5)
rank = on_command("排行榜", aliases={"修仙排行榜", "灵石排行榜", "战力排行榜", "境界排行榜"}, priority=5)
time_mes = on_message(priority=999)
remaname = on_command("改名", priority=5)
level_up = on_command("突破", priority=5)
in_closing = on_command("闭关", priority=5)
out_closing = on_command("出关", aliases={"灵石出关"}, priority=5)
give_stone = on_command("送灵石", priority=5)
do_work = on_command("悬赏令", priority=5)
steal_stone = on_command("偷灵石", priority=5)
gm_command = on_command("神秘力量", permission=SUPERUSER, priority=5)

race = {}  # 押注信息记录
work = {}  # 悬赏令信息记录
sql_message = XiuxianDateManage()  # sql类


@run_xiuxian.handle()
async def _(event: GroupMessageEvent):
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


@xiuxian_message.handle()
async def _(event: GroupMessageEvent):
    """我的修仙信息"""
    user_id = event.get_user_id()
    mess = sql_message.get_user_message(user_id)

    if mess:
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
            need_exp = XiuxianDateManage().get_level_power(is_updata_level)
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
    else:
        msg = "未曾踏入修仙世界，输入 我要修仙 加入我们，看破这世间虚妄!"

    await run_xiuxian.finish(msg, at_sender=True)


@sign_in.handle()
async def _(event: GroupMessageEvent):
    """修仙签到"""
    user_id = event.get_user_id()
    result = sql_message.get_sign(user_id)
    sql_message.update_power2(user_id)
    await sign_in.send(result, at_sender=True)


@help_in.handle()
async def _():
    """修仙帮助"""
    msg = __xiuxian_notes__
    await help_in.send(msg, at_sender=True)


@dice.handle()
async def _(event: GroupMessageEvent):
    """金银阁，大小信息"""
    global race
    message = event.message
    user_id = event.get_user_id()
    group_id = await get_group_id(event.get_session_id())
    in_msg = ["大", "小", "1", "2", "3", "4", "5", "6"]

    try:
        race[group_id]
    except KeyError:
        await price.finish()

    if race[group_id].player[0] == user_id:
        pass
    else:
        await dice.finish("吃瓜道友请不要捣乱！！！")

    price_num = race[group_id].price
    if price_num == 0:
        await dice.finish("道友押注失败,请发送【押注+数字】押注！", at_sender=True)

    if str(message) in in_msg:
        pass
    else:
        await dice.finish("请输入正确的结果【大】【小】或者 1-6 之间的数字！")

    value = random.randint(1, 6)
    msg = Message("[CQ:dice,value={}]".format(value))

    if value >= 4 and str(message) == "大":
        del race[group_id]
        sql_message.update_ls(user_id, price_num, 1)
        await dice.send(msg)
        await dice.finish(
            "最终结果为{}，你猜对了，收获灵石{}块".format(value, price_num), at_sender=True
        )
    elif value <= 3 and str(message) == "小":
        del race[group_id]
        sql_message.update_ls(user_id, price_num, 1)
        await dice.send(msg)
        await dice.finish(
            "最终结果为{}，你猜对了，收获灵石{}块".format(value, price_num), at_sender=True
        )
    elif str(value) == str(message):
        del race[group_id]
        sql_message.update_ls(user_id, price_num * 6, 1)
        await dice.send(msg)
        await dice.finish(
            "最终结果为{}，你猜对了，收获灵石{}块".format(value, price_num * 6), at_sender=True
        )
    else:
        del race[group_id]
        sql_message.update_ls(user_id, price_num, 2)
        await dice.send(msg)
        await dice.finish(
            "最终结果为{}，你猜错了，损失灵石{}块".format(value, price_num), at_sender=True
        )


@dufang.handle()
async def _(event: GroupMessageEvent):
    """金银阁，开场信息"""
    global race
    user_id = event.get_user_id()
    group_id = await get_group_id(event.get_session_id())
    user_message = sql_message.get_user_message(user_id)
    if user_message:
        if user_message.stone == 0:
            await price.finish(f"走开走开，没钱还来玩！", at_sender=True)
    else:
        await price.finish(f"本阁没有这位道友的信息！输入【我要修仙】加入吧！", at_sender=True)

    try:
        if race[group_id].start == 1 and race[group_id].player[0] == user_id:
            await dufang.finish(f"道友的活动已经开始了，发送【押注+数字】参与")
        elif race[group_id].start == 1 and race[group_id].player[0] != user_id:
            await dufang.finish(f"已有其他道友进行中")
    except KeyError:
        pass
    race[group_id] = gamebingo()
    race[group_id].start_change(1)
    race[group_id].add_player(user_id)
    race[group_id].time = datetime.now()
    await dufang.finish(f"发送【押注+数字】参与", at_sender=True)


@price.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    """金银阁，押注信息"""
    global race
    user_id = event.get_user_id()
    group_id = await get_group_id(event.get_session_id())
    msg = args.extract_plain_text().strip()

    user_message = sql_message.get_user_message(user_id)
    try:
        race[group_id]
    except KeyError:
        await price.finish(f"金银阁未开始，请输入【金银阁】开场", at_sender=True)
    try:
        if race[group_id].player[0] == user_id:
            pass
        else:
            await price.finish("吃瓜道友请不要捣乱！")
    except KeyError:
        await price.finish()
    if msg:
        price_num = msg
        if race[group_id].price != 0:
            await price.finish("钱财离手，不可退回！", at_sender=True)
        elif int(user_message.stone) < int(price_num):
            await price.finish("道友的金额不足，请重新输入！")
        elif price_num.isdigit():
            race[group_id].add_price(int(price_num))
        else:
            await price.finish("请输入正确的金额！")
    else:
        await price.finish(f"请输入押注金额", at_sender=True)

    out_msg = f"押注完成，发送【大】【小】或者 1-6 之间的数字参与本局游戏！"
    await price.finish(out_msg, at_sender=True)


@remaker.handle()
async def _(event: GroupMessageEvent):
    """重置灵根信息"""
    user_id = event.get_user_id()
    name, root_type = XiuxianJsonDate().linggen_get()
    result = sql_message.ramaker(name, root_type, user_id)
    sql_message.update_power2(user_id)   # 更新战力
    await remaker.send(message=result, at_sender=True)


@rank.handle()
async def _(event: GroupMessageEvent):
    # rank = on_command('排行榜', aliases={'修仙排行榜', '灵石排行榜', '战力排行榜', '境界排行榜'}, priority=5)
    message = str(event.message)
    if message == "排行榜" or message == "修仙排行榜" or message == "境界排行榜":
        p_rank = sql_message.realm_top()
        await rank.finish(message=p_rank)
    elif message == "灵石排行榜":
        a_rank = sql_message.stone_top()
        await rank.finish(message=a_rank)
    elif message == "战力排行榜":
        a_rank = sql_message.power_top()
        await rank.finish(message=a_rank)

# 重置每日签到
@scheduler.scheduled_job(
    "cron",
    hour=0,
    minute=0,
)
async def _():
    sql_message.singh_remake()
    logger.info("每日修仙签到重置成功！")


@time_mes.handle()
async def _(event: GroupMessageEvent):
    """押注超时校验"""
    global race
    group_id = await get_group_id(event.get_session_id())
    try:
        if race[group_id]:
            race_time = race[group_id].time
            time_now = datetime.now()
            if (time_now - race_time).seconds > 30:
                del race[group_id]
                await time_mes.finish("太久没押注开始，被挤走了")
            else:
                pass
        else:
            pass
    except KeyError:
        pass


@remaname.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    """修改道号"""
    user_id = event.get_user_id()
    user_name = args.extract_plain_text().strip()
    if sql_message.get_user_message(user_id) is None:
        await in_closing.finish("修仙界没有道友的信息，请输入【我要修仙】加入！")

    mes = sql_message.update_user_name(user_id, user_name)
    await remaname.finish(mes)


@in_closing.handle()
async def _(event: GroupMessageEvent):
    """闭关"""
    user_type = 1  # 状态1为闭关
    user_id = event.get_user_id()

    if sql_message.get_user_message(user_id) is None:
        # 校验是否存在用户信息
        await in_closing.finish("修仙界没有道友的信息，请输入【我要修仙】加入！")
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


@out_closing.handle()
async def _(event: GroupMessageEvent):
    """出关"""
    user_type = 0  # 状态0为无事件
    user_id = event.get_user_id()

    user_mes = sql_message.get_user_message(user_id)  # 获取用户信息
    level = user_mes.level
    use_exp = user_mes.exp

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
            await out_closing.finish(
                "闭关结束，本次闭关到达上限，共增加修为：{}".format(user_get_exp_max), at_sender=True
            )
        else:
            # 用户获取的修为没有到达上限

            if str(event.message) == "灵石出关":
                user_stone = user_mes.stone  # 用户灵石数
                if exp <= user_stone:
                    exp = exp * 2
                    sql_message.in_closing(user_id, user_type)
                    sql_message.update_exp(user_id, exp)
                    sql_message.update_ls(user_id, exp, 2)
                    sql_message.update_power2(user_id)  # 更新战力
                    await out_closing.finish(
                        "闭关结束，共闭关{}分钟，本次闭关增加修为：{}，消耗灵石{}枚".format(exp_time, exp, exp/2), at_sender=True
                    )
                else:
                    exp = exp + user_stone
                    sql_message.in_closing(user_id, user_type)
                    sql_message.update_exp(user_id, exp)
                    sql_message.update_ls(user_id, user_stone, 2)
                    sql_message.update_power2(user_id)  # 更新战力
                    await out_closing.finish(
                        "闭关结束，共闭关{}分钟，本次闭关增加修为：{}，消耗灵石{}枚".format(exp_time, exp, user_stone), at_sender=True
                    )
            else:
                sql_message.in_closing(user_id, user_type)
                sql_message.update_exp(user_id, exp)
                sql_message.update_power2(user_id)  # 更新战力
                await out_closing.finish(
                    "闭关结束，共闭关{}分钟，本次闭关增加修为：{}".format(exp_time, exp), at_sender=True
                )

    elif user_cd_message.type == 2:
        await out_closing.finish("悬赏令事件进行中，请输入【悬赏令结算】结束！", at_sender=True)


async def get_group_id(session_id):
    """获取group_id"""
    res = re.findall("_(.*)_", session_id)
    group_id = res[0]
    return group_id


@level_up.handle()
async def update_level(event: GroupMessageEvent):
    """突破"""
    user_id = event.get_user_id()
    user_msg = sql_message.get_user_message(user_id)

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

    le = OtherSet().get_type(exp, level_rate, level_name)

    if le == "失败":
        # 突破失败
        sql_message.updata_level_cd(user_id)  # 更新突破CD

        # 失败惩罚，随机扣减修为
        percentage = random.randint(
            XiuConfig().level_punishment_floor, XiuConfig().level_punishment_limit
        )
        now_exp = int(int(exp) * (percentage / 100))

        sql_message.update_j_exp(user_id, now_exp)  # 更新用户修为
        await level_up.finish("道友突破失败,境界受损,修为减少{}，过段时间再突破吧！".format(now_exp))

    elif type(le) == list:
        # 突破成功
        sql_message.updata_level(user_id, le[0])  # 更新境界
        sql_message.update_power2(user_id)  # 更新战力
        sql_message.updata_level_cd(user_id)  # 更新CD
        await level_up.finish("恭喜道友突破{}成功".format(le[0]))
    else:
        # 最高境界
        await level_up.finish(le)


@give_stone.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    """送灵石"""
    user_id = event.get_user_id()
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


@do_work.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    """悬赏令"""
    global work
    user_type = 2
    work_list = []
    user_id = event.get_user_id()

    text = args.extract_plain_text().strip()

    if sql_message.get_user_message(user_id) is None:
        await do_work.finish("修仙界没有道友的信息，请输入【我要修仙】加入！")

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
            
#偷灵石
@steal_stone.handle()
async def _(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    user_id = event.get_user_id()
    user_message = sql_message.get_user_message(user_id)
    steal_user = None
    steal_user_stone = None

    if user_message is None:
        await steal_stone.finish('修仙界没有你的信息！请输入我要修仙，踏入修行')

    user_stone_num = user_message.stone
    steal_qq = None  # 艾特的时候存到这里, 要偷的人
    steal_name = None
    msg = args.extract_plain_text().strip()

    nick_name = re.findall("\D+", msg)  ## 道号

    coststone_num = XiuConfig().tou  # print(give_stone_num)# print(user_stone_num)
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
            if int(steal_success) < OtherSet().get_power_rate(user_message.stone, steal_user.stone):
                sql_message.update_ls(user_id, coststone_num, 2)  # 减少手续费
                await steal_stone.finish('道友偷窃失手了，被对方发现并被派去华哥厕所义务劳工！')

            get_stone = random.randint(5, 100)
            sql_message.update_ls(user_id, coststone_num, 2)  # 减少手续费

            if int(get_stone) > int(steal_user_stone):
                sql_message.update_ls(user_id, steal_user_stone, 1)  # 增加偷到的灵石
                sql_message.update_ls(steal_qq, steal_user_stone, 2)  # 减少被偷的人的灵石
                await steal_stone.finish(
                    "{}道友已经被榨干了~".format(steal_user.user_name))
            else:
                sql_message.update_ls(user_id, get_stone, 1)  # 增加偷到的灵石
                sql_message.update_ls(steal_qq, get_stone, 2)  # 减少被偷的人的灵石
                await steal_stone.finish(
                    "共偷取{}道友{}枚灵石！".format(steal_user.user_name, get_stone))
        else:
            await steal_stone.finish(result)

    else:
        await steal_stone.finish("对方未踏入修仙界，不要对杂修出手！")

    if nick_name:
        give_message = sql_message.get_user_message2(nick_name[0])
        give_user_stone = give_message.stone
        if give_message:
            steal_success2 = random.randint(0, 100)

            result = OtherSet().get_power_rate(user_message.power, give_message.power)
            if isinstance(result, int):
                if int(steal_success2) < result:
                    sql_message.update_ls(user_id, coststone_num, 2)  # 减少手续费
                    await steal_stone.finish('道友偷窃失手了，被对方发现并被派去华哥厕所义务劳工！')
                get_stone2 = random.randint(5, 100)
                sql_message.update_ls(user_id, coststone_num, 2)  # 减少手续费
                if int(get_stone2) > int(give_user_stone):
                    sql_message.update_ls(user_id, give_user_stone, 1)  # 增加偷到的灵石
                    sql_message.update_ls(give_message.user_id, give_user_stone, 2)  # 减少被偷的人的灵石
                    await steal_stone.finish("{}道友已经被榨干了~".format(give_message.user_name))
                else:
                    sql_message.update_ls(user_id, get_stone2, 1)  # 增加偷到的灵石
                    sql_message.update_ls(give_message.user_id, get_stone2, 2)  # 减少被偷的人的灵石
                    await steal_stone.finish("共偷取{}道友{}枚灵石！".format(give_message.user_name, get_stone2))
            else:
                await steal_stone.finish(result)
        else:
            await steal_stone.finish("对方未踏入修仙界，不要对杂修出手！")

    else:
        await steal_stone.finish("未获取道号信息，请输入正确的道号！")


# GM加灵石
@gm_command.handle()
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
