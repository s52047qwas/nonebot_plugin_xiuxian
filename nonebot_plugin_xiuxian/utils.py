from nonebot.log import logger

from .xiuxian2_handle import XiuxianDateManage
from nonebot.adapters.onebot.v11 import (
    Bot,
    MessageEvent,
    GroupMessageEvent,
    MessageSegment,
)
import math
from base64 import b64encode
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from wcwidth import wcwidth
import re

from .data_source import jsondata
from .xiuxian_config import JsonConfig, XiuConfig

def check_user_type(user_id, need_type):
    """
    :说明: `check_user_type`
    > 匹配用户状态，返回是否状态一致
    :返回参数:
      * `isType: 是否一致
      * `msg: 消息体
    """
    isType = False
    msg = ''
    user_cd_message = XiuxianDateManage().get_user_cd(user_id)
    if user_cd_message == None:
        user_type = 0
    else:
        user_type = user_cd_message.type
    
    if user_type == need_type:#状态一致
        isType = True
    else:
        if user_type == 1:
            msg = "道友现在在闭关呢，小心走火入魔！"
            
        elif user_type == 2:
            msg = "道友现在在做悬赏令呢，小心走火入魔！"

        elif user_type == 3:
            msg = "道友现在正在秘境中，分身乏术！"
        
        elif user_type == 0:
            msg = "道友现在什么都没干呢~"

    return isType, msg

def check_user(event: GroupMessageEvent):
    """
    判断用户信息是否存在
    :返回参数:
      * `isUser: 是否存在
      * `user_info: 用户
      * `msg: 消息体
    """
    
    isUser = False
    user_id = event.get_user_id()
    user_info = XiuxianDateManage().get_user_message(user_id)
    if user_info is None:
        msg = "修仙界没有道友的信息，请输入【我要修仙】加入！"
    else:
        isUser = True
        msg = ''
    
    return isUser, user_info, msg

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
    try:
        if isinstance(event, GroupMessageEvent):
            await bot.call_api(
                "send_group_forward_msg", group_id=event.group_id, messages=messages
            )
        else:
            await bot.call_api(
                "send_private_forward_msg", user_id=event.user_id, messages=messages
            )
    except Exception as e:  # 发送群消息失败
        print(messages)
        if isinstance(event, GroupMessageEvent):
            msg = ""
            for message in messages:
                msg += message['data']['content']
                msg += "========================\n"
            pic = await get_msg_pic(msg)
            await bot.send_group_msg(group_id=event.group_id, message=MessageSegment.image(pic))
        #logger.error(f"推送失败：{e}")

async def send_forward_msg_list(
    bot: Bot,
    event: MessageEvent,
    messages: list,  # 格式[*dict] 例[*{"type": "node", "data": {"name": name, "uin": uin, "content": msg}}]
):
    """
    合并消息转发
    区分人
    """

    if isinstance(event, GroupMessageEvent):
        await bot.call_api(
            "send_group_forward_msg", group_id=event.group_id, messages=messages
        )
    else:
        await bot.call_api(
            "send_private_forward_msg", user_id=event.user_id, messages=messages
        )

async def data_check_conf(bot, event):
    """
    判断当前群是否启用修仙功能
    """

    def get_group_id(session_id):
        """获取group_id"""
        res = re.findall("_(.*)_", session_id)
        group_id = res[0]
        return group_id

    group_id = get_group_id(event.get_session_id())
    conf_data = JsonConfig().read_data()

    try:
        if group_id in conf_data["group"]:
            await bot.send(event=event, message=f"本群已关闭修仙模组，请联系管理员开启！")
            raise ConfError
        else:
            pass
    except KeyError:
        pass


class ConfError(ValueError):
    pass


