import random
from ..xiuxian2_handle import *
from .reward_data_source import *
import json
from .workmake import *

class workhandle(XiuxianJsonDate):
    
    
    def do_work(self,key,work_list=None,name=None,level="江湖好手", exp=None, user_id=None):
        """悬赏令获取"""
        if key == 0:   # 如果没有获取过，则返回悬赏令
            data = workmake(level, exp)
            get_work_list = []
            for k, v in data.items():
                
                get_work_list.append([k, v[0], v[1], v[2], v[3]])
                
                # name = random.choice(list(data[i].keys()))
                # # get_work_list.append([name, data[i][name]["rate"], data[i][name]["succeed_thank"], data[i][name]["time"]])
                # get_work_list.append([name, int(exp / data[i][name]["needexp"] * 100) , data[i][name]["succeed_thank"], data[i][name]["time"], data[i][name]["spoils"]])
                
            savef(user_id,json.dumps(data, ensure_ascii=False))
            return get_work_list

        if key == 1:  ##返回对应的悬赏令信息
            try:
                data = readf(user_id)
                return data[name][2]
            except:
                pass
            

        elif key == 2:   # 如果是结算，则获取结果
            
            data = readf(user_id)
            
            bigsuc = False
            if data[work_list][0] >= 100:
                bigsuc = True
                
            successstr = '悬赏成功了！'
            failstr = '悬赏失败了。。'
                
            if random.randint(1, 100) <= data[work_list][0]:
                return successstr, data[work_list][1], data[work_list][3], bigsuc
            else:
                return failstr, int(data[work_list][1] / 2), False, bigsuc
            
            
            
