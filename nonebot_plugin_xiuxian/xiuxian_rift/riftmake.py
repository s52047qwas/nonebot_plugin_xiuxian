import random

USERRANK = {
    '江湖好手':50,
    '练气境初期':49,
    '练气境中期':48,
    '练气境圆满':47,
    '筑基境初期':46,
    '筑基境中期':45,
    '筑基境圆满':44,
    '结丹境初期':43,
    '结丹境中期':42,
    '结丹境圆满':41,
    '元婴境初期':40,
    '元婴境中期':39,
    '元婴境圆满':38,
    '化神境初期':37,
    '化神境中期':36,
    '化神境圆满':35,
    '炼虚境初期':34,
    '炼虚境中期':33,
    '炼虚境圆满':32,
    '合体境初期':31,
    '合体境中期':30,
    '合体境圆满':29,
    '大乘境初期':28,
    '大乘境中期':27,
    '大乘境圆满':26,
    '渡劫境初期':25,
    '渡劫境中期':24,
    '渡劫境圆满':23,
    '半步真仙':22,
}
STORY = {
    "宝物":{
        "丹药":{
            "name":{
                "筑基丹":{
                    "name":"筑基丹",
                    "rank":44,
                    "id":0,
                },
                "小回血丹":{
                    "name":"小回血丹",
                    "rank":50,
                    "id":0,
                },
                "大回血丹":{
                    "name":"大回血丹",
                    "rank":46,
                    "id":0,
                },
                "修炼丹":{
                    "name":"修炼丹",
                    "rank":50,
                    "id":0,
                },
            }
        },
        "筑基丹":{
            "rank":44,
            "success":"道友在秘境中搜寻了一番，竟获大回血丹一枚！",
            "fail":"道友在秘境中搜寻了一番，竟然毛都没获得！"
        },
        "小回血丹":{
            "rank":50,
            "success":"道友在秘境中搜寻了一番，竟获大回血丹一枚！",
            "fail":"道友在秘境中搜寻了一番，竟然毛都没获得！"
        },
        "大回血丹":{
            "rank":46,
            "success":"道友在秘境中搜寻了一番，竟获大回血丹一枚！",
            "fail":"道友在秘境中搜寻了一番，竟然毛都没获得！"
        },
        "修炼丹":{
            "rank":50,
            "success":"道友在秘境中搜寻了一番，竟获修炼丹一枚！",
            "fail":"道友在秘境中搜寻了一番，竟然毛都没获得！"
        },
    },
    "战斗":{
        "Boss战斗":{
            "Boss数据":{
                "name":["墨蛟","婴鲤兽","千目妖","鸡冠蛟","妖冠蛇","铁火蚁","天晶蚁","银光鼠","紫云鹰","狗青"],
                "hp":10,
                "mp":10,
                "atk":0.2,
            },
            "success":{
                "desc":"道友大战一番成功战胜{}!",
                "give":{
                    "exp":0.05,
                    "stone":20000,
                }
            }

        },
        "掉血事件":{
            "desc":"秘境内竟然散布着浓烈的毒气，道友贸然闯入！",
            "cost":{
                "exp":0.05,
                "hp":0.3,
                "mp":0.3,
                "stone":10000,
            }
        },
    },
    "功法":{},
}

def get_dy_info(user_level, rift_rank):
    """获取丹药事件的信息"""
    user_rank = USERRANK[user_level] #type=int，用户等级
    dy_name = get_dy_by_user_level(user_level, rift_rank)
    dy_info = STORY['丹药']['name'][dy_name]
    init_rate = 40 #初始概率为40
    finall_rate = init_rate + ((dy_info['rank'] - user_rank + rift_rank) * 5)
    finall_rate = finall_rate if finall_rate <= 100 else 100
    is_success = False
    if random.randint(0, 100) <= finall_rate: #成功
        is_success = True
        return is_success, dy_info
    return is_success, dy_info


def get_dy_by_user_level(user_level, rift_rank):
    """根据用户等级随机获取一个丹药"""
    user_rank = USERRANK[user_level]#type=int，用户等级
    dy_name = STORY["宝物"]['丹药']['name']
    get_dy = []#可以获取到丹药的列表
    for k, v in dy_name.items():
        if user_rank - rift_rank <= v['rank']:  #秘境等级会增幅用户等级
            get_dy.append(k)

    return random.choice(get_dy)