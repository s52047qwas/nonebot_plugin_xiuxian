from ..data_source import *
import os



WORKDATA = Path() / "data" / "xiuxian" / "work"

class reward(JsonDate):
    
    def __init__(self):
        self.Reward_ansa_jsonpath = WORKDATA / "暗杀.json"
        self.Reward_levelprice_jsonpath = WORKDATA / "等级奖励稿.json"
        self.Reward_yaocai_jsonpath = WORKDATA / "灵材.json"
        self.Reward_zuoyao_jsonpath = WORKDATA / "镇妖.json"
        
    def reward_ansa_data(self):
        """获取暗杀名单信息"""
        with open(self.Reward_ansa_jsonpath, 'r', encoding='utf-8') as e:
            file_data = e.read()
            data = json.loads(file_data)
            return data
        
    def reward_levelprice_data(self):
        """获取等级奖励信息"""
        with open(self.Reward_levelprice_jsonpath, 'r', encoding='utf-8') as e:
            file_data = e.read()
            data = json.loads(file_data)
            return data
        
    def reward_yaocai_data(self):
        """获取药材信息"""
        with open(self.Reward_yaocai_jsonpath, 'r', encoding='utf-8') as e:
            file_data = e.read()
            data = json.loads(file_data)
            return data
        
    def reward_zuoyao_data(self):
        """获取捉妖信息"""
        with open(self.Reward_zuoyao_jsonpath, 'r', encoding='utf-8') as e:
            file_data = e.read()
            data = json.loads(file_data)
            return data
        

PLAYERSDATA = Path() / "data" / "xiuxian" / "players"
def readf(user_id):
    user_id = str(user_id)
    
    FILEPATH = PLAYERSDATA / user_id / "workinfo.json"
    with open(FILEPATH, "r", encoding="UTF-8") as f:
        data = f.read()
    return json.loads(data)

def savef(user_id, data):
    user_id = str(user_id)
    
    if not os.path.exists(PLAYERSDATA / user_id):
        print("目录不存在，创建目录")
        os.makedirs(PLAYERSDATA / user_id)
    
    FILEPATH = PLAYERSDATA / user_id / "workinfo.json"
       
    savemode = "w" if os.path.exists(FILEPATH) else "x"
    with open(FILEPATH, mode=savemode, encoding="UTF-8") as f:
        f.write(data)
        f.close
    return True