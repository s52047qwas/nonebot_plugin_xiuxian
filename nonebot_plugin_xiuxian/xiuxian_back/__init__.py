from nonebot import on_command
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
from nonebot.params import CommandArg, RegexGroup
from ..utils import data_check_conf, check_user, send_forward_msg
from ..xiuxian2_handle import XiuxianDateManage
from ..data_source import jsondata


shop = on_command("坊市", priority=5)
mind_back = on_command('我的背包', aliases={'我的物品'}, priority=5)
use = on_command("使用", priority=5)
buy = on_command("购买", priority=5)

sql_message = XiuxianDateManage()  # sql类

@buy.handle()
async def _(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    """购物"""
    await data_check_conf(bot, event)
    isUser, user_info, msg = check_user(event)
    if not isUser:
        await buy.finish(msg, at_sender=True)
    user_id = user_info.user_id

    goods_data = jsondata.shop_data()
    get_goods = str(args)
    logger.info(f'商品名称：{get_goods}')

    for i, v in goods_data.items():
        logger.info(f'商品列表：{v}')
        if v['name'] == get_goods:
            logger.info(f"sql字段：{user_id}, {i, get_goods}, {v['type']}, {1}, {v['desc']}")
            price = v['price']
            if user_info.stone >= price:
                sql_message.update_ls(user_id, price, 2)
                sql_message.send_back(user_id, i, v['name'], v['type'], 1)
                await buy.finish('购买成功！', at_sender=True)
            else:
                await buy.finish('没钱还敢来买东西！！', at_sender=True)
        else:
            continue
            # await buy.finish('没有获取道商品信息！')
    await buy.finish('没有获取道商品信息', at_sender=True)
    
@shop.handle()
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
    
@mind_back.handle()
async def _(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    """我的背包"""
    await data_check_conf(bot, event)
    isUser, user_info, msg = check_user(event)
    if not isUser:
        await buy.finish(msg, at_sender=True)
    user_id = user_info.user_id
    data = jsondata.shop_data()  # 物品json信息
    back_msg = sql_message.get_back_msg(user_id)  # 背包sql信息

    # ["user_id", "goods_id", "goods_name", "goods_type", "goods_num", "create_time", "update_time",
    #  "remake", "day_num", "all_num", "action_time", "state"]
    msg = f"{user_info.user_name}的背包\n"
    for i in back_msg:
        msg += f"名称：{i[2]},类型：{i[3]},数量：{i[4]}," \
              f"效果：{data[str(i[1])]['desc']},售价：{data[str(i[1])]['selling']}\n"
    await mind_back.finish(msg)
    
@use.handle()
async def _(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    """使用物品
        # ["user_id", "goods_id", "goods_name", "goods_type", "goods_num", "create_time", "update_time",
    #  "remake", "day_num", "all_num", "action_time", "state"]
    """
    await data_check_conf(bot, event)
    isUser, user_info, msg = check_user(event)
    if not isUser:
        await buy.finish(msg, at_sender=True)
    user_id = user_info.user_id
    await use.finish('调试中，未开启！')
    get_goods = str(args)
    data = jsondata.shop_data()  # 物品json信息
    back_msg = sql_message.get_back_msg(user_id)  # 背包sql信息

    for i in back_msg:
        if i[2] == get_goods:
            pass