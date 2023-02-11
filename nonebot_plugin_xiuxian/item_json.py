import json
import os
from pathlib import Path
import random
from typing import List

READPATH = Path() / "data" / "xiuxian" 
SKILLPATHH = READPATH / "功法"
WEAPONPATH = READPATH / "装备"
ELIXIRPATH = READPATH / "丹药"
XIULIANITEMPATH = READPATH / "修炼物品"

class Items:
    def __init__(self) -> None:
        self.mainbuff_jsonpath = SKILLPATHH / "主功法.json"
        self.secbuff_jsonpath = SKILLPATHH / "神通.json"
        self.weapon_jsonpath = WEAPONPATH / "法器.json"
        self.armor_jsonpath = WEAPONPATH / "防具.json"
        self.elixir_jsonpath = ELIXIRPATH / "丹药.json"
        self.yaocai_jsonpath = ELIXIRPATH / "药材.json"
        self.mix_elixir_type_jsonpath = ELIXIRPATH / "炼丹丹药.json"
        self.ldl_jsonpath = ELIXIRPATH / "炼丹炉.json"
        self.jlq_jsonpath = XIULIANITEMPATH / "聚灵旗.json"
        self.items = {}
        self.set_item_data(self.get_armor_data(), "防具")
        self.set_item_data(self.get_weapon_data(), "法器")
        self.set_item_data(self.get_main_buff_data(), "功法")
        self.set_item_data(self.get_sec_buff_data(), "神通")
        self.set_item_data(self.get_elixir_data(), "丹药")
        self.set_item_data(self.get_yaocai_data(), "药材")
        self.set_item_data(self.get_mix_elixir_type_data(), "合成丹药")
        self.set_item_data(self.get_ldl_data(), "炼丹炉")
        self.set_item_data(self.get_jlq_data(), "聚灵旗")
        self.savef(self.items)
    
    def readf(self, FILEPATH):
        with open(FILEPATH, "r", encoding="UTF-8") as f:
            data = f.read()
        return json.loads(data)
    
    def savef(self, data):
        FILEPATH = Path() / "data" / "xiuxian" / "items.json"
        data = json.dumps(data, ensure_ascii=False, indent=4)
        save_mode = "w" if os.path.exists(FILEPATH) else "x"
        with open(FILEPATH, mode=save_mode, encoding="UTF-8") as f:
            f.write(data)

    def get_armor_data(self):
        return self.readf(self.armor_jsonpath)

    def get_weapon_data(self):
        return self.readf(self.weapon_jsonpath)

    def get_main_buff_data(self):
        return self.readf(self.mainbuff_jsonpath)

    def get_sec_buff_data(self):
        return self.readf(self.secbuff_jsonpath)
    
    def get_elixir_data(self):
        return self.readf(self.elixir_jsonpath)

    def get_yaocai_data(self):
        return self.readf(self.yaocai_jsonpath)

    def get_mix_elixir_type_data(self):
        return self.readf(self.mix_elixir_type_jsonpath)
    
    def get_ldl_data(self):
        return self.readf(self.ldl_jsonpath)
    
    def get_jlq_data(self):
        return self.readf(self.jlq_jsonpath)
    
    def get_data_by_item_id(self, item_id):
        return self.items[str(item_id)]

    def set_item_data(self, dict_data, item_type):
        for k, v in dict_data.items():
            if item_type == '功法' or item_type == '神通':
                v['rank'], v['level'] = v['level'], v['rank']
                v['type'] = '技能'
            self.items[k] = v
            self.items[k].update({'item_type':item_type})
            
    def get_data_by_item_type(self, item_type):
        temp_dict = {}
        for k, v in self.items.items():
            if v['item_type'] in item_type:
                temp_dict[k] = v
        return temp_dict
        
    def get_random_id_list_by_rank_and_item_type(
        self, 
        fanil_rank : int, 
        item_type : List = None
        ):
        """
        获取随机一个物品ID，可以指定物品类型，物品等级和用户等级相差6级以上会被抛弃
        :param fanil_rank：用户的最终rank，最终rank由用户rank和rank增幅事件构成
        :param item_type：type：list，物品类型，可以为空，枚举值：法器、防具、神通、功法、丹药
        :return 获得的ID列表，type：list
        """
        l_id = []
        for k, v in self.items.items():
            if item_type != None:
                if v['item_type'] in item_type  and int(v['rank']) >= fanil_rank and int(v['rank']) - fanil_rank <= 6:
                    l_id.append(k)
                else:
                    continue
            else:#全部随机
                if int(v['rank']) >= fanil_rank and int(v['rank']) - fanil_rank <= 9:
                    l_id.append(k)
                else:
                    continue
        return l_id
