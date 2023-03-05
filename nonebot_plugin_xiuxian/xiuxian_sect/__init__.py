from ..xiuxian2_handle import XiuxianDateManage
from nonebot import get_bot, on_command, on_regex, require
from nonebot.log import logger
from nonebot.adapters.onebot.v11 import (
    PRIVATE_FRIEND,
    Bot,
    GROUP,
    Message,
    MessageEvent,
    GroupMessageEvent,
    MessageSegment,
)
from nonebot.params import CommandArg, RegexGroup
from ..data_source import jsondata
from ..xiuxian_config import XiuConfig, USERRANK
from ..utils import Txt2Img
import re
from .sectconfig import get_config
import random
from ..cd_manager import add_cd, check_cd, cd_msg
from ..utils import check_user,send_forward_msg, data_check_conf, get_msg_pic, pic_msg_format
from ..read_buff import BuffJsonDate, get_main_info_msg, UserBuffDate, get_sec_msg
from ..item_json import Items

items = Items()
config = get_config()
LEVLECOST = config["LEVLECOST"]

# 定时任务
materialsupdate = require("nonebot_plugin_apscheduler").scheduler
resetusertask = require("nonebot_plugin_apscheduler").scheduler
upatkpractice = on_command("升级攻击修炼", priority=5)
my_sect = on_command("我的宗门", aliases={"宗门信息"}, priority=5)
create_sect = on_command("创建宗门", priority=5)
join_sect = on_command("加入宗门", priority=5)
sect_position_update = on_command("宗门职位变更", priority=5)
sect_donate = on_command("宗门捐献", priority=5)
sect_out = on_command("退出宗门", priority=5)
sect_kick_out = on_command("踢出宗门", priority=5)
sect_owner_change = on_command("宗主传位", priority=5)
sect_list = on_command("宗门列表", priority=5)
sect_help = on_command("宗门帮助", priority=5)
sect_task = on_command("宗门任务接取", aliases={"我的宗门任务"}, priority=5)
sect_task_complete = on_command("宗门任务完成", priority=5)
sect_task_refresh = on_command("宗门任务刷新", priority=5)
sect_mainbuff_get = on_command("宗门功法搜寻", aliases={"搜寻宗门功法"}, priority=5)
sect_mainbuff_learn = on_command("学习宗门功法", priority=5)
sect_secbuff_get = on_command("宗门神通搜寻", aliases={"搜寻宗门神通"}, priority=5)
sect_secbuff_learn = on_command("学习宗门神通", priority=5)
sect_buff_info = on_command("宗门功法查看", aliases={"查看宗门功法"}, priority=5)
sect_users = on_command("宗门成员查看", aliases={"查看宗门成员"}, priority=5)
sect_elixir_room_make = on_command("宗门丹房建设", aliases={"建设宗门丹房"}, priority=5)
sect_elixir_get = on_command("宗门丹药领取", aliases={"领取宗门丹药领取"}, priority=5)


__sect_help__ = f"""
指令：
1、我的宗门：查看当前所处宗门信息
2、创建宗门：创建宗门，需求：{XiuConfig().sect_create_cost}灵石，需求境界{XiuConfig().sect_min_level}
3、加入宗门：加入一个宗门
4、宗门职位变更：宗主可以改变宗门成员的职位等级
5、宗门捐献：建设宗门，提高宗门建设度，每{config["等级建设度"]}建设度会提高1级攻击修炼等级上限
6、退出宗门：退出当前宗门
7、踢出宗门：踢出对应宗门成员
8、宗主传位：宗主可以传位宗门成员
9、升级攻击修炼：升级道友的攻击修炼等级，每级修炼等级提升4%攻击力
10、宗门列表：查看所有宗门列表
11、宗门任务接取、我的宗门任务：接取宗门任务，可以增加宗门建设度和资材，每日上限：{config["每日宗门任务次上限"]}次
12、宗门任务完成：完成所接取的宗门任务，完成间隔时间：{config["宗门任务完成cd"]}秒
13、宗门任务刷新：刷新当前所接取的宗门任务，刷新间隔时间：{config["宗门任务刷新cd"]}秒
14、宗门功法、神通搜寻：宗主可消耗宗门资材和宗门灵石搜寻功法或者神通
15、学习宗门功法、神通：宗门成员可消耗宗门资材来学习宗门功法或者神通，后接功法名称
16、宗门功法查看：查看当前宗门已有的功法
17、宗门成员查看、查看宗门成员：查看所在宗门的成员信息
18、宗门丹房建设、建设宗门丹房：建设宗门丹房，可以让每个宗门成员每日领取丹药
19、宗门丹药领取、领取宗门丹药领取：领取宗门丹药
非指令：
1、拥有定时任务：每日{config["发放宗门资材"]["时间"]}点发放{config["发放宗门资材"]["倍率"]}倍对应宗门建设度的资材
""".strip()

userstask = {}

@sect_help.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    """修仙帮助"""
    await data_check_conf(bot, event)
    font_size = 26
    title = "宗门帮助信息"
    msg = __sect_help__
    img = Txt2Img(font_size)
    pic = img.save(title, msg)
    await sect_help.finish(MessageSegment.image(pic))
#     msg = __sect_help__
#     await sect_help.finish(msg)

sql_message = XiuxianDateManage()  # sql类

# 定时任务每1小时按照宗门贡献度增加资材
@materialsupdate.scheduled_job("cron",hour=config["发放宗门资材"]["时间"])
async def _():
    all_sects = sql_message.get_all_sects_id_scale()
    for s in all_sects:
        sql_message.update_sect_materials(sect_id=s[0], sect_materials=s[1] * config["发放宗门资材"]["倍率"], key=1)
    
    logger.info('已更新所有宗门的资材')


#每日0点重置用户宗门任务次数、宗门丹药领取次数
@resetusertask.scheduled_job("cron", hour=0, minute=0)
async def _():
    sql_message.sect_task_reset()
    sql_message.sect_elixir_get_num_reset()
    all_sects = sql_message.get_all_sects_id_scale()
    for s in all_sects:
        sect_info = sql_message.get_sect_info(s[0])
        if int(sect_info.elixir_room_level) != 0:
            elixir_room_cost = config['宗门丹房参数']['elixir_room_level'][str(sect_info.elixir_room_level)]['level_up_cost']['建设度']
            if sect_info.sect_materials < elixir_room_cost:
                logger.info("该宗门的资材无法维持丹房")
                continue
            else:
                sql_message.update_sect_materials(sect_id=sect_info.sect_id, sect_materials=elixir_room_cost, key=2)
    logger.info('已重置用户宗门任务次数、宗门丹药领取次数，已扣除丹房维护费')

@sect_elixir_room_make.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    await data_check_conf(bot, event)
    isUser, user_info, msg = check_user(event)
    if not isUser:
        if XiuConfig().img:
            msg = await pic_msg_format(msg, event)
            pic = await get_msg_pic(msg)
            await sect_elixir_room_make.finish(MessageSegment.image(pic))
        else:
            await sect_elixir_room_make.finish(msg, at_sender=True)
    sect_id = user_info.sect_id
    if sect_id:
        sect_position = user_info.sect_position
        owner_idx = [k for k, v in jsondata.sect_config_data().items() if v.get("title", "") == "宗主"]
        owner_position = int(owner_idx[0]) if len(owner_idx) == 1 else 0
        if sect_position == owner_position:
            elixir_room_config = config['宗门丹房参数']
            elixir_room_level_up_config = elixir_room_config['elixir_room_level']
            sect_info = sql_message.get_sect_info(sect_id)
            elixir_room_level = sect_info.elixir_room_level#宗门丹房等级
            if int(elixir_room_level) == len(elixir_room_level_up_config):
                msg = f"宗门丹房等级已经达到最高等级，无法继续建设了！"
                if XiuConfig().img:
                    msg = await pic_msg_format(msg, event)
                    pic = await get_msg_pic(msg)
                    await sect_elixir_room_make.finish(MessageSegment.image(pic))
                else:
                    await sect_elixir_room_make.finish(msg, at_sender=True)
            to_up_level = int(elixir_room_level) + 1
            elixir_room_level_up_sect_scale_cost = elixir_room_level_up_config[str(to_up_level)]['level_up_cost']['建设度']
            elixir_room_level_up_use_stone_cost = elixir_room_level_up_config[str(to_up_level)]['level_up_cost']['stone']
            if elixir_room_level_up_use_stone_cost > int(sect_info.sect_used_stone):
                msg = f"宗门可用灵石不满足升级条件，当前升级需要消耗宗门灵石：{elixir_room_level_up_use_stone_cost}枚！"
                if XiuConfig().img:
                    msg = await pic_msg_format(msg, event)
                    pic = await get_msg_pic(msg)
                    await sect_elixir_room_make.finish(MessageSegment.image(pic))
                else:
                    await sect_elixir_room_make.finish(msg, at_sender=True)
            elif elixir_room_level_up_sect_scale_cost > int(sect_info.sect_scale):
                msg = f"宗门建设度不满足升级条件，当前升级需要达到宗门建设度：{elixir_room_level_up_sect_scale_cost}点！"
                if XiuConfig().img:
                    msg = await pic_msg_format(msg, event)
                    pic = await get_msg_pic(msg)
                    await sect_elixir_room_make.finish(MessageSegment.image(pic))
                else:
                    await sect_elixir_room_make.finish(msg, at_sender=True)
            else:
                msg = f"宗门消耗：{elixir_room_level_up_use_stone_cost}宗门灵石\n"
                msg += f"成功升级宗门丹房，当前丹房为：{elixir_room_level_up_config[str(to_up_level)]['name']}！"
                sql_message.update_sect_scale_and_used_stone(sect_id, sect_info.sect_used_stone - elixir_room_level_up_use_stone_cost, sect_info.sect_scale)
                sql_message.update_sect_elixir_room_level(sect_id, to_up_level)
                if XiuConfig().img:
                    msg = await pic_msg_format(msg, event)
                    pic = await get_msg_pic(msg)
                    await sect_elixir_room_make.finish(MessageSegment.image(pic))
                else:
                    await sect_elixir_room_make.finish(msg, at_sender=True)
        else:
            msg = f"道友不是宗主，无法使用该命令！"
            if XiuConfig().img:
                msg = await pic_msg_format(msg, event)
                pic = await get_msg_pic(msg)
                await sect_elixir_room_make.finish(MessageSegment.image(pic))
            else:
                await sect_elixir_room_make.finish(msg, at_sender=True)
    else:
        msg = f"道友尚未加入宗门！"
        if XiuConfig().img:
            msg = await pic_msg_format(msg, event)
            pic = await get_msg_pic(msg)
            await sect_elixir_room_make.finish(MessageSegment.image(pic))
        else:
            await sect_elixir_room_make.finish(msg, at_sender=True)
        
