import datetime
import json
import random
from .xiuxian2_handle import XiuxianDateManage
from .read_buff import UserBuffDate


def Player_fight(player1: dict, player2: dict, type_in, bot_id):
    """
    回合制战斗
    type_in : 1-切磋，不消耗气血、真元
              2-战斗，消耗气血、真元
    数据示例：
    {"user_id": None,"道号": None, "气血": None, "攻击": None, "真元": None, '会心':None, 'exp':None}
    """
    user1_buff_date = UserBuffDate(player1['user_id'])  # 1号的buff信息
    user1_main_buff_data = user1_buff_date.get_user_main_buff_data()
    user1_hp_buff = user1_main_buff_data['hpbuff'] if user1_main_buff_data != None else 0
    user1_mp_buff = user1_main_buff_data['mpbuff'] if user1_main_buff_data != None else 0
    user2_buff_date = UserBuffDate(player2['user_id'])  # 2号的buff信息
    user2_main_buff_data = user2_buff_date.get_user_main_buff_data()
    user2_hp_buff = user2_main_buff_data['hpbuff'] if user2_main_buff_data != None else 0
    user2_mp_buff = user2_main_buff_data['mpbuff'] if user2_main_buff_data != None else 0
    # 有技能，则开启技能模式

    player1_skil_open = False
    player2_skil_open = False
    if user1_buff_date.get_user_sec_buff_data() != None:
        user1_skill_date = user1_buff_date.get_user_sec_buff_data()
        player1_skil_open = True
    if user2_buff_date.get_user_sec_buff_data() != None:
        user2_skill_date = user2_buff_date.get_user_sec_buff_data()
        player2_skil_open = True

    play_list = []
    suc = None
    isSql = False
    if type_in == 2:
        isSql = True
    user1_turn_skip = True
    user2_turn_skip = True
    player1_init_hp = player1['气血']
    player2_init_hp = player2['气血']

    player1_turn_cost = 0  # 先设定为初始值 0
    player2_turn_cost = 0  # 先设定为初始值 0
    player1_f_js = get_user_def_buff(player1['user_id'])
    player2_f_js = get_user_def_buff(player2['user_id'])
    player1_js = player1_f_js
    player2_js = player2_f_js
    user1_skill_sh = 0
    user2_skill_sh = 0
    user1_buff_turn = True
    user2_buff_turn = True
    while True:
        msg1 = "{}发起攻击，造成了{}伤害\n"
        msg2 = "{}发起攻击，造成了{}伤害\n"
        if player1_skil_open:  # 是否开启技能
            if user1_turn_skip:  # 无需跳过回合
                play_list.append(get_msg_dict(player1, player1_init_hp, f"☆------{player1['道号']}的回合------☆"))
                user1_hp_cost, user1_mp_cost, user1_skill_type, skill_rate = get_skill_hp_mp_data(player1, user1_skill_date)
                if player1_turn_cost == 0:  # 没有持续性技能生效
                    player1_js = player1_f_js  # 没有持续性技能生效,减伤恢复
                    if isEnableUserSikll(player1, user1_hp_cost, user1_mp_cost, player1_turn_cost,
                                         skill_rate):  # 满足技能要求，#此处为技能的第一次释放
                        skill_msg, user1_skill_sh, player1_turn_cost = get_skill_sh_data(player1, user1_skill_date)
                        if user1_skill_type == 1:  # 直接伤害类技能
                            play_list.append(get_msg_dict(player1, player1_init_hp, skill_msg))
                            player1 = calculate_skill_cost(player1, user1_hp_cost, user1_mp_cost)
                            player2['气血'] = player2['气血'] - int(user1_skill_sh * player2_js)  # 玩家1的伤害 * 玩家2的减伤
                            play_list.append(get_msg_dict(player1, player1_init_hp, f"{player2['道号']}剩余血量{player2['气血']}"))

                        elif user1_skill_type == 2:  # 持续性伤害技能
                            play_list.append(get_msg_dict(player1, player1_init_hp, skill_msg))
                            player1 = calculate_skill_cost(player1, user1_hp_cost, user1_mp_cost)
                            player2['气血'] = player2['气血'] - int(user1_skill_sh * player2_js)  # 玩家1的伤害 * 玩家2的减伤
                            play_list.append(get_msg_dict(player1, player1_init_hp, f"{player2['道号']}剩余血量{player2['气血']}"))

                        elif user1_skill_type == 3:  # buff类技能
                            user1_buff_type = user1_skill_date['bufftype']
                            if user1_buff_type == 1:  # 攻击类buff
                                isCrit, player1_sh = get_turnatk(player1, user1_skill_sh)  # 判定是否暴击
                                if isCrit:
                                    msg1 = "{}发起会心一击，造成了{}伤害\n"
                                else:
                                    msg1 = "{}发起攻击，造成了{}伤害\n"
                                player1 = calculate_skill_cost(player1, user1_hp_cost, user1_mp_cost)
                                play_list.append(get_msg_dict(player1, player1_init_hp, skill_msg))
                                play_list.append(get_msg_dict(player1, player1_init_hp, msg1.format(player1['道号'], player1_sh)))
                                player2['气血'] = player2['气血'] - int(player1_sh * player2_js)  # 玩家1的伤害 * 玩家2的减伤
                                play_list.append(get_msg_dict(player1, player1_init_hp, f"{player2['道号']}剩余血量{player2['气血']}"))


                            elif user1_buff_type == 2:  # 减伤类buff,需要在player2处判断
                                isCrit, player1_sh = get_turnatk(player1)  # 判定是否暴击
                                if isCrit:
                                    msg1 = "{}发起会心一击，造成了{}伤害\n"
                                else:
                                    msg1 = "{}发起攻击，造成了{}伤害\n"

                                player1 = calculate_skill_cost(player1, user1_hp_cost, user1_mp_cost)
                                play_list.append(get_msg_dict(player1, player1_init_hp, skill_msg))
                                play_list.append(get_msg_dict(player1, player1_init_hp, msg1.format(player1['道号'], player1_sh)))
                                player2['气血'] = player2['气血'] - int(player1_sh * player2_js)  # 玩家1的伤害 * 玩家2的减伤
                                play_list.append(get_msg_dict(player1, player1_init_hp, f"{player2['道号']}剩余血量{player2['气血']}"))
                                player1_js = player1_f_js - user1_skill_sh if player1_f_js - user1_skill_sh > 0.1 else 0.1

                        elif user1_skill_type == 4:  # 封印类技能
                            play_list.append(get_msg_dict(player1, player1_init_hp, skill_msg))
                            player1 = calculate_skill_cost(player1, user1_hp_cost, user1_mp_cost)

                            if user1_skill_sh:  # 命中
                                user2_turn_skip = False
                                user2_buff_turn = False

                    else:  # 没放技能，打一拳
                        isCrit, player1_sh = get_turnatk(player1)  # 判定是否暴击
                        if isCrit:
                            msg1 = "{}发起会心一击，造成了{}伤害\n"
                        else:
                            msg1 = "{}发起攻击，造成了{}伤害\n"
                        play_list.append(get_msg_dict(player1, player1_init_hp, msg1.format(player1['道号'], player1_sh)))
                        player2['气血'] = player2['气血'] - int(player1_sh * player2_js)  # 玩家1的伤害 * 玩家2的减伤
                        play_list.append(get_msg_dict(player1, player1_init_hp, f"{player2['道号']}剩余血量{player2['气血']}"))


                else:  # 持续性技能判断,不是第一次
                    if user1_skill_type == 2:  # 持续性伤害技能
                        player1_turn_cost = player1_turn_cost - 1
                        skill_msg = get_persistent_skill_msg(player1['道号'], user1_skill_date['name'], user1_skill_sh,
                                                            player1_turn_cost)
                        play_list.append(get_msg_dict(player1, player1_init_hp, skill_msg))
                        isCrit, player1_sh = get_turnatk(player1)  # 判定是否暴击
                        if isCrit:
                            msg1 = "{}发起会心一击，造成了{}伤害\n"
                        else:
                            msg1 = "{}发起攻击，造成了{}伤害\n"
                        play_list.append(get_msg_dict(player1, player1_init_hp, msg1.format(player1['道号'], player1_sh)))
                        # 玩家1的伤害 * 玩家2的减伤,持续性伤害不影响普攻
                        player2['气血'] = player2['气血'] - int((user1_skill_sh + player1_sh) * player2_js)
                        play_list.append(get_msg_dict(player1, player1_init_hp, f"{player2['道号']}剩余血量{player2['气血']}"))


                    elif user1_skill_type == 3:  # buff类技能
                        user1_buff_type = user1_skill_date['bufftype']
                        if user1_buff_type == 1:  # 攻击类buff
                            isCrit, player1_sh = get_turnatk(player1, user1_skill_sh)  # 判定是否暴击

                            if isCrit:
                                msg1 = "{}发起会心一击，造成了{}伤害\n"
                            else:
                                msg1 = "{}发起攻击，造成了{}伤害\n"

                            player1_turn_cost = player1_turn_cost - 1
                            play_list.append(get_msg_dict(player1, player1_init_hp, f"{user1_skill_date['name']}增伤剩余:{player1_turn_cost}回合"))
                            play_list.append(get_msg_dict(player1, player1_init_hp, msg1.format(player1['道号'], player1_sh)))
                            player2['气血'] = player2['气血'] - int(player1_sh * player2_js)  # 玩家1的伤害 * 玩家2的减伤
                            play_list.append(get_msg_dict(player1, player1_init_hp, f"{player2['道号']}剩余血量{player2['气血']}"))


                        elif user1_buff_type == 2:  # 减伤类buff,需要在player2处判断
                            isCrit, player1_sh = get_turnatk(player1)  # 判定是否暴击
                            if isCrit:
                                msg1 = "{}发起会心一击，造成了{}伤害\n"
                            else:
                                msg1 = "{}发起攻击，造成了{}伤害\n"

                            player1_turn_cost = player1_turn_cost - 1
                            play_list.append(get_msg_dict(player1, player1_init_hp, f"{user1_skill_date['name']}减伤剩余{player1_turn_cost}回合"))
                            play_list.append(get_msg_dict(player1, player1_init_hp, msg1.format(player1['道号'], player1_sh)))
                            player2['气血'] = player2['气血'] - int(player1_sh * player2_js)  # 玩家1的伤害 * 玩家2的减伤
                            play_list.append(get_msg_dict(player1, player1_init_hp, f"{player2['道号']}剩余血量{player2['气血']}"))
                            player1_js = player1_f_js - user1_skill_sh if player1_f_js - user1_skill_sh > 0.1 else 0.1

                    elif user1_skill_type == 4:  # 封印类技能
                        player1_turn_cost = player1_turn_cost - 1
                        skill_msg = get_persistent_skill_msg(player1['道号'], user1_skill_date['name'], user1_skill_sh,
                                                            player1_turn_cost)
                        play_list.append(get_msg_dict(player1, player1_init_hp, skill_msg))
                        isCrit, player1_sh = get_turnatk(player1)  # 判定是否暴击
                        if isCrit:
                            msg1 = "{}发起会心一击，造成了{}伤害\n"
                        else:
                            msg1 = "{}发起攻击，造成了{}伤害\n"
                        play_list.append(get_msg_dict(player1, player1_init_hp, msg1.format(player1['道号'], player1_sh)))

                        player2['气血'] = player2['气血'] - int(player1_sh * player2_js)  # 玩家1的伤害 * 玩家2的减伤
                        play_list.append(get_msg_dict(player1, player1_init_hp, f"{player2['道号']}剩余血量{player2['气血']}"))
                        if player1_turn_cost == 0:  # 封印时间到
                            user2_turn_skip = True
                            user2_buff_turn = True


            else:  # 休息回合-1
                play_list.append(get_msg_dict(player1, player1_init_hp, f"☆------{player1['道号']}动弹不得！------☆"))
                if player1_turn_cost > 0:
                    player1_turn_cost -= 1
                if player1_turn_cost == 0 and user1_buff_turn:
                    user1_turn_skip = True

        else:  # 没有技能的derB
            if user1_turn_skip:
                play_list.append(get_msg_dict(player1, player1_init_hp, f"☆------{player1['道号']}的回合------☆"))
                isCrit, player1_sh = get_turnatk(player1)  # 判定是否暴击
                if isCrit:
                    msg1 = "{}发起会心一击，造成了{}伤害\n"
                else:
                    msg1 = "{}发起攻击，造成了{}伤害\n"
                play_list.append(get_msg_dict(player1, player1_init_hp, msg1.format(player1['道号'], player1_sh)))
                player2['气血'] = player2['气血'] - player1_sh
                play_list.append(get_msg_dict(player1, player1_init_hp, f"{player2['道号']}剩余血量{player2['气血']}"))

            else:
                play_list.append(get_msg_dict(player1, player1_init_hp, f"☆------{player1['道号']}动弹不得！------☆"))

        if player2['气血'] <= 0:  # 玩家2气血小于0，结算
            play_list.append({"type": "node", "data": {"name": "Bot", "uin": int(bot_id), "content": "{}胜利".format(player1['道号'])}})
            suc = f"{player1['道号']}"
            if isSql:
                XiuxianDateManage().update_user_hp_mp(player1['user_id'], int(player1['气血'] / (1 + user1_hp_buff)),
                                                      int(player1['真元'] / (1 + user1_mp_buff)))
                XiuxianDateManage().update_user_hp_mp(player2['user_id'], 1, int(player2['真元'] / (1 + user2_mp_buff)))
            break

        if player1_turn_cost < 0:  # 休息为负数，如果休息，则跳过回合，正常是0
            user1_turn_skip = False
            player1_turn_cost += 1

        if player2_skil_open:  # 有技能
            if user2_turn_skip:  # 玩家2无需跳过回合
                play_list.append(get_msg_dict(player2, player2_init_hp, f"☆------{player2['道号']}的回合------☆"))
                user2_hp_cost, user2_mp_cost, user2_skill_type, skill_rate = get_skill_hp_mp_data(player2, user2_skill_date)
                if player2_turn_cost == 0:  # 没有持续性技能生效
                    player2_js = player2_f_js
                    if isEnableUserSikll(player2, user2_hp_cost, user2_mp_cost, player2_turn_cost,
                                         skill_rate):  # 满足技能要求，#此处为技能的第一次释放
                        skill_msg, user2_skill_sh, player2_turn_cost = get_skill_sh_data(player2, user2_skill_date)
                        if user2_skill_type == 1:  # 直接伤害类技能
                            play_list.append(get_msg_dict(player2, player2_init_hp, skill_msg))
                            player1['气血'] = player1['气血'] - int(user2_skill_sh * player1_js)  # 玩家2的伤害 * 玩家1的减伤
                            play_list.append(get_msg_dict(player2, player2_init_hp, f"{player1['道号']}剩余血量{player1['气血']}"))
                            player2 = calculate_skill_cost(player2, user2_hp_cost, user2_mp_cost)


                        elif user2_skill_type == 2:  # 持续性伤害技能
                            play_list.append(get_msg_dict(player2, player2_init_hp, skill_msg))
                            player1['气血'] = player1['气血'] - int(user2_skill_sh * player1_js)  # 玩家2的伤害 * 玩家1的减伤
                            play_list.append(get_msg_dict(player2, player2_init_hp, f"{player1['道号']}剩余血量{player1['气血']}"))
                            player2 = calculate_skill_cost(player2, user2_hp_cost, user2_mp_cost)


                        elif user2_skill_type == 3:  # buff类技能
                            user2_buff_type = user2_skill_date['bufftype']
                            if user2_buff_type == 1:  # 攻击类buff
                                isCrit, player2_sh = get_turnatk(player2, user2_skill_sh)  # 判定是否暴击
                                if isCrit:
                                    msg2 = "{}发起会心一击，造成了{}伤害\n"
                                else:
                                    msg2 = "{}发起攻击，造成了{}伤害\n"

                                play_list.append(get_msg_dict(player2, player2_init_hp, skill_msg))
                                play_list.append(get_msg_dict(player2, player2_init_hp, msg2.format(player2['道号'], player2_sh)))
                                player1['气血'] = player1['气血'] - int(player2_sh * player1_js)
                                play_list.append(get_msg_dict(player2, player2_init_hp, f"{player1['道号']}剩余血量{player1['气血']}"))
                                player2 = calculate_skill_cost(player2, user2_hp_cost, user2_mp_cost)

                            elif user2_buff_type == 2:  # 减伤类buff,需要在player2处判断
                                isCrit, player2_sh = get_turnatk(player2)  # 判定是否暴击
                                if isCrit:
                                    msg2 = "{}发起会心一击，造成了{}伤害\n"
                                else:
                                    msg2 = "{}发起攻击，造成了{}伤害\n"
                                play_list.append(get_msg_dict(player2, player2_init_hp, skill_msg))
                                play_list.append(get_msg_dict(player2, player2_init_hp, msg2.format(player2['道号'], player2_sh)))
                                player1['气血'] = player1['气血'] - int(player2_sh * player1_js)
                                play_list.append(get_msg_dict(player2, player2_init_hp, f"{player1['道号']}剩余血量{player1['气血']}"))
                                player2_js = player2_f_js - user2_skill_sh if player2_f_js - user2_skill_sh > 0.1 else 0.1
                                player2 = calculate_skill_cost(player2, user2_hp_cost, user2_mp_cost)


                        elif user2_skill_type == 4:  # 封印类技能
                            play_list.append(get_msg_dict(player2, player2_init_hp, skill_msg))
                            player2 = calculate_skill_cost(player2, user2_hp_cost, user2_mp_cost)

                            if user2_skill_sh:  # 命中
                                user1_turn_skip = False
                                user1_buff_turn = False

                    else:  # 没放技能
                        isCrit, player2_sh = get_turnatk(player2)  # 判定是否暴击
                        if isCrit:
                            msg2 = "{}发起会心一击，造成了{}伤害\n"
                        else:
                            msg2 = "{}发起攻击，造成了{}伤害\n"
                        play_list.append(get_msg_dict(player2, player2_init_hp, msg2.format(player2['道号'], player2_sh)))
                        player1['气血'] = player1['气血'] - int(player2_sh * player1_js)  # 玩家2的伤害 * 玩家1的减伤
                        play_list.append(get_msg_dict(player2, player2_init_hp, f"{player1['道号']}剩余血量{player1['气血']}"))


                else:  # 持续性技能判断,不是第一次
                    if user2_skill_type == 2:  # 持续性伤害技能
                        player2_turn_cost = player2_turn_cost - 1
                        skill_msg = get_persistent_skill_msg(player2['道号'], user2_skill_date['name'], user2_skill_sh,
                                                            player2_turn_cost)
                        play_list.append(get_msg_dict(player2, player2_init_hp, skill_msg))

                        isCrit, player2_sh = get_turnatk(player2)  # 判定是否暴击
                        if isCrit:
                            msg2 = "{}发起会心一击，造成了{}伤害\n"
                        else:
                            msg2 = "{}发起攻击，造成了{}伤害\n"

                        play_list.append(get_msg_dict(player2, player2_init_hp, msg2.format(player2['道号'], player2_sh)))
                        player1['气血'] = player1['气血'] - int((user2_skill_sh + player2_sh) * player1_js)
                        play_list.append(get_msg_dict(player2, player2_init_hp, f"{player1['道号']}剩余血量{player1['气血']}"))


                    elif user2_skill_type == 3:  # buff类技能
                        user2_buff_type = user2_skill_date['bufftype']
                        if user2_buff_type == 1:  # 攻击类buff
                            isCrit, player2_sh = get_turnatk(player2, user2_skill_sh)  # 判定是否暴击

                            if isCrit:
                                msg2 = "{}发起会心一击，造成了{}伤害\n"
                            else:
                                msg2 = "{}发起攻击，造成了{}伤害\n"
                            player2_turn_cost = player2_turn_cost - 1
                            play_list.append(get_msg_dict(player2, player2_init_hp, f"{user2_skill_date['name']}增伤剩余{player2_turn_cost}回合"))
                            play_list.append(get_msg_dict(player2, player2_init_hp, msg2.format(player2['道号'], player2_sh)))
                            player1['气血'] = player1['气血'] - int(player2_sh * player1_js)  # 玩家2的伤害 * 玩家1的减伤
                            play_list.append(get_msg_dict(player2, player2_init_hp, f"{player1['道号']}剩余血量{player1['气血']}"))

                        elif user2_buff_type == 2:  # 减伤类buff,需要在player2处判断
                            isCrit, player2_sh = get_turnatk(player2)  # 判定是否暴击
                            if isCrit:
                                msg2 = "{}发起会心一击，造成了{}伤害\n"
                            else:
                                msg2 = "{}发起攻击，造成了{}伤害\n"

                            player2_turn_cost = player2_turn_cost - 1
                            play_list.append(get_msg_dict(player2, player2_init_hp, f"{user2_skill_date['name']}减伤剩余{player2_turn_cost}回合！"))
                            play_list.append(get_msg_dict(player2, player2_init_hp, msg2.format(player2['道号'], player2_sh)))
                            player1['气血'] = player1['气血'] - int(player2_sh * player1_js)  # 玩家1的伤害 * 玩家2的减伤
                            play_list.append(get_msg_dict(player2, player2_init_hp, f"{player1['道号']}剩余血量{player1['气血']}"))

                            player2_js = player2_f_js - user2_skill_sh  if player2_f_js - user2_skill_sh > 0.1 else 0.1

                    elif user2_skill_type == 4:  # 封印类技能
                        player2_turn_cost = player2_turn_cost - 1
                        skill_msg = get_persistent_skill_msg(player2['道号'], user2_skill_date['name'], user2_skill_sh,
                                                            player2_turn_cost)
                        play_list.append(get_msg_dict(player2, player2_init_hp, skill_msg))

                        isCrit, player2_sh = get_turnatk(player2)  # 判定是否暴击
                        if isCrit:
                            msg2 = "{}发起会心一击，造成了{}伤害\n"
                        else:
                            msg2 = "{}发起攻击，造成了{}伤害\n"
                        play_list.append(get_msg_dict(player2, player2_init_hp, msg2.format(player2['道号'], player2_sh)))
                        player1['气血'] = player1['气血'] - int(player2_sh * player1_js)  # 玩家1的伤害 * 玩家2的减伤
                        play_list.append(get_msg_dict(player2, player2_init_hp, f"{player1['道号']}剩余血量{player1['气血']}"))

                        if player2_turn_cost == 0:  # 封印时间到
                            user1_turn_skip = True
                            user1_buff_turn = True

            else:  # 休息回合-1
                play_list.append(get_msg_dict(player2, player2_init_hp, f"☆------{player2['道号']}动弹不得！------☆"))
                if player2_turn_cost > 0:
                    player2_turn_cost -= 1
                if player2_turn_cost == 0 and user2_buff_turn:
                    user2_turn_skip = True
        else:  # 没有技能的derB
            if user2_turn_skip:
                play_list.append(get_msg_dict(player2, player2_init_hp, f"☆------{player2['道号']}的回合------☆"))
                isCrit, player2_sh = get_turnatk(player2)  # 判定是否暴击
                if isCrit:
                    msg2 = "{}发起会心一击，造成了{}伤害\n"
                else:
                    msg2 = "{}发起攻击，造成了{}伤害\n"
                play_list.append(get_msg_dict(player2, player2_init_hp, msg2.format(player2['道号'], player2_sh)))
                player1['气血'] = player1['气血'] - player2_sh
                play_list.append(get_msg_dict(player2, player2_init_hp, f"{player1['道号']}剩余血量{player1['气血']}"))

            else:
                play_list.append(get_msg_dict(player2, player2_init_hp, f"☆------{player2['道号']}动弹不得！------☆"))

        if player1['气血'] <= 0:  # 玩家2气血小于0，结算
            play_list.append({"type": "node", "data": {"name": "Bot", "uin": int(bot_id), "content": "{}胜利".format(player2['道号'])}})
            suc = f"{player2['道号']}"
            if isSql:
                XiuxianDateManage().update_user_hp_mp(player1['user_id'], 1, int(player1['真元'] / (1 + user1_mp_buff)))
                XiuxianDateManage().update_user_hp_mp(player2['user_id'], int(player2['气血'] / (1 + user2_hp_buff)),
                                                      int(player2['真元'] / (1 + user2_mp_buff)))
            break

        if player2_turn_cost < 0:  # 休息为负数，如果休息，则跳过回合，正常是0
            user2_turn_skip = False
            player2_turn_cost += 1

        if user1_turn_skip == False and user2_turn_skip == False:
            play_list.append({"type": "node", "data": {"name": "Bot", "uin": int(bot_id), "content": "双方都动弹不得！"}})
            user1_turn_skip = True
            user2_turn_skip = True

        if player1['气血'] <= 0 or player2['气血'] <= 0:
            play_list.append({"type": "node", "data": {"name": "Bot", "uin": int(bot_id), "content": "逻辑错误！"}})
            break

    return play_list, suc


