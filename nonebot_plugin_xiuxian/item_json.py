import json
import os
from pathlib import Path

READPATH = Path() / "data" / "xiuxian" 
SKILLPATHH = READPATH / "功法"
WEAPONPATH = READPATH / "装备"

class Items:
    def __init__(self) -> None:
        self.mainbuff_jsonpath = SKILLPATHH / "主功法.json"
        self.secbuff_jsonpath = SKILLPATHH / "神通.json"
        self.weapon_jsonpath = WEAPONPATH / "法器.json"
        self.armor_jsonpath = WEAPONPATH / "防具.json"
        self.items = {}
        self.set_item_data(self.get_armor_data(), "装备")
        self.set_item_data(self.get_weapon_data(), "装备")
        self.set_item_data(self.get_main_buff_data(), "技能")
        self.set_item_data(self.get_sec_buff_data(), "技能")
        self.savef(self.items)
    
    def readf(FILEPATH):
        with open(FILEPATH, "r", encoding="UTF-8") as f:
            data = f.read()
        return json.loads(data)
    
    def savef(data):
        FILEPATH = Path() / "data" / "xiuxian" / "items.json"
        data = json.dumps(data, ensure_ascii=False, indent=4)
        save_mode = "w" if os.path.exists(FILEPATH) else "x"
        with open(FILEPATH, mode=save_mode, encoding="UTF-8") as f:
            f.write(data)
            f.close

    def get_armor_data(self):
        return self.readf(self.armor_jsonpath)

    def get_weapon_data(self):
        return self.readf(self.weapon_jsonpath)

    def get_main_buff_data(self):
        return self.readf(self.mainbuff_jsonpath)

    def get_sec_buff_data(self):
        return self.readf(self.secbuff_jsonpath)
    
    def get_data_by_item_id(self, item_id):
        return self.items[item_id]

    def set_item_data(self, dict_data, item_type):
        for k, v in dict_data.items():
            if item_type == "技能":
                v['rank'], v['level'] = v['level'], v['rank']
            self.items[k] = v
            self.items[k].update({'item_type':item_type})
        
    