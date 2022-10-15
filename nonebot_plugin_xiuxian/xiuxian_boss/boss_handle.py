from ..xiuxian2_handle import OtherSet, XiuxianDateManage
import json
import os
from pathlib import Path
import random

class BossDateManage(OtherSet):

    def player_fight(self, player: dict, boss: dict, type_in: 1):
        """
        回合制战斗
        type_in : 1 为完整返回战斗过程（未加）
        2：只返回战斗结果
        数据示例：
        {"道号": None, "气血": None, "攻击": None, "真元": None, '会心':None}
        """
        msg1 = "{}发起攻击，造成了{}伤害\n"
        msg2 = "{}发起攻击，造成了{}伤害\n"
        
        player['会心'] = 1
        boss['会心'] = 1.2

        play_list = []
        suc = None
        get_stone = 0
        sh = 0
        qx = boss['气血']
        while True:
            player_gj = int(round(random.uniform(0.95, 1.05), 2) * player['攻击'])
            if random.randint(0, 100) <= player['会心']:
                player_gj = int(player_gj * 1.5)
                msg1 = "{}发起会心一击，造成了{}伤害\n"

            boss_gj = int(round(random.uniform(0.95, 1.05), 2) * boss['攻击'])
            if random.randint(0, 100) <= boss['会心']:
                boss_gj = int(boss_gj * 1.5)
                msg2 = "{}发起会心一击，造成了{}伤害\n"

            # 造成的伤害
            # play1_sh: int = int(player1_gj) - player2['防御']
            # play2_sh: int = int(player2_gj) - player1['防御']
            
            player_sh: int = int(player_gj)
            boss_sh: int = int(boss_gj)

            # print(msg1.format(player1['道号'], play1_sh))
            play_list.append(msg1.format(player['道号'], player_sh))

            boss['气血'] = boss['气血'] - player_sh
            sh += player_sh
            # print(f"{player2['道号']}剩余血量{player2['气血']}")
            play_list.append(f"{boss['name']}剩余血量{boss['气血']}")
            ##更新boss信息
            # XiuxianDateManage().update_user_attribute(player2['user_id'], player2['气血'], player2['真元'], player2['攻击'])

            if boss['气血'] <= 0:
                # print("{}胜利".format(player1['道号']))
                play_list.append("{}胜利".format(player['道号']))
                suc = f"{player['道号']}"
                get_stone = int(boss['stone'] * (sh / qx))
                
                boss = None
                # XiuxianDateManage().update_user_attribute(player2['user_id'], 1, player2['真元'],
                #                                             player2['攻击'])
                break

            # print(msg2.format(player2['道号'], play2_sh))
            play_list.append(msg2.format(boss['name'], boss_sh))

            player['气血'] = player['气血'] - boss_sh
            # print(f"{player1['道号']}剩余血量{player1['气血']}\n")
            play_list.append(f"{player['道号']}剩余血量{player['气血']}\n")
            XiuxianDateManage().update_user_hp_mp(player['user_id'], player['气血'], player['真元'])

            if player['气血'] <= 0:
                # print("{}胜利".format(player2['道号']))
                play_list.append("{}胜利".format(boss['name']))
                suc = f"{boss['name']}"
                
                get_stone = int(boss['stone'] * (sh / qx))
                boss['stone'] = boss['stone'] - get_stone
                
                XiuxianDateManage().update_user_hp_mp(player['user_id'], 1, player['真元'])
                break

            if player['气血'] <= 0 or boss['气血'] <= 0:
                play_list.append("逻辑错误！！！")
                break

        return play_list, suc, boss, get_stone       
    




GROUPSJSONPATH = Path(__file__).parent
FILEPATH = GROUPSJSONPATH / 'groups.json'
def readf():
    if not os.path.exists(GROUPSJSONPATH):
        print("目录不存在，创建目录")
        os.makedirs(GROUPSJSONPATH)
        
    
    with open(FILEPATH, "r", encoding="UTF-8") as f:
        data = f.read()
    return json.loads(data)


def savef(data):
    if not os.path.exists(GROUPSJSONPATH):
        print("目录不存在，创建目录")
        os.makedirs(GROUPSJSONPATH)
    
    savemode = "w" if os.path.exists(FILEPATH) else "x"
    with open(FILEPATH, mode=savemode, encoding="UTF-8") as f:
        f.write(data)
        f.close
    return True