import random
from .riftconfig import get_config
from ..xiuxian2_handle import OtherSet
from .jsondata import read_f
from ..read_buff import BuffJsonDate, get_main_info_msg, get_sec_msg
from ..xiuxian2_handle import XiuxianDateManage
from ..player_fight import Boss_fight

sql_message = XiuxianDateManage()
skill_data = read_f()
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

NONEMSG = [
    "道友在秘境中晕头转向，等到清醒时竟然发现已被秘境踢出，毫无所获！",
    "道友进入秘境发现此地烟雾缭绕，无法前行，只能原路而返空手而归！",
]

TREASUREMSG = [
    "道友进入秘境后搜刮了一番，{}",
    "道友进入秘境后竟然发现了一位前辈坐化于此，{}"
]

STORY = {
    "宝物":{
        "type_rate":300,
        "丹药":{
            "type_rate":40,
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
        "功法":{
            "type_rate":20,
        },
        "神通":{
            "type_rate":20,
        },
        "灵石":{
            "type_rate":80,
            "value":4000 #基础值，会被秘境等级增幅
        },
        "修为":{
            "type_rate":20,
            "value":0.0004 #基础值，会被秘境等级增幅
        }
        # "法器":{
        #     "type_rate":20,
            
        # },
        # "法宝":{
        #     "type_rate":20,
            
        # },
    },
    "战斗":{
        "type_rate":100,
        "Boss战斗":{
            "type_rate":200,
            "Boss数据":{
                "name":["墨蛟","婴鲤兽","千目妖","鸡冠蛟","妖冠蛇","铁火蚁","天晶蚁","银光鼠","紫云鹰","狗青"],
                "hp":[1.2, 1.4, 1.6, 1.8, 2, 3],
                "mp":10,
                "atk":[0.1, 0.12, 0.14, 0.16, 0.18, 0.5],
            },
            "success":{
                "desc":"道友大战一番成功战胜{}!",
                "give":{
                    "exp":[0.01, 0.02, 0.03, 0.04, 0.05],
                    "stone":5000
                }
            },
            "fail":{
                "desc":"道友大战一番不敌{}，仓皇逃窜！",
            }
        },
        "掉血事件":{
            "type_rate":50,
            "desc":[
                "秘境内竟然散布着浓烈的毒气，道友贸然闯入！{}！",
                "秘境内竟然藏着一群未知势力，道友被打劫了！{}！"
                ],
            "cost":{
                "exp":{
                    "type_rate":50,
                    "value":[0.01, 0.02, 0.03]
                },
                "hp":{
                    "type_rate":100,
                    "value":[0.1, 0.2, 0.3]
                },
                "stone":{
                    "type_rate":50,
                    "value":[5000, 10000, 15000]
                },
            }
        },
    },
    "无事":{
        "type_rate":50,
    }
}


def get_boss_battle_info(user_info, rift_rank):
    """获取Boss战事件的内容"""
    boss_data = STORY['战斗']['Boss战斗']["Boss数据"]
    player = {"user_id": None, "道号": None, "气血": None, "攻击": None, "真元": None, '会心': None, '防御': 0}
    userinfo = sql_message.get_user_real_info(user_info.user_id)
    player['user_id'] = userinfo.user_id
    player['道号'] = userinfo.user_name
    player['气血'] = userinfo.hp
    player['攻击'] = userinfo.atk
    player['真元'] = userinfo.mp
    player['会心'] = 0
    player['exp'] = userinfo.exp
    
    base_exp = userinfo.exp
    boss_info = {"name": None, "气血": None, "攻击": None, "真元": None, 'stone':1}
    boss_info["name"] = random.choice(boss_data["name"])
    boss_info["气血"] = int(base_exp * random.choice(boss_data["hp"]))
    boss_info["攻击"] = int(base_exp * random.choice(boss_data["atk"]))
    boss_info["真元"] = base_exp * boss_data["mp"]
    
    result, victor, bossinfo_new, stone = Boss_fight(player, boss_info, 1)#未开启，1不写入，2写入
    dev_msg = '但是没生效捏'#要删掉的
    if victor == player['道号']:#获胜
        user_rank = 50 - USERRANK[user_info.level]#50-用户当前等级
        success_info = STORY['战斗']['Boss战斗']["success"]
        msg = success_info['desc'].format(boss_info["name"])
        give_exp = random.choice(success_info["give"]["exp"]) * user_info.exp
        give_stone = (rift_rank + user_rank) * success_info["give"]["stone"]
        # sql_message.update_exp(user_info.user_id, get_exp)
        # sql_message.update_ls(user_info.user_id, get_stone, 1)#负数也挺正常
        msg += f"获得了修为：{give_exp}点，灵石：{give_stone}枚！{dev_msg}"
    else:#输了
        fail_info = STORY['战斗']['Boss战斗']["fail"]
        msg = fail_info['desc'].format(boss_info["name"])
        msg += f"{dev_msg}"
    return result, msg


def get_dxsj_info(rift_type, user_info):
    """获取掉血事件的内容"""
    battle_data = STORY['战斗']
    cost_type = get_dict_type_rate(battle_data[rift_type]['cost'])
    value = random.choice(battle_data[rift_type]['cost'][cost_type]['value'])
    dev_msg = '但是没生效捏'#要删掉的
    if cost_type == "exp":
        exp = int(user_info.exp * value)
        # sql_message.update_j_exp(user_info.user_id, exp)
        msg = random.choice(battle_data[rift_type]['desc']).format(f"修为减少了：{exp}点！{dev_msg}")
    elif cost_type == "hp":
        cost_hp = int((user_info.exp / 2) * value)
        now_hp = user_info.hp - cost_hp
        if now_hp < 0:
            now_hp = 1
        # sql_message.update_user_hp_mp(user_info.user_id, now_hp, user_info.mp)
        msg = random.choice(battle_data[rift_type]['desc']).format(f"气血减少了：{cost_hp}点！{dev_msg}")#要删掉的
    elif cost_type == "stone":
        cost_stone = value
        # sql_message.update_ls(user_info.user_id, cost_stone, 2)#负数也挺正常
        msg = random.choice(battle_data[rift_type]['desc']).format(f"灵石减少了：{cost_stone}枚！{dev_msg}")#要删掉的
    return msg


def get_treasure_info(user_info, rift_rank):
    user_rank = 50 - USERRANK[user_info.level]#50-用户当前等级
    rift_type = get_goods_type()#功法、神通、灵石、修为、丹药、法器、法宝
    treasure_data = STORY["宝物"]
    dev_msg = '但是没生效捏'#要删掉的
    if rift_type == "灵石":
        ls_data = treasure_data["灵石"]
        give_ls = ls_data["value"] * (rift_rank + user_rank)
        # sql_message.update_ls(user_id, give_ls, 1)
        temp_msg = f"获得了灵石{give_ls}枚！{dev_msg}"
        msg = random.choice(TREASUREMSG).format(temp_msg)
    elif rift_type == "修为":
        exp_data = treasure_data["修为"]
        give_exp = int(user_info.exp * exp_data["value"] * (rift_rank + user_rank))
        # sql_message.update_exp(user_id, give_exp)
        temp_msg = f"有所感悟，修为增加了：{give_exp}点！{dev_msg}"
        msg = random.choice(TREASUREMSG).format(temp_msg)
    elif rift_type == "法器":#todo
        msg = "法器没做好捏"
        
    elif rift_type == "法宝":#todo
        msg = "法宝没做好捏"
        
    elif rift_type == "功法":
        give_main_info = get_main_info(user_info.level, rift_rank)
        if give_main_info[0]:#获得了
            main_buff_id = give_main_info[1]
            main_buff = BuffJsonDate().get_main_buff(main_buff_id)
            temp_msg = f"竟然获得了{main_buff['rank']}功法：{main_buff['name']}！{dev_msg}"
            msg = random.choice(TREASUREMSG).format(temp_msg)
        else:
            msg = '竟空手而归！'
        
    elif rift_type == "神通":
        give_sec_info = get_sec_info(user_info.level, rift_rank)
        if give_sec_info[0]:#获得了
            sec_buff_id = give_sec_info[1]
            sec_buff = BuffJsonDate().get_sec_buff(sec_buff_id)
            temp_msg = f"竟然获得了{sec_buff['rank']}功法：{sec_buff['name']}！{dev_msg}"
            msg = random.choice(TREASUREMSG).format(temp_msg)
        else:
            msg = '竟空手而归！'
        
    elif rift_type == "丹药":
        dy_info = get_dy_info(user_info.level, rift_rank)
        if dy_info[0]:
            dy_info = dy_info[1]
            temp_msg = f"竟然获得了丹药：{dy_info['name']}！丹药id：{dy_info['id']},{dev_msg}"
            msg = random.choice(TREASUREMSG).format(temp_msg)
        else:
            msg = '竟空手而归！'
    return msg

def get_dict_type_rate(data_dict):
    """根据字典内概率，返回字典key"""
    temp_dict = {}
    for i, v in data_dict.items():
        try:
            temp_dict[i] = v["type_rate"]
        except:
            continue
    key = OtherSet().calculated(temp_dict)
    return key

def get_rift_type():
    """根据概率返回秘境等级"""
    data_dict = get_config()['rift']
    return get_dict_type_rate(data_dict)

def get_story_type():
    """根据概率返回事件类型"""
    data_dict = STORY
    return get_dict_type_rate(data_dict)

def get_battle_type():
    """根据概率返回战斗事件的类型"""
    data_dict = STORY['战斗']
    return get_dict_type_rate(data_dict)

def get_goods_type():
    data_dict = STORY['宝物']
    return get_dict_type_rate(data_dict)

def get_dy_info(user_level, rift_rank):
    """获取丹药事件的信息"""
    user_rank = USERRANK[user_level] #type=int，用户等级
    dy_name = get_dy_by_user_level(user_level, rift_rank)
    dy_info = STORY['宝物']['丹药']['name'][dy_name]
    init_rate = 40 #初始概率为40
    finall_rate = init_rate + ((dy_info['rank'] - user_rank + rift_rank) * 5)
    finall_rate = finall_rate if finall_rate <= 100 else 100
    is_success = False
    if random.randint(0, 100) <= finall_rate: #成功
        is_success = True
        return is_success, dy_info
    return is_success, dy_info


def get_dy_by_user_level(user_level, rift_rank):
    """根据用户等级、秘境等级随机获取一个丹药"""
    user_rank = USERRANK[user_level]#type=int，用户等级
    dy_name = STORY["宝物"]['丹药']['name']
    get_dy = []#可以获取到丹药的列表
    for k, v in dy_name.items():
        if user_rank - rift_rank <= v['rank']:  #秘境等级会增幅用户等级
            get_dy.append(k)

    return random.choice(get_dy)

def get_main_info(user_level, rift_rank):
    """获取功法的信息"""
    user_rank = USERRANK[user_level] #type=int，用户等级
    main_buff_type = get_skill_by_rank(user_level, rift_rank)#天地玄黄
    main_buff_id_list = skill_data[main_buff_type]['gf_list']
    init_rate = 60 #初始概率为60
    finall_rate = init_rate + rift_rank * 5
    finall_rate = finall_rate if finall_rate <= 100 else 100
    is_success = False
    if random.randint(0, 100) <= finall_rate: #成功
        is_success = True
        main_buff_id = random.choice(main_buff_id_list)
        return is_success, main_buff_id
    return is_success

def get_sec_info(user_level, rift_rank):
    """获取神通的信息"""
    user_rank = USERRANK[user_level] #type=int，用户等级
    sec_buff_type = get_skill_by_rank(user_level, rift_rank)#天地玄黄
    sec_buff_id_list = skill_data[sec_buff_type]['st_list']
    init_rate = 60 #初始概率为60
    finall_rate = init_rate + rift_rank * 5
    finall_rate = finall_rate if finall_rate <= 100 else 100
    is_success = False
    if random.randint(0, 100) <= finall_rate: #成功
        is_success = True
        sec_buff_id = random.choice(sec_buff_id_list)
        return is_success, sec_buff_id
    return is_success

def get_skill_by_rank(user_level, rift_rank):
    """根据用户等级、秘境等级随机获取一个技能"""
    user_rank = USERRANK[user_level]#type=int，用户等级
    temp_dict = []
    for k, v in skill_data.items():
        if user_rank - rift_rank <= v['rank']:  #秘境等级会增幅用户等级
            temp_dict.append(k)
    return random.choice(temp_dict)




class Rift:
    def __init__(self) -> None:
        self.name = ''
        self.rank = 0
        self.count = 0
        self.l_user_id = []
        self.time = 0
        
