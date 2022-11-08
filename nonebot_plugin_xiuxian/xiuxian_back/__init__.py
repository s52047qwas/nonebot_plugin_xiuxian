import asyncio
from nonebot import get_bot, on_command, require
from nonebot.adapters.onebot.v11 import (
    PRIVATE_FRIEND,
    Bot,
    GROUP,
    Message,
    MessageEvent,
    GroupMessageEvent,
    MessageSegment,
    GROUP_ADMIN,
    GROUP_OWNER
)
from nonebot.permission import SUPERUSER
from nonebot.log import logger
from nonebot.params import CommandArg, RegexGroup
from ..utils import data_check_conf, check_user, send_forward_msg
from ..xiuxian2_handle import XiuxianDateManage, OtherSet
from ..item_json import Items
from ..data_source import jsondata
from .back_util import get_user_back_msg, check_equipment_can_use, get_use_equipment_sql, get_shop_data, save_shop, get_item_msg
from .backconfig import get_config, savef
import random
from datetime import datetime
from ..read_buff import get_weapon_info_msg, get_armor_info_msg, get_sec_msg, get_main_info_msg, UserBuffDate

items = Items()
config = get_config()
groups = config['open'] #list，群拍卖行使用
auction = {}
AUCTIONSLEEPTIME = 60#拍卖初始等待时间（秒）

auction_offer_flag = False #出价标志
AUCTIONOFFERSLEEPTIME = 10#每次出价增加拍卖剩余的时间（秒）
auction_offer_time_count = 0 #计算剩余时间
auction_offer_all_count = 0 #控制线程等待时间


# 定时任务
set_auction_by_scheduler = require("nonebot_plugin_apscheduler").scheduler

shop = on_command("坊市查看", aliases={'查看坊市'}, priority=5)
shop_added = on_command("坊市上架", priority=5)
shop_off = on_command("坊市下架", priority=5)
mind_back = on_command('我的背包', aliases={'我的物品'}, priority=5 , permission= GROUP)
use = on_command("使用", priority=5)
buy = on_command("坊市购买", priority=5)
set_auction = on_command("群拍卖行", priority=5, permission= GROUP and (SUPERUSER | GROUP_ADMIN | GROUP_OWNER))
creat_auction = on_command("举行拍卖会", priority=5, permission= GROUP and (SUPERUSER))
offer_auction = on_command("出价", priority=5, permission= GROUP)
back_help = on_command("背包帮助", priority=5, permission= GROUP)

sql_message = XiuxianDateManage()  # sql类

__back_help__ = f"""
背包帮助信息:
指令：
1、我的背包、我的物品：查看自身背包信息
2、使用+物品名字：使用物品
3、坊市购买+物品编号：购买坊市内的物品
4、坊市查看、查看坊市：查询坊市在售物品
5、坊市上架：坊市上架 物品 金额，上架背包内的物品
6、坊市下架+物品编号：下架坊市内的物品，管理员和群主可以下架任意编号的物品！
7、群拍卖行开启、关闭：开启拍卖行功能，管理员指令，注意：会在机器人所在的全部已开启此功能的群内通报拍卖行消息
8、举行拍卖会：管理员指令，会立刻生成一次拍卖会
9、出价+金额：对本次排行会的物品进行出价
10、背包帮助：获取背包帮助指令
非指令：

""".strip()

# 定时任务生成拍卖会
@set_auction_by_scheduler.scheduled_job("interval", 
                       hours=2, 
                       minutes=0)
