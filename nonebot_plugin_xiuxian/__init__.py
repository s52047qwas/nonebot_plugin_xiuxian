import re
from nonebot.log import logger
from nonebot import get_driver
from nonebot import on_command,require,on_message
from nonebot.params import CommandArg, RawCommand,Depends, Arg, ArgStr, RegexMatched
from nonebot.adapters.onebot.v11 import Bot, Event, GROUP, GROUP_ADMIN, GROUP_OWNER, Message, MessageEvent, \
    GroupMessageEvent, MessageSegment
from .xiuxian2_handle import XiuxianDateManage, XiuxianJsonDate, OtherSet
from datetime import datetime
import random
from .xiuxian_opertion import gamebingo, do_is_work, time_msg
from .xiuxian_config import XiuConfig
from .data_source import jsondata

scheduler = require("nonebot_plugin_apscheduler").scheduler


__xiuxian_version__ = "v0.0.1"
__xiuxian_notes__ = f'''
修仙模拟器帮助信息:
指令：
1、我要修仙：进入修仙模式
2、我的修仙信息：获取修仙数据
3、修仙签到：获取灵石及修为
4、重入仙途：重置灵根数据，每次100灵石
5、金银阁：猜大小，赌灵石
6、改名xx：修改你的道号
7、突破：修为足够后，可突破境界（一定几率失败）
8、闭关、出关：修炼增加修为，挂机功能
9、送灵石+数量+道号或者艾特对应人
10、排行榜：修仙排行榜，灵石排行榜
11、悬赏令：获取任务单，接取任务示例：悬赏令接取1， 结算命令示例：悬赏令结算
-简易灵根帮助-
混沌灵根>融合灵根>超灵根>龙灵根>天灵根>变异灵根>真灵根>伪灵根
'''.strip()

driver = get_driver()


run_xiuxian = on_command('我要修仙',priority=5)
xiuxian_message = on_command('我的修仙信息',aliases={'我的存档'},priority=5)
restart = on_command('再入仙途',aliases={'重新修仙'},priority=5)
package = on_command('我的纳戒',aliases={'升级纳戒'},priority=5)
sign_in = on_command('修仙签到',priority=5)
dufang = on_command('#金银阁',aliases={'金银阁'},priority=5)
dice = on_command('大',aliases={'小'},priority=5)
price = on_command('押注',priority=5)
help_in = on_command('修仙帮助',priority=5)
remaker = on_command('重入仙途',priority=5)
use = on_command('#使用',priority=5)
buy = on_command('#购买',priority=5)
level_rank = on_command('境界排行',aliases={'修仙排行榜','排行榜'},priority=5)
stone_rank = on_command('灵石排行',aliases={'灵石排行榜'},priority=5)
time_mes = on_message(priority=999)
remaname = on_command('改名',priority=5)
level_up = on_command('突破',priority=5)
in_closing = on_command('闭关',priority=5)
out_closing = on_command('出关',priority=5)
give_stone = on_command('送灵石', priority=5)
do_work = on_command("悬赏令", priority=5)

race = {}  # 押注信息记录
work = {}  # 悬赏令信息记录
sql_message = XiuxianDateManage()

@run_xiuxian.handle()
async def _(event: GroupMessageEvent):
    user_id = event.get_user_id()
    # group_id = await get_group_id(event.get_session_id())
    # text = args.extract_plain_text().strip()   获取命令后面的信息
    user_name = event.sender.card if event.sender.card else event.sender.nickname  # 获取为用户名
    root, root_type = XiuxianJsonDate().linggen_get()     # 获取灵根，灵根类型

    rate = sql_message.get_root_rate(root_type)
    power = 100 * float(rate)
    create_time = str(datetime.now())

    msg = sql_message.create_user(user_id, root, root_type, int(power), create_time, user_name)
    await run_xiuxian.finish(msg, at_sender=True)

