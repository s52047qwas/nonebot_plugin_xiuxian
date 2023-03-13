from PIL import Image, ImageDraw, ImageFont
import asyncio
import asyncio
from pathlib import Path

from PIL import Image
from .download import get_avatar_by_user_id_and_save

from .send_image_tool import convert_img


TEXT_PATH = Path(__file__).parent / 'texture2d'

first_color = (242, 250, 242)
second_color = (57, 57, 57)


FONT_ORIGIN_PATH = Path(__file__).parent / 'font.ttf'

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
    line = Image.open(TEXT_PATH / 'line3.png').resize((400, 60)).convert("RGBA")
    line_draw = ImageDraw.Draw(line)
    word = f"QQ:{user_id}"
    w, h = await linewh(line, word)
    line_draw.text((w, h), word, first_color, font_36, 'lm')
    #绘制QQ信息
    img.paste(line, (130,520), line)
    
    DETAIL_baseinfo = {}
    DETAIL_baseinfo["灵根"] = DETAIL_MAP["灵根"]
    DETAIL_baseinfo["突破状态"] = DETAIL_MAP["突破状态"]
    DETAIL_baseinfo['主修功法'] = DETAIL_MAP['主修功法']
    DETAIL_baseinfo['副修神通'] = DETAIL_MAP['副修神通']
    DETAIL_baseinfo["攻击力"] = DETAIL_MAP["攻击力"]
    DETAIL_baseinfo["法器"] = DETAIL_MAP["法器"]
    DETAIL_baseinfo["防具"] = DETAIL_MAP["防具"]
    
    DETAIL_right = {}
    DETAIL_right['道号'] = DETAIL_MAP['道号']
    DETAIL_right['境界'] = DETAIL_MAP['境界']
    DETAIL_right['修为'] = DETAIL_MAP['修为']
    DETAIL_right['灵石'] = DETAIL_MAP['灵石']
    DETAIL_right['战力'] = DETAIL_MAP['战力']
    
    tasks1 = []
    for key, value in DETAIL_right.items():
        tasks1.append(_draw_line(img, key, value, DETAIL_right))
    await asyncio.gather(*tasks1)
    
    baseinfo = Image.open(TEXT_PATH / 'line2.png').resize((900, 100)).convert("RGBA")
    baseword = '【基本信息】'
    w, h = await linewh(baseinfo, baseword)
    baseinfo_draw = ImageDraw.Draw(baseinfo)
    baseinfo_draw.text((w, h), baseword, first_color, font_40, 'lm')
    img.paste(baseinfo, (100, 600), baseinfo)
    
    tasks2 = []
    for key, value in DETAIL_baseinfo.items():
        tasks2.append(_draw_base_info_line(img, key, value, DETAIL_baseinfo))
    await asyncio.gather(*tasks2)
    
    sectinfo = Image.open(TEXT_PATH / 'line2.png').resize((900, 100)).convert("RGBA")
    sectword = '【宗门信息】'
    w, h = await linewh(sectinfo, sectword)
    sectinfo_draw = ImageDraw.Draw(sectinfo)
    sectinfo_draw.text((w, h), sectword, first_color, font_40, 'lm')
    img.paste(sectinfo, (100, 1442), sectinfo)
    
    DETAIL_sectinfo = {}
    DETAIL_sectinfo['所在宗门'] = DETAIL_MAP['所在宗门']
    DETAIL_sectinfo['宗门职位'] = DETAIL_MAP['宗门职位']
    tasks3 = []
    for key, value in DETAIL_sectinfo.items():
        tasks3.append(_draw_sect_info_line(img, key, value, DETAIL_sectinfo))
    await asyncio.gather(*tasks3)
    
    paihang = Image.open(
        TEXT_PATH / 'line2.png').resize((900, 100)).convert("RGBA")
    paihangword = '【排行信息】'
    w, h = await linewh(paihang, paihangword)
    paihang_draw = ImageDraw.Draw(paihang)
    paihang_draw.text((w, h), paihangword, first_color, font_40, 'lm')
    img.paste(paihang, (100, 1773), paihang)

    DETAIL_paihang = {}
    DETAIL_paihang['注册位数'] = DETAIL_MAP['注册位数']
    DETAIL_paihang['修为排行'] = DETAIL_MAP['修为排行']
    DETAIL_paihang['灵石排行'] = DETAIL_MAP['灵石排行']

    tasks4 = []
    for key, value in DETAIL_paihang.items():
        tasks4.append(_draw_ph_info_line(img, key, value, DETAIL_paihang))
    await asyncio.gather(*tasks4)
    res = await convert_img(img)
    return res

async def _draw_line(img: Image.Image, key, value, DETAIL_MAP):

    line = Image.open(TEXT_PATH / 'line3.png').resize((450, 68))
    line_draw = ImageDraw.Draw(line)
    word = f"{key}：{value}"
    w, h = await linewh(line, word)
    
    line_draw.text((70, h), word, first_color, font_36, 'lm')
    img.paste(line, (550, 100 + list(DETAIL_MAP.keys()).index(key) * 103), line)
    
async def _draw_base_info_line(img: Image.Image, key, value, DETAIL_MAP):

    line = Image.open(TEXT_PATH / 'line4.png').resize((900, 100))
    line_draw = ImageDraw.Draw(line)
    word = f"{key}：{value}"
    w, h = await linewh(line, word)
    
    line_draw.text((100, h), word, first_color, font_36, 'lm')
    img.paste(line, (100, 703 + list(DETAIL_MAP.keys()).index(key) * 103), line)
    
async def _draw_sect_info_line(img: Image.Image, key, value, DETAIL_MAP):

    line = Image.open(TEXT_PATH / 'line4.png').resize((900, 100))
    line_draw = ImageDraw.Draw(line)
    word = f"{key}：{value}"
    w, h = await linewh(line, word)
    
    line_draw.text((100, h), word, first_color, font_36, 'lm')
    img.paste(line, (100, 1547 + list(DETAIL_MAP.keys()).index(key) * 103), line)
    
async def _draw_ph_info_line(img: Image.Image, key, value, DETAIL_MAP):

    line = Image.open(TEXT_PATH / 'line4.png').resize((900, 100))
    line_draw = ImageDraw.Draw(line)
    word = f"{key}：{value}"
    w, h = await linewh(line, word)

    line_draw.text((100, h), word, first_color, font_36, 'lm')
    img.paste(line, (100, 1878 + list(DETAIL_MAP.keys()).index(key) * 103), line)

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
