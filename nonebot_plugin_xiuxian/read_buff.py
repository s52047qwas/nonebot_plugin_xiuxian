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
        
    
    def get_main_buff(self, id):
        return readf(self.mainbuff_jsonpath)[id]
    
    def get_sec_buff(self, id):
        return readf(self.secbuff_jsonpath)[id]
    
    
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


    



