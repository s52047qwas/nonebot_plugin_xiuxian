import datetime
import json
import random
from .xiuxian2_handle import XiuxianDateManage
from .read_buff import UserBuffDate

def Player_fight(player1: dict, player2: dict, type_in: 1):
        """
        回合制战斗
        type_in : 1 为完整返回战斗过程（未加）
        2：只返回战斗结果
        数据示例：
        {"user_id": None,"道号": None, "气血": None, "攻击": None, "真元": None, '会心':None, 'exp':None}
        """
        user1buffdate = UserBuffDate(player1['user_id'])#1号的buff信息
        user2buffdate = UserBuffDate(player2['user_id'])#2号的buff信息
        
        ###有技能，则开启技能模式
        player1_skil_open = False
        player2_skil_open = False
        if user1buffdate.get_user_sec_buff_data() != None:
            user1skilldate = user1buffdate.get_user_sec_buff_data()
            player1_skil_open = True
        if user2buffdate.get_user_sec_buff_data() != None:
            user2skilldate = user2buffdate.get_user_sec_buff_data()
            player2_skil_open = True
        
        msg1 = "{}发起攻击，造成了{}伤害\n"
        msg2 = "{}发起攻击，造成了{}伤害\n"

        play_list = []
        suc = None
        
        user1turnskip = True
        user2turnskip = True
        player1turncost = 0 #先设定为初始值 0
        player2turncost = 0 #先设定为初始值 0
        player1js = 1#减伤率
        player2js = 1#减伤率
        user1skillsh = 0
        user2skillsh = 0
        while True:
            
            if user1turnskip:#无需跳过回合             
                if player1_skil_open:
                    user1hpconst, user1mpcost, user1skill_type = get_skill_hp_mp_data(player1, user1skilldate)
                    
                    if player1turncost == 0:#没有持续性技能生效
                        player1js = 1
                        if isEnableUserSikll(player1, user1hpconst, user1mpcost, player1turncost):#满足技能要求，#此处为技能的第一次释放
                            skillmsg, user1skillsh, player1turncost = get_skill_sh_data(player1, user1skilldate)
                            if user1skill_type == 1:#直接伤害类技能
                                play_list.append(skillmsg)
                                player2['气血'] = player2['气血'] - int(user1skillsh * player2js)#玩家1的伤害 * 玩家2的减伤
                                play_list.append(f"{player2['道号']}剩余血量{player2['气血']}")
                            elif user1skill_type == 2:#持续性伤害技能
                                play_list.append(skillmsg)
                                player2['气血'] = player2['气血'] - int(user1skillsh * player2js)#玩家1的伤害 * 玩家2的减伤
                                play_list.append(f"{player2['道号']}剩余血量{player2['气血']}")
                            elif user1skill_type == 3:#buff类技能
                                user1buff_type = user1skilldate['bufftype']
                                if user1buff_type == 1:#攻击类buff
                                    isisCrit, player1_sh = get_turnatk(player1, user1skillsh)#判定是否暴击
                                    
                                    if isisCrit:
                                        msg1 = "{}发起会心一击，造成了{}伤害\n"
                                    
                                    play_list.append(skillmsg)
                                    play_list.append(msg1.format(player1['道号'], player1_sh))
                                    player2['气血'] = player2['气血'] - int(player1_sh * player2js)#玩家1的伤害 * 玩家2的减伤
                                    play_list.append(f"{player2['道号']}剩余血量{player2['气血']}")

                                    
                                elif user1buff_type == 2:#减伤类buff,需要在player2处判断
                                    isisCrit, player1_sh = get_turnatk(player1)#判定是否暴击
                                    if isisCrit:
                                        msg1 = "{}发起会心一击，造成了{}伤害\n"
                                    
                                    play_list.append(skillmsg)
                                    play_list.append(msg1.format(player1['道号'], player1_sh))
                                    player2['气血'] = player2['气血'] - int(player1_sh * player2js)#玩家1的伤害 * 玩家2的减伤
                                    play_list.append(f"{player2['道号']}剩余血量{player2['气血']}")
                                    player1js = 1 - user1skillsh
                                    
                        else:#没放技能
                            isisCrit, player1_sh = get_turnatk(player1)#判定是否暴击
                            if isisCrit:
                                msg1 = "{}发起会心一击，造成了{}伤害\n"
                            play_list.append(msg1.format(player1['道号'], player1_sh))
                            player2['气血'] = player2['气血'] - int(player1_sh * player2js)#玩家1的伤害 * 玩家2的减伤
                            play_list.append(f"{player2['道号']}剩余血量{player2['气血']}")
                                
                    else:#持续性技能判断,不是第一次
                        if user1skill_type == 2:#持续性伤害技能
                            player1turncost = player1turncost - 1
                            skillmsg  = get_persistent_skill_msg(player1['道号'], user1skilldate['name'], user1skillsh, player1turncost)
                            play_list.append(skillmsg)
                            
                            isisCrit, player1_sh = get_turnatk(player1)#判定是否暴击
                            if isisCrit:
                                msg1 = "{}发起会心一击，造成了{}伤害\n"
                                
                            play_list.append(msg1.format(player1['道号'], player1_sh))
                            player2['气血'] = player2['气血'] - int((user1skillsh + player1_sh) * player2js)#玩家1的伤害 * 玩家2的减伤,持续性伤害不影响普攻
                            play_list.append(f"{player2['道号']}剩余血量{player2['气血']}")

                        elif user1skill_type == 3:#buff类技能
                            user1buff_type = user1skilldate['bufftype']
                            if user1buff_type == 1:#攻击类buff
                                isisCrit, player1_sh = get_turnatk(player1, user1skillsh)#判定是否暴击
                                    
                                if isisCrit:
                                    msg1 = "{}发起会心一击，造成了{}伤害\n"
                                play_list.append(skillmsg)
                                play_list.append(msg1.format(player1['道号'], player1_sh))
                                player2['气血'] = player2['气血'] - int(player1_sh * player2js)#玩家1的伤害 * 玩家2的减伤
                                play_list.append(f"{player2['道号']}剩余血量{player2['气血']}")
                                player1turncost = player1turncost - 1

                                    
                            elif user1buff_type == 2:#减伤类buff,需要在player2处判断
                                isisCrit, player1_sh = get_turnatk(player1)#判定是否暴击
                                if isisCrit:
                                    msg1 = "{}发起会心一击，造成了{}伤害\n"
                                    
                                play_list.append(skillmsg)
                                play_list.append(msg1.format(player1['道号'], player1_sh))
                                player2['气血'] = player2['气血'] - int(player1_sh * player2js)#玩家1的伤害 * 玩家2的减伤
                                play_list.append(f"{player2['道号']}剩余血量{player2['气血']}")
                                player1js = 1 - user1skillsh
                                player1turncost = player1turncost - 1
                                
                                               
                else:#没有技能的derB
                    isisCrit, player1_sh = get_turnatk(player1)#判定是否暴击
                    if isisCrit:
                        msg1 = "{}发起会心一击，造成了{}伤害\n"
                    play_list.append(msg1.format(player1['道号'], player1_sh))
                    player2['气血'] = player2['气血'] - player1_sh
                    play_list.append(f"{player2['道号']}剩余血量{player2['气血']}")

                   
            if player2['气血'] <= 0:
                play_list.append("{}胜利".format(player1['道号']))
                suc = f"{player1['道号']}"
                # XiuxianDateManage().update_user_hp_mp(player2['user_id'], 1, player2['真元'])#先注释
                break            
            
            if player2turncost < 0:#休息为负数，如果休息，则跳过回合，正常是0
                user2turnskip = False
                player2turncost += 1
                user1turnskip = True
            
            if user2turnskip:#无需跳过回合             
                if player2_skil_open:
                    user2hpconst, user2mpcost, user2skill_type = get_skill_hp_mp_data(player2, user2skilldate)
                    if player2turncost == 0:#没有持续性技能生效
                        player2js = 1
                        if isEnableUserSikll(player2, user2hpconst, user2mpcost, player2turncost):#满足技能要求，#此处为技能的第一次释放
                            skillmsg, user2skillsh, player2turncost = get_skill_sh_data(player2, user2skilldate)
                            if user2skill_type == 1:#直接伤害类技能
                                play_list.append(skillmsg)
                                player1['气血'] = player1['气血'] - int(user2skillsh * player1js)#玩家2的伤害 * 玩家1的减伤
                                play_list.append(f"{player1['道号']}剩余血量{player1['气血']}")
                            elif user2skill_type == 2:#持续性伤害技能
                                play_list.append(skillmsg)
                                player1['气血'] = player1['气血'] - int(user2skillsh * player1js)#玩家2的伤害 * 玩家1的减伤
                                play_list.append(f"{player1['道号']}剩余血量{player1['气血']}")
                            elif user2skill_type == 3:#buff类技能
                                user2buff_type = user2skilldate['bufftype']
                                if user2buff_type == 1:#攻击类buff
                                    isisCrit, player2_sh = get_turnatk(player2, user2skillsh)#判定是否暴击
                                    
                                    if isisCrit:
                                        msg2 = "{}发起会心一击，造成了{}伤害\n"
                                    
                                    play_list.append(skillmsg)
                                    play_list.append(msg2.format(player1['道号'], player2_sh))
                                    player1['气血'] = player1['气血'] - int(player2_sh * player1js)#玩家2的伤害 * 玩家1的减伤
                                    play_list.append(f"{player1['道号']}剩余血量{player1['气血']}")

                                    
                                elif user1buff_type == 2:#减伤类buff,需要在player2处判断
                                    isisCrit, player2_sh = get_turnatk(player2)#判定是否暴击
                                    if isisCrit:
                                        msg2 = "{}发起会心一击，造成了{}伤害\n"
                                    
                                    play_list.append(skillmsg)
                                    play_list.append(msg2.format(player2['道号'], player2_sh))
                                    player1['气血'] = player1['气血'] - int(player2_sh * player1js)#玩家2的伤害 * 玩家1的减伤
                                    play_list.append(f"{player1['道号']}剩余血量{player1['气血']}")
                                    player2js = 1 - user2skillsh
                                    player2turncost = player2turncost - 1
                                    
                        else:#没放技能
                            isisCrit, player2_sh = get_turnatk(player2)#判定是否暴击
                            if isisCrit:
                                msg2 = "{}发起会心一击，造成了{}伤害\n"
                            play_list.append(msg1.format(player2['道号'], player2_sh))
                            player1['气血'] = player1['气血'] - int(player2_sh * player1js)#玩家2的伤害 * 玩家1的减伤
                            play_list.append(f"{player1['道号']}剩余血量{player1['气血']}")
                                
                    else:#持续性技能判断,不是第一次
                        if user2skill_type == 2:#持续性伤害技能
                            player2turncost = player2turncost - 1
                            skillmsg  = get_persistent_skill_msg(player2['道号'], user2skilldate['name'], user2skillsh, player2turncost)
                            play_list.append(skillmsg)
                            
                            isisCrit, player2_sh = get_turnatk(player2)#判定是否暴击
                            if isisCrit:
                                msg2 = "{}发起会心一击，造成了{}伤害\n"
                                
                            play_list.append(msg2.format(player2['道号'], player2_sh))
                            player1['气血'] = player1['气血'] - int((user2skillsh + player2_sh) * player1js)#玩家2的伤害 * 玩家1的减伤,持续性伤害不影响普攻
                            play_list.append(f"{player1['道号']}剩余血量{player1['气血']}")

                        elif user2skill_type == 3:#buff类技能
                            user2buff_type = user2skilldate['bufftype']
                            if user2buff_type == 2:#攻击类buff
                                isisCrit, player2_sh = get_turnatk(player2, user2skillsh)#判定是否暴击
                                    
                                if isisCrit:
                                    msg2 = "{}发起会心一击，造成了{}伤害\n"
                                play_list.append(skillmsg)
                                play_list.append(msg2.format(player2['道号'], player2_sh))
                                player1['气血'] = player1['气血'] - int(player2_sh * player1js)#玩家2的伤害 * 玩家1的减伤
                                play_list.append(f"{player1['道号']}剩余血量{player1['气血']}")
                                player2turncost = player2turncost - 1

                                    
                            elif user2buff_type == 2:#减伤类buff,需要在player2处判断
                                isisCrit, player1_sh = get_turnatk(player2)#判定是否暴击
                                if isisCrit:
                                    msg2 = "{}发起会心一击，造成了{}伤害\n"
                                    
                                play_list.append(skillmsg)
                                play_list.append(msg2.format(player2['道号'], player2_sh))
                                player1['气血'] = player1['气血'] - int(player2_sh * player1js)#玩家1的伤害 * 玩家2的减伤
                                play_list.append(f"{player1['道号']}剩余血量{player1['气血']}")
                                player2js = 1 - user2skillsh
                                player2turncost = player2turncost - 1    
                                           
                else:#没有技能的derB
                    isisCrit, player2_sh = get_turnatk(player2)#判定是否暴击
                    if isisCrit:
                        msg2 = "{}发起会心一击，造成了{}伤害\n"
                    play_list.append(msg1.format(player2['道号'], player2_sh))
                    player1['气血'] = player1['气血'] - player2_sh
                    play_list.append(f"{player1['道号']}剩余血量{player1['气血']}")
                    
            if player1['气血'] <= 0:
                play_list.append("{}胜利".format(player2['道号']))
                suc = f"{player2['道号']}"
                # XiuxianDateManage().update_user_hp_mp(player2['user_id'], 1, player2['真元'])#先注释
                break      
                 
            if player1turncost < 0:#休息为负数，如果休息，则跳过回合，正常是0
                user1turnskip = False
                player1turncost += 1
                user2turnskip = True
            
            if user1turnskip == False and user2turnskip == False:
                play_list.append('双方都动弹不得！')
                user1turnskip = True
                user2turnskip = True
                
            if player1['气血'] <= 0 or player2['气血'] <= 0:
                play_list.append("逻辑错误！！！")
                break

        return play_list, suc
    