class Txt2Img:
    """保存帮助信息为图片文件
    插件copy为nonebot-plugin-txt2img
    git：https://github.com/mobyw/nonebot-plugin-txt2img"""

    def __init__(self, size=30):
        self.font_family = str(jsondata.FONT_FILE)
        self.user_font_size = int(size * 1.5)
        self.lrc_font_size = int(size)
        self.line_space = int(size)
        self.lrc_line_space = int(size / 2)
        self.stroke = 5
        self.share_img_width = 1080

    def wrap(self, string):
        max_width = int(1850 / self.lrc_font_size)
        temp_len = 0
        result = ''
        for ch in string:
            result += ch
            temp_len += wcwidth(ch)
            if ch == '\n':
                temp_len = 0
            if temp_len >= max_width:
                temp_len = 0
                result += '\n'
        result = result.rstrip()
        return result

    def save(self, title, lrc):
        """MI Note"""
        border_color = (220, 211, 196)
        text_color = (125, 101, 89)

        out_padding = 30
        padding = 45
        banner_size = 20

        user_font = ImageFont.truetype(self.font_family, self.user_font_size)
        lyric_font = ImageFont.truetype(self.font_family, self.lrc_font_size)

        if title == ' ':
            title = ''

        lrc = self.wrap(lrc)

        if lrc.find("\n") > -1:
            lrc_rows = len(lrc.split("\n"))
        else:
            lrc_rows = 1

        w = self.share_img_width

        if title:
            inner_h = (
                padding * 2
                + self.user_font_size
                + self.line_space
                + self.lrc_font_size * lrc_rows
                + (lrc_rows - 1) * (self.lrc_line_space)
            )
        else:
            inner_h = (
                padding * 2
                + self.lrc_font_size * lrc_rows
                + (lrc_rows - 1) * (self.lrc_line_space)
            )

        h = out_padding * 2 + inner_h

        out_img = Image.new(mode="RGB", size=(w, h), color=(255, 255, 255))
        draw = ImageDraw.Draw(out_img)

        mi_img = Image.open(jsondata.BACKGROUND_FILE)
        mi_banner = Image.open(jsondata.BANNER_FILE).resize(
            (banner_size, banner_size), resample=3
        )

        # add background
        for x in range(int(math.ceil(h / 100))):
            out_img.paste(mi_img, (0, x * 100))

        # add border
        def draw_rectangle(draw, rect, width):
            for i in range(width):
                draw.rectangle(
                    (rect[0] + i, rect[1] + i, rect[2] - i, rect[3] - i),
                    outline=border_color,
                )

        draw_rectangle(
            draw, (out_padding, out_padding, w - out_padding, h - out_padding), 2
        )

        # add banner
        out_img.paste(mi_banner, (out_padding, out_padding))
        out_img.paste(
            mi_banner.transpose(Image.FLIP_TOP_BOTTOM),
            (out_padding, h - out_padding - banner_size + 1),
        )
        out_img.paste(
            mi_banner.transpose(Image.FLIP_LEFT_RIGHT),
            (w - out_padding - banner_size + 1, out_padding),
        )
        out_img.paste(
            mi_banner.transpose(Image.FLIP_LEFT_RIGHT).transpose(Image.FLIP_TOP_BOTTOM),
            (w - out_padding - banner_size + 1, h - out_padding - banner_size + 1),
        )

        if title:
            user_w, user_h = ImageDraw.Draw(
                Image.new(mode="RGB", size=(1, 1))
            ).textsize(title, font=user_font, spacing=self.line_space)
            draw.text(
                ((w - user_w) // 2, out_padding + padding),
                title,
                font=user_font,
                fill=text_color,
                spacing=self.line_space,
            )
            draw.text(
                (
                    out_padding + padding,
                    out_padding + padding + self.user_font_size + self.line_space,
                ),
                lrc,
                font=lyric_font,
                fill=text_color,
                spacing=self.lrc_line_space,
            )
        else:
            draw.text(
                (out_padding + padding, out_padding + padding),
                lrc,
                font=lyric_font,
                fill=text_color,
                spacing=self.lrc_line_space,
            )
        return self.img2b64(out_img)

    def img2b64(self, out_img) -> str:
        """ image to base64 """
        buf = BytesIO()
        out_img.save(buf, format="PNG")
        base64_str = "base64://" + b64encode(buf.getvalue()).decode()
        return base64_str

async def get_msg_pic(msg, title=' ', font_size=55):
    img = Txt2Img(font_size)
    pic = img.save(title, msg)
    return pic

async def pic_msg_format(msg, event):
    user_name = (
        event.sender.card if event.sender.card else event.sender.nickname
    )
    result = "@" + user_name + "\n" + msg
    return result


def cal_max_hp(user_msg, hp_buff):
    if user_msg.level.startswith("化圣境"):
        exp = XiuxianDateManage().get_level_power(user_msg.level) * XiuConfig().closing_exp_upper_limit
    else:
        exp = user_msg.exp
    logger.info( f"hp_buff:{hp_buff}！")
    max_hp = int( exp/2 * (1 + hp_buff) )
    return max_hp

def cal_max_mp(user_msg, mp_buff):
    if user_msg.level.startswith("化圣境"):
        exp = XiuxianDateManage().get_level_power(user_msg.level) * XiuConfig().closing_exp_upper_limit
    else:
        exp = user_msg.exp
    logger.info(f"mp_buff:{mp_buff}！")
    max_mp = int(exp * (1 + mp_buff))
    return max_mp