async def _():
    bot = get_bot()
    if groups != []:
        global auction
        if auction != {}:#存在拍卖会
            logger.info("本群已存在一场拍卖会")
            return
        else:
            try:
                auction_id_list = config['auction_config']['auction_id_list']
                auction_id = random.choice(auction_id_list)
            except IndexError:
                msg = "获取不到拍卖物品的信息，请检查配置文件！"
                logger.info(msg)
                return
            auction_info = items.get_data_by_item_id(auction_id)
            msg = '本次拍卖的物品为：\n'   
            msg += get_auction_msg(auction_id)
            msg += f"\n底价为{config['auction_config']['auction_start_prict']}灵石"
            msg += "\n请诸位道友发送 出价+金额 来进行拍卖吧！"
            msg += f"\n本次竞拍时间为：{AUCTIONSLEEPTIME}秒！"
            auction['id'] = auction_id
            auction['user_id'] = 0
            auction['now_price'] = config['auction_config']['auction_start_prict']
            auction['name'] = auction_info['name']
            auction['type'] = auction_info['type']
            auction['start_time'] = datetime.now()
            auction['group_id'] = 0
            for group_id in groups:
                await bot.send_group_msg(group_id=int(group_id), message=msg)
            await asyncio.sleep(AUCTIONSLEEPTIME)#先睡60秒
            
            global auction_offer_flag
            while auction_offer_flag:#有人出价
                global auction_offer_all_count
                if auction_offer_all_count == 0:
                    auction_offer_flag = False
                    break
                first_time = auction_offer_all_count * AUCTIONOFFERSLEEPTIME
                auction_offer_all_count = 0
                await asyncio.sleep(first_time)
            
            if auction['user_id'] == 0:
                msg = "很可惜，本次拍卖会流拍了！"
                auction = {}
                for group_id in groups:
                    await bot.send_group_msg(group_id=int(group_id), message=msg)
                return
            
            user_info = sql_message.get_user_message(auction['user_id'])
            msg = "本次拍卖会结束！"
            msg += f"恭喜来自群{auction['group_id']}的{user_info.user_name}道友成功拍卖获得：{auction['type']}-{auction['name']}！"
            for group_id in groups:
                await bot.send_group_msg(group_id=int(group_id), message=msg)
                
            sql_message.send_back(user_info.user_id, auction['id'], auction['name'], auction['type'], 1)
            sql_message.update_ls(user_info.user_id, int(auction['now_price']), 2)
            auction = {}
            global auction_offer_time_count
            auction_offer_time_count = 0
            return


@back_help.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    await data_check_conf(bot, event)
    await back_help.finish(__back_help__)

