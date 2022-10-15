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
)
from nonebot.params import CommandArg, RegexGroup
from ..data_source import jsondata
from ..xiuxian_config import XiuConfig
import re

# 定时任务
materialsupdate = require("nonebot_plugin_apscheduler").scheduler
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

jsd = jsondata.sect_config_data()['sect_scale']
__sect_help__ = f"""
宗门帮助信息:
指令：
1、我的宗门：查看当前所处宗门信息
2、创建宗门：创建宗门，需求：{XiuConfig().sect_create_cost}灵石，需求境界{XiuConfig().sect_min_level}
3、加入宗门：加入一个宗门
4、宗门职位变更：宗主可以改变宗门成员的职位等级
5、宗门捐献：建设宗门，提高宗门建设度，每{jsd}建设度会提高1级攻击修炼等级上限
6、退出宗门：退出当前宗门
7、踢出宗门：踢出对应宗门成员
8、宗门传位：宗主可以传位宗门成员
9、升级攻击修炼：升级道友的攻击修炼等级，每级修炼等级提升10%攻击力
10、宗门列表：查看所有宗门列表
""".strip()

@sect_help.handle()
async def _():
    """修仙帮助"""
    msg = __sect_help__
    await sect_help.finish(msg)

sql_message = XiuxianDateManage()  # sql类
# 定时任务每1小时按照宗门贡献度增加资材
@materialsupdate.scheduled_job("cron",hour='11-12')
async def _():
    all_sects = sql_message.get_all_sects_id_scale()
    for s in all_sects:
        sql_message.update_sect_materials(sect_id=s[0], sect_materials=s[1], key=1)
    
    logger.info('已更新所有宗门的资材')

@upatkpractice.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    try:
        user_id, group_id, userinfo = await data_check(bot, event)
    except MsgError:
        return

    
    sect_id = userinfo.sect_id
    if sect_id:
        sect_materials = int(sql_message.get_sect_info(sect_id).sect_materials)#当前资材
        useratkpractice = int(userinfo.atkpractice) #当前等级
        if useratkpractice == 25:
            await upatkpractice.finish(f"道友的攻击修炼等级已达到最高等级!")
        
        sect_level = get_sect_level(sect_id)[0] if get_sect_level(sect_id)[0] <= 25 else 25#获取当前宗门修炼等级上限，500w建设度1级,上限25级

        sect_position = userinfo.sect_position
        if sect_position == 4:
            await upatkpractice.finish(f"道友所在宗门的职位为：{jsondata.sect_config_data()[f'{sect_position}']['title']}，不满足使用资材的条件!")

        if useratkpractice >= sect_level:
            await upatkpractice.finish(f"道友的攻击修炼等级已达到当前宗门修炼等级的最高等级：{sect_level}，请捐献灵石提升贡献度吧！")

        cost = LEVLECOST[useratkpractice]
        if int(userinfo.stone) < cost:
            await upatkpractice.finish(f"道友的灵石不够，还需{cost - int(userinfo.stone)}灵石!")
        
        if sect_materials < cost * 10:
            await upatkpractice.finish(f"道友的所处的宗门资材不足，还需{cost * 10 - sect_materials}资材!")
        
        sql_message.update_ls(user_id, cost, 2)
        sql_message.update_sect_materials(sect_id, cost * 10, 2)
        sql_message.update_user_atkpractice(user_id, useratkpractice + 1)
        await upatkpractice.finish(f"升级成功，道友当前攻击修炼等级：{useratkpractice + 1}，消耗灵石：{cost}枚，消耗宗门资材{cost * 10}！")
    else:
        await upatkpractice.finish(f"修炼逆天而行消耗巨大，请加入宗门再进行修炼！")


@sect_list.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    sectlists = sql_message.get_all_scale()
    msg = ''
    for sect in sectlists:
        print(sect)
        user_name = sql_message.get_user_message(sect.sect_owner).user_name
        msg += f'编号{sect.sect_id}：{sect.sect_name}，宗主：{user_name}，宗门建设度：{sect.sect_scale}\n'
    
    await sect_list.finish(msg)

@sect_owner_change.handle()
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


@create_sect.handle()
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
    await create_sect.finish(msg, at_sender=True)

@sect_kick_out.handle()
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


@sect_out.handle()
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

@sect_donate.handle()
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


@sect_position_update.handle()
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

@join_sect.handle()
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

# editer:zyp981204
@my_sect.handle()
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
    宗门位面排名：{top_idx_list.index(sect_id) + 1}
    宗门拥有资材：{sect_info.sect_materials}
    """
            if sect_position == owner_position:
                msg += f"\n   宗门储备：{sect_info.sect_used_stone}灵石"
        else:
            msg = "一介散修，莫要再问。"
    else:
        msg = "未曾踏入修仙世界，输入 我要修仙 加入我们，看破这世间虚妄!"

    await my_sect.finish(msg, at_sender=True)

def get_sect_level(sect_id):
    sect = sql_message.get_sect_info(sect_id)
    return divmod(sect.sect_scale, jsd)

LEVLECOST = {
    0:10000,
    1:20000,
    2:40000,
    3:80000,
    4:160000,
    5:320000,
    6:500000,
    7:500000,
    8:500000,
    9:500000,
    10:500000,
    11:500000,
    12:500000,
    13:500000,
    14:500000,
    15:500000,
    16:500000,
    17:500000,
    18:500000,
    19:500000,
    20:500000,
    21:500000,
    22:500000,
    23:500000,
    24:500000,
    25:0,
}


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