async def Boss_fight(player1: dict, boss: dict, type_in=2, bot_id=0):
    """
    回合制战斗
    type_in : 1-切磋，不消耗气血、真元
              2-战斗，消耗气血、真元
    数据示例：
    {"user_id": None,"道号": None, "气血": None, "攻击": None, "真元": None, '会心':None, 'exp':None}
    """
    user1_buff_date = UserBuffDate(player1['user_id'])  # 1号的buff信息
    user1_main_buff_data = user1_buff_date.get_user_main_buff_data()
    user1_hp_buff = user1_main_buff_data['hpbuff'] if user1_main_buff_data != None else 0
    user1_mp_buff = user1_main_buff_data['mpbuff'] if user1_main_buff_data != None else 0

    # 有技能，则开启技能模式

    player1_skil_open = False
    if user1_buff_date.get_user_sec_buff_data() != None:
        user1_skill_date = user1_buff_date.get_user_sec_buff_data()
        player1_skil_open = True

    play_list = []
    player_init_hp = player1['气血']
    suc = None
    isSql = False
    if type_in == 2:
        isSql = True
    user1_turn_skip = True
    boss_turn_skip = True
    player1_turn_cost = 0  # 先设定为初始值 0
    player1_f_js = get_user_def_buff(player1['user_id'])
    player1_js = player1_f_js  # 减伤率
    boss['减伤'] = 1  # boss减伤率
    user1_skill_sh = 0

    user1buffturn = True
    bossbuffturn = True

    get_stone = 0
    sh = 0
    qx = boss['气血']
    boss_now_stone = boss['stone']
    boss_js = boss['减伤']
    boss['会心'] = 30

    while True:
        msg1 = "{}发起攻击，造成了{}伤害\n"
        msg2 = "{}发起攻击，造成了{}伤害\n"
        if player1_skil_open:  # 是否开启技能
            if user1_turn_skip:  # 无需跳过回合
                turn_start_msg = f"☆------{player1['道号']}的回合------☆"
                play_list.append(get_msg_dict(player1, player_init_hp, turn_start_msg))
                user1hpconst, user1mpcost, user1skill_type, skillrate = get_skill_hp_mp_data(player1, user1_skill_date)
                if player1_turn_cost == 0:  # 没有持续性技能生效
                    player1_js = player1_f_js  # 没有持续性技能生效,减伤恢复
                    if isEnableUserSikll(player1, user1hpconst, user1mpcost, player1_turn_cost,
                                         skillrate):  # 满足技能要求，#此处为技能的第一次释放
                        skillmsg, user1_skill_sh, player1_turn_cost = get_skill_sh_data(player1, user1_skill_date)
                        if user1skill_type == 1:  # 直接伤害类技能
                            play_list.append(get_msg_dict(player1, player_init_hp, skillmsg))
                            player1 = calculate_skill_cost(player1, user1hpconst, user1mpcost)
                            boss['气血'] = boss['气血'] - int(user1_skill_sh * boss_js)  # 玩家1的伤害 * boss的减伤
                            boss_hp_msg = f"{boss['name']}剩余血量{boss['气血']}"
                            play_list.append(get_msg_dict(player1, player_init_hp, boss_hp_msg))
                            sh += user1_skill_sh

                        elif user1skill_type == 2:  # 持续性伤害技能
                            play_list.append(get_msg_dict(player1, player_init_hp, skillmsg))
                            player1 = calculate_skill_cost(player1, user1hpconst, user1mpcost)
                            boss['气血'] = boss['气血'] - int(user1_skill_sh * boss_js)  # 玩家1的伤害 * 玩家2的减伤
                            boss_hp_msg = f"{boss['name']}剩余血量{boss['气血']}"
                            play_list.append(get_msg_dict(player1, player_init_hp, boss_hp_msg))
                            sh += user1_skill_sh


                        elif user1skill_type == 3:  # buff类技能
                            user1buff_type = user1_skill_date['bufftype']
                            if user1buff_type == 1:  # 攻击类buff
                                isCrit, player1_sh = get_turnatk(player1, user1_skill_sh)  # 判定是否暴击
                                if isCrit:
                                    msg1 = "{}发起会心一击，造成了{}伤害\n"
                                else:
                                    msg1 = "{}发起攻击，造成了{}伤害\n"
                                player1 = calculate_skill_cost(player1, user1hpconst, user1mpcost)
                                play_list.append(get_msg_dict(player1, player_init_hp, skillmsg))
                                player1_atk_msg = msg1.format(player1['道号'], player1_sh)
                                play_list.append(get_msg_dict(player1, player_init_hp, player1_atk_msg))
                                boss['气血'] = boss['气血'] - int(player1_sh * boss_js)  # 玩家1的伤害 * 玩家2的减伤
                                boss_hp_msg = f"{boss['name']}剩余血量{boss['气血']}"
                                play_list.append(get_msg_dict(player1, player_init_hp, boss_hp_msg))
                                sh += player1_sh


                            elif user1buff_type == 2:  # 减伤类buff,需要在player2处判断
                                isCrit, player1_sh = get_turnatk(player1)  # 判定是否暴击
                                if isCrit:
                                    msg1 = "{}发起会心一击，造成了{}伤害\n"
                                else:
                                    msg1 = "{}发起攻击，造成了{}伤害\n"

                                player1 = calculate_skill_cost(player1, user1hpconst, user1mpcost)
                                play_list.append(get_msg_dict(player1, player_init_hp, skillmsg))
                                player1_atk_msg = msg1.format(player1['道号'], player1_sh)
                                play_list.append(get_msg_dict(player1, player_init_hp, player1_atk_msg))
                                boss['气血'] = boss['气血'] - int(player1_sh * boss_js)  # 玩家1的伤害 * 玩家2的减伤
                                boss_hp_msg = f"{boss['name']}剩余血量{boss['气血']}"
                                play_list.append(get_msg_dict(player1, player_init_hp, boss_hp_msg))
                                player1_js = player1_f_js - user1_skill_sh if player1_f_js - user1_skill_sh > 0.1 else 0.1
                                sh += player1_sh

                        elif user1skill_type == 4:  # 封印类技能
                            play_list.append(get_msg_dict(player1, player_init_hp, skillmsg))
                            player1 = calculate_skill_cost(player1, user1hpconst, user1mpcost)

                            if user1_skill_sh:  # 命中
                                boss_turn_skip = False
                                bossbuffturn = False

                    else:  # 没放技能，打一拳
                        isCrit, player1_sh = get_turnatk(player1)  # 判定是否暴击
                        if isCrit:
                            msg1 = "{}发起会心一击，造成了{}伤害\n"
                        else:
                            msg1 = "{}发起攻击，造成了{}伤害\n"
                        player1_atk_msg = msg1.format(player1['道号'], player1_sh)
                        play_list.append(get_msg_dict(player1, player_init_hp, player1_atk_msg))
                        boss['气血'] = boss['气血'] - int(player1_sh * boss_js)  # 玩家1的伤害 * 玩家2的减伤
                        boss_hp_msg = f"{boss['name']}剩余血量{boss['气血']}"
                        play_list.append(get_msg_dict(player1, player_init_hp, boss_hp_msg))
                        sh += player1_sh


                else:  # 持续性技能判断,不是第一次
                    if user1skill_type == 2:  # 持续性伤害技能
                        player1_turn_cost = player1_turn_cost - 1
                        skillmsg = get_persistent_skill_msg(player1['道号'], user1_skill_date['name'], user1_skill_sh,
                                                            player1_turn_cost)
                        play_list.append(get_msg_dict(player1, player_init_hp, skillmsg))
                        isCrit, player1_sh = get_turnatk(player1)  # 判定是否暴击
                        if isCrit:
                            msg1 = "{}发起会心一击，造成了{}伤害\n"
                        else:
                            msg1 = "{}发起攻击，造成了{}伤害\n"
                        player1_atk_msg = msg1.format(player1['道号'], player1_sh)
                        play_list.append(get_msg_dict(player1, player_init_hp, player1_atk_msg))
                        boss['气血'] = boss['气血'] - int((user1_skill_sh + player1_sh) * boss_js)
                        boss_hp_msg = f"{boss['name']}剩余血量{boss['气血']}"
                        play_list.append(get_msg_dict(player1, player_init_hp, boss_hp_msg))
                        sh += player1_sh + user1_skill_sh

                    elif user1skill_type == 3:  # buff类技能
                        user1buff_type = user1_skill_date['bufftype']
                        if user1buff_type == 1:  # 攻击类buff
                            isCrit, player1_sh = get_turnatk(player1, user1_skill_sh)  # 判定是否暴击

                            if isCrit:
                                msg1 = "{}发起会心一击，造成了{}伤害\n"
                            else:
                                msg1 = "{}发起攻击，造成了{}伤害\n"
                            player1_turn_cost = player1_turn_cost - 1
                            play_list.append(get_msg_dict(player1, player_init_hp, f"{user1_skill_date['name']}增伤剩余:{player1_turn_cost}回合"))
                            player1_atk_msg = msg1.format(player1['道号'], player1_sh)
                            play_list.append(get_msg_dict(player1, player_init_hp, player1_atk_msg))
                            boss['气血'] = boss['气血'] - int(player1_sh * boss_js)  # 玩家1的伤害 * 玩家2的减伤
                            boss_hp_msg = f"{boss['name']}剩余血量{boss['气血']}"
                            play_list.append(get_msg_dict(player1, player_init_hp, boss_hp_msg))
                            sh += player1_sh

                        elif user1buff_type == 2:  # 减伤类buff,需要在player2处判断
                            isCrit, player1_sh = get_turnatk(player1)  # 判定是否暴击
                            if isCrit:
                                msg1 = "{}发起会心一击，造成了{}伤害\n"
                            else:
                                msg1 = "{}发起攻击，造成了{}伤害\n"

                            player1_turn_cost = player1_turn_cost - 1
                            play_list.append(get_msg_dict(player1, player_init_hp, f"减伤剩余{player1_turn_cost}回合！"))
                            player1_atk_msg = msg1.format(player1['道号'], player1_sh)
                            play_list.append(get_msg_dict(player1, player_init_hp, player1_atk_msg))
                            boss['气血'] = boss['气血'] - int(player1_sh * boss_js)  # 玩家1的伤害 * 玩家2的减伤
                            boss_hp_msg = f"{boss['name']}剩余血量{boss['气血']}"
                            play_list.append(get_msg_dict(player1, player_init_hp, boss_hp_msg))
                            player1_js = player1_f_js - user1_skill_sh if player1_f_js - user1_skill_sh > 0.1 else 0.1
                            sh += player1_sh

                    elif user1skill_type == 4:  # 封印类技能
                        player1_turn_cost = player1_turn_cost - 1
                        skillmsg = get_persistent_skill_msg(player1['道号'], user1_skill_date['name'], user1_skill_sh,
                                                            player1_turn_cost)
                        play_list.append(get_msg_dict(player1, player_init_hp, skillmsg))
                        isCrit, player1_sh = get_turnatk(player1)  # 判定是否暴击
                        if isCrit:
                            msg1 = "{}发起会心一击，造成了{}伤害\n"
                        else:
                            msg1 = "{}发起攻击，造成了{}伤害\n"
                        player1_atk_msg = msg1.format(player1['道号'], player1_sh)
                        play_list.append(get_msg_dict(player1, player_init_hp, player1_atk_msg))
                        boss['气血'] = boss['气血'] - int(player1_sh * boss_js)  # 玩家1的伤害 * 玩家2的减伤
                        boss_hp_msg = f"{boss['name']}剩余血量{boss['气血']}"
                        play_list.append(get_msg_dict(player1, player_init_hp, boss_hp_msg))
                        sh += player1_sh
                        if player1_turn_cost == 0:  # 封印时间到
                            boss_turn_skip = True
                            bossbuffturn = True

            else:  # 休息回合-1
                play_list.append(get_msg_dict(player1, player_init_hp, f"☆------{player1['道号']}动弹不得！------☆"))
                if player1_turn_cost > 0:
                    player1_turn_cost -= 1
                if player1_turn_cost == 0:
                    user1_turn_skip = True

        else:  # 没有技能的derB
            play_list.append(get_msg_dict(player1, player_init_hp, f"☆------{player1['道号']}的回合------☆"))
            isCrit, player1_sh = get_turnatk(player1)  # 判定是否暴击
            if isCrit:
                msg1 = "{}发起会心一击，造成了{}伤害\n"
            else:
                msg1 = "{}发起攻击，造成了{}伤害\n"
            player1_atk_msg = msg1.format(player1['道号'], player1_sh)
            play_list.append(get_msg_dict(player1, player_init_hp, player1_atk_msg))
            boss['气血'] = boss['气血'] - player1_sh
            boss_hp_msg = f"{boss['name']}剩余血量{boss['气血']}"
            play_list.append(get_msg_dict(player1, player_init_hp, boss_hp_msg))
            sh += player1_sh

        if boss['气血'] <= 0:  # boss气血小于0，结算
            play_list.append({"type": "node", "data": {"name": "Bot", "uin": int(bot_id), "content": "{}胜利".format(player1['道号'])}})
            suc = "群友赢了"
            get_stone = boss_now_stone
            if isSql:
                XiuxianDateManage().update_user_hp_mp(player1['user_id'], int(player1['气血'] / (1 + user1_hp_buff)),
                                                      int(player1['真元'] / (1 + user1_mp_buff)))

            break

        if player1_turn_cost < 0:  # 休息为负数，如果休息，则跳过回合，正常是0
            user1_turn_skip = False
            player1_turn_cost += 1

            # 没有技能的derB
        if boss_turn_skip:
            play_list.append(get_boss_dict(boss, qx, f"☆------{boss['name']}的回合------☆", bot_id))
            isCrit, boss_sh = get_turnatk(boss)  # 判定是否暴击
            if isCrit:
                msg2 = "{}发起会心一击，造成了{}伤害\n"
            else:
                msg2 = "{}发起攻击，造成了{}伤害\n"
            play_list.append(get_boss_dict(boss, qx, msg2.format(boss['name'], boss_sh), bot_id))
            player1['气血'] = player1['气血'] - (boss_sh * player1_js)
            play_list.append(get_boss_dict(boss, qx, f"{player1['道号']}剩余血量{player1['气血']}", bot_id))

        else:
            play_list.append(get_boss_dict(boss, qx, f"☆------{boss['name']}动弹不得！------☆", bot_id))

        if player1['气血'] <= 0:  # 玩家2气血小于0，结算
            play_list.append({"type": "node", "data": {"name": "Bot", "uin": int(bot_id), "content": "{}胜利".format(boss['name'])}})
            suc = "Boss赢了"
            get_stone = int(boss_now_stone * (sh / qx))
            boss['stone'] = boss_now_stone - get_stone

            if isSql:
                XiuxianDateManage().update_user_hp_mp(player1['user_id'], 1, int(player1['真元'] / (1 + user1_mp_buff)))

            break

        if player1['气血'] <= 0 or boss['气血'] <= 0:
            play_list.append({"type": "node", "data": {"name": "Bot", "uin": int(bot_id), "content": "逻辑错误！"}})
            break

    return play_list, suc, boss, get_stone