@buy.handle()
async def _(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    """购物"""
    await data_check_conf(bot, event)
    isUser, user_info, msg = check_user(event)
    if not isUser:
        await buy.finish(msg, at_sender=True)
    user_id = user_info.user_id
    group_id = str(event.group_id)
    shop_data = get_shop_data(group_id)
    if shop_data[group_id] == {}:
        msg = "坊市目前空空如也！"
        await buy.finish(msg, at_sender=True)
        
    arg = args.extract_plain_text().strip()
    try:
        arg = int(arg)
        if arg <= 0 or arg > len(shop_data[group_id]):
            msg = "请输入正确的编号！"
            await buy.finish(msg, at_sender=True)
    except  ValueError:
        msg = "请输入正确的编号！"
        await buy.finish(msg, at_sender=True)
        
    goods_price = shop_data[group_id][str(arg)]['price']
    if user_info.stone <= goods_price:
        msg = '没钱还敢来买东西！！'
        await buy.finish(msg, at_sender=True)
    elif int(user_id) == int(shop_data[group_id][str(arg)]['user_id']):
            msg = "道友自己的东西就不要自己购买啦！"
            await buy.finish(msg, at_sender=True)
    else:
        
        msg = f"道友成功购买{shop_data[group_id][str(arg)]['user_name']}道友寄售的物品{shop_data[group_id][str(arg)]['goods_name']}，消耗灵石{goods_price}枚！"
        sql_message.update_ls(user_id, goods_price, 2)
        sql_message.send_back(user_id, shop_data[group_id][str(arg)]['goods_id'], shop_data[group_id][str(arg)]['goods_name'], shop_data[group_id][str(arg)]['goods_type'], 1)
        service_charge = int(goods_price * 0.05)#手续费5%
        give_stone = goods_price - service_charge
        shop_msg1 = Message(f"道友上架的{shop_data[group_id][str(arg)]['goods_name']}已被购买，获得灵石{give_stone}枚，坊市收取手续费：{service_charge}枚灵石！")
        shop_msg2 = Message(f"[CQ:at,qq={shop_data[group_id][str(arg)]['user_id']}]")
        shop_msg = shop_msg1 + shop_msg2
        sql_message.update_ls(shop_data[group_id][str(arg)]['user_id'], give_stone, 1)
        await bot.send(event=event, message=shop_msg)
        del shop_data[group_id][str(arg)]
        shop_data[group_id] = reset_dict_num(shop_data[group_id])
        save_shop(shop_data)
        await buy.finish(msg, at_sender=True)
    # goods_data = jsondata.shop_data()
    # get_goods = str(args)
    # logger.info(f'商品名称：{get_goods}')

    # for i, v in goods_data.items():
    #     logger.info(f'商品列表：{v}')
    #     if v['name'] == get_goods:
    #         logger.info(f"sql字段：{user_id}, {i, get_goods}, {v['type']}, {1}, {v['desc']}")
    #         price = v['price']
    #         if user_info.stone >= price:
    #             sql_message.update_ls(user_id, price, 2)
    #             sql_message.send_back(user_id, i, v['name'], v['type'], 1)
    #             await buy.finish('购买成功！', at_sender=True)
    #         else:
    #             await buy.finish('没钱还敢来买东西！！', at_sender=True)
    #     else:
    #         continue
    #         # await buy.finish('没有获取道商品信息！')
    await buy.finish('购物功能未实现', at_sender=True)
    
@shop.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    """坊市查看"""
    await data_check_conf(bot, event)
    print(event)
    isUser, user_info, msg = check_user(event)
    if not isUser:
        await shop.finish(msg, at_sender=True)

    group_id = str(event.group_id)
    shop_data = get_shop_data(group_id)
    data_list = []
    if shop_data[group_id] == {}:
        msg = "坊市目前空空如也！"
        await shop.finish(msg, at_sender=True)
    for k, v in shop_data[group_id].items():
        msg = f"编号：{k}\n"
        msg += f"{v['desc']}"
        msg += f"\n价格：{v['price']}枚灵石\n"
        msg += f"拥有人：{v['user_name']} 道友\n"
        data_list.append(msg)
    await send_forward_msg(bot, event, '坊市', bot.self_id, data_list)
    await shop.finish()
    
@shop_added.handle()
async def _(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    """上架坊市"""
    await data_check_conf(bot, event)
    isUser, user_info, msg = check_user(event)
    if not isUser:
        await shop_added.finish(msg, at_sender=True)
    user_id = user_info.user_id
    args = args.extract_plain_text().split()
    if args == []:
        msg = "请输入正确指令！例如：坊市上架 物品 金额"
        await shop_added.finish(msg, at_sender=True)
    goods_name = args[0]
    
    back_msg = sql_message.get_back_msg(user_id)  # 背包sql信息,list(back)
    if back_msg == None:
        msg = "道友的背包空空如也！"
        await shop_added.finish(msg, at_sender=True)
    in_flag = False #判断指令是否正确，道具是否在背包内
    for back in back_msg:
        if goods_name == back.goods_name:
            in_flag = True
            goods_id = back.goods_id
            goods_type = back.goods_type
            goods_state = back.state
            break
    if not in_flag:
        msg = f"请检查该道具 {goods_name} 是否在背包内！"
        await use.finish(msg, at_sender=True)
    try:
        price = args[1]
    except IndexError:
        msg = "请输入正确的指令！例如：坊市上架 物品 金额"
        await shop_added.finish(msg, at_sender=True)
    try:
        price = int(price)
        if price < 0:
            msg = "请不要设置负数！"
            await shop_added.finish(msg, at_sender=True)
    except ValueError:
        msg = "请输入正确的金额！"
        await shop_added.finish(msg, at_sender=True)
    
    try:
        args[2]
        msg = "请输入正确的指令！例如：坊市上架 物品 金额"
        await shop_added.finish(msg, at_sender=True)
    except IndexError:
        pass
    
    if goods_type == "装备" and int(goods_state) == 1:
        msg = f"装备：{goods_name}已经被道友装备在身，无法上架！"
        await shop_added.finish(msg, at_sender=True)
    
    group_id = str(event.group_id)
    shop_data = get_shop_data(group_id)
    if shop_data == {}:
        shop_data[group_id] = {}
    
    id = len(shop_data[group_id]) + 1
    shop_data[group_id][id] = {}
    shop_data[group_id][id]['user_id'] = user_id
    shop_data[group_id][id]['goods_name'] = goods_name
    shop_data[group_id][id]['goods_id'] = goods_id
    shop_data[group_id][id]['goods_type'] = goods_type
    shop_data[group_id][id]['desc'] = get_item_msg(goods_id)
    shop_data[group_id][id]['price'] = price
    shop_data[group_id][id]['user_name'] = user_info.user_name
    sql_message.update_back_j(user_id, goods_id, all_num = 1)
    save_shop(shop_data)
    msg = f"物品：{goods_name}成功上架坊市，金额：{price}枚灵石！"
    await shop_added.finish(msg)
    
@shop_off.handle()
async def _(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    """下架商品"""
    await data_check_conf(bot, event)
    isUser, user_info, msg = check_user(event)
    if not isUser:
        await shop_off.finish(msg, at_sender=True)
    user_id = user_info.user_id
    group_id = str(event.group_id)
    shop_data = get_shop_data(group_id)
    if shop_data[group_id] == {}:
        msg = "坊市目前空空如也！"
        await shop_off.finish(msg, at_sender=True)
        
    arg = args.extract_plain_text().strip()
    try:
        arg = int(arg)
        if arg <= 0 or arg > len(shop_data[group_id]):
            msg = "请输入正确的编号！"
            await shop_off.finish(msg, at_sender=True)
    except  ValueError:
        msg = "请输入正确的编号！"
        await shop_off.finish(msg, at_sender=True)
    
    if shop_data[group_id][str(arg)]['user_id'] == user_id:
        sql_message.send_back(user_id, shop_data[group_id][str(arg)]['goods_id'], shop_data[group_id][str(arg)]['goods_name'], shop_data[group_id][str(arg)]['goods_type'], 1)
        msg = f"成功下架物品：{shop_data[group_id][str(arg)]['goods_name']}！"
        del shop_data[group_id][str(arg)]
        shop_data[group_id] = reset_dict_num(shop_data[group_id])
        save_shop(shop_data)
        await shop_off.finish(msg, at_sender=True)
        
    elif event.sender.role == "admin" or event.sender.role == "owner":
        sql_message.send_back(shop_data[group_id][str(arg)]['user_id'], shop_data[group_id][str(arg)]['goods_id'], shop_data[group_id][str(arg)]['goods_name'], shop_data[group_id][str(arg)]['goods_type'], 1)
        msg = f"成功下架{shop_data[group_id][str(arg)]['user_id']}的物品：{shop_data[group_id][str(arg)]['goods_name']}！"
        msg1 = Message(f"道友上架的{shop_data[group_id][str(arg)]['goods_name']}已被管理员{user_id}下架！")
        msg2 = Message(f"[CQ:at,qq={shop_data[group_id][str(arg)]['user_id']}]")
        msg3 = msg1 + msg2
        del shop_data[group_id][str(arg)]
        shop_data[group_id] = reset_dict_num(shop_data[group_id])
        save_shop(shop_data)
        await bot.send(event=event, message=msg3)
        await shop_off.finish(msg, at_sender=True)
    else:
        msg = "这东西不是你的！"
        await shop_off.finish(msg, at_sender=True)

    
@mind_back.handle()
async def _(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    """我的背包"""
    await data_check_conf(bot, event)
    isUser, user_info, msg = check_user(event)
    if not isUser:
        await buy.finish(msg, at_sender=True)
    user_id = user_info.user_id

    # ["user_id", "goods_id", "goods_name", "goods_type", "goods_num", "create_time", "update_time",
    #  "remake", "day_num", "all_num", "action_time", "state"]
    msg = get_user_back_msg(user_id)
    if msg != []:
        await send_forward_msg(bot, event, '背包', bot.self_id, msg)
        await mind_back.finish()
    else:
        msg = '道友的背包空空如也！'
        await mind_back.finish(msg, at_sender=True)
    
@use.handle()
async def _(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    """使用物品
        # ["user_id", "goods_id", "goods_name", "goods_type", "goods_num", "create_time", "update_time",
    #  "remake", "day_num", "all_num", "action_time", "state"]
    """
    await data_check_conf(bot, event)
    isUser, user_info, msg = check_user(event)
    if not isUser:
        await use.finish(msg, at_sender=True)
    user_id = user_info.user_id
    # await use.finish('调试中，未开启！')
    arg = args.extract_plain_text().strip()
    
    back_msg = sql_message.get_back_msg(user_id)  # 背包sql信息,list(back)
    if back_msg == None:
        msg = "道友的背包空空如也！"
        await use.finish(msg, at_sender=True)
    in_flag = False #判断指令是否正确，道具是否在背包内
    for back in back_msg:
        if arg == back.goods_name:
            in_flag = True
            goods_id = back.goods_id
            goods_type = back.goods_type
            break
    if not in_flag:
        msg = f"请检查该道具 {arg} 是否在背包内！"
        await use.finish(msg, at_sender=True)
    
    
    if goods_type == "装备":
        if not check_equipment_can_use(user_id, goods_id):
            msg = f"该装备已被装备，请勿重复装备！"
            await use.finish(msg, at_sender=True)
        else:#可以装备
            sql_str, item_type = get_use_equipment_sql(user_id, goods_id)
            for sql in sql_str:
                sql_message.update_back_equipment(sql)
            if item_type == "法器":
                sql_message.updata_user_faqi_buff(user_id, goods_id)
            if item_type == "防具":
                sql_message.updata_user_armor_buff(user_id, goods_id)
            msg = f"成功装备{arg}！"
            await use.finish(msg, at_sender=True)
    elif goods_type == "技能":
        user_buff_info = UserBuffDate(user_id).BuffInfo
        skill_info = items.get_data_by_item_id(goods_id)
        skill_type = skill_info['item_type']
        if skill_type == "神通":
            if int(user_buff_info.sec_buff) == int(goods_id):
                msg = f"道友已学会该神通：{skill_info['name']}，请勿重复学习！"
            else:#学习sql
                sql_message.update_back_j(user_id, goods_id)
                sql_message.updata_user_sec_buff(user_id, goods_id)
                msg = f"恭喜道友学会神通：{skill_info['name']}！"
        elif skill_type == "功法":
            if int(user_buff_info.main_buff) == int(goods_id):
                msg = f"道友已学会该功法：{skill_info['name']}，请勿重复学习！"
            else:#学习sql
                sql_message.update_back_j(user_id, goods_id)
                sql_message.updata_user_main_buff(user_id, goods_id)
                msg = f"恭喜道友学会功法：{skill_info['name']}！"
        else:
            msg = "发生未知错误！"
        
        await use.finish(msg)
    else:
        await use.finish('该类型物品调试中，未开启！')
        
@creat_auction.handle()
async def _(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    await data_check_conf(bot, event)
    group_id = event.group_id
    
    if group_id not in groups:
        msg = '本群尚未开启拍卖会功能，请联系管理员开启！'
        await creat_auction.finish(msg, at_sender=True)
    
    global auction
    if auction != {}:
        await creat_auction.finish(f'本群已存在一场拍卖会，请等待拍卖会结束！')
    
    try:
        auction_id_list = config['auction_config']['auction_id_list']
        auction_id = random.choice(auction_id_list)
    except IndexError:
        msg = "获取不到拍卖物品的信息，请检查配置文件！"
        await creat_auction.finish(msg, at_sender=True)
    
    auction_info = items.get_data_by_item_id(auction_id)
    msg = '本次拍卖的物品为：\n'   
    msg += get_auction_msg(auction_id)
    msg += f"\n底价为{config['auction_config']['auction_start_prict']}灵石"
    msg += "\n请诸位道友发送 出价+金额 来进行拍卖吧！"
    msg += f"\n本次竞拍时间为：{AUCTIONSLEEPTIME}秒！"
    
    auction['id'] = auction_id
    auction['user_id'] = 0
    auction['now_price'] = config['auction_config']['auction_start_prict']
    auction['name'] = auction_info['name']
    auction['type'] = auction_info['type']
    auction['start_time'] = datetime.now()
    auction['group_id'] = group_id
    
    for group_id in groups:
        await bot.send_group_msg(group_id=int(group_id), message=msg)
    await asyncio.sleep(AUCTIONSLEEPTIME)#先睡60秒
    
    global auction_offer_flag
    while auction_offer_flag:#有人出价
        global auction_offer_all_count
        if auction_offer_all_count == 0:
            auction_offer_flag = False
            break
        first_time = auction_offer_all_count * AUCTIONOFFERSLEEPTIME
        auction_offer_all_count = 0
        await asyncio.sleep(first_time)
    
    if auction['user_id'] == 0:
        msg = "很可惜，本次拍卖会流拍了！"
        auction = {}
        for group_id in groups:
            await bot.send_group_msg(group_id=int(group_id), message=msg)
        await creat_auction.finish()
    
    user_info = sql_message.get_user_message(auction['user_id'])
    msg = "本次拍卖会结束！"
    msg += f"恭喜来自群{auction['group_id']}的{user_info.user_name}道友成功拍卖获得：{auction['type']}-{auction['name']}！"
    for group_id in groups:
        await bot.send_group_msg(group_id=int(group_id), message=msg)
        
    sql_message.send_back(user_info.user_id, auction['id'], auction['name'], auction['type'], 1)
    sql_message.update_ls(user_info.user_id, int(auction['now_price']), 2)
    auction = {}
    global auction_offer_time_count
    auction_offer_time_count = 0
    await creat_auction.finish(msg)


@offer_auction.handle()
async def _(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    await data_check_conf(bot, event)
    group_id = event.group_id
    if group_id not in groups:
        msg = '本群尚未开启拍卖会功能，请联系管理员开启！'
        await offer_auction.finish(msg, at_sender=True)
        
    isUser, user_info, msg = check_user(event)
    if not isUser:
        await offer_auction.finish(msg, at_sender=True)
    
    global auction
    if auction == {}:
        msg = f'本群不存在拍卖会，请等待拍卖会开启！'
        await offer_auction.finish(msg, at_sender=True)
    
    price = args.extract_plain_text().strip()
    try:
        price = int(price)
    except ValueError:
        msg = f"请发送正确的灵石数量"
        await offer_auction.finish(msg, at_sender=True)
    
    if price <= 0 or price <= auction['now_price'] or price > user_info.stone:
        msg = f"走开走开，别捣乱！小心清空你灵石捏！"
        await offer_auction.finish(msg, at_sender=True)
    
    global auction_offer_flag, auction_offer_time_count, auction_offer_all_count
    auction_offer_flag = True#有人出价
    auction_offer_time_count += 1
    auction_offer_all_count += 1
    auction['user_id'] = user_info.user_id
    auction['now_price'] = price
    auction['group_id'] = group_id
    now_time = datetime.now()
    dif_time = OtherSet().date_diff(now_time, auction['start_time'])
    msg = f"来自群{group_id}的{user_info.user_name}道友出价：{price}枚灵石！" \
        f"竞拍时间增加：{AUCTIONOFFERSLEEPTIME}秒，竞拍剩余时间：{int(AUCTIONSLEEPTIME - dif_time + AUCTIONOFFERSLEEPTIME * auction_offer_time_count)}秒"
    for group_id in groups:
        await bot.send_group_msg(group_id=int(group_id), message=msg)
        
    await offer_auction.finish()

@set_auction.handle()
async def _(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    await data_check_conf(bot, event)
    mode = args.extract_plain_text().strip()
    group_id = event.group_id
    is_in_group = is_in_groups(event) #True在，False不在

    if mode == '开启':
        if is_in_group:
            await set_auction.finish(f'本群已开启群拍卖行，请勿重复开启!')
        else:
            config['open'].append(group_id)
            savef(config)
            await set_auction.finish(f'已开启本群拍卖行!')

    elif mode == '关闭':
        if is_in_group:
            config['open'].remove(group_id)
            savef(config)
            await set_auction.finish(f'已关闭本群拍卖行!')
        else:
            await set_auction.finish(f'本群未开启群拍卖行!')
    
    else:
        await set_auction.finish(__back_help__) 


def reset_dict_num(dict):
    i = 1
    temp_dict = {}
    for k, v in dict.items():
        temp_dict[i] = v
        temp_dict[i]['编号'] = i
        i += 1
    return temp_dict

def is_in_groups(event: GroupMessageEvent):
    return event.group_id in groups

def get_auction_msg(auction_id):
    item_info = items.get_data_by_item_id(auction_id)
    _type = item_info['type']
    if _type == "装备":
        if item_info['item_type'] == "防具":
            msg = get_armor_info_msg(auction_id, item_info)
        if item_info['item_type'] == '法器':
            msg = get_weapon_info_msg(auction_id, item_info)
    
    if _type == "技能":
        if item_info['item_type'] == '神通':
            msg = f"{item_info['level']}神通-{item_info['name']}："
            msg += get_sec_msg(item_info)
        if item_info['item_type'] == '功法':
            msg = f"{item_info['level']}功法-"
            msg += get_main_info_msg(auction_id)[1]
    
    if _type == "丹药":
        msg = f"名字：{item_info['name']}"
        msg += f"效果:{item_info['desc']}"
    
    return msg
