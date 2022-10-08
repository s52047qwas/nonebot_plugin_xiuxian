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
    workjson = {}
    worklist = [yaocaidata[level], anshadata[level], zuoyaodata[level]]
    i = 1
    for w in worklist:
        workname = random.choice(w)
        levelpricedata_temp = random.choice(levelpricedata[level])
        rate = countrate(exp, levelpricedata_temp["needexp"])
        spoilsdata_temp = random.choice(spoilsdata[level])
        print(f'{i}、寻找{workname},完成几率{rate},报酬{levelpricedata_temp["award"]}灵石,预计需{levelpricedata_temp["time"]}分钟,可能获取额外{spoilsdata_temp}')
        workjson[workname] = [rate, levelpricedata_temp["award"], levelpricedata_temp["time"], spoilsdata_temp]
        i += 1
    
    jsondata = json.dumps(workjson, ensure_ascii=False)
    
    return workjson

def countrate(exp, needexp):
    rate = int(exp / needexp * 100)
    if rate >= 100:
        rate = 100
    return rate    