def get_turnatk(player, buff = 0):
    isCrit = False
    turnatk = int(round(random.uniform(0.95, 1.05), 2) * (player['攻击'] * (buff + 1)))#攻击波动,buff是攻击buff
    if random.randint(0, 100) <= player['会心']:#会心判断
        turnatk = int(turnatk * 1.5)
        isCrit = True
    return isCrit, int(turnatk)


def isEnableUserSikll(player, hpcost, mpcost, turncost):#是否满足技能释放条件
    skill = False
    if turncost < 0:#判断是否进入休息状态
        return skill
    
    if player['气血'] > hpcost and player['真元'] >= mpcost:#判断血量、真元是否满足
        if random.randint(0, 100) <= 70:#随机概率释放技能
            skill = True
    return skill

def get_skill_hp_mp_data(player, secbuffdata):
    hpcost = int(secbuffdata['hpcost'] * player['气血']) if secbuffdata['hpcost'] != 0 else 0
    mpcost = int(secbuffdata['mpcost'] * player['exp']) if secbuffdata['mpcost'] != 0 else 0
    return hpcost, mpcost, secbuffdata['type']


def get_persistent_skill_msg(username, skillname, sh, turn):
    return f"{username}的持续性技能：{skillname}，造成{sh}伤害，剩余回合：{turn}！"