@xiuxian_message.handle()
async def _(event: GroupMessageEvent):
    user_id = event.get_user_id()
    # group_id = await get_group_id(event.get_session_id())

    mess = sql_message.get_user_message(user_id)

    if mess:
        user_name = mess.user_name
        if user_name:
            pass
        else:
            user_name = '无名氏(发送改名+道号更新)'
         level_rate = sql_message.get_root_rate(mess.root_type)  # 灵根倍率
        # realm_rate = ((OtherSet().level.index(mess.level)) * 0.2) + 1  # 境界倍率
        realm_rate = jsondata.level_data()[mess.level]['spend']   # 境界倍率
        list_all = len(XiuConfig().level) - 1
        now_index = XiuConfig().level.index(mess.level)
        is_updata_level = XiuConfig().level[now_index + 1]
        need_exp = XiuxianDateManage().get_level_power(is_updata_level)
        # print(level_rate)
        # print(realm_rate)
        msg = f'''{user_name}道友的信息
灵根为：{mess[3]}
灵根类型为：{mess[4]}
灵根倍率为：{round(level_rate,2)}
当前境界：{mess[5]}
境界倍率为：{round(realm_rate,2)}
当前灵石：{mess[2]}
当前修为：{mess.exp}(修炼效率+{int((level_rate * realm_rate) * 100)}%)
到下个境界还需{need_exp-mess.exp}修为
你的战力为：{mess[6]}'''
    else:
        msg = '未曾踏入修仙世界，输入 我要修仙 加入我们，看破这世间虚妄!'

    await run_xiuxian.finish(msg,at_sender=True)

@sign_in.handle()
async def _(event: GroupMessageEvent):
    user_id = event.get_user_id()
    group_id = await get_group_id(event.get_session_id())
    result = sql_message.get_sign(user_id)
    await sign_in.send(result, at_sender=True)


@help_in.handle()
async def _(event: GroupMessageEvent):
    msg = __xiuxian_notes__
    await help_in.send(msg, at_sender=True)

@dice.handle()
async def _(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg(), cmd: Message = RawCommand()):
    global race
    message = event.message
    user_id = event.get_user_id()
    group_id = await get_group_id(event.get_session_id())
    try:
        race[group_id]
    except KeyError:
        await price.finish()

    if race[group_id].player[0] == user_id:
        pass
    else:
        await dice.finish('吃瓜道友请不要捣乱！！！')

    price_num = race[group_id].price
    if price_num==0:
        await dice.finish('道友押注失败,请发送【押注+数字】押注！', at_sender=True)


    if str(message) == '大' or str(message) == '小':
        pass
    else:
        await dice.finish('请输入正确的结果【大】或者【小】！')

    value = random.randint(1, 6)
    msg = Message("[CQ:dice,value={}]".format(value))

    if value >= 4:
        if str(message)=='大':
            del race[group_id]
            sql_message.update_ls(user_id,price_num,1)
            await dice.send(msg)
            await dice.finish('最终结果为{}，你猜对了，收获灵石{}块'.format(value,price_num),at_sender=True)
        else:
            del race[group_id]
            sql_message.update_ls(user_id, price_num, 2)
            await dice.send(msg)
            await dice.finish('最终结果为{}，你猜错了，损失灵石{}块'.format(value, price_num),at_sender=True)
    elif value <= 3:
        if str(message) == '大':
            del race[group_id]
            sql_message.update_ls(user_id, price_num, 2)
            await dice.send(msg)
            await dice.finish('最终结果为{}，你猜错了，损失灵石{}块'.format(value, price_num),at_sender=True)
        else:
            del race[group_id]
            sql_message.update_ls(user_id, price_num, 1)
            await dice.send(msg)
            await dice.finish('最终结果为{}，你猜对了，收获灵石{}块'.format(value, price_num),at_sender=True)


@dufang.handle()
async def _(bot: Bot, event: GroupMessageEvent, args: Message=CommandArg(), cmd: Message=RawCommand()):
    global race
    user_id = event.get_user_id()
    group_id = await get_group_id(event.get_session_id())
    user_message = sql_message.get_user_message(user_id)
    if user_message:
        if user_message.stone==0:
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
    await dufang.finish(f'发送【押注+数字】参与',at_sender=True)


