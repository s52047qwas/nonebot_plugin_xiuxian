from .reward_data_source import *
import random
from ..item_json import Items
from ..xiuxian_config import USERRANK
from ..xiuxian2_handle import OtherSet

def workmake(work_level, exp, user_level):
    if work_level == '江湖好手':
        work_level = '江湖好手'
    else:
        work_level = work_level[:3]#取境界前3位，补全初期、中期、圆满任务可不取

    jsondata = reward()
    item_s = Items()
    yaocai_data = jsondata.reward_yaocai_data()
    levelpricedata = jsondata.reward_levelprice_data()
    ansha_data = jsondata.reward_ansa_data()
    zuoyao_data = jsondata.reward_zuoyao_data()
    work_json = {}
    work_list = [yaocai_data[work_level], ansha_data[work_level], zuoyao_data[work_level]]
    i = 1
    for w in work_list:
        work_name_list = []
        for k, v in w.items():
            work_name_list.append(k)
        work_name = random.choice(work_name_list)
        work_info = w[work_name]
        level_price_data = levelpricedata[work_level][work_info['level']]

        rate, isOut = countrate(exp, level_price_data["needexp"])
        success_msg = work_info['succeed']
        fail_msg = work_info['fail']
        item_type = get_random_item_type()
        item_id = item_s.get_random_id_list_by_rank_and_item_type(USERRANK[user_level], item_type)
        if item_id == []:
            item_id = 0
        else:
            item_id = random.choice(item_id)

        ## 每15分钟结算一次基础灵石奖励
        work_json[work_name] = [rate, int(level_price_data["award"] * level_price_data["time"] / 15), int(level_price_data["time"] * isOut), item_id, success_msg, fail_msg]
        i += 1
    return work_json

def get_random_item_type():
    type_rate = {
        "功法":{
            "type_rate":100,
        },
        "神通":{
            "type_rate":100,
        },
        "药材":{
            "type_rate":1000,
        }
    }
    temp_dict = {}
    for i, v in type_rate.items():
        try:
            temp_dict[i] = v["type_rate"]
        except:
            continue
    key = []
    key.append(OtherSet().calculated(temp_dict))
    return key

def countrate(exp, needexp):
    rate = int(exp / needexp * 100)
    isOut = 1
    if rate >= 100:
        i = 1
        flag = True
        while(flag):
            r = exp / needexp * 100
            if r > 100:
                i += 1
                exp /= 1.5
            else:
                flag = False
                
        rate = 100
        isOut = float(1 - i * 0.05)
        if isOut < 0.5:
            isOut = 0.5
    return rate, round(isOut, 2)