def get_msg_dict(player, player_init_hp, msg):
    return {"type": "node", "data": {"name": f"{player['道号']}，当前血量：{int(player['气血'])} / {int(player_init_hp)}", "uin": int(player['user_id']), "content": msg}}

def get_boss_dict(boss, boss_init_hp, msg, bot_id):
    return {"type": "node", "data": {"name": f"{boss['name']}当前血量：{int(boss['气血'])} / {int(boss_init_hp)}", "uin": int(bot_id), "content": msg}}

def get_user_def_buff(user_id):
    user_armor_data = UserBuffDate(user_id).get_user_armor_buff_data()
    if user_armor_data != None:
        def_buff = user_armor_data['def_buff']
    else:
        def_buff = 0
    return round(1 - def_buff, 2)#初始减伤率


def get_turnatk(player, buff=0):
    isCrit = False
    turnatk = int(round(random.uniform(0.95, 1.05), 2) * (player['攻击'] * (buff + 1)))  # 攻击波动,buff是攻击buff
    if random.randint(0, 100) <= player['会心']:  # 会心判断
        turnatk = int(turnatk * 1.5)
        isCrit = True
    return isCrit, turnatk


def isEnableUserSikll(player, hpcost, mpcost, turncost, skillrate):  # 是否满足技能释放条件
    skill = False
    if turncost < 0:  # 判断是否进入休息状态
        return skill

    if player['气血'] > hpcost and player['真元'] >= mpcost:  # 判断血量、真元是否满足
        if random.randint(0, 100) <= skillrate:  # 随机概率释放技能
            skill = True
    return skill