@price.handle()
async def _(bot: Bot, event: GroupMessageEvent, args: Message=CommandArg(), cmd: Message=CommandArg()):
    global race
    user_id = event.get_user_id()
    group_id = await get_group_id(event.get_session_id())
    msg = args.extract_plain_text().strip()

    user_message = sql_message.get_user_message(user_id)
    try:
        race[group_id]
    except KeyError:
        await price.finish(f"金银阁未开始，请输入【金银阁】开场",at_sender=True)
    try:
        if race[group_id].player[0] == user_id:
            pass
        else:
            await price.finish('吃瓜道友请不要捣乱！')
    except KeyError:
        await price.finish()
    if msg:
        price_num = msg
        if race[group_id].price != 0:
            await price.finish('钱财离手，不可退回！', at_sender=True)
        elif int(user_message.stone) < int(price_num):
            await price.finish('道友的金额不足，请重新输入！')
        elif price_num.isdigit():
            race[group_id].add_price(int(price_num))
        else:
            await price.finish('请输入正确的金额！')
    else:
        await price.finish(f"请输入押注金额", at_sender=True)

    out_msg = f'押注完成，发送【大】或者【小】 参与本局游戏！'
    await price.finish(out_msg, at_sender=True)



@remaker.handle()
async def _(bot: Bot, event: GroupMessageEvent, args: Message=CommandArg(), cmd: Message=RawCommand()):
    user_id = event.get_user_id()
    group_id = await get_group_id(event.get_session_id())

    name, type = XiuxianJsonDate().linggen_get()
    result = sql_message.ramaker(name, type ,user_id)
    await remaker.send(message=result,at_sender=True)


@level_rank.handle()
async def _():
    rank = sql_message.realm_top()
    await level_rank.send(message=rank)

@stone_rank.handle()
async def _():
    rank = sql_message.stone_top()
    await stone_rank.send(message=rank)


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
async def _(bot: Bot,event: GroupMessageEvent):
    global race
    group_id = await get_group_id(event.get_session_id())
    # print(event.sender.card if event.sender.card else event.sender.nickname)
    try:
        if race[group_id]:
            race_time = race[group_id].time
            time_now = datetime.now()
            if (time_now - race_time).seconds >30:
                del race[group_id]
                await time_mes.finish('太久没押注开始，被挤走了')
            else:
                pass
        else:
            pass
    except KeyError:
        pass

@remaname.handle()
async def _(bot: Bot,event: GroupMessageEvent,args: Message = CommandArg()):
    user_id = event.get_user_id()
    group_id = await get_group_id(event.get_session_id())
    user_name = args.extract_plain_text().strip()
    if sql_message.get_user_message(user_id) is None:
        await in_closing.finish("修仙界没有道友的信息，请输入【我要修仙】加入！")

    mes = sql_message.update_user_name(user_id,user_name)
    await remaname.finish(mes)


@in_closing.handle()
async def _(bot: Bot, event: GroupMessageEvent,args: Message = CommandArg()):
    user_type = 1
    user_id = event.get_user_id()

    if sql_message.get_user_message(user_id) is None:
        await in_closing.finish("修仙界没有道友的信息，请输入【我要修仙】加入！")
    user_cd_message = sql_message.get_user_cd(user_id)

    if user_cd_message is None:
        sql_message.in_closing(user_id, user_type)
        await in_closing.finish("进入闭关状态，如需出关，发送【出关】！", at_sender=True)
    elif user_cd_message.type == 0:
        sql_message.in_closing(user_id, user_type)
        await in_closing.finish("进入闭关状态，如需出关，发送【出关】！", at_sender=True)
    elif user_cd_message.type == 1:
        await in_closing.finish("已经在闭关中，请输入【出关】结束！", at_sender=True)
    elif user_cd_message.type == 2:
        await in_closing.finish("悬赏令事件进行中，请输入【悬赏令结算】结束！", at_sender=True)

