import json
import os
from pathlib import Path
from .item_json import Items

from .xiuxian2_handle import XiuxianDateManage


READPATH = Path() / "data" / "xiuxian" 
SKILLPATHH = READPATH / "功法"
WEAPONPATH = READPATH / "装备"

items = Items()
class BuffJsonDate:

    def __init__(self):
        """json文件路径"""
        self.mainbuff_jsonpath = SKILLPATHH / "主功法.json"
        self.secbuff_jsonpath = SKILLPATHH / "神通.json"
        self.gfpeizhi_jsonpath = SKILLPATHH / "功法概率设置.json"
        self.weapon_jsonpath = WEAPONPATH / "法器.json"
        self.armor_jsonpath = WEAPONPATH / "防具.json"
    
    def get_main_buff(self, id):
        return readf(self.mainbuff_jsonpath)[str(id)]
    
    def get_sec_buff(self, id):
        return readf(self.secbuff_jsonpath)[str(id)]
    
    def get_gfpeizhi(self):
        return readf(self.gfpeizhi_jsonpath)
    
    def get_weapon_data(self):
        return readf(self.weapon_jsonpath)
    
    def get_weapon_info(self, id):
        return readf(self.weapon_jsonpath)[str(id)]
    
    def get_armor_data(self):
        return readf(self.armor_jsonpath)
    
    def get_armor_info(self, id):
        return readf(self.armor_jsonpath)[str(id)]
        
    
    
class UserBuffDate:
    
    def __init__(self, user_id):
        """用户Buff数据"""
        self.user_id = user_id
        self.BuffInfo = get_user_buff(self.user_id)
        
    
    
    def get_user_main_buff_data(self):
        try:
            main_buff_data = items.get_data_by_item_id(self.BuffInfo.main_buff)
        except:
            main_buff_data = None
        return main_buff_data
    
    def get_user_sec_buff_data(self):
        try:
            sec_buff_data = items.get_data_by_item_id(self.BuffInfo.sec_buff)
        except:
            sec_buff_data = None
        return sec_buff_data

    def get_user_weapon_data(self):
        try:
            weapon_data = items.get_data_by_item_id(self.BuffInfo.faqi_buff)
        except:
            weapon_data = None
        return weapon_data
    
    def get_user_armor_buff_data(self):
        try:
            armor_buff_data = items.get_data_by_item_id(self.BuffInfo.armor_buff)
        except:
            armor_buff_data = None
        return armor_buff_data



def get_weapon_info_msg(weapon_id, weapon_info=None):
    """
    获取一个法器(武器)信息msg
    :param weapon_id：法器(武器)ID
    :param weapon_info：法器(武器)信息json，可不传
    :return 法器(武器)信息msg
    """
    msg = ''
    if weapon_info == None:
        weapon_info = items.get_data_by_item_id(weapon_id)
    atk_buff_msg = f"提升{int(weapon_info['atk_buff'] * 100)}%攻击力！" if weapon_info['atk_buff'] != 0 else ''
    crit_buff_msg = f"提升{int(weapon_info['crit_buff'] * 100)}%会心率！" if weapon_info['crit_buff'] != 0 else ''
    msg += f"名字：{weapon_info['name']}\n"
    msg += f"品阶：{weapon_info['level']}\n"
    msg += f"效果：{atk_buff_msg}{crit_buff_msg}"
    return  msg

def get_armor_info_msg(armor_id, armor_info=None):
    """
    获取一个法宝(防具)信息msg
    :param armor_id：法宝(防具)ID
    :param armor_info：法宝(防具)信息json，可不传
    :return 法宝(防具)信息msg
    """
    msg = ''
    if armor_info == None:
        armor_info = items.get_data_by_item_id(armor_id)
    def_buff_msg = f"提升{int(armor_info['def_buff'] * 100)}%减伤率！"
    msg += f"名字：{armor_info['name']}\n"
    msg += f"品阶：{armor_info['level']}\n"
    msg += f"效果：{def_buff_msg}"
    return  msg

def get_main_info_msg(id):
    mainbuff = items.get_data_by_item_id(id)
    hpmsg = f"提升{round(mainbuff['hpbuff'] * 100, 0)}%气血" if mainbuff['hpbuff'] != 0 else ''
    mpmsg = f"提升{round(mainbuff['mpbuff'] * 100, 0)}%真元" if mainbuff['mpbuff'] != 0 else ''
    atkmsg = f"提升{round(mainbuff['atkbuff'] * 100, 0)}%攻击力" if mainbuff['atkbuff'] != 0 else ''
    ratemsg = f"提升{round(mainbuff['ratebuff'] * 100, 0)}%修炼速度" if mainbuff['ratebuff'] != 0 else ''
    msg = f"{mainbuff['name']}：{hpmsg},{mpmsg},{atkmsg},{ratemsg}。"
    return mainbuff, msg


