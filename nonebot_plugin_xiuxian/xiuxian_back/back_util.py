from ..item_json import Items
from ..xiuxian2_handle import XiuxianDateManage
from ..read_buff import UserBuffDate, get_weapon_info_msg, get_armor_info_msg, get_sec_msg, get_main_info_msg
from datetime import datetime
import json
import os
from pathlib import Path

items = Items()
sql_message = XiuxianDateManage()

def check_equipment_can_use(user_id, goods_id):
    """
    装备数据库字段：
        good_type -> '装备'
        state -> 0-未使用，1-已使用
        goods_num -> '目前数量'
        all_num -> '总数量'
        update_time ->使用的时候更新
        action_time ->使用的时候更新
    判断:
        state = 0, goods_num = 1, all_num =1  可使用
        state = 1, goods_num = 1, all_num =1  已使用
        state = 1, goods_num = 2, all_num =2  已装备，多余的，不可重复使用
    顶用：
    """
    flag = False
    back_equipment = sql_message.get_item_by_good_id_and_user_id(user_id, goods_id)
    if back_equipment.state == 0:
        flag = True
    return flag

def get_use_equipment_sql(user_id, goods_id):
    """
    使用装备
    返回sql，和法器或防具
    """
    sql_str = []
    item_info = items.get_data_by_item_id(goods_id)
    user_buff_info = UserBuffDate(user_id).BuffInfo
    now_time = datetime.now()
    item_type = ''
    if item_info['item_type'] == "法器":
        item_type = "法器"
        in_use_id = user_buff_info.faqi_buff
        sql_str.append(f"UPDATE back set update_time='{now_time}',action_time='{now_time}',state=1 WHERE user_id={user_id} and goods_id={goods_id}")#装备
        if in_use_id != 0:
            sql_str.append(f"UPDATE back set update_time='{now_time}',action_time='{now_time}',state=0 WHERE user_id={user_id} and goods_id={in_use_id}")#取下原有的
            
    if item_info['item_type'] == "防具":
        item_type = "防具"
        in_use_id = user_buff_info.armor_buff
        sql_str.append(f"UPDATE back set update_time='{now_time}',action_time='{now_time}',state=1 WHERE user_id={user_id} and goods_id={goods_id}")#装备
        if in_use_id != 0:
            sql_str.append(f"UPDATE back set update_time='{now_time}',action_time='{now_time}',state=0 WHERE user_id={user_id} and goods_id={in_use_id}")#取下原有的
    
    return sql_str, item_type
    

def check_equipment_use_msg(user_id, goods_id):
    """
    检测装备是否已用
    """
    user_back = sql_message.get_item_by_good_id_and_user_id(user_id, goods_id)
    now_num = user_back.goods_num
    all_num = user_back.all_num
    state = user_back.state
    is_use = False
    if state == 0:
        is_use = False
    if state == 1:
        is_use = True
    return is_use

def get_user_back_msg(user_id):
    """
    获取背包内的所有物品信息
    """
    l_equipment_msg = []
    l_skill_msg = []
    l_elixir_msg = []
    l_msg = []
    user_backs = sql_message.get_back_msg(user_id) #list(back)
    if user_backs == None:
        return l_msg
    for user_back in user_backs:
        if user_back.goods_type == "装备":
            l_equipment_msg = get_equipment_msg(l_equipment_msg, user_id, user_back.goods_id, user_back.goods_num)
        elif user_back.goods_type == "技能":
            l_skill_msg = get_skill_msg(l_skill_msg, user_id, user_back.goods_id, user_back.goods_num)
        elif user_back.goods_type == "丹药":
            l_elixir_msg = get_elixir_msg(l_elixir_msg, user_back.goods_id, user_back.goods_num)
    if l_equipment_msg != []:
        l_msg.append("☆------装备------☆")
        for msg in l_equipment_msg:
            l_msg.append(msg)
    
    if l_skill_msg != []:
        l_msg.append("☆------技能------☆")
        for msg in l_skill_msg:
            l_msg.append(msg)
    
    if l_elixir_msg != []:
        l_msg.append("☆------丹药------☆")
        for msg in l_elixir_msg:
            l_msg.append(msg)
    
    return l_msg

def get_equipment_msg(l_msg, user_id, goods_id, goods_num):
    """
    获取背包内的装备信息
    """
    item_info = items.get_data_by_item_id(goods_id)
    
    if item_info['item_type'] == '防具':
        msg = get_armor_info_msg(goods_id, item_info)
    elif item_info['item_type'] == '法器':
        msg = get_weapon_info_msg(goods_id, item_info)
    msg += f"\n拥有数量：{goods_num}"
    is_use = check_equipment_use_msg(user_id, goods_id)
    if is_use:
        msg += f"\n已装备"
    else:
        msg += f"\n可装备"
    l_msg.append(msg)
    return l_msg

def get_skill_msg(l_msg, user_id, goods_id, goods_num):
    """
    获取背包内的技能信息
    """
    item_info = items.get_data_by_item_id(goods_id)
    
    if item_info['item_type'] == '神通':
        msg = f"{item_info['level']}神通-{item_info['name']}："
        msg += get_sec_msg(item_info)
    elif item_info['item_type'] == '功法':
        msg = f"{item_info['level']}功法-"
        msg += get_main_info_msg(goods_id)[1]
    msg += f"\n拥有数量：{goods_num}"
    l_msg.append(msg)
    return l_msg

def get_elixir_msg(l_msg, goods_id, goods_num):
    """
    获取背包内的丹药信息
    """
    item_info = items.get_data_by_item_id(goods_id)
    msg = f"名字：{item_info['name']}\n"
    msg +=f"效果：{item_info['desc']}\n"
    msg += f"拥有数量：{goods_num}"
    l_msg.append(msg)
    return l_msg

def get_item_msg(goods_id):
    """
    获取单个物品的消息
    """
    item_info = items.get_data_by_item_id(goods_id)
    if item_info['type'] == '丹药':
        msg = f"名字：{item_info['name']}\n"
        msg +=f"效果：{item_info['desc']}"
        
    elif item_info['item_type'] == '神通':
        msg = f"名字：{item_info['name']}\n"
        msg += f"品阶：{item_info['level']}\n"
        msg += f"效果：{get_sec_msg(item_info)}"
    
    elif item_info['item_type'] == '功法':
        msg = f"名字：{item_info['name']}\n"
        msg += f"品阶：{item_info['level']}\n"
        msg += f"效果：{get_main_info_msg(goods_id)[1]}"
        
    
    elif item_info['item_type'] == '防具':
        msg = get_armor_info_msg(goods_id, item_info)
        
    elif item_info['item_type'] == '法器':
        msg = get_weapon_info_msg(goods_id, item_info)
    return msg


def get_shop_data(group_id):
    try:
        data = read_shop()
    except:
        data = {}
    try:
        data[group_id]
    except:
        data[group_id] = {}
    save_shop(data)
    return data

PATH = Path(__file__).parent
FILEPATH = PATH / 'shop.json'
def read_shop():
    with open(FILEPATH, "r", encoding="UTF-8") as f:
        data = f.read()
    return json.loads(data)


def save_shop(data):
    data = json.dumps(data, ensure_ascii=False, indent=4)
    savemode = "w" if os.path.exists(FILEPATH) else "x"
    with open(FILEPATH, mode=savemode, encoding="UTF-8") as f:
        f.write(data)
    return True