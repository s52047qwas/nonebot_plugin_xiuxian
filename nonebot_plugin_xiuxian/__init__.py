import re
from itertools import chain
from nonebot.log import logger
from nonebot import get_driver
from nonebot import on_command,require,on_message
from nonebot.params import CommandArg, RawCommand,Depends, Arg, ArgStr, RegexMatched
from nonebot.adapters.onebot.v11 import Bot, Event, GROUP, GROUP_ADMIN, GROUP_OWNER, Message, MessageEvent, GroupMessageEvent,MessageSegment
from .xiuxian2_handle import XiuxianDateManage,linggen_get,XiuxianJsonDate,OtherSet
from datetime import datetime
import random
from .xiuxian_opertion import gamebingo

scheduler = require("nonebot_plugin_apscheduler").scheduler


__xiuxian_version__ = "v0.0.1"
__xiuxian_notes__ = f'''
修仙模拟器帮助信息:
指令：
1、我要修仙：进入修仙模式
2、我的修仙信息：获取修仙数据
3、修仙签到：获取灵石及修为
4、重入仙途：重置灵根数据，每次100灵石
5、#金银阁：猜大小，赌灵石
6、改名xx：修改你的道号
7、突破：修为足够后，可突破境界（一定几率失败）
8、闭关、出关：修炼增加修为，挂机功能
9、送灵石+数量+道号或者艾特对应人
10、排行榜：修仙排行榜，灵石排行榜
10、其他功能to do中 
'''.strip()

driver = get_driver()


run_xiuxian = on_command('我要修仙',priority=5)
xiuxian_message = on_command('我的修仙信息',aliases={'我的存档'},priority=5)
rename = on_command('改名',priority=5)
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

race = {}
sql_message = XiuxianDateManage()

@run_xiuxian.handle()
async def _(bot: Bot, event: GroupMessageEvent,args: Message = CommandArg()):
    user_id = event.get_user_id()
    group_id = await get_group_id(event.get_session_id())
    # text = args.extract_plain_text().strip()   获取命令后面的信息
    user_name = event.sender.card if event.sender.card else event.sender.nickname
    name, type = linggen_get()
    rate  = sql_message.get_type_power(type)
    power = 100 * float(rate)
    create_time = str(datetime.now())

    msg = sql_message.create_user(user_id,name,type,int(power),create_time,user_name)
    await run_xiuxian.finish(msg,at_sender=True)

@xiuxian_message.handle()
async def _(event: GroupMessageEvent):
    user_id = event.get_user_id()
    group_id = await get_group_id(event.get_session_id())


    mess = sql_message.get_user_message(user_id)
    user_name = mess.user_name
    if user_name:
        pass
    else:
        user_name = '无名氏(发送改名+道号更新)'
    if mess:
        msg = f'''{user_name}道友的信息
灵根为：{mess[3]}
灵根类型为：{mess[4]}
当前境界：{mess[5]}
当前灵石：{mess[2]}
当前修为：{mess.exp}
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

    name, type = linggen_get()
    result = sql_message.ramaker(name,type,user_id)
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
        await in_closing.finish("已经在历练中，请输入【结束历练】结束！", at_sender=True)

@out_closing.handle()
async def _(bot: Bot, event: GroupMessageEvent,args: Message = CommandArg()):
    user_type = 0
    user_id = event.get_user_id()

    user_mes = sql_message.get_user_message(user_id)
    level = user_mes.level
    use_exp = user_mes.exp

    max_exp = int(OtherSet().set_closing_type(level))
    user_get_exp_max = max_exp - use_exp
    now_time = datetime.now()
    user_cd_message = sql_message.get_user_cd(user_id)

    if user_cd_message is None:
        await out_closing.finish("没有查到道友的信息，修炼发送【闭关】，进入修炼状态！",at_sender=True)
    elif user_cd_message.type == 0:
        await out_closing.finish("道友现在什么都没干呢~", at_sender=True)
    elif user_cd_message.type == 1:
        in_closing_time = datetime.strptime(user_cd_message.create_time, "%Y-%m-%d %H:%M:%S.%f")
        exp_time = (now_time - in_closing_time).seconds // 60
        exp = exp_time * 10
        if exp >= user_get_exp_max:
            sql_message.in_closing(user_id,user_type)
            sql_message.update_exp(user_id,user_get_exp_max)
            await out_closing.finish("闭关结束，本次闭关到达上限，共增加修为：{}".format(user_get_exp_max), at_sender=True)
        else:
            sql_message.in_closing(user_id, user_type)
            sql_message.update_exp(user_id, exp)
            await out_closing.finish("闭关结束，共闭关{}分钟，本次闭关增加修为：{}".format(exp_time, exp),at_sender=True)
    elif user_cd_message.type == 2:
        await out_closing.finish("已经在历练中，请输入【结束历练】结束！")



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
        cd = (time_now - datetime.strptime(level_cd, '%Y-%m-%d %H:%M:%S.%f')).seconds
        if cd < 6000:
            await level_up.finish('目前无法突破，还需要{}分钟'.format(100 - (cd//60)))
    else:
        pass

    level_name = user_mes.level  #境界
    exp = user_mes.exp   #修为

    level_rate = XiuxianJsonDate().level_rate(level_name)  #对应境界突破的概率

    le = OtherSet().get_type(exp, level_rate, level_name)

    if le=='失败':
        sql_message.updata_level_cd(user_id)
        percentage = random.randint(1, 10)
        now_exp = int(int(exp) * (percentage / 100))
        sql_message.update_j_exp(user_id, now_exp)
        await level_up.finish('道友突破失败,境界受损,修为减少{}，过段时间再突破吧！'.format(now_exp))
    elif type(le)==list:
        sql_message.updata_level(user_id,le[0])
        sql_message.update_power(user_id)
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
    print(give_stone_num)
    print(user_stone_num)
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












