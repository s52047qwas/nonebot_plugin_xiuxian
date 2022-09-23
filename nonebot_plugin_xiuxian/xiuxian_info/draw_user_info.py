from PIL import Image, ImageDraw, ImageFont
import asyncio
import asyncio
from pathlib import Path

from PIL import Image
from .download import get_avatar_by_user_id_and_save

from .utils.send_image_tool import convert_img


TEXT_PATH = Path(__file__).parent / 'texture2d'

first_color = (242, 250, 242)
second_color = (57, 57, 57)


FONT_ORIGIN_PATH = Path(__file__).parent / 'font.ttf'

USER_AVATAR_PATH = Path(__file__).parent / 'USER_AVATAR'


def font_origin(size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(FONT_ORIGIN_PATH), size=size)


font_36 = font_origin(36)
font_40 = font_origin(40)
font_24 = font_origin(24)


async def draw_user_info_img(user_id, DETAIL_MAP):
    based_w = 1100
    based_h = 2250
    #获取背景图
    img = Image.open(TEXT_PATH / 'back.png').resize((based_w, based_h)).convert("RGBA")
    #获取用户头像圆框
    user_status = Image.open(TEXT_PATH / 'user_state.png').resize((450, 450)).convert("RGBA")
    temp = await get_avatar_by_user_id_and_save(user_id)
    user_avatar = await img_author(temp, user_status)
    r, g, b, a = user_status.split()
    #绘制头像框位置
    img.paste(user_avatar, (100, 100), mask=a) 
    # img_draw = ImageDraw.Draw(img)
    #h获取信息图片
    line = Image.open(TEXT_PATH / 'line.png').resize((400, 60)).convert("RGBA")
    line_draw = ImageDraw.Draw(line)
    word = f"QQ:{user_id}"
    w, h = await linewh(line, word)
    line_draw.text((w, h), word, first_color, font_36, 'lm')
    #绘制QQ信息
    img.paste(line, (130,520), line)
    
    DETAIL_baseinfo = {}
    DETAIL_baseinfo["灵根"] = DETAIL_MAP["灵根"]
    DETAIL_baseinfo["突破状态"] = DETAIL_MAP["突破状态"]
    DETAIL_MAP.pop("灵根")
    DETAIL_MAP.pop("突破状态")
    DETAIL_right = DETAIL_MAP
    
    tasks1 = []
    for index, name in enumerate(DETAIL_right):
        tasks1.append(_draw_line(img, name, index, DETAIL_right))
    await asyncio.gather(*tasks1)
    
    baseinfo = Image.open(TEXT_PATH / 'line.png').resize((900, 100)).convert("RGBA")
    baseword = '基本信息'
    w, h = await linewh(baseinfo, baseword)
    baseinfo_draw = ImageDraw.Draw(baseinfo)
    baseinfo_draw.text((w, h), baseword, first_color, font_40, 'lm')
    img.paste(baseinfo, (100, 600), baseinfo)
    
    tasks2 = []
    for index, name in enumerate(DETAIL_baseinfo):
        tasks2.append(_draw_base_info_line(img, name, index, DETAIL_baseinfo))
    await asyncio.gather(*tasks2)
    
    res = await convert_img(img)
    return res

async def _draw_line(img: Image.Image, name: str, index: int, DETAIL_MAP):
    detail = DETAIL_MAP[name]
    line = Image.open(TEXT_PATH / 'line.png').resize((450, 68))
    line_draw = ImageDraw.Draw(line)
    word = f"{name}:{detail}"
    w, h = await linewh(line, word)
    
    line_draw.text((50, h), word, first_color, font_36, 'lm')
    img.paste(line, (600, 100 + index * 103), line)
    
async def _draw_base_info_line(img: Image.Image, name: str, index: int, DETAIL_MAP):
    detail = DETAIL_MAP[name]
    line = Image.open(TEXT_PATH / 'line.png').resize((900, 100))
    line_draw = ImageDraw.Draw(line)
    word = f"{name}:{detail}"
    w, h = await linewh(line, word)
    
    line_draw.text((100, h), word, first_color, font_36, 'lm')
    img.paste(line, (100, 703 + index * 103), line)
    
   

async def img_author(img, bg):
    
    w, h = img.size
    alpha_layer = Image.new('L', (w, w), 0)
    draw = ImageDraw.Draw(alpha_layer)
    draw.ellipse((0, 0, w, w), fill=255)
    bg.paste(img, (88, 80), alpha_layer)
    
    return bg

async def linewh(line, word):
    lw, lh = line.size
    gs_font_36 = font_origin(36)
    w, h = gs_font_36.getsize(word)
    return (lw - w) / 2, lh / 2