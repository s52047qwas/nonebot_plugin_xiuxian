import random
from collections import namedtuple
from pathlib import Path
from ..data_source import JsonDate
from ..xiuxian_config import XiuConfig
from ..xiuxian2_handle import *
from .reward_data_source import *
import json
from .workmake import *

DATABASE =Path() / "data" / "xiuxian"

xiuxian_data = namedtuple("xiuxian_data", ["no", "user_id", "linggen", "level"])

UserDate = namedtuple("UserDate",
                      ["id", "user_id", "stone", "root", "root_type", "level", "power", "create_time", "is_sign", "exp",
                       "user_name", "level_up_cd", "level_up_rate"])
UserCd = namedtuple("UserCd", [ "user_id", "type", "create_time", "scheduled_time"])

num = '578043031'

class workhandle(XiuxianJsonDate):
    
    
    def do_work(self,key,work_list=None,name=None,level="江湖好手", exp=None, user_id=None):
        """悬赏令获取"""
        # with open(self.do_work_jsonpath, 'r', encoding='utf-8') as e:
        #     a = e.read()
        #     data = json.loads(a)
        
        # jsondata = reward()
        # data = jsondata.reward_that_data()
        # data = data[level]#获取对应境界的任务，默认江湖好手 
        # print("111",data)
        # print(type(data))
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
            
            # for i in data:
            #     try:
            #         return data[i][name]['time']
            #     except:
            #         pass

        elif key == 2:   # 如果是结算，则获取结果
            # work_event = None
            
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
            
            # for i, v in data.items():
            #     for vk, vv in v.items():
            #         if vk == work_list:
            #             work_event = vv
            
            # rate = int(exp / work_event["needexp"] * 100)  #根据修为计算成功率
            # print(rate)
            # bigsuc = False
            # if rate >= 100:
            #     bigsuc = True
            
            # if random.randint(1, 100) <= rate:
            #     return random.choice(work_event["succeed"]), work_event["succeed_thank"], random.choice(work_event["spoils"]), bigsuc
            # else:
            #     return random.choice(work_event["fail"]), work_event["fail_thank"], False, bigsuc
            
            # if random.randint(1, 100) <= work_event["rate"]:
            #     return random.choice(work_event["succeed"]), work_event["succeed_thank"]
            # else:
            #     return random.choice(work_event["fail"]), work_event["fail_thank"]
            
            
