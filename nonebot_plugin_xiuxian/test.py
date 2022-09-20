from pathlib import Path
import json
import random


DATABASE = Path() / "xiuxian"



class JsonDate:
    """处理JSON数据"""

    def __init__(self):
        """json文件路径"""
        self.root_jsonpath = DATABASE / "灵根.json"
        self.level_rate_jsonpath = DATABASE / "突破概率.json"
        self.Reward_that_jsonpath = DATABASE / "悬赏令test.json"
        self.level_jsonpath = DATABASE / "境界.json"
        self.sect_json_pth = DATABASE / "宗门玩法配置.json"

    def level_data(self):
        """境界数据"""
        with open(self.level_jsonpath, 'r', encoding='utf-8') as e:
            a = e.read()
            data = json.loads(a)
            return data

    def sect_config_data(self):
        """宗门玩法配置"""
        with open(self.sect_json_pth, "r", encoding="utf-8") as fp:
            file = fp.read()
            config_data = json.loads(file)
            return config_data

    def root_data(self):
        """获取灵根数据"""
        with open(self.root_jsonpath, 'r', encoding='utf-8') as e:
            file_data = e.read()
            data = json.loads(file_data)
            return data

    def level_rate_data(self):
        """获取境界突破概率"""
        with open(self.level_rate_jsonpath, 'r', encoding='utf-8') as e:
            file_data = e.read()
            data = json.loads(file_data)
            return data

    def reward_that_data(self):
        """获取悬赏令信息"""
        with open(self.Reward_that_jsonpath, 'r', encoding='utf-8') as e:
            file_data = e.read()
            data = json.loads(file_data)
            return data

    def my_test_file(self, pathfile):
        with open(pathfile, 'r', encoding='utf-8') as e:
            file_data = e.read()
            data = json.loads(file_data)
            return data

class reward(JsonDate):
    
    def __init__(self):
        self.Reward_that_jsonpath = DATABASE / "悬赏令test.json"

def do_work(key, work_list=None, name=None, level="江湖好手", exp=None):
        """悬赏令获取"""
        # with open(self.do_work_jsonpath, 'r', encoding='utf-8') as e:
        #     a = e.read()
        #     data = json.loads(a)
        data = reward().reward_that_data()
        data = data[level]#获取对应境界的任务，默认江湖好手 
        # print("111",data)
        # print(type(data))
        if key == 0:   # 如果没有获取过，则返回悬赏令
            get_work_list = []
            for i in data:
                name = random.choice(list(data[i].keys()))
                # get_work_list.append([name, data[i][name]["rate"], data[i][name]["succeed_thank"], data[i][name]["time"]])
                get_work_list.append([name, int(exp / data[i][name]["needexp"] * 100) , data[i][name]["succeed_thank"], data[i][name]["time"], data[i][name]["spoils"]])
            return get_work_list

        if key == 1:  ##返回对应的悬赏令信息
            for i in data:
                try:
                    return data[i][name]['time']
                except:
                    pass

        elif key == 2:   # 如果是结算，则获取结果
            work_event = None
            for i, v in data.items():
                for vk, vv in v.items():
                    if vk == work_list:
                        work_event = vv
            
            rate = int(exp / work_event["needexp"] * 100)  #根据修为计算成功率
            bigsuc = False
            if rate >= 100:
                bigsuc = True
            
            if random.randint(1, 100) <= rate:
                return random.choice(work_event["succeed"]), work_event["succeed_thank"], random.choice(work_event["spoils"]), bigsuc
            else:
                return random.choice(work_event["fail"]), work_event["fail_thank"]
            
work_list = []
work_msg = do_work(0, level="结丹境", exp=90000)
n = 1
work_msg_f = f"""     ✨道友的个人悬赏令✨"""
for i in work_msg:
    if i[1] >= 100:
        i[1] = 100
    work_list.append([i[0], i[3]])
    work_msg_f += f"""
{n}、{i[0]}     完成机率{i[1]}   基础报酬{i[2]}灵石   预计需{i[3]}分钟   可能获取额外战利品{''.join(sp + ' ' for sp in i[4])}"""
    n += 1
    work_msg_f += "\n(悬赏令每小时更新一次)"
    
    # work[user_id].msg = work_msg_f
    # work[user_id].world = work_list
print(work_msg_f)
print(work_list)