@out_closing.handle()
async def _(bot: Bot, event: GroupMessageEvent,args: Message = CommandArg()):
    user_type = 0
    user_id = event.get_user_id()

    user_mes = sql_message.get_user_message(user_id)
    level = user_mes.level
    use_exp = user_mes.exp

    max_exp = int(OtherSet().set_closing_type(level)) * 1.5
    user_get_exp_max = int(max_exp) - use_exp
    now_time = datetime.now()
    user_cd_message = sql_message.get_user_cd(user_id)

    if user_cd_message is None:
        await out_closing.finish("没有查到道友的信息，修炼发送【闭关】，进入修炼状态！",at_sender=True)
    elif user_cd_message.type == 0:
        await out_closing.finish("道友现在什么都没干呢~", at_sender=True)
    elif user_cd_message.type == 1:
        in_closing_time = datetime.strptime(user_cd_message.create_time, "%Y-%m-%d %H:%M:%S.%f")
        # exp_time = (now_time - in_closing_time).seconds // 60   # 闭关时长计算
        exp_time = OtherSet().date_diff(now_time,in_closing_time) // 60    # 闭关时长计算
        level_rate = sql_message.get_root_rate(user_mes.root_type)  # 灵根倍率
        # realm_rate = ((OtherSet().level.index(level)) * 0.2) + 1   # 境界倍率
        realm_rate = jsondata.level_data()[level]['spend']   # 境界倍率
        exp = int(exp_time * 10 * level_rate * realm_rate)

        # print("max_exp",max_exp)
        # print("user_get_exp_max",user_get_exp_max)
        # print("level_rate", level_rate)
        # print("realm_rate", realm_rate)
        # print("exp", exp)
        # print("OtherSet().level.index(level)", OtherSet().level.index(level))
        # print("user_level", level)


        if exp >= user_get_exp_max:
            sql_message.in_closing(user_id,user_type)
            sql_message.update_exp(user_id,user_get_exp_max)
            await out_closing.finish("闭关结束，本次闭关到达上限，共增加修为：{}".format(user_get_exp_max), at_sender=True)
        else:
            sql_message.in_closing(user_id, user_type)
            sql_message.update_exp(user_id, exp)
            await out_closing.finish("闭关结束，共闭关{}分钟，本次闭关增加修为：{}".format(exp_time, exp),at_sender=True)
    elif user_cd_message.type == 2:
        await out_closing.finish("悬赏令事件进行中，请输入【悬赏令结算】结束！",at_sender=True)



async def get_group_id(session_id):
    res = re.findall("_(.*)_", session_id)
    group_id = res[0]
    return group_id