def get_skill_hp_mp_data(player, secbuffdata):
    hpcost = int(secbuffdata['hpcost'] * player['气血']) if secbuffdata['hpcost'] != 0 else 0
    mpcost = int(secbuffdata['mpcost'] * player['exp']) if secbuffdata['mpcost'] != 0 else 0
    return hpcost, mpcost, secbuffdata['skill_type'], secbuffdata['rate']


def calculate_skill_cost(player, hpcost, mpcost):
    player['气血'] = player['气血'] - hpcost  # 气血消耗
    player['真元'] = player['真元'] - mpcost  # 真元消耗

    return player


def get_persistent_skill_msg(username, skillname, sh, turn):
    if sh == True:
        return f"{username}的封印技能：{skillname}，剩余回合：{turn}！"
    return f"{username}的持续性技能：{skillname}，造成{sh}伤害，剩余回合：{turn}！"


def get_skill_sh_data(player, secbuffdata):
    skillmsg = ''
    if secbuffdata['skill_type'] == 1:  # 连续攻击类型
        turncost = -secbuffdata['turncost']
        isCrit, turnatk = get_turnatk(player)
        atkvalue = secbuffdata['atkvalue']  # 列表
        skillsh = 0
        atkmsg = ''
        for value in atkvalue:
            atkmsg += f"{int(value * turnatk)}伤害、"
            skillsh += int(value * turnatk)

        if turncost == 0:
            turnmsg = '！'
        else:
            turnmsg = f"，休息{secbuffdata['turncost']}回合！"

        if isCrit:
            skillmsg = f"{player['道号']}发动技能：{secbuffdata['name']}，消耗气血{int(secbuffdata['hpcost'] * player['气血']) if secbuffdata['hpcost'] != 0 else 0}点、真元{int(secbuffdata['mpcost'] * player['exp']) if secbuffdata['mpcost'] != 0 else 0}点，{secbuffdata['desc']}并且发生了会心一击，造成{atkmsg[:-1]}{turnmsg}"
        else:
            skillmsg = f"{player['道号']}发动技能：{secbuffdata['name']}，消耗气血{int(secbuffdata['hpcost'] * player['气血']) if secbuffdata['hpcost'] != 0 else 0}点、真元{int(secbuffdata['mpcost'] * player['exp']) if secbuffdata['mpcost'] != 0 else 0}点，{secbuffdata['desc']}造成{atkmsg[:-1]}{turnmsg}"

        return skillmsg, skillsh, turncost

    elif secbuffdata['skill_type'] == 2:  # 持续伤害类型
        turncost = secbuffdata['turncost']
        isCrit, turnatk = get_turnatk(player)
        skillsh = int(secbuffdata['atkvalue'] * player['攻击'])  # 改动
        atkmsg = ''
        if isCrit:
            skillmsg = f"{player['道号']}发动技能：{secbuffdata['name']}，消耗气血{int(secbuffdata['hpcost'] * player['气血']) if secbuffdata['hpcost'] != 0 else 0}点、真元{int(secbuffdata['mpcost'] * player['exp']) if secbuffdata['mpcost'] != 0 else 0}点，{secbuffdata['desc']}并且发生了会心一击，造成{skillsh}点伤害，持续{turncost}回合！"
        else:
            skillmsg = f"{player['道号']}发动技能：{secbuffdata['name']}，消耗气血{int(secbuffdata['hpcost'] * player['气血']) if secbuffdata['hpcost'] != 0 else 0}点、真元{int(secbuffdata['mpcost'] * player['exp']) if secbuffdata['mpcost'] != 0 else 0}点，{secbuffdata['desc']}造成{skillsh}点伤害，持续{turncost}回合！"

        return skillmsg, skillsh, turncost

    elif secbuffdata['skill_type'] == 3:  # 持续buff类型
        turncost = secbuffdata['turncost']
        skillsh = secbuffdata['buffvalue']
        atkmsg = ''
        if secbuffdata['bufftype'] == 1:
            skillmsg = f"{player['道号']}发动技能：{secbuffdata['name']}，消耗气血{int(secbuffdata['hpcost'] * player['气血']) if secbuffdata['hpcost'] != 0 else 0}点、真元{int(secbuffdata['mpcost'] * player['exp']) if secbuffdata['mpcost'] != 0 else 0}点，{secbuffdata['desc']}攻击力增加{skillsh}倍，持续{turncost}回合！"
        elif secbuffdata['bufftype'] == 2:
            skillmsg = f"{player['道号']}发动技能：{secbuffdata['name']}，消耗气血{int(secbuffdata['hpcost'] * player['气血']) if secbuffdata['hpcost'] != 0 else 0}点、真元{int(secbuffdata['mpcost'] * player['exp']) if secbuffdata['mpcost'] != 0 else 0}点，{secbuffdata['desc']}获得{skillsh * 100}%的减伤，持续{turncost}回合！"

        return skillmsg, skillsh, turncost

    elif secbuffdata['skill_type'] == 4:  # 封印类技能
        turncost = secbuffdata['turncost']
        if random.randint(0, 100) <= secbuffdata['success']:  # 命中
            skillsh = True
            skillmsg = f"{player['道号']}发动技能：{secbuffdata['name']}，消耗气血{int(secbuffdata['hpcost'] * player['气血']) if secbuffdata['hpcost'] != 0 else 0}点、真元{int(secbuffdata['mpcost'] * player['exp']) if secbuffdata['mpcost'] != 0 else 0}点，使对手动弹不得,{secbuffdata['desc']}持续{turncost}回合！"
        else:  # 未命中
            skillsh = False
            skillmsg = f"{player['道号']}发动技能：{secbuffdata['name']}，消耗气血{int(secbuffdata['hpcost'] * player['气血']) if secbuffdata['hpcost'] != 0 else 0}点、真元{int(secbuffdata['mpcost'] * player['exp']) if secbuffdata['mpcost'] != 0 else 0}点，{secbuffdata['desc']}但是被对手躲避！"

        return skillmsg, skillsh, turncost
