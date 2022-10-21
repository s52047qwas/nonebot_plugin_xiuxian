import json
import os
from pathlib import Path

from .xiuxian2_handle import XiuxianDateManage


READPATH = Path() / "data" / "xiuxian" / "功法"
class BuffJsonDate:

    def __init__(self):
        """json文件路径"""
        self.mainbuff_jsonpath = READPATH / "主功法.json"
        self.secbuff_jsonpath = READPATH / "神通.json"
        self.gfpeizhi_jsonpath = READPATH / "功法概率设置.json"
    
    def get_main_buff(self, id):
        return readf(self.mainbuff_jsonpath)[id]
    
    def get_sec_buff(self, id):
        return readf(self.secbuff_jsonpath)[id]
    
    def get_gfpeizhi(self):
        return readf(self.gfpeizhi_jsonpath)
    
    
class UserBuffDate:
    
    def __init__(self, user_id):
        """用户Buff数据"""
        self.user_id = user_id
        self.BuffInfo = get_user_buff(self.user_id)
        
    
    
    def get_user_main_buff_data(self):
        try:
            mainbuffdata = BuffJsonDate().get_main_buff(str(self.BuffInfo.main_buff))
        except:
            mainbuffdata = None
        return mainbuffdata
    
    def get_user_sec_buff_data(self):
        try:
            secbuffdata = BuffJsonDate().get_sec_buff(str(self.BuffInfo.sec_buff))
        except:
            secbuffdata = None
        return secbuffdata


def get_main_info_msg(id):
    mainbuff = BuffJsonDate().get_main_buff(id)
    hpmsg = f"提升{mainbuff['hpbuff'] * 100}%气血" if mainbuff['hpbuff'] != 0 else ''
    mpmsg = f"提升{mainbuff['mpbuff'] * 100}%真元" if mainbuff['mpbuff'] != 0 else ''
    atkmsg = f"提升{mainbuff['atkbuff'] * 100}%攻击力" if mainbuff['atkbuff'] != 0 else ''
    ratemsg = f"提升{mainbuff['ratebuff'] * 100}%修炼速度" if mainbuff['ratebuff'] != 0 else ''
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


    