@level_up.handle()
async def update_level(event: GroupMessageEvent):
    user_id = event.get_user_id()
    group_id = await get_group_id(event.get_session_id())

    user_mes = sql_message.get_user_message(user_id)

    level_cd = user_mes.level_up_cd
    if level_cd:
        time_now = datetime.now()
        cd = OtherSet().date_diff(time_now,level_cd)
        if cd < XiuConfig().level_up_cd * 60:
            await level_up.finish('目前无法突破，还需要{}分钟'.format( XiuConfig().level_up_cd - (cd // 60)))
    else:
        pass

    level_name = user_mes.level  #境界
    exp = user_mes.exp   #修为
    level_rate = jsondata.level_rate_data()[level_name]  #对应境界突破的概率

    le = OtherSet().get_type(exp, level_rate, level_name)

    if le=='失败':
        sql_message.updata_level_cd(user_id)
        percentage = random.randint(1, 10)
        now_exp = int(int(exp) * (percentage / 100))
        sql_message.update_j_exp(user_id, now_exp)
        await level_up.finish('道友突破失败,境界受损,修为减少{}，过段时间再突破吧！'.format(now_exp))
    elif type(le)==list:
        sql_message.updata_level(user_id,le[0])
        sql_message.update_power2(user_id)
        sql_message.updata_level_cd(user_id)
        await level_up.finish('恭喜道友突破{}成功'.format(le[0]))
    else:
        await level_up.finish(le)


@give_stone.handle()
async def _(bot: Bot, event: GroupMessageEvent,args: Message = CommandArg()):
    user_id = event.get_user_id()
    user_message = sql_message.get_user_message(user_id)
    if user_message is None:
        await give_stone.finish('修仙界没有你的信息！请输入我要修仙，踏入修行')

    user_stone_num = user_message.stone
    give_qq = None  #艾特的时候存到这里
    give_name = None
    msg = args.extract_plain_text().strip()

    stone_num = re.findall("\d+", msg)  ##灵石数
    nick_name = re.findall("\D+", msg)  ##道号

    if stone_num:
        pass
    else:
        await give_stone.finish('请输入正确的灵石数量！')

    give_stone_num = stone_num[0]
    # print(give_stone_num)
    # print(user_stone_num)
    if int(give_stone_num) > int(user_stone_num):
        await give_stone.finish('道友的灵石不够，请重新输入！')

    for arg in args:
        if arg.type == "at":
            give_qq = arg.data.get('qq','')

    if give_qq:
        if give_qq == user_id :
            await give_stone.finish("请不要送灵石给自己！")
        else:
            give_user = sql_message.get_user_message(give_qq)
            if give_user:
                sql_message.update_ls(user_id, give_stone_num, 2)  # 减少用户灵石
                give_stone_num2 = int(give_stone_num) * 0.03
                num = int(give_stone_num) - int(give_stone_num2)
                sql_message.update_ls(give_qq, num, 1)   # 增加用户灵石

                await give_stone.finish(
                    "共赠送{}枚灵石给{}道友！收取手续费{}枚".format(give_stone_num,give_qq, int(give_stone_num2)))
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
                    "共赠送{}枚灵石给{}道友！收取手续费{}枚".format(give_stone_num, give_message.user_name, int(give_stone_num2)))
        else:
            await give_stone.finish("对方未踏入修仙界，不可赠送！")

    else:
        await give_stone.finish("未获取道号信息，请输入正确的道号！")


@do_work.handle()
async def _(bot: Bot, event: GroupMessageEvent,args: Message = CommandArg()):
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
                    get_work = work[user_id].world[int(work_num[0])-1]
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
            work_time = datetime.strptime(user_cd_message.create_time, "%Y-%m-%d %H:%M:%S.%f")
            exp_time = (datetime.now() - work_time).seconds // 60  # 时长计算
            time2 = XiuxianJsonDate().do_work(key=1,name=user_cd_message.scheduled_time)
            if exp_time < time2:
                await do_work.finish(f"进行中的悬赏令【{user_cd_message.scheduled_time}】，预计{time2 - exp_time}分钟后可结束",
                                     at_sender=True)
            else:
                work_sf = XiuxianJsonDate().do_work(2,user_cd_message.scheduled_time)
                sql_message.update_ls(user_id,work_sf[1],1)
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
        work_msg_f +=f"\n(悬赏令每小时更新一次)"
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
            n+=1
        work_msg_f +=f"\n(榜单每小时更新一次)"
        work[user_id] = do_is_work(user_id)
        work[user_id].time = datetime.now()
        work[user_id].msg = work_msg_f
        work[user_id].world = work_list
        await do_work.finish(work_msg_f)

    elif user_cd_message.type == 1:
        await do_work.finish("已经在闭关中，请输入【出关】结束后才能获取悬赏令！", at_sender=True)

    elif user_cd_message.type == 2:
        work_time = datetime.strptime(user_cd_message.create_time, "%Y-%m-%d %H:%M:%S.%f")
        exp_time = (datetime.now() - work_time).seconds // 60   # 闭关时长计算
        time2 = XiuxianJsonDate().do_work(key=1, name=user_cd_message.scheduled_time)
        if exp_time < time2:
            await do_work.finish(f"进行中的悬赏令【{user_cd_message.scheduled_time}】，预计{time2 - exp_time}分钟后可结束", at_sender=True)
        else:
            await do_work.finish(f"进行中的悬赏令【{user_cd_message.scheduled_time}】，已结束，请输入【悬赏令结算】结算任务信息！",
                                 at_sender=True)