def get_user_buff(user_id):
    BuffInfo = XiuxianDateManage().get_user_buff_info(user_id)
    if BuffInfo == None:
        XiuxianDateManage().initialize_user_buff_info(user_id)
        return XiuxianDateManage().get_user_buff_info(user_id)
    else:
        return BuffInfo


def readf(FILEPATH):
    with open(FILEPATH, "r", encoding="UTF-8") as f:
        data = f.read()
    return json.loads(data)
    
def get_sec_msg(secbuffdata):
    if secbuffdata == None:
        msg = "无"
        return msg
    hpmsg = f"，消耗当前血量{int(secbuffdata['hpcost'] * 100)}%" if secbuffdata['hpcost'] != 0 else ''
    mpmsg = f"，消耗真元{int(secbuffdata['mpcost'] * 100)}%" if secbuffdata['mpcost'] != 0 else ''

    if secbuffdata['skill_type'] == 1:
        shmsg = ''
        for value in secbuffdata['atkvalue']:
            shmsg += f"{value}倍、"
        if secbuffdata['turncost'] == 0:
            msg = f"攻击{len(secbuffdata['atkvalue'])}次，造成{shmsg[:-1]}伤害{hpmsg}{mpmsg}，释放概率：{secbuffdata['rate']}%"
        else:
            msg = f"连续攻击{len(secbuffdata['atkvalue'])}次，造成{shmsg[:-1]}伤害{hpmsg}{mpmsg}，休息{secbuffdata['turncost']}回合，释放概率：{secbuffdata['rate']}%"
    elif secbuffdata['skill_type'] == 2:
        msg = f"持续伤害，造成{secbuffdata['atkvalue']}倍攻击力伤害{hpmsg}{mpmsg}，持续{secbuffdata['turncost']}回合，释放概率：{secbuffdata['rate']}%"
    elif secbuffdata['skill_type'] == 3:
        if secbuffdata['bufftype'] == 1:
            msg = f"增强自身，提高{secbuffdata['buffvalue']}倍攻击力{hpmsg}{mpmsg}，持续{secbuffdata['turncost']}回合，释放概率：{secbuffdata['rate']}%"
        elif secbuffdata['bufftype'] == 2:
            msg = f"增强自身，提高{secbuffdata['buffvalue'] * 100}%减伤率{hpmsg}{mpmsg}，持续{secbuffdata['turncost']}回合，释放概率：{secbuffdata['rate']}%"
    elif secbuffdata['skill_type'] == 4:
        msg = f"封印对手{hpmsg}{mpmsg}，持续{secbuffdata['turncost']}回合，释放概率：{secbuffdata['rate']}%，命中成功率{secbuffdata['success']}%"

    return msg


PLAYERSDATA = Path() / "data" / "xiuxian" / "players"
def get_player_info(user_id, info_name):
    if info_name == "mix_elixir_info":#灵田信息
        mix_elixir_infoconfigkey = ["收取时间", "收取等级", "灵田数量", '药材速度', "丹药控火", "丹药耐药性", "炼丹记录", "炼丹经验"]
        MIXELIXIRINFOCONFIG = {
            "收取时间":0,
            "收取等级":0,
            "灵田数量":1,
            '药材速度':0,
            "丹药控火":0,
            "丹药耐药性":0,
            "炼丹记录":{},
            "炼丹经验":0
        }
        try:
            player_info = read_player_info(user_id, info_name)
            for key in mix_elixir_infoconfigkey:
                if key not in list(player_info.keys()):
                    player_info[key] = MIXELIXIRINFOCONFIG[key]
            save_player_info(user_id, player_info, info_name)
        except:
            player_info = MIXELIXIRINFOCONFIG
            save_player_info(user_id, player_info, info_name)
    return player_info

def read_player_info(user_id, info_name):
    user_id = str(user_id)
    FILEPATH = PLAYERSDATA / user_id / f"{info_name}.json"
    with open(FILEPATH, "r", encoding="UTF-8") as f:
        data = f.read()
    return json.loads(data)

def save_player_info(user_id, data, info_name):
    user_id = str(user_id)
    
    if not os.path.exists(PLAYERSDATA / user_id):
        print("目录不存在，创建目录")
        os.makedirs(PLAYERSDATA / user_id)
    
    FILEPATH = PLAYERSDATA / user_id / f"{info_name}.json"
    data = json.dumps(data, ensure_ascii=False, indent=4)
    save_mode = "w" if os.path.exists(FILEPATH) else "x"
    with open(FILEPATH, mode=save_mode, encoding="UTF-8") as f:
        f.write(data)