def get_skill_sh_data(player, secbuffdata):
    skillmsg = ''
    if secbuffdata['type'] == 1:#连续攻击类型
        turncost = -secbuffdata['turncost']
        isCrit, turnatk = get_turnatk(player)
        atkvalue = secbuffdata['atkvalue']#列表
        skillsh = 0
        atkmsg = ''
        for value in atkvalue:
            atkmsg += f"{int(value * turnatk)}伤害、"
            skillsh += int(value * turnatk)
           
        if isCrit:
            skillmsg = f"{player['道号']}发动技能：{secbuffdata['name']}，并且发生了会心一击，造成{atkmsg[:-1]}，休息{secbuffdata['turncost']}回合！"
        else:
            skillmsg = f"{player['道号']}发动技能：{secbuffdata['name']}，造成{atkmsg[:-1]}，休息{secbuffdata['turncost']}回合！"
            
        return skillmsg, skillsh, turncost

    elif secbuffdata['type'] == 2:#持续伤害类型
        turncost = secbuffdata['turncost']
        isCrit, turnatk = get_turnatk(player)
        skillsh = int(secbuffdata['atkvalue'] * player['攻击']) #改动
        atkmsg = ''
        if isCrit:
            skillmsg = f"{player['道号']}发动技能：{secbuffdata['name']}，并且发生了会心一击，造成{skillsh}点伤害，持续{turncost}回合！"
        else:
            skillmsg = f"{player['道号']}发动技能：{secbuffdata['name']}，造成{skillsh}点伤害，持续{turncost}回合！"
        
        return skillmsg, skillsh, turncost
            
    elif secbuffdata['type'] == 3:#持续buff类型
        turncost = secbuffdata['turncost']
        skillsh = secbuffdata['buffvalue']
        atkmsg = ''
        if secbuffdata['bufftype'] == 1:
            skillmsg = f"{player['道号']}发动技能：{secbuffdata['name']}，攻击力增加{skillsh}倍，持续{turncost}回合！"
        elif secbuffdata['bufftype'] == 2:
            skillmsg = f"{player['道号']}发动技能：{secbuffdata['name']}，获得{skillsh * 100}%的减伤，持续{turncost}回合！"
        
        return skillmsg, skillsh, turncost
    
    