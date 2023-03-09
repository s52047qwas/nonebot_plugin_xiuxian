import json
import os
from pathlib import Path

configkey = [
    "LEVLECOST", 
    "等级建设度", 
    "发放宗门资材", 
    "每日宗门任务次上限", 
    "宗门任务完成cd", 
    "宗门任务刷新cd", 
    "宗门任务",
    "宗门主功法参数",
    "宗门神通参数",
    "宗门丹房参数"
    ]
CONFIG = {
    "LEVLECOST" : {
    #攻击修炼的灵石消耗
    '0':1000,
    '1':2000,
    '2':4000,
    '3':8000,
    '4':16000,
    '5':32000,
    '6':50000,
    '7':50000,
    '8':50000,
    '9':50000,
    '10':100000,
    '11':100000,
    '12':100000,
    '13':100000,
    '14':100000,
    '15':100000,
    '16':100000,
    '17':100000,
    '18':100000,
    '19':100000,
    '20':200000,
    '21':200000,
    '22':200000,
    '23':200000,
    '24':200000,
    '25':0,
    },
    "等级建设度":500000,#决定宗门修炼上限等级的参数，500万贡献度每级
    "发放宗门资材":{
        "时间":"11-12",#定时任务发放宗门资材，每日11-12点根据 对应宗门贡献度的 * 倍率 发放资材
        "倍率":1,#倍率
    },
    "每日宗门任务次上限":3,
    "宗门任务完成cd":1800,#宗门任务每次完成间隔，单位秒
    "宗门任务刷新cd":300,#宗门任务刷新间隔，单位秒
    "宗门主功法参数":{
        "获取消耗的资材":600000,#最终消耗会乘档位
        "获取消耗的灵石":30000,#最终消耗会乘档位
        "获取到功法的概率":100,
        "建设度":10000000,#建设度除以此参数，一共10档（10档目前无法配置,对应天地玄黄人上下）
        "学习资材消耗":600000,#最终消耗会乘档位
    },
    "宗门神通参数":{
        "获取消耗的资材":600000,#最终消耗会乘档位
        "获取消耗的灵石":30000,#最终消耗会乘档位
        "获取到神通的概率":100,
        "建设度":10000000,#建设度除以此参数，一共10档（10档目前无法配置,对应天地玄黄人上下）
        "学习资材消耗":600000,#最终消耗会乘档位
    },
    "宗门丹房参数":{
        "领取贡献度要求":50000,
        "elixir_room_level":{
            "1":{
                "name":"黄级",
                "level_up_cost":{
                    "建设度":30000000,#升级消耗建设度
                    "stone":200000 #升级消耗宗门灵石
                },
                "give_level":{
                    "give_num":1,#每日领取的丹药数量
                    "rank_up":1#rank增幅等级，影响丹药获取品质，目前高于6会无法获得丹药
                }
            },
            "2":{
                "name":"玄级",
                "level_up_cost":{
                    "建设度":80000000,
                    "stone":400000
                },
                "give_level":{
                    "give_num":1,
                    "rank_up":1
                }
            },
            "3":{
                "name":"地级",
                "level_up_cost":{
                    "建设度":150000000,
                    "stone":800000
                },
                "give_level":{
                    "give_num":2,
                    "rank_up":1
                }
            },
            "4":{
                "name":"天级",
                "level_up_cost":{
                    "建设度":250000000,
                    "stone":1600000
                },
                "give_level":{
                    "give_num":3,
                    "rank_up":1
                }
            },
            "5":{
                "name":"仙级",
                "level_up_cost":{
                    "建设度":400000000,
                    "stone":3200000
                },
                "give_level":{
                    "give_num":4,
                    "rank_up":1
                }
            }
        }
        
    },
    "宗门任务":{
        #type=1：需要扣气血，type=2：需要扣灵石
        #cost：消耗，type=1时，气血百分比，type=2时，消耗灵石
        #give：给与玩家当前修为的百分比修为
        #sect：给与所在宗门 储备的灵石，同时会增加灵石 * 10 的建设度
            "狩猎邪修": {
         "desc": "传言山外村庄有邪修抢夺灵石，请道友下山为民除害",
         "type": 1,
         "cost": 0.35,
         "give": 0.01,
         "sect": 14000
      },
      "查抄窝点": {
         "desc": "有少量弟子不在金银阁消费，私自架设小型窝点，请道友前去查抄",
         "type": 1,
         "cost": 0.25,
         "give": 0.008,
         "sect": 10000
      },
      "九转仙丹": {
         "desc": "山门将开，宗门急缺一批药草熬制九转丹，请道友下山购买",
         "type": 2,
         "cost": 5000,
         "give": 0.01,
         "sect": 15000
      },
      "仗义疏财": {
         "desc": "在宗门外见到师弟欠了别人灵石被追打催债，请道友帮助其还清赌债",
         "type": 2,
         "cost": 4000,
         "give": 0.008,
         "sect": 12000
      },
      "红尘寻宝": {
         "desc": "山下一月一度的市场又开张了，其中虽凡物较多，但是请道友慷慨解囊，为宗门购买一些蒙尘奇宝",
         "type": 2,
         "cost": 6000,
         "give": 0.012,
         "sect": 18000
      }
    }
}

def get_config():
    try:
        config = readf()
        for key in configkey:
            if key not in list(config.keys()):
                config[key] = CONFIG[key]
        savef(config)
    except:
        config = CONFIG
        savef(config)
    return config

CONFIGJSONPATH = Path(__file__).parent
FILEPATH = CONFIGJSONPATH / 'config.json'
def readf():
    with open(FILEPATH, "r", encoding="UTF-8") as f:
        data = f.read()
    return json.loads(data)


def savef(data):
    data = json.dumps(data, ensure_ascii=False, indent=3)
    savemode = "w" if os.path.exists(FILEPATH) else "x"
    with open(FILEPATH, mode=savemode, encoding="UTF-8") as f:
        f.write(data)
        f.close
    return True
