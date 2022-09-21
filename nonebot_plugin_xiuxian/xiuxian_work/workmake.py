import os
from .reward_data_source import *
import random

readpath  =os.path.join(os.path.dirname(os.path.realpath(__file__)), 'userworkdata') 

def workmake(level, exp):
    jsondata = reward()
    yaocaidata = jsondata.reward_yaocai_data()
    levelpricedata = jsondata.reward_levelprice_data()
    anshadata = jsondata.reward_ansa_data()
    zuoyaodata = jsondata.reward_zuoyao_data()
    spoilsdata = jsondata.reward_spoils_data()
    
    yaocaidata_name = random.choice(yaocaidata[level])
    levelpricedata_temp = random.choice(levelpricedata[level])
    spoilsdata_temp = random.choice(spoilsdata[level])
    rate = countrate(exp, levelpricedata_temp["needexp"])
    workjson = {}
    
    print(f'1、寻找{yaocaidata_name},完成几率{rate},报酬{levelpricedata_temp["award"]}灵石,预计需{levelpricedata_temp["time"]}分钟,可能获取额外{spoilsdata_temp}')
    
    workjson[yaocaidata_name] = [rate, levelpricedata_temp["award"], levelpricedata_temp["time"], spoilsdata_temp]
    
    levelpricedata_temp = random.choice(levelpricedata[level])
    zuoyaodata_name = random.choice(zuoyaodata[level])
    rate = countrate(exp, levelpricedata_temp["needexp"])
    spoilsdata_temp = random.choice(spoilsdata[level])
    
    print(f'2、捕捉{zuoyaodata_name},完成几率{rate},报酬{levelpricedata_temp["award"]}灵石,预计需{levelpricedata_temp["time"]}分钟,可能获取额外{spoilsdata_temp}')
    
    workjson[zuoyaodata_name] = [rate, levelpricedata_temp["award"], levelpricedata_temp["time"], spoilsdata_temp]
    
    levelpricedata_temp = random.choice(levelpricedata[level])
    anshadata_name = random.choice(anshadata[level])
    rate = countrate(exp, levelpricedata_temp["needexp"])
    spoilsdata_temp = random.choice(spoilsdata[level])
    
    print(f'3、{anshadata_name},完成几率{rate},报酬{levelpricedata_temp["award"]}灵石,预计需{levelpricedata_temp["time"]}分钟,可能获取额外{spoilsdata_temp}')
    
    workjson[anshadata_name] = [rate, levelpricedata_temp["award"], levelpricedata_temp["time"], spoilsdata_temp]
    
    jsondata = json.dumps(workjson, ensure_ascii=False)
    
    return workjson

def countrate(exp, needexp):
    rate = int(exp / needexp * 100)
    if rate >= 100:
        rate = 100
    return rate    

def readf(user_id):
    with open(os.path.join(readpath, f"{user_id}.json"), "r", encoding="UTF-8") as f:
        data = f.read()
    return json.loads(data)

def savef(user_id, data):
    savemode = "w" if os.path.exists(os.path.join(readpath, f"{user_id}.json")) else "x"
    with open(os.path.join(readpath, f"{user_id}.json"), mode=savemode, encoding="UTF-8") as f:
        f.write(data)
        f.close
    return True
