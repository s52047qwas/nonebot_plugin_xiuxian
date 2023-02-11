from ..item_json import Items
import json
import os
from pathlib import Path


mix_config = Items().get_data_by_item_type(['合成丹药'])
mix_configs = {}
for k, v in mix_config.items():
    mix_configs[k] = v['elixir_config']






yonhudenji = 0
Llandudno_info = {
    "max_num":10,
    "rank":20
}

async def check_mix(elixir_config):
    is_mix = False
    l_id = []
    # mix_configs = await get_mix_config()
    for k, v in mix_configs.items():#这里是丹药配方
        type_list = []
        for ek, ev in elixir_config.items():#这是传入的值判断
            #传入的丹药config
            type_list.append(ek)
        formula_list = []
        for vk, vv in v.items():#这里是每个配方的值
            formula_list.append(vk)
        if sorted(type_list) == sorted(formula_list):#key满足了
            flag = False
            for typek in type_list:
                if elixir_config[typek] >= v[typek]:
                    flag = True
                    continue
                else:
                    flag = False
                    break
            if flag:
                l_id.append(k)

            continue
        else:
            continue
    id = 0 
    if l_id != []:
        is_mix = True
        id_config = {}
        for id in l_id:
            for k, v in mix_configs[id].items():
                id_config[id] = v
                break
        id = sorted(id_config.items(), key= lambda x: x[1], reverse=True)[0][0]#选出最优解
                
    return is_mix, id

async def get_mix_elixir_msg(yaocai):
    mix_elixir_msg = {}
    num = 0
    for k, v in yaocai.items():#这里是用户所有的药材dict
        i = 1
        while i <= v['num'] and i <= 5:#尝试第一个药材为主药
            # _zhuyao = v['主药']['h_a_c']['type'] * v['主药']['h_a_c']['power'] * i
            for kk, vv in yaocai.items():
                if kk == k:#相同的药材不能同时做药引
                    continue
                o = 1
                while o <= vv['num'] and o <= 5:
                    # _yaoyin = vv['药引']['h_a_c']['type'] * vv['药引']['h_a_c']['power'] * o
                    if await tiaohe(v, i, vv, o):#调和失败
                    # if await absolute(_zhuyao + _yaoyin) > yonhudenji:#调和失败
                        o += 1
                        continue
                    else:
                        elixir_config = {}
                        zhuyao_type = str(v['主药']['type'])
                        zhuyao_power = v['主药']['power'] * i
                        elixir_config[zhuyao_type] = zhuyao_power
                        for kkk, vvv in yaocai.items():
                            p = 1
                            #尝试加入辅药
                            while p <= vvv['num'] and p <= 5:
                                fuyao_type = str(vvv['辅药']['type'])
                                fuyao_power = vvv['辅药']['power'] * p
                                elixir_config = {}
                                zhuyao_type = str(v['主药']['type'])
                                zhuyao_power = v['主药']['power'] * i
                                elixir_config[zhuyao_type] = zhuyao_power
                                elixir_config[fuyao_type] = fuyao_power     
                                # print(elixir_config)         
                                is_mix, id = await check_mix(elixir_config)
                                if is_mix:#有可以合成的
                                    if i + o + p <= Llandudno_info["max_num"]:
                                        
                                        mix_elixir_msg[num] = {}
                                        mix_elixir_msg[num]['id'] = id
                                        mix_elixir_msg[num]['配方'] = elixir_config
                                        mix_elixir_msg[num]['配方简写'] = f"主药{v['name']}{i}药引{vv['name']}{o}辅药{vvv['name']}{p}"
                                        mix_elixir_msg[num]['主药'] = v['name']
                                        mix_elixir_msg[num]['主药_num'] = i
                                        mix_elixir_msg[num]['主药_level'] = v['level']
                                        mix_elixir_msg[num]['药引'] = vv['name']
                                        mix_elixir_msg[num]['药引_num'] = o
                                        mix_elixir_msg[num]['药引_level'] = vv['level']
                                        mix_elixir_msg[num]['辅药'] = vvv['name']
                                        mix_elixir_msg[num]['辅药_num'] = p
                                        mix_elixir_msg[num]['辅药_level'] = vvv['level']
                                        num += 1
                                        p += 1
                                        continue
                                    else:
                                        p += 1
                                        continue
                                else:
                                    p += 1
                                    continue
                            continue    
                    o += 1
            i += 1
    temp_dict = {}
    temp_id_list = []
    finall_mix_elixir_msg = {}
    if mix_elixir_msg == {}:
        return finall_mix_elixir_msg
    for k, v in mix_elixir_msg.items():
        temp_id_list.append(v['id'])
    temp_id_list = set(temp_id_list)
    for id in temp_id_list:
        temp_dict[id] = {}
        for k, v in mix_elixir_msg.items():
            if id == v['id']:
                temp_dict[id][k] = v['主药_num'] + v['药引_num'] + v['辅药_num']
            else:
                continue
        id = sorted(temp_dict[id].items(), key=lambda x: x[1])[0][0]
        finall_mix_elixir_msg[id] = {}
        finall_mix_elixir_msg[id]['id'] = mix_elixir_msg[id]['id']
        finall_mix_elixir_msg[id]['配方'] = mix_elixir_msg[id]

    return finall_mix_elixir_msg

async def absolute(x):
    if x >= 0:
        return x
    else:
        return -x

async def tiaohe(zhuyao_info, zhuyao_num, yaoyin_info, yaoyin_num):
    _zhuyao = zhuyao_info['主药']['h_a_c']['type'] * zhuyao_info['主药']['h_a_c']['power'] * zhuyao_num
    _yaoyin = yaoyin_info['药引']['h_a_c']['type'] * yaoyin_info['药引']['h_a_c']['power'] * yaoyin_num
    
    return await absolute(_zhuyao + _yaoyin) > yonhudenji

CONFIGJSONPATH = Path(__file__).parent
FILEPATH = CONFIGJSONPATH / 'mix_configs.json'
def readf():
    with open(FILEPATH, "r", encoding="UTF-8") as f:
        data = f.read()
    return json.loads(data)


def savef(data):
    data = json.dumps(data, ensure_ascii=False, indent=3)
    savemode = "w" if os.path.exists(FILEPATH) else "x"
    with open(FILEPATH, mode=savemode, encoding="UTF-8") as f:
        f.write(data)
        f.close
    return True