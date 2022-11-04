from ..item_json import Items
from ..xiuxian2_handle import XiuxianDateManage
from ..read_buff import UserBuffDate, get_weapon_info_msg, get_armor_info_msg, get_sec_msg, get_main_info_msg
from .backconfig import get_config

items = Items()
sql_message = XiuxianDateManage()



def check_equipment_use(user_id, goods_id):
    """
    检测装备是否可用
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
    user_info = sql_message.get_user_message(user_id)
    user_buff_info = UserBuffDate(user_id).BuffInfo #type(BuffInfo)
    l_equipment_msg = []
    l_skill_msg = []
    l_elixir_msg = []
    l_msg = []
    user_backs = sql_message.get_back_msg(user_id) #list(back)
    for user_back in user_backs:
        if user_back.goods_type == "装备":
            l_equipment_msg = get_equipment_msg(l_equipment_msg, user_id, user_back.goods_id)
        elif user_back.goods_type == "技能":
            l_skill_msg = get_skill_msg(l_skill_msg, user_id, user_back.goods_id)
        elif user_back.goods_type == "丹药":
            #处理丹药信息逻辑
            pass
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

def get_equipment_msg(l_msg, user_id, goods_id):
    """
    获取背包内的装备信息
    """
    item_info = items.get_data_by_item_id(goods_id)
    
    if item_info['item_type'] == '防具':
        msg = get_armor_info_msg(goods_id, item_info)
    elif item_info['item_type'] == '法器':
        msg = get_weapon_info_msg(goods_id, item_info)
        
    is_use = check_equipment_use(user_id, goods_id)
    if is_use:
        msg += f"\n已使用"
    else:
        msg += f"\n可使用"
    l_msg.append(msg)
    return l_msg

def get_skill_msg(l_msg, user_id, goods_id):
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
        
    is_use = check_equipment_use(user_id, goods_id)
    if is_use:
        msg += f"\n已学习"
    else:
        msg += f"\n可学习"
    l_msg.append(msg)
    return l_msg