@sect_elixir_get.handle()
async def _(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    await data_check_conf(bot, event)
    isUser, user_info, msg = check_user(event)
    if not isUser:
        if XiuConfig().img:
            msg = await pic_msg_format(msg, event)
            pic = await get_msg_pic(msg)
            await sect_elixir_get.finish(MessageSegment.image(pic))
        else:
            await sect_elixir_get.finish(msg, at_sender=True)

    sect_id = user_info.sect_id
    if sect_id:
        sect_position = user_info.sect_position
        elixir_room_config = config['宗门丹房参数']
        if sect_position == 4:
            msg = f"道友所在宗门的职位为：{jsondata.sect_config_data()[f'{sect_position}']['title']}，不满足学习!"
            if XiuConfig().img:
                msg = await pic_msg_format(msg, event)
                pic = await get_msg_pic(msg)
                await sect_elixir_get.finish(MessageSegment.image(pic))
            else:
                await sect_elixir_get.finish(msg, at_sender=True)
        else:
            sect_info = sql_message.get_sect_info(sect_id)
            if int(sect_info.elixir_room_level)  == 0:
                msg = f"道友的宗门目前还未建设丹房！"
                if XiuConfig().img:
                    msg = await pic_msg_format(msg, event)
                    pic = await get_msg_pic(msg)
                    await sect_elixir_get.finish(MessageSegment.image(pic))
                else:
                    await sect_elixir_get.finish(msg, at_sender=True)
            if int(user_info.sect_contribution) < elixir_room_config['领取贡献度要求']:
                msg = f"道友的宗门贡献度不满足领取条件，当前宗门贡献度要求：{elixir_room_config['领取贡献度要求']}点！"
                if XiuConfig().img:
                    msg = await pic_msg_format(msg, event)
                    pic = await get_msg_pic(msg)
                    await sect_elixir_get.finish(MessageSegment.image(pic))
                else:
                    await sect_elixir_get.finish(msg, at_sender=True)
            elixir_room_level_up_config = elixir_room_config['elixir_room_level']
            elixir_room_cost = elixir_room_level_up_config[str(sect_info.elixir_room_level)]['level_up_cost']['建设度']
            if sect_info.sect_materials < elixir_room_cost:
                msg = f"当前宗门资材无法维护丹房，请等待{config['发放宗门资材']['时间']}点发放宗门资材后尝试领取！"
                if XiuConfig().img:
                    msg = await pic_msg_format(msg, event)
                    pic = await get_msg_pic(msg)
                    await sect_elixir_get.finish(MessageSegment.image(pic))
                else:
                    await sect_elixir_get.finish(msg, at_sender=True)
            if int(user_info.sect_elixir_get) == 1:
                msg = f"道友已经领取过了，不要贪心哦~"
                if XiuConfig().img:
                    msg = await pic_msg_format(msg, event)
                    pic = await get_msg_pic(msg)
                    await sect_elixir_get.finish(MessageSegment.image(pic))
                else:
                    await sect_elixir_get.finish(msg, at_sender=True)
            if int(sect_info.elixir_room_level)  == 1:
                msg = f"\n道友成功领取到丹药：渡厄丹！"
                sql_message.send_back(user_info.user_id, 1999, "渡厄丹", "丹药", 1, bind_flag=1)#1级丹房送1个渡厄丹
                sql_message.update_user_sect_elixir_get_num(user_info.user_id)
                if XiuConfig().img:
                    msg = await pic_msg_format(msg, event)
                    pic = await get_msg_pic(msg)
                    await sect_elixir_get.finish(MessageSegment.image(pic))
                else:
                    await sect_elixir_get.finish(msg, at_sender=True)
            else:
                sect_now_room_config = elixir_room_level_up_config[str(sect_info.elixir_room_level)]
                give_num = sect_now_room_config['give_level']['give_num'] - 1
                rank_up = sect_now_room_config['give_level']['rank_up']
                give_dict = {}
                give_elixir_id_list = items.get_random_id_list_by_rank_and_item_type(fanil_rank=USERRANK[user_info.level] - rank_up, item_type = ['丹药'])
                if give_elixir_id_list == []:#没有合适的ID，全部给渡厄丹
                    msg = f"道友成功领取到丹药：渡厄丹 2 枚！"
                    sql_message.send_back(user_info.user_id, 1999, "渡厄丹", "丹药", 2, bind_flag=1)#送1个渡厄丹
                    sql_message.update_user_sect_elixir_get_num(user_info.user_id)
                    if XiuConfig().img:
                        msg = await pic_msg_format(msg, event)
                        pic = await get_msg_pic(msg)
                        await sect_elixir_get.finish(MessageSegment.image(pic))
                    else:
                        await sect_elixir_get.finish(msg, at_sender=True)
                i = 1
                while i <= give_num:
                    id = random.choice(give_elixir_id_list)
                    if int(id) == 1999:#不给渡厄丹了
                        continue
                    else:
                        try:
                            give_dict[id] += 1
                            i += 1
                        except:
                            give_dict[id] = 1
                            i += 1
                msg = f"\n道友成功领取到丹药：渡厄丹 1 枚！\n"
                sql_message.send_back(user_info.user_id, 1999, "渡厄丹", "丹药", 1, bind_flag=1)#送1个渡厄丹
                for k, v in give_dict.items():
                    goods_info = items.get_data_by_item_id(k)
                    msg += f"道友成功领取到丹药：{goods_info['name']} {v} 枚！\n"
                    sql_message.send_back(user_info.user_id, k, goods_info['name'], '丹药', v, bind_flag=1)
                sql_message.update_user_sect_elixir_get_num(user_info.user_id)
                if XiuConfig().img:
                    msg = await pic_msg_format(msg, event)
                    pic = await get_msg_pic(msg)
                    await sect_elixir_get.finish(MessageSegment.image(pic))
                else:
                    await sect_elixir_get.finish(msg, at_sender=True)
    else:
        msg = f"道友尚未加入宗门！"
        if XiuConfig().img:
            msg = await pic_msg_format(msg, event)
            pic = await get_msg_pic(msg)
            await sect_elixir_get.finish(MessageSegment.image(pic))
        else:
            await sect_elixir_get.finish(msg, at_sender=True)

@sect_buff_info.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    await data_check_conf(bot, event)
    isUser, user_info, msg = check_user(event)
    if not isUser:
        if XiuConfig().img:
            msg = await pic_msg_format(msg, event)
            pic = await get_msg_pic(msg)
            await sect_buff_info.finish(MessageSegment.image(pic))
        else:
            await sect_buff_info.finish(msg, at_sender=True)
    sect_id = user_info.sect_id
    if sect_id:
        sect_info = sql_message.get_sect_info(sect_id)
        if sect_info.mainbuff == 0 and sect_info.secbuff == 0:
            msg = f"本宗尚未获得任何功法、神通，请宗主发送宗门功法、神通搜寻来获得！"
            if XiuConfig().img:
                msg = await pic_msg_format(msg, event)
                pic = await get_msg_pic(msg)
                await sect_buff_info.finish(MessageSegment.image(pic))
            else:
                await sect_buff_info.finish(msg, at_sender=True)
        msg = ''
        
        if sect_info.mainbuff != 0:
            mainbufflist = get_sect_mainbuff_id_list(sect_id)
            mainmsg = '\n☆------宗门功法------☆\n'
            for main in mainbufflist:
                mainbuff, mainbuffmsg = get_main_info_msg(str(main))
                mainmsg += f"{mainbuff['level']}：{mainbuffmsg}\n"
            msg += mainmsg
            
        if sect_info.secbuff != 0:
            secbufflist = get_sect_secbuff_id_list(sect_id)
            secmsg = '☆------宗门神通------☆\n'
            for sec in secbufflist:
                secbuff = items.get_data_by_item_id(sec)
                secbuffmsg = get_sec_msg(secbuff)
                secmsg += f"{secbuff['level']}：{secbuff['name']} {secbuffmsg}\n"
            msg += secmsg
        if XiuConfig().img:
            msg = await pic_msg_format(msg, event)
            pic = await get_msg_pic(msg)
            await sect_buff_info.finish(MessageSegment.image(pic))
        else:
            await sect_buff_info.finish(msg, at_sender=True)
    else:
        msg = f"道友尚未加入宗门！"
        if XiuConfig().img:
            msg = await pic_msg_format(msg, event)
            pic = await get_msg_pic(msg)
            await sect_buff_info.finish(MessageSegment.image(pic))
        else:
            await sect_buff_info.finish(msg, at_sender=True)

buffrankkey = {
    "人阶下品":1,
    "人阶上品":2,
    "黄阶下品":3,
    "黄阶上品":4,
    "玄阶下品":5,
    "玄阶上品":6,
    "地阶下品":7,
    "地阶上品":8,
    "天阶下品":9,
    "天阶上品":10,
}

@sect_mainbuff_learn.handle()
async def _(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    await data_check_conf(bot, event)
    isUser, user_info, msg = check_user(event)
    if not isUser:
        if XiuConfig().img:
            msg = await pic_msg_format(msg, event)
            pic = await get_msg_pic(msg)
            await sect_mainbuff_learn.finish(MessageSegment.image(pic))
        else:
            await sect_mainbuff_learn.finish(msg, at_sender=True)
    msg = args.extract_plain_text().strip()
    sect_id = user_info.sect_id
    if sect_id:
        sect_position = user_info.sect_position
        if sect_position == 4:
            msg = f"道友所在宗门的职位为：{jsondata.sect_config_data()[f'{sect_position}']['title']}，不满足学习!"
            if XiuConfig().img:
                msg = await pic_msg_format(msg, event)
                pic = await get_msg_pic(msg)
                await sect_mainbuff_learn.finish(MessageSegment.image(pic))
            else:
                await sect_mainbuff_learn.finish(msg, at_sender=True)
        else:
            sect_info = sql_message.get_sect_info(sect_id)
            if sect_info.mainbuff == 0:
                msg = f"本宗尚未获得宗门功法，请宗主发送宗门功法搜寻来获得宗门功法！"
                if XiuConfig().img:
                    msg = await pic_msg_format(msg, event)
                    pic = await get_msg_pic(msg)
                    await sect_mainbuff_learn.finish(MessageSegment.image(pic))
                else:
                    await sect_mainbuff_learn.finish(msg, at_sender=True)
            
            sectmainbuffidlist = get_sect_mainbuff_id_list(sect_id)
            
            if msg not in get_mainname_list(sectmainbuffidlist):
                msg = f"本宗还没有该功法，请发送本宗有的功法进行学习！"
                if XiuConfig().img:
                    msg = await pic_msg_format(msg, event)
                    pic = await get_msg_pic(msg)
                    await sect_mainbuff_learn.finish(MessageSegment.image(pic))
                else:
                    await sect_mainbuff_learn.finish(msg, at_sender=True)
                
            userbuffinfo = UserBuffDate(user_info.user_id).BuffInfo
            mainbuffid = get_mainnameid(msg, sectmainbuffidlist)
            if str(userbuffinfo.main_buff) == str(mainbuffid):
                msg = f"道友请勿重复学习！"
                if XiuConfig().img:
                    msg = await pic_msg_format(msg, event)
                    pic = await get_msg_pic(msg)
                    await sect_mainbuff_learn.finish(MessageSegment.image(pic))
                else:
                    await sect_mainbuff_learn.finish(msg, at_sender=True)
        
            mainbuffconfig = config['宗门主功法参数']
            mainbuff = items.get_data_by_item_id(mainbuffid)
            mainbufftype = mainbuff['level']
            mainbuffgear = buffrankkey[mainbufftype]
            #获取逻辑
            materialscost = mainbuffgear * mainbuffconfig['学习资材消耗']
            if sect_info.sect_materials >= materialscost:
                sql_message.update_sect_materials(sect_id, materialscost, 2)
                sql_message.updata_user_main_buff(user_info.user_id, mainbuffid)
                mainbuff, mainbuffmsg = get_main_info_msg(str(mainbuffid))
                msg = f"本次学习消耗{materialscost}宗门资材，成功学习到本宗{mainbufftype}功法：{mainbuff['name']}\n{mainbuffmsg}"
                if XiuConfig().img:
                    msg = await pic_msg_format(msg, event)
                    pic = await get_msg_pic(msg)
                    await sect_mainbuff_learn.finish(MessageSegment.image(pic))
                else:
                    await sect_mainbuff_learn.finish(msg, at_sender=True)
            else:
                msg = f"本次学习需要消耗{materialscost}宗门资材，不满足条件！"
                if XiuConfig().img:
                    msg = await pic_msg_format(msg, event)
                    pic = await get_msg_pic(msg)
                    await sect_mainbuff_learn.finish(MessageSegment.image(pic))
                else:
                    await sect_mainbuff_learn.finish(msg, at_sender=True)
    else:
        msg = f"道友尚未加入宗门！"
        if XiuConfig().img:
            msg = await pic_msg_format(msg, event)
            pic = await get_msg_pic(msg)
            await sect_mainbuff_learn.finish(MessageSegment.image(pic))
        else:
            await sect_mainbuff_learn.finish(msg, at_sender=True)

@sect_mainbuff_get.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    await data_check_conf(bot, event)

    isUser, user_info, msg = check_user(event)
    if not isUser:
        if XiuConfig().img:
            msg = await pic_msg_format(msg, event)
            pic = await get_msg_pic(msg)
            await sect_mainbuff_get.finish(MessageSegment.image(pic))
        else:
            await sect_mainbuff_get.finish(msg, at_sender=True)
    sect_id = user_info.sect_id
    if sect_id:
        sect_position = user_info.sect_position
        owner_idx = [k for k, v in jsondata.sect_config_data().items() if v.get("title", "") == "宗主"]
        owner_position = int(owner_idx[0]) if len(owner_idx) == 1 else 0
        if sect_position == owner_position:
            mainbuffconfig = config['宗门主功法参数']
            sect_info = sql_message.get_sect_info(sect_id)
            mainbuffgear, mainbufftype = get_sectbufftxt(sect_info.sect_scale, mainbuffconfig)
            #获取逻辑
            stonecost = mainbuffgear * mainbuffconfig['获取消耗的灵石']
            materialscost = mainbuffgear * mainbuffconfig['获取消耗的资材']
            if sect_info.sect_used_stone >= stonecost and sect_info.sect_materials >= materialscost:
                if random.randint(0, 100) <= mainbuffconfig['获取到功法的概率']:
                    mainbuffid = random.choice(BuffJsonDate().get_gfpeizhi()[mainbufftype]['gf_list'])
                    mainbuffidlist = get_sect_mainbuff_id_list(sect_id)
                    if mainbuffid in mainbuffidlist:
                        msg = f"本次搜寻到了重复的功法！不消耗资源！"
                        if XiuConfig().img:
                            msg = await pic_msg_format(msg, event)
                            pic = await get_msg_pic(msg)
                            await sect_mainbuff_get.finish(MessageSegment.image(pic))
                        else:
                            await sect_mainbuff_get.finish(msg, at_sender=True)
                    sql_message.update_sect_materials(sect_id, materialscost, 2)
                    sql_message.update_sect_scale_and_used_stone(sect_id, sect_info.sect_used_stone - stonecost, sect_info.sect_scale)
                    mainbuffidlist.append(mainbuffid)
                    sql = set_sect_list(mainbuffidlist)
                    
                    sql_message.update_sect_mainbuff(sect_id, sql)
                    mainbuff, mainbuffmsg = get_main_info_msg(mainbuffid)
                    msg = f"本次搜寻消耗{stonecost}宗门灵石，{materialscost}宗门资材，成功获取到{mainbufftype}功法：{mainbuff['name']}\n{mainbuffmsg}"
                    if XiuConfig().img:
                        msg = await pic_msg_format(msg, event)
                        pic = await get_msg_pic(msg)
                        await sect_mainbuff_get.finish(MessageSegment.image(pic))
                    else:
                        await sect_mainbuff_get.finish(msg, at_sender=True)
                else:
                    msg = f"本次搜寻消耗{stonecost}宗门灵石，{materialscost}宗门资材，可惜失败了！"
                    if XiuConfig().img:
                        msg = await pic_msg_format(msg, event)
                        pic = await get_msg_pic(msg)
                        await sect_mainbuff_get.finish(MessageSegment.image(pic))
                    else:
                        await sect_mainbuff_get.finish(msg, at_sender=True)

            else:
                msg = f"本次搜寻需要消耗{stonecost}宗门灵石，{materialscost}宗门资材，不满足条件！"
                if XiuConfig().img:
                    msg = await pic_msg_format(msg, event)
                    pic = await get_msg_pic(msg)
                    await sect_mainbuff_get.finish(MessageSegment.image(pic))
                else:
                    await sect_mainbuff_get.finish(msg, at_sender=True)
        else:
            msg = f"道友不是宗主，无法使用该命令！"
            if XiuConfig().img:
                msg = await pic_msg_format(msg, event)
                pic = await get_msg_pic(msg)
                await sect_mainbuff_get.finish(MessageSegment.image(pic))
            else:
                await sect_mainbuff_get.finish(msg, at_sender=True)
    else:
        msg = f"道友尚未加入宗门！"
        if XiuConfig().img:
            msg = await pic_msg_format(msg, event)
            pic = await get_msg_pic(msg)
            await sect_mainbuff_get.finish(MessageSegment.image(pic))
        else:
            await sect_mainbuff_get.finish(msg, at_sender=True)

@sect_secbuff_get.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    await data_check_conf(bot, event)

    isUser, user_info, msg = check_user(event)
    if not isUser:
        if XiuConfig().img:
            msg = await pic_msg_format(msg, event)
            pic = await get_msg_pic(msg)
            await sect_secbuff_get.finish(MessageSegment.image(pic))
        else:
            await sect_secbuff_get.finish(msg, at_sender=True)
    sect_id = user_info.sect_id
    if sect_id:
        sect_position = user_info.sect_position
        owner_idx = [k for k, v in jsondata.sect_config_data().items() if v.get("title", "") == "宗主"]
        owner_position = int(owner_idx[0]) if len(owner_idx) == 1 else 0
        if sect_position == owner_position:
            secbuffconfig = config['宗门神通参数']
            sect_info = sql_message.get_sect_info(sect_id)
            secbuffgear, secbufftype = get_sectbufftxt(sect_info.sect_scale, secbuffconfig)
            #获取逻辑
            stonecost = secbuffgear * secbuffconfig['获取消耗的灵石']
            materialscost = secbuffgear * secbuffconfig['获取消耗的资材']
            if sect_info.sect_used_stone >= stonecost and sect_info.sect_materials >= materialscost:
                if random.randint(0, 100) <= secbuffconfig['获取到神通的概率']:
                    secbuffid = random.choice(BuffJsonDate().get_gfpeizhi()[secbufftype]['st_list'])
                    secbuffidlist = get_sect_secbuff_id_list(sect_id)
                    if secbuffid in secbuffidlist:
                        msg = f"本次搜寻到了重复的神通！不消耗资源！"
                        if XiuConfig().img:
                            msg = await pic_msg_format(msg, event)
                            pic = await get_msg_pic(msg)
                            await sect_secbuff_get.finish(MessageSegment.image(pic))
                        else:
                            await sect_secbuff_get.finish(msg, at_sender=True)

                    sql_message.update_sect_materials(sect_id, materialscost, 2)
                    sql_message.update_sect_scale_and_used_stone(sect_id, sect_info.sect_used_stone - stonecost, sect_info.sect_scale)     
                    secbuffidlist.append(secbuffid)         
                    sql = set_sect_list(secbuffidlist)
                    sql_message.update_sect_secbuff(sect_id, sql)
                    secbuff = items.get_data_by_item_id(secbuffid)
                    secmsg = get_sec_msg(secbuff)
                    msg = f"本次搜寻消耗{stonecost}宗门灵石，{materialscost}宗门资材，成功获取到{secbufftype}神通：{secbuff['name']}\n{secmsg}"
                    if XiuConfig().img:
                        msg = await pic_msg_format(msg, event)
                        pic = await get_msg_pic(msg)
                        await sect_secbuff_get.finish(MessageSegment.image(pic))
                    else:
                        await sect_secbuff_get.finish(msg, at_sender=True)
                else:
                    msg = f"本次搜寻消耗{stonecost}宗门灵石，{materialscost}宗门资材，可惜失败了！"
                    if XiuConfig().img:
                        msg = await pic_msg_format(msg, event)
                        pic = await get_msg_pic(msg)
                        await sect_secbuff_get.finish(MessageSegment.image(pic))
                    else:
                        await sect_secbuff_get.finish(msg, at_sender=True)

            else:
                msg = f"本次搜寻需要消耗{stonecost}宗门灵石，{materialscost}宗门资材，不满足条件！"
                if XiuConfig().img:
                    msg = await pic_msg_format(msg, event)
                    pic = await get_msg_pic(msg)
                    await sect_secbuff_get.finish(MessageSegment.image(pic))
                else:
                    await sect_secbuff_get.finish(msg, at_sender=True)
        else:
            msg = f"道友不是宗主，无法使用该命令！"
            if XiuConfig().img:
                msg = await pic_msg_format(msg, event)
                pic = await get_msg_pic(msg)
                await sect_secbuff_get.finish(MessageSegment.image(pic))
            else:
                await sect_secbuff_get.finish(msg, at_sender=True)
    else:
        msg = f"道友尚未加入宗门！"
        if XiuConfig().img:
            msg = await pic_msg_format(msg, event)
            pic = await get_msg_pic(msg)
            await sect_secbuff_get.finish(MessageSegment.image(pic))
        else:
            await sect_secbuff_get.finish(msg, at_sender=True)
        
@sect_secbuff_learn.handle()
async def _(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    await data_check_conf(bot, event)

    isUser, user_info, msg = check_user(event)
    if not isUser:
        if XiuConfig().img:
            msg = await pic_msg_format(msg, event)
            pic = await get_msg_pic(msg)
            await sect_secbuff_learn.finish(MessageSegment.image(pic))
        else:
            await sect_secbuff_learn.finish(msg, at_sender=True)
    msg = args.extract_plain_text().strip()
    sect_id = user_info.sect_id
    if sect_id:
        sect_position = user_info.sect_position
        if sect_position == 4:
            msg = f"道友所在宗门的职位为：{jsondata.sect_config_data()[f'{sect_position}']['title']}，不满足学习!"
            if XiuConfig().img:
                msg = await pic_msg_format(msg, event)
                pic = await get_msg_pic(msg)
                await sect_secbuff_learn.finish(MessageSegment.image(pic))
            else:
                await sect_secbuff_learn.finish(msg, at_sender=True)
        else:
            sect_info = sql_message.get_sect_info(sect_id)
            if sect_info.secbuff == 0:
                msg = f"本宗尚未获得宗门神通，请宗主发送宗门神通搜寻来获得宗门神通！"
                if XiuConfig().img:
                    msg = await pic_msg_format(msg, event)
                    pic = await get_msg_pic(msg)
                    await sect_secbuff_learn.finish(MessageSegment.image(pic))
                else:
                    await sect_secbuff_learn.finish(msg, at_sender=True)
                
            sectsecbuffidlist = get_sect_secbuff_id_list(sect_id)
            
            if msg not in get_secname_list(sectsecbuffidlist):
                msg = f"本宗还没有该神通，请发送本宗有的神通进行学习！"
                if XiuConfig().img:
                    msg = await pic_msg_format(msg, event)
                    pic = await get_msg_pic(msg)
                    await sect_secbuff_learn.finish(MessageSegment.image(pic))
                else:
                    await sect_secbuff_learn.finish(msg, at_sender=True)
            
            userbuffinfo = UserBuffDate(user_info.user_id).BuffInfo
            secbuffid = get_secnameid(msg, sectsecbuffidlist)
            if str(userbuffinfo.sec_buff) == str(secbuffid):
                msg = f"道友请勿重复学习！"
                if XiuConfig().img:
                    msg = await pic_msg_format(msg, event)
                    pic = await get_msg_pic(msg)
                    await sect_secbuff_learn.finish(MessageSegment.image(pic))
                else:
                    await sect_secbuff_learn.finish(msg, at_sender=True)

            secbuffconfig = config['宗门神通参数']
            
            secbuff = items.get_data_by_item_id(secbuffid)
            secbufftype = secbuff['level']
            secbuffgear = buffrankkey[secbufftype]
            #获取逻辑
            materialscost = secbuffgear * secbuffconfig['学习资材消耗']
            if sect_info.sect_materials >= materialscost:
                sql_message.update_sect_materials(sect_id, materialscost, 2)
                sql_message.updata_user_sec_buff(user_info.user_id, secbuffid)
                secmsg = get_sec_msg(secbuff)
                msg = f"本次学习消耗{materialscost}宗门资材，成功学习到本宗{secbufftype}神通：{secbuff['name']}\n{secbuff['name']}：{secmsg}"
                if XiuConfig().img:
                    msg = await pic_msg_format(msg, event)
                    pic = await get_msg_pic(msg)
                    await sect_secbuff_learn.finish(MessageSegment.image(pic))
                else:
                    await sect_secbuff_learn.finish(msg, at_sender=True)
            else:
                msg = f"本次学习需要消耗{materialscost}宗门资材，不满足条件！"
                if XiuConfig().img:
                    msg = await pic_msg_format(msg, event)
                    pic = await get_msg_pic(msg)
                    await sect_secbuff_learn.finish(MessageSegment.image(pic))
                else:
                    await sect_secbuff_learn.finish(msg, at_sender=True)
    else:
        msg = f"道友尚未加入宗门！"
        if XiuConfig().img:
            msg = await pic_msg_format(msg, event)
            pic = await get_msg_pic(msg)
            await sect_secbuff_learn.finish(MessageSegment.image(pic))
        else:
            await sect_secbuff_learn.finish(msg, at_sender=True)


@upatkpractice.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    await data_check_conf(bot, event)

    try:
        user_id, group_id, userinfo = await data_check(bot, event)
    except MsgError:
        return

    
    sect_id = userinfo.sect_id
    if sect_id:
        sect_materials = int(sql_message.get_sect_info(sect_id).sect_materials)#当前资材
        useratkpractice = int(userinfo.atkpractice) #当前等级
        if useratkpractice == 25:
            msg = f"道友的攻击修炼等级已达到最高等级!"
            if XiuConfig().img:
                msg = await pic_msg_format(msg, event)
                pic = await get_msg_pic(msg)
                await upatkpractice.finish(MessageSegment.image(pic))
            else:
                await upatkpractice.finish(msg, at_sender=True)
        
        sect_level = get_sect_level(sect_id)[0] if get_sect_level(sect_id)[0] <= 25 else 25#获取当前宗门修炼等级上限，500w建设度1级,上限25级

        sect_position = userinfo.sect_position
        if sect_position == 4:
            msg = f"道友所在宗门的职位为：{jsondata.sect_config_data()[f'{sect_position}']['title']}，不满足使用资材的条件!"
            if XiuConfig().img:
                msg = await pic_msg_format(msg, event)
                pic = await get_msg_pic(msg)
                await upatkpractice.finish(MessageSegment.image(pic))
            else:
                await upatkpractice.finish(msg, at_sender=True)

        if useratkpractice >= sect_level:
            msg = f"道友的攻击修炼等级已达到当前宗门修炼等级的最高等级：{sect_level}，请捐献灵石提升贡献度吧！"
            if XiuConfig().img:
                msg = await pic_msg_format(msg, event)
                pic = await get_msg_pic(msg)
                await upatkpractice.finish(MessageSegment.image(pic))
            else:
                await upatkpractice.finish(msg, at_sender=True)

        cost = LEVLECOST[f'{useratkpractice}']
        if int(userinfo.stone) < cost:
            msg = f"道友的灵石不够，还需{cost - int(userinfo.stone)}灵石!"
            if XiuConfig().img:
                msg = await pic_msg_format(msg, event)
                pic = await get_msg_pic(msg)
                await upatkpractice.finish(MessageSegment.image(pic))
            else:
                await upatkpractice.finish(msg, at_sender=True)
        
        if sect_materials < cost * 10:
            msg = f"道友的所处的宗门资材不足，还需{cost * 10 - sect_materials}资材!"
            if XiuConfig().img:
                msg = await pic_msg_format(msg, event)
                pic = await get_msg_pic(msg)
                await upatkpractice.finish(MessageSegment.image(pic))
            else:
                await upatkpractice.finish(msg, at_sender=True)
        
        sql_message.update_ls(user_id, cost, 2)
        sql_message.update_sect_materials(sect_id, cost * 10, 2)
        sql_message.update_user_atkpractice(user_id, useratkpractice + 1)
        msg = f"升级成功，道友当前攻击修炼等级：{useratkpractice + 1}，消耗灵石：{cost}枚，消耗宗门资材{cost * 10}！"
        if XiuConfig().img:
            msg = await pic_msg_format(msg, event)
            pic = await get_msg_pic(msg)
            await upatkpractice.finish(MessageSegment.image(pic))
        else:
            await upatkpractice.finish(msg, at_sender=True)
    else:
        msg = f"修炼逆天而行消耗巨大，请加入宗门再进行修炼！"
        if XiuConfig().img:
            msg = await pic_msg_format(msg, event)
            pic = await get_msg_pic(msg)
            await upatkpractice.finish(MessageSegment.image(pic))
        else:
            await upatkpractice.finish(msg, at_sender=True)

@sect_task_refresh.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    await data_check_conf(bot, event)

    isUser, user_info, msg = check_user(event)
    if not isUser:
        if XiuConfig().img:
            msg = await pic_msg_format(msg, event)
            pic = await get_msg_pic(msg)
            await sect_task_refresh.finish(MessageSegment.image(pic))
        else:
            await sect_task_refresh.finish(msg, at_sender=True)
    user_id = str(user_info.user_id)
    sect_id = user_info.sect_id
    if sect_id:
        if isUserTask(user_id):
            if cd := check_cd(event, '宗门任务刷新'):
            # 如果 CD 还没到 则直接结束
                msg = cd_msg(cd)
                if XiuConfig().img:
                    msg = await pic_msg_format(msg, event)
                    pic = await get_msg_pic(msg)
                    await sect_task_refresh.finish(MessageSegment.image(pic))
                else:
                    await sect_task_refresh.finish(msg, at_sender=True)
            create_user_sect_task(user_id)
            add_cd(event, config['宗门任务刷新cd'], '宗门任务刷新')
            msg = f"已刷新，道友当前接取的任务：{userstask[user_id]['任务名称']}\n{userstask[user_id]['任务内容']['desc']}"
            if XiuConfig().img:
                msg = await pic_msg_format(msg, event)
                pic = await get_msg_pic(msg)
                await sect_task_refresh.finish(MessageSegment.image(pic))
            else:
                await sect_task_refresh.finish(msg, at_sender=True)
        else:
            msg = f"道友目前还没有宗门任务，请发送指令宗门任务接取来获取吧"
            if XiuConfig().img:
                msg = await pic_msg_format(msg, event)
                pic = await get_msg_pic(msg)
                await sect_task_refresh.finish(MessageSegment.image(pic))
            else:
                await sect_task_refresh.finish(msg, at_sender=True)

    else:
        msg = f"道友尚未加入宗门，请加入宗门后再发送该指令！"
        if XiuConfig().img:
            msg = await pic_msg_format(msg, event)
            pic = await get_msg_pic(msg)
            await sect_task_refresh.finish(MessageSegment.image(pic))
        else:
            await sect_task_refresh.finish(msg, at_sender=True)

@sect_list.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    """宗门列表：当前为返回转发内容"""
    await data_check_conf(bot, event)

    sectlists = sql_message.get_all_scale()
    msg = ''
    msg_list = []
    for sect in sectlists:
        # print(sect)
        user_name = sql_message.get_user_message(sect.sect_owner).user_name
        msg += f'编号{sect.sect_id}：{sect.sect_name}，宗主：{user_name}，宗门建设度：{sect.sect_scale}\n'
        msg_list.append(f'编号{sect.sect_id}：{sect.sect_name}，宗主：{user_name}，宗门建设度：{sect.sect_scale}')

    await send_forward_msg(bot, event, '宗门列表', bot.self_id, msg_list)
    await sect_list.finish()
    # await sect_list.finish(msg)

@sect_users.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    """查看所在宗门成员信息"""
    await data_check_conf(bot, event)
    
    msg = ''
    msg_list = []
    isUser, user_info, msg = check_user(event)
    if not isUser:
        if XiuConfig().img:
            msg = await pic_msg_format(msg, event)
            pic = await get_msg_pic(msg)
            await sect_users.finish(MessageSegment.image(pic))
        else:
            await sect_users.finish(msg, at_sender=True)

    if user_info:
        sect_id = user_info.sect_id
        if sect_id:
            sect_info = sql_message.get_sect_info(sect_id)
            userlist = sql_message.get_all_users_by_sect_id(sect_id)
            msg = f'☆【{sect_info.sect_name}】的成员信息☆\n'
            i = 1
            for user in userlist:
                msg += f"编号{i}：{user.user_name}，{user.level}，宗门职位：{jsondata.sect_config_data()[f'{user.sect_position}']['title']}，宗门贡献度：{user.sect_contribution}\n"
                msg_list.append(
                    f"编号{i}：{user.user_name}，{user.level}，宗门职位：{jsondata.sect_config_data()[f'{user.sect_position}']['title']}，宗门贡献度：{user.sect_contribution}")
                i += 1
        else:
            msg_list.append("一介散修，莫要再问。")
    else:
        msg_list.append("未曾踏入修仙世界，输入 我要修仙 加入我们，看破这世间虚妄!")
    await send_forward_msg(bot, event, '宗门成员', bot.self_id, msg_list)
    await sect_users.finish()


@sect_task.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    await data_check_conf(bot, event)

    try:
        user_id, group_id, userinfo = await data_check(bot, event)
    except MsgError:
        return
    
    sect_id = userinfo.sect_id
    if sect_id:
        user_now_num = int(userinfo.sect_task)
        if user_now_num >= config["每日宗门任务次上限"]:
            msg = f"道友已完成{user_now_num}次，今日无法再获取宗门任务了！"
            if XiuConfig().img:
                msg = await pic_msg_format(msg, event)
                pic = await get_msg_pic(msg)
                await sect_task.finish(MessageSegment.image(pic))
            else:
                await sect_task.finish(msg, at_sender=True)
        
        if isUserTask(user_id): #已有任务
            msg = f"道友当前已接取了任务：{userstask[user_id]['任务名称']}\n{userstask[user_id]['任务内容']['desc']}"
            if XiuConfig().img:
                msg = await pic_msg_format(msg, event)
                pic = await get_msg_pic(msg)
                await sect_task.finish(MessageSegment.image(pic))
            else:
                await sect_task.finish(msg, at_sender=True)

        create_user_sect_task(user_id)
        msg = f"{userstask[user_id]['任务内容']['desc']}"
        if XiuConfig().img:
            msg = await pic_msg_format(msg, event)
            pic = await get_msg_pic(msg)
            await sect_task.finish(MessageSegment.image(pic))
        else:
            await sect_task.finish(msg, at_sender=True)
    else:
        msg = f"道友尚未加入宗门，请加入宗门后再获取任务！"
        if XiuConfig().img:
            msg = await pic_msg_format(msg, event)
            pic = await get_msg_pic(msg)
            await sect_task.finish(MessageSegment.image(pic))
        else:
            await sect_task.finish(msg, at_sender=True)


@sect_task_complete.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    await data_check_conf(bot, event)

    try:
        user_id, group_id, userinfo = await data_check(bot, event)
    except MsgError:
        return

    
    sect_id = userinfo.sect_id
    if sect_id:
        if not isUserTask(user_id):
            msg = f"道友当前没有接取宗门任务"
            if XiuConfig().img:
                msg = await pic_msg_format(msg, event)
                pic = await get_msg_pic(msg)
                await sect_task_complete.finish(MessageSegment.image(pic))
            else:
                await sect_task_complete.finish(msg, at_sender=True)
        
        if cd := check_cd(event, '宗门任务'):
            # 如果 CD 还没到 则直接结束
            msg = cd_msg(cd)
            if XiuConfig().img:
                msg = await pic_msg_format(msg, event)
                pic = await get_msg_pic(msg)
                await sect_task_complete.finish(MessageSegment.image(pic))
            else:
                await sect_task_complete.finish(msg, at_sender=True)
        
        if userstask[user_id]['任务内容']['type'] == 1:#type=1：需要扣气血，type=2：需要扣灵石
            costhp = int((userinfo.exp / 2) * userstask[user_id]['任务内容']['cost'])
            if userinfo.hp < userinfo.exp / 10 or costhp >= userinfo.hp:
                msg = "重伤未愈，动弹不得！"
                if XiuConfig().img:
                    msg = await pic_msg_format(msg, event)
                    pic = await get_msg_pic(msg)
                    await sect_task_complete.finish(MessageSegment.image(pic))
                else:
                    await sect_task_complete.finish(msg, at_sender=True)
            
            get_exp = int(userinfo.exp * userstask[user_id]['任务内容']['give'])
            sect_stone = int(userstask[user_id]['任务内容']['sect'])
            sql_message.update_user_hp_mp(user_id, userinfo.hp - costhp, userinfo.mp)
            sql_message.update_exp(user_id, get_exp)
            sql_message.donate_update(userinfo.sect_id, sect_stone)
            sql_message.update_sect_materials(sect_id, sect_stone * 10, 1)
            sql_message.update_user_sect_task(user_id, 1)
            sql_message.update_user_sect_contribution(user_id, userinfo.sect_contribution + int(sect_stone))
            msg = f"道友大战一番，气血减少：{costhp}，获得修为：{get_exp}，所在宗门建设度增加：{sect_stone}，资材增加：{sect_stone * 10}, 宗门贡献度增加：{int(sect_stone)}"
            userstask[user_id] = {}
            add_cd(event, config['宗门任务完成cd'], '宗门任务')
            if XiuConfig().img:
                msg = await pic_msg_format(msg, event)
                pic = await get_msg_pic(msg)
                await sect_task_complete.finish(MessageSegment.image(pic))
            else:
                await sect_task_complete.finish(msg, at_sender=True)

        elif userstask[user_id]['任务内容']['type'] == 2:#type=1：需要扣气血，type=2：需要扣灵石
            costls = userstask[user_id]['任务内容']['cost']

            if costls > int(userinfo.stone):
                msg = f"道友的灵石不足以完成宗门任务，当前任务所需灵石：{costls}"
                if XiuConfig().img:
                    msg = await pic_msg_format(msg, event)
                    pic = await get_msg_pic(msg)
                    await sect_task_complete.finish(MessageSegment.image(pic))
                else:
                    await sect_task_complete.finish(msg, at_sender=True)

            get_exp = int(userinfo.exp * userstask[user_id]['任务内容']['give'])
            sect_stone = int(userstask[user_id]['任务内容']['sect'])
            sql_message.update_ls(user_id, costls, 2)
            sql_message.update_exp(user_id, get_exp)
            sql_message.donate_update(userinfo.sect_id, sect_stone)
            sql_message.update_sect_materials(sect_id, sect_stone * 10, 1)
            sql_message.update_user_sect_task(user_id, 1)
            sql_message.update_user_sect_contribution(user_id, userinfo.sect_contribution + int(sect_stone))
            msg = f"道友为了完成任务购买宝物消耗灵石：{costls}枚，获得修为：{get_exp}，所在宗门建设度增加：{sect_stone}，资材增加：{sect_stone * 10}, 宗门贡献度增加：{int(sect_stone)}"
            userstask[user_id] = {}
            add_cd(event, config['宗门任务完成cd'], '宗门任务')
            if XiuConfig().img:
                msg = await pic_msg_format(msg, event)
                pic = await get_msg_pic(msg)
                await sect_task_complete.finish(MessageSegment.image(pic))
            else:
                await sect_task_complete.finish(msg, at_sender=True)
    else:
        msg = f"道友尚未加入宗门，请加入宗门后再完成任务！"
        if XiuConfig().img:
            msg = await pic_msg_format(msg, event)
            pic = await get_msg_pic(msg)
            await sect_task_complete.finish(MessageSegment.image(pic))
        else:
            await sect_task_complete.finish(msg, at_sender=True)

@sect_owner_change.handle()
async def _(bot: Bot,event: GroupMessageEvent, args: Message = CommandArg()):
    """宗主传位"""
    await data_check_conf(bot, event)

    user_id = event.get_user_id()
    user_message = sql_message.get_user_message(user_id)
    if not user_message:
        msg = "修仙界没有你的信息！请输入'我要修仙'，踏入修行"
        if XiuConfig().img:
            msg = await pic_msg_format(msg, event)
            pic = await get_msg_pic(msg)
            await sect_owner_change.finish(MessageSegment.image(pic))
        else:
            await sect_owner_change.finish(msg, at_sender=True)
    if not user_message.sect_id:
        msg = "道友还未加入一方宗门。"
        if XiuConfig().img:
            msg = await pic_msg_format(msg, event)
            pic = await get_msg_pic(msg)
            await sect_owner_change.finish(MessageSegment.image(pic))
        else:
            await sect_owner_change.finish(msg, at_sender=True)
    position_this = [k for k, v in jsondata.sect_config_data().items() if v.get("title", "") == "宗主"]
    owner_position = int(position_this[0]) if len(position_this) == 1 else 0
    if user_message.sect_position != owner_position:
        msg = "只有宗主才能进行传位。"
        if XiuConfig().img:
            msg = await pic_msg_format(msg, event)
            pic = await get_msg_pic(msg)
            await sect_owner_change.finish(MessageSegment.image(pic))
        else:
            await sect_owner_change.finish(msg, at_sender=True)
    give_qq = None  # 艾特的时候存到这里
    for arg in args:
        # print(args)
        if arg.type == "at":
            give_qq = arg.data.get("qq", "")
    if give_qq:
        if give_qq == user_id:
            msg = "无法对自己的进行传位操作。"
            if XiuConfig().img:
                msg = await pic_msg_format(msg, event)
                pic = await get_msg_pic(msg)
                await sect_owner_change.finish(MessageSegment.image(pic))
            else:
                await sect_owner_change.finish(msg, at_sender=True)
        else:
            give_user = sql_message.get_user_message(give_qq)
            if give_user.sect_id == user_message.sect_id:
                sql_message.update_usr_sect(give_user.user_id, give_user.sect_id, owner_position)
                sql_message.update_usr_sect(user_message.user_id, user_message.sect_id, owner_position + 1)
                sql_message.sect_owner_update(user_message.sect_id, give_user.user_id)
                sect_info = sql_message.get_sect_info_by_id(give_user.sect_id)
                msg = f"传老宗主{user_message.user_name}法旨，即日起{give_user.user_name}继任{sect_info.sect_name}宗主"
                if XiuConfig().img:
                    msg = await pic_msg_format(msg, event)
                    pic = await get_msg_pic(msg)
                    await sect_owner_change.finish(MessageSegment.image(pic))
                else:
                    await sect_owner_change.finish(msg, at_sender=True)
            else:
                msg = f"{give_user.user_name}不在你管理的宗门内，请检查。"
                if XiuConfig().img:
                    msg = await pic_msg_format(msg, event)
                    pic = await get_msg_pic(msg)
                    await sect_owner_change.finish(MessageSegment.image(pic))
                else:
                    await sect_owner_change.finish(msg, at_sender=True)
    else:
        msg = f"请按照规范进行操作，ex:宗主传位@XXX，将XXX道友（需在自己管理下的宗门）升为宗主，自己则变为宗主下一等职位。"
        if XiuConfig().img:
            msg = await pic_msg_format(msg, event)
            pic = await get_msg_pic(msg)
            await sect_owner_change.finish(MessageSegment.image(pic))
        else:
            await sect_owner_change.finish(msg, at_sender=True)


@create_sect.handle()
async def _(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    """创建宗门，对灵石、修为等级有要求，且需要当前状态无宗门"""
    await data_check_conf(bot, event)

    try:
        user_id, group_id, mess = await data_check(bot, event)
    except MsgError:
        return

    if mess:
        # 首先判断是否满足创建宗门的三大条件
        level = mess.level
        list_level_all = list(jsondata.level_data().keys())
        if list_level_all.index(level) < list_level_all.index(
                XiuConfig().sect_min_level) or mess.stone < XiuConfig().sect_create_cost or mess.sect_id:
            msg = f"创建宗门要求：（1）创建者境界最低要求为{XiuConfig().sect_min_level}；" \
                  f"（2）花费{XiuConfig().sect_create_cost}灵石费用；" \
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
                sql_message.update_ls(user_id, XiuConfig().sect_min_level, 2)
                msg = f"恭喜{mess.user_name}道友创建宗门——{sect_name}，宗门编号为{new_sect.sect_id}。为道友贺！为仙道贺！"
            else:
                msg = f"道友确定要创建无名之宗门？还请三思。"
    else:
        msg = f"区区凡人，也想创立万世仙门，大胆！"
    if XiuConfig().img:
        msg = await pic_msg_format(msg, event)
        pic = await get_msg_pic(msg)
        await create_sect.finish(MessageSegment.image(pic))
    else:
        await create_sect.finish(msg, at_sender=True)

@sect_kick_out.handle()
async def _(bot: Bot,event: GroupMessageEvent, args: Message = CommandArg()):
    """踢出宗门"""
    await data_check_conf(bot, event)

    user_id = event.get_user_id()
    user_message = sql_message.get_user_message(user_id)
    if not user_message:
        msg = "修仙界没有你的信息！请输入我要修仙，踏入修行"
        if XiuConfig().img:
            msg = await pic_msg_format(msg, event)
            pic = await get_msg_pic(msg)
            await sect_kick_out.finish(MessageSegment.image(pic))
        else:
            await sect_kick_out.finish(msg, at_sender=True)
    if not user_message.sect_id:
        msg = "道友还未加入一方宗门。"
        if XiuConfig().img:
            msg = await pic_msg_format(msg, event)
            pic = await get_msg_pic(msg)
            await sect_kick_out.finish(MessageSegment.image(pic))
        else:
            await sect_kick_out.finish(msg, at_sender=True)
    give_qq = None  # 艾特的时候存到这里
    for arg in args:
        # print(args)
        if arg.type == "at":
            give_qq = arg.data.get("qq", "")
    if give_qq:
        if give_qq == user_id:
            msg = "无法对自己的进行踢出操作，试试退出宗门？"
            if XiuConfig().img:
                msg = await pic_msg_format(msg, event)
                pic = await get_msg_pic(msg)
                await sect_kick_out.finish(MessageSegment.image(pic))
            else:
                await sect_kick_out.finish(msg, at_sender=True)
        else:
            give_user = sql_message.get_user_message(give_qq)
            if give_user.sect_id == user_message.sect_id:
                position_zhanglao = [k for k, v in jsondata.sect_config_data().items() if v.get("title", "") == "长老"]
                idx_position = int(position_zhanglao[0]) if len(position_zhanglao) == 1 else 1
                if user_message.sect_position <= idx_position:
                    if give_user.sect_position <= user_message.sect_position:
                        msg = f"{give_user.user_name}的宗门职务为{jsondata.sect_config_data()[f'{give_user.sect_position}']['title']}，不在你之下，无权操作。"
                        if XiuConfig().img:
                            msg = await pic_msg_format(msg, event)
                            pic = await get_msg_pic(msg)
                            await sect_kick_out.finish(MessageSegment.image(pic))
                        else:
                            await sect_kick_out.finish(msg, at_sender=True)
                    else:
                        sect_info = sql_message.get_sect_info_by_id(give_user.sect_id)
                        sql_message.update_usr_sect(give_user.user_id, None, None)
                        sql_message.update_user_sect_contribution(give_user.user_id, 0)
                        msg = f"传{jsondata.sect_config_data()[f'{user_message.sect_position}']['title']}" \
                            f"{user_message.user_name}法旨，即日起{give_user.user_name}被" \
                            f"{sect_info.sect_name}除名"
                        if XiuConfig().img:
                            msg = await pic_msg_format(msg, event)
                            pic = await get_msg_pic(msg)
                            await sect_kick_out.finish(MessageSegment.image(pic))
                        else:
                            await sect_kick_out.finish(msg, at_sender=True)
                else:
                    msg = f"你的宗门职务为{jsondata.sect_config_data()[f'{user_message.sect_position}']['title']}，只有长老及以上可执行踢出操作。"
                    if XiuConfig().img:
                        msg = await pic_msg_format(msg, event)
                        pic = await get_msg_pic(msg)
                        await sect_kick_out.finish(MessageSegment.image(pic))
                    else:
                        await sect_kick_out.finish(msg, at_sender=True)
            else:
                msg = f"{give_user.user_name}不在你管理的宗门内，请检查。"
                if XiuConfig().img:
                    msg = await pic_msg_format(msg, event)
                    pic = await get_msg_pic(msg)
                    await sect_kick_out.finish(MessageSegment.image(pic))
                else:
                    await sect_kick_out.finish(msg, at_sender=True)
    else:
        msg = f"请按照规范进行操作，ex:踢出宗门@XXX，将XXX道友（需在自己管理下的宗门）踢出宗门"
        if XiuConfig().img:
            msg = await pic_msg_format(msg, event)
            pic = await get_msg_pic(msg)
            await sect_kick_out.finish(MessageSegment.image(pic))
        else:
            await sect_kick_out.finish(msg, at_sender=True)


@sect_out.handle()
async def _(bot: Bot,event: GroupMessageEvent, args: Message = CommandArg()):
    """退出宗门"""
    await data_check_conf(bot, event)

    user_id = event.get_user_id()
    user_message = sql_message.get_user_message(user_id)
    if not user_message:
        msg = "修仙界没有你的信息！请输入我要修仙，踏入修行"
        if XiuConfig().img:
            msg = await pic_msg_format(msg, event)
            pic = await get_msg_pic(msg)
            await sect_out.finish(MessageSegment.image(pic))
        else:
            await sect_out.finish(msg, at_sender=True)
    if not user_message.sect_id:
        msg = "道友还未加入一方宗门。"
        if XiuConfig().img:
            msg = await pic_msg_format(msg, event)
            pic = await get_msg_pic(msg)
            await sect_out.finish(MessageSegment.image(pic))
        else:
            await sect_out.finish(msg, at_sender=True)
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
                    msg = f"欲退出的宗门编号{int(sect_out_id[0])}似乎有误，未在宗门名录上发现!"
                    if XiuConfig().img:
                        msg = await pic_msg_format(msg, event)
                        pic = await get_msg_pic(msg)
                        await sect_out.finish(MessageSegment.image(pic))
                    else:
                        await sect_out.finish(msg, at_sender=True)
                else:
                    sql_message.update_usr_sect(user_id, None, None)
                    sect_info = sql_message.get_sect_info_by_id(int(sect_out_id[0]))
                    sql_message.update_user_sect_contribution(user_id, 0)
                    msg = f"道友已退出{sect_info.sect_name}，今后就是自由散修，是福是祸，犹未可知。"
                    if XiuConfig().img:
                        msg = await pic_msg_format(msg, event)
                        pic = await get_msg_pic(msg)
                        await sect_out.finish(MessageSegment.image(pic))
                    else:
                        await sect_out.finish(msg, at_sender=True)
            else:
                msg = f"道友所在宗门编号为{user_message.sect_id}，与欲退出的宗门编号{int(sect_out_id[0])}不符"
                if XiuConfig().img:
                    msg = await pic_msg_format(msg, event)
                    pic = await get_msg_pic(msg)
                    await sect_out.finish(MessageSegment.image(pic))
                else:
                    await sect_out.finish(msg, at_sender=True)
        else:
            msg = "欲退出的宗门编号解析异常"
            if XiuConfig().img:
                msg = await pic_msg_format(msg, event)
                pic = await get_msg_pic(msg)
                await sect_out.finish(MessageSegment.image(pic))
            else:
                await sect_out.finish(msg, at_sender=True)
    else:
        msg = "宗主无法直接退出宗门，如确有需要，请完成宗主传位后另行尝试。"
        if XiuConfig().img:
            msg = await pic_msg_format(msg, event)
            pic = await get_msg_pic(msg)
            await sect_out.finish(MessageSegment.image(pic))
        else:
            await sect_out.finish(msg, at_sender=True)

@sect_donate.handle()
async def _(bot: Bot,event: GroupMessageEvent, args: Message = CommandArg()):
    """宗门捐献"""
    await data_check_conf(bot, event)

    user_id = event.get_user_id()
    user_message = sql_message.get_user_message(user_id)
    if not user_message:
        msg = "修仙界没有你的信息！请输入我要修仙，踏入修行"
        if XiuConfig().img:
            msg = await pic_msg_format(msg, event)
            pic = await get_msg_pic(msg)
            await sect_donate.finish(MessageSegment.image(pic))
        else:
            await sect_donate.finish(msg, at_sender=True)
    if not user_message.sect_id:
        msg = "道友还未加入一方宗门。"
        if XiuConfig().img:
            msg = await pic_msg_format(msg, event)
            pic = await get_msg_pic(msg)
            await sect_donate.finish(MessageSegment.image(pic))
        else:
            await sect_donate.finish(msg, at_sender=True)
    msg = args.extract_plain_text().strip()
    donate_num = re.findall("\d+", msg)  # 捐献灵石数
    if len(donate_num) > 0:
        if int(donate_num[0]) > user_message.stone:
            msg = f"道友的灵石数量小于欲捐献数量{int(donate_num[0])}，请检查"
            if XiuConfig().img:
                msg = await pic_msg_format(msg, event)
                pic = await get_msg_pic(msg)
                await sect_donate.finish(MessageSegment.image(pic))
            else:
                await sect_donate.finish(msg, at_sender=True)
        else:
            sql_message.update_ls(user_id, int(donate_num[0]), 2)
            sql_message.donate_update(user_message.sect_id, int(donate_num[0]))
            sql_message.update_user_sect_contribution(user_id, user_message.sect_contribution + int(donate_num[0]))
            msg = f"道友捐献灵石{int(donate_num[0])}枚，增加宗门建设度{int(donate_num[0]) * 10}，宗门贡献度增加：{int(donate_num[0])}点，蒸蒸日上！"
            if XiuConfig().img:
                msg = await pic_msg_format(msg, event)
                pic = await get_msg_pic(msg)
                await sect_donate.finish(MessageSegment.image(pic))
            else:
                await sect_donate.finish(msg, at_sender=True)
    else:
        msg = "捐献的灵石数量解析异常"
        if XiuConfig().img:
            msg = await pic_msg_format(msg, event)
            pic = await get_msg_pic(msg)
            await sect_donate.finish(MessageSegment.image(pic))
        else:
            await sect_donate.finish(msg, at_sender=True)


@sect_position_update.handle()
async def _(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    """宗门职位变更，首先确认操作者的职位是长老及以上（宗主可以变更宗主及以下，长老可以变更长老以下），然后读取变更等级及艾特目标"""
    await data_check_conf(bot, event)

    try:
        user_id, group_id, user_message = await data_check(bot, event)
    except MsgError:
        return

    position_zhanglao = [k for k, v in jsondata.sect_config_data().items() if v.get("title", "") == "长老"]
    idx_position = int(position_zhanglao[0]) if len(position_zhanglao) == 1 else 1
    if user_message.sect_position > idx_position:
        msg = f"你的宗门职位为{jsondata.sect_config_data()[f'{user_message.sect_position}']['title']}，无权进行职位管理"
        if XiuConfig().img:
            msg = await pic_msg_format(msg, event)
            pic = await get_msg_pic(msg)
            await sect_position_update.finish(MessageSegment.image(pic))
        else:
            await sect_position_update.finish(msg, at_sender=True)

    give_qq = None  # 艾特的时候存到这里
    msg = args.extract_plain_text().strip()
    position_num = re.findall("\d+", msg)  # 职位品阶

    for arg in args:
        # print(args)
        if arg.type == "at":
            give_qq = arg.data.get("qq", "")
    if give_qq:
        if give_qq == user_id:
            msg = "无法对自己的职位进行管理。"
            if XiuConfig().img:
                msg = await pic_msg_format(msg, event)
                pic = await get_msg_pic(msg)
                await sect_position_update.finish(MessageSegment.image(pic))
            else:
                await sect_position_update.finish(msg, at_sender=True)
        else:
            if len(position_num) > 0 and position_num[0] in list(jsondata.sect_config_data().keys()):
                give_user = sql_message.get_user_message(give_qq)
                if give_user.sect_id == user_message.sect_id and give_user.sect_position > user_message.sect_position:
                    if int(position_num[0]) > user_message.sect_position:
                        sql_message.update_usr_sect(give_user.user_id, give_user.sect_id, int(position_num[0]))
                        msg = f"传{jsondata.sect_config_data()[f'{user_message.sect_position}']['title']}" \
                            f"{user_message.user_name}法旨，即日起{give_user.user_name}为" \
                            f"本宗{jsondata.sect_config_data()[f'{int(position_num[0])}']['title']}"
                        if XiuConfig().img:
                            msg = await pic_msg_format(msg, event)
                            pic = await get_msg_pic(msg)
                            await sect_position_update.finish(MessageSegment.image(pic))
                        else:
                            await sect_position_update.finish(msg, at_sender=True)
                    else:
                        msg = "道友试图变更的职位品阶必须在你品阶之下"
                        if XiuConfig().img:
                            msg = await pic_msg_format(msg, event)
                            pic = await get_msg_pic(msg)
                            await sect_position_update.finish(MessageSegment.image(pic))
                        else:
                            await sect_position_update.finish(msg, at_sender=True)
                else:
                    msg = "请确保变更目标道友与你在同一宗门，且职位品阶在你之下。"
                    if XiuConfig().img:
                        msg = await pic_msg_format(msg, event)
                        pic = await get_msg_pic(msg)
                        await sect_position_update.finish(MessageSegment.image(pic))
                    else:
                        await sect_position_update.finish(msg, at_sender=True)
            else:
                msg = "职位品阶数字解析异常，请输入宗门职位变更帮助，查看支持的数字解析配置"
                if XiuConfig().img:
                    msg = await pic_msg_format(msg, event)
                    pic = await get_msg_pic(msg)
                    await sect_position_update.finish(MessageSegment.image(pic))
                else:
                    await sect_position_update.finish(msg, at_sender=True)
    else:
        msg = f"请按照规范进行操作，ex:宗门职位变更2@XXX，将XXX道友（需在自己管理下的宗门）的" \
            f"变更为{jsondata.sect_config_data().get('2', {'title': '没有找到2品阶'})['title']}"
        if XiuConfig().img:
            msg = await pic_msg_format(msg, event)
            pic = await get_msg_pic(msg)
            await sect_position_update.finish(MessageSegment.image(pic))
        else:
            await sect_position_update.finish(msg, at_sender=True)

@join_sect.handle()
async def _(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    """加入宗门，后跟宗门ID，要求加入者当前状态无宗门，入门默认为外门弟子"""
    await data_check_conf(bot, event)

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
    if XiuConfig().img:
        msg = await pic_msg_format(msg, event)
        pic = await get_msg_pic(msg)
        await join_sect.finish(MessageSegment.image(pic))
    else:
        await join_sect.finish(msg, at_sender=True)

# editer:zyp981204
@my_sect.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    """查看所在宗门信息"""
    await data_check_conf(bot, event)

    try:
        user_id, group_id, mess = await data_check(bot, event)
    except MsgError:
        return

    if mess:
        elixir_room_level_up_config = config['宗门丹房参数']['elixir_room_level']
        sect_id = mess.sect_id
        sect_position = mess.sect_position
        user_name = mess.user_name
        sect_info = sql_message.get_sect_info(sect_id)
        owner_idx = [k for k, v in jsondata.sect_config_data().items() if v.get("title", "") == "宗主"]
        owner_position = int(owner_idx[0]) if len(owner_idx) == 1 else 0
        if sect_id:
            _, sql_res = sql_message.scale_top()
            top_idx_list = [_[0] for _ in sql_res]
            if int(sect_info.elixir_room_level) == 0:
                elixir_room_name = "暂无"
            else:
                elixir_room_name= elixir_room_level_up_config[str(sect_info.elixir_room_level)]['name']
            msg = f"""{user_name}所在宗门
    宗门名讳：{sect_info.sect_name}
    宗门编号：{sect_id}
    宗   主：{sql_message.get_user_message(sect_info.sect_owner).user_name}
    道友职位：{jsondata.sect_config_data()[f"{sect_position}"]["title"]}
    宗门建设度：{sect_info.sect_scale}
    洞天福地：{sect_info.sect_fairyland if sect_info.sect_fairyland else "暂无"}
    宗门位面排名：{top_idx_list.index(sect_id) + 1}
    宗门拥有资材：{sect_info.sect_materials}
    宗门贡献度：{mess.sect_contribution}
    宗门丹房：{elixir_room_name}
    """
            if sect_position == owner_position:
                msg += f"\n   宗门储备：{sect_info.sect_used_stone}灵石"
        else:
            msg = "一介散修，莫要再问。"
    else:
        msg = "未曾踏入修仙世界，输入 我要修仙 加入我们，看破这世间虚妄!"
    if XiuConfig().img:
        msg = await pic_msg_format(msg, event)
        pic = await get_msg_pic(msg)
        await my_sect.finish(MessageSegment.image(pic))
    else:
        await my_sect.finish(msg, at_sender=True)

def create_user_sect_task(user_id):
    tasklist = config["宗门任务"]
    key = random.choices(list(tasklist))[0]
    userstask[user_id]['任务名称'] = key
    userstask[user_id]['任务内容'] = tasklist[key]

def isUserTask(user_id):
    "判断用户是否已有任务 True：有任务"
    Flag = False
    try:
        userstask[user_id]
    except:
        userstask[user_id] = {}

    if userstask[user_id] != {}:
        Flag = True

    return Flag


def get_sect_mainbuff_id_list(sect_id):
    """获取宗门功法id列表"""
    sect_info = sql_message.get_sect_info(sect_id)
    mainbufflist = str(sect_info.mainbuff)[1:-1].split(',')
    return mainbufflist

def get_sect_secbuff_id_list(sect_id):
    """获取宗门神通id列表"""
    sect_info = sql_message.get_sect_info(sect_id)
    secbufflist = str(sect_info.secbuff)[1:-1].split(',')
    return secbufflist

def set_sect_list(bufflist):
    """传入ID列表，返回[ID列表]"""
    sqllist1 = ''
    for buff in bufflist:
        if buff == '':
            continue
        sqllist1 += f'{buff},'
    sqllist = f"[{sqllist1[:-1]}]"
    return sqllist
    
def get_mainname_list(bufflist):
    """根据传入的功法列表，返回功法名字列表"""
    namelist = []
    for buff in bufflist:
        mainbuff = items.get_data_by_item_id(buff)
        namelist.append(mainbuff['name'])
    return namelist

def get_secname_list(bufflist):
    """根据传入的神通列表，返回神通名字列表"""
    namelist = []
    for buff in bufflist:
        secbuff = items.get_data_by_item_id(buff)
        namelist.append(secbuff['name'])
    return namelist

def get_mainnameid(buffname, bufflist):
    """根据传入的功法名字，获取到功法的id"""
    tempdict = {}
    buffid = 0
    for buff in bufflist:
        mainbuff = items.get_data_by_item_id(buff)
        tempdict[mainbuff['name']] = buff
    for k, v in tempdict.items():
        if buffname == k:
            buffid = v
    return buffid

def get_secnameid(buffname, bufflist):
    tempdict = {}
    buffid = 0
    for buff in bufflist:
        secbuff = items.get_data_by_item_id(buff)
        tempdict[secbuff['name']] = buff
    for k, v in tempdict.items():
        if buffname == k:
            buffid = v
    return buffid
    

def get_sectbufftxt(sect_scale, config):
    """
    获取宗门当前获取功法的品阶 档位 + 3
    参数：sect_scale=宗门建设度
    config=宗门主功法参数
    """
    bufftxt = {1:'人阶下品',2:'人阶上品',3:'黄阶下品',4:'黄阶上品',5:'玄阶下品',6:'玄阶上品',7:'地阶下品',8:'地阶上品',9:'天阶下品',10:'天阶上品'}
    buffgear = divmod(sect_scale, config['建设度'])[0]
    if buffgear >= 7:
        buffgear = 10
    elif buffgear == 0:
        buffgear = 3
    else:
        buffgear = buffgear + 3
    return buffgear, bufftxt[buffgear]



def get_sect_level(sect_id):
    sect = sql_message.get_sect_info(sect_id)
    return divmod(sect.sect_scale, config["等级建设度"])

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


async def get_group_id(session_id):
    """获取group_id"""
    res = re.findall("_(.*)_", session_id)
    group_id = res[0]
    return group_id

class MsgError(ValueError):
    pass


