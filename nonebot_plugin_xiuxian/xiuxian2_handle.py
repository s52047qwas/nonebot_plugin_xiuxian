import datetime
import json
import random
import sqlite3
from collections import namedtuple
from pathlib import Path
from .data_source import jsondata
from .xiuxian_config import XiuConfig

DATABASE =Path() / "data" / "xiuxian"

xiuxian_data = namedtuple("xiuxian_data", ["no", "user_id", "linggen", "level"])

UserDate = namedtuple("UserDate", ["id", "user_id", "stone", "root","root_type","level","power","create_time","is_sign","exp","user_name","level_up_cd"])
UserCd = namedtuple("UserCd", [ "user_id", "type", "create_time", "scheduled_time"])


class XiuxianDateManage:
    def __init__(self):
        self.database_path = DATABASE
        if not self.database_path.exists():
            self.database_path.mkdir(parents=True)
            self.database_path /= "xiuxian.db"
            self.conn = sqlite3.connect(self.database_path)
            # self._create_file()
        else:
            self.database_path /= "xiuxian.db"
            self.conn = sqlite3.connect(self.database_path)
        print(f"数据库已连接！")
        # self._check_data()

    def close(self):
        self.conn.close()
        print("数据库关闭！")

    def _create_file(self) -> None:
        """创建数据库文件"""
        c = self.conn.cursor()
        c.execute('''CREATE TABLE User_xiuxian
                           (NO            INTEGER PRIMARY KEY UNIQUE,
                           USERID         TEXT     ,
                           level          INTEGER  ,
                           root           INTEGER
                           );''')
        c.execute('''''')
        c.execute('''''')
        self.conn.commit()

    def _check_data(self):
        """检查数据完整性"""
        c = self.conn.cursor()
        try:
            c.execute(f"select count(1) from user_cd")
        except:
            c.execute("""CREATE TABLE user_cd
                                    (user_id       INTEGER PRIMARY KEY UNIQUE,
                                    type           INTEGER,
                                    create_time    INTEGER,
                                    scheduled_time INTEGER);""")

        # sql = "select * FROM level where name=?"
        # c.execute(sql, ("融合灵根",))
        # result = c.fetchone()
        # if result:
        #     pass
        # else:
        #     c.execute(f"DELETE from level")
        #     c.executescript(f"""INSERT INTO "main"."level" ("name", "power") VALUES ('江湖好手', 100);
        # INSERT INTO "main"."level" ("name", "power") VALUES ('练气境初期', 1000);
        # INSERT INTO "main"."level" ("name", "power") VALUES ('练气境中期', 2000);
        # INSERT INTO "main"."level" ("name", "power") VALUES ('练气境圆满', 3000);
        # INSERT INTO "main"."level" ("name", "power") VALUES ('筑基境初期', 8000);
        # INSERT INTO "main"."level" ("name", "power") VALUES ('筑基境中期', 9000);
        # INSERT INTO "main"."level" ("name", "power") VALUES ('筑基境圆满', 10000);
        # INSERT INTO "main"."level" ("name", "power") VALUES ('伪灵根', 0.8);
        # INSERT INTO "main"."level" ("name", "power") VALUES ('真灵根', 1);
        # INSERT INTO "main"."level" ("name", "power") VALUES ('天灵根', 1.2);
        # INSERT INTO "main"."level" ("name", "power") VALUES ('变异灵根', 1.2);
        # INSERT INTO "main"."level" ("name", "power") VALUES ('超灵根', 1.4);
        # INSERT INTO "main"."level" ("name", "power") VALUES ('龙灵根', 1.3);
        # INSERT INTO "main"."level" ("name", "power") VALUES ('混沌灵根', 1.5);
        # INSERT INTO "main"."level" ("name", "power") VALUES ('融合灵根', 1.5);
        # INSERT INTO "main"."level" ("name", "power") VALUES ('结丹境初期', 20000);
        # INSERT INTO "main"."level" ("name", "power") VALUES ('结丹境中期', 40000);
        # INSERT INTO "main"."level" ("name", "power") VALUES ('结丹境圆满', 80000);
        # INSERT INTO "main"."level" ("name", "power") VALUES ('元婴境初期', 160000);
        # INSERT INTO "main"."level" ("name", "power") VALUES ('元婴境中期', 360000);
        # INSERT INTO "main"."level" ("name", "power") VALUES ('元婴境圆满', 720000);""")


    @classmethod
    def close_dbs(cls):
        XiuxianDateManage().close()

    def _create_user(self, user_id: str,root:str,type:str,power:str,create_time,user_name) -> None:
        """在数据库中创建用户并初始化"""
        c = self.conn.cursor()
        sql = f"INSERT INTO user_xiuxian (user_id,stone,root,root_type,level,power,create_time,user_name) VALUES (?,0,?,?,'江湖好手',?,?,?)"
        c.execute(sql, (user_id,root,type,power,create_time,user_name))
        self.conn.commit()


    def get_user_message(self,user_id):
        '''根据USER_ID获取用户信息'''
        cur = self.conn.cursor()
        sql = f"select * from user_xiuxian where user_id=?"
        cur.execute(sql, (user_id,))
        result = cur.fetchone()
        if not result:
            return None
        else:
            return UserDate(*result)

    def get_user_message2(self,user_id):
        '''根据user_name获取用户信息'''
        cur = self.conn.cursor()
        sql = f"select * from user_xiuxian where user_name=?"
        cur.execute(sql, (user_id,))
        result = cur.fetchone()
        if not result:
            return None
        else:
            return UserDate(*result)

    def create_user(self,user_id,*args):
        """校验用户是否存在"""
        cur = self.conn.cursor()
        sql = f"select * from user_xiuxian where user_id=?"
        cur.execute(sql, (user_id,))
        result = cur.fetchone()
        if not result:
            self._create_user(user_id,args[0],args[1],args[2],args[3],args[4])
            self.conn.commit()
            return '欢迎进入修仙世界的，你的灵根为：{},类型是：{},你的战力为：{},当前境界：江湖好手'.format(args[0], args[1], args[2],args[3])
        else:
            return '您已迈入修仙世界，输入【我的修仙信息】获取数据吧！'

    def get_sign(self,user_id):
        '''获取用户签到信息'''
        cur = self.conn.cursor()
        sql = f"select is_sign from user_xiuxian where user_id=?"
        cur.execute(sql, (user_id,))
        result = cur.fetchone()
        if not result:
            return '修仙界没有你的足迹，输入 我要修仙 加入修仙世界吧！'
        elif result[0]==0:
            ls = random.randint(XiuConfig().sign_in_lingshi_lower_limit,XiuConfig().sign_in_lingshi_upper_limit)
            exp = random.randint(XiuConfig().sign_in_xiuwei_lower_limit,XiuConfig().sign_in_xiuwei_upper_limit)
            sql2 = f"UPDATE user_xiuxian SET is_sign=1,stone=stone+?,exp=exp+? WHERE user_id=?"
            cur.execute(sql2, (ls, exp,user_id))
            self.conn.commit()
            return '签到成功，获取{}块灵石,修为增加{}！'.format(ls,exp)
        elif result[0]==1:
            return '贪心的人是不会有好运的！'

    def ramaker(self,lg,type,user_id):
        """洗灵根"""
        cur = self.conn.cursor()

        # 查灵石
        sql_s = f"SELECT stone FROM user_xiuxian WHERE user_id=?"
        cur.execute(sql_s, (user_id,))
        result = cur.fetchone()
        if result[0]>=XiuConfig().remake:
            sql = f"UPDATE user_xiuxian SET root=?,root_type=?,stone=stone-? WHERE user_id=?"
            cur.execute(sql, (lg, type, XiuConfig().remake, user_id))
            self.conn.commit()

            self.update_power2(user_id)
            return "逆天之行，重获新生，新的灵根为：{}，类型为：{}".format(lg,type)
        else:
            return "你的灵石还不够呢，快去赚点灵石吧！"


    def get_root_rate(self,name):
        """获取灵根倍率"""
        data = jsondata.root_data()
        return data[name]['type_speeds']

    def get_level_power(self,name):
        """获取境界倍率"""
        data = jsondata.level_data()
        return data[name]['power']


    def update_power2(self,user_id) -> None:
        """更新战力"""
        UserMessage = self.get_user_message(user_id)
        cur = self.conn.cursor()
        level = jsondata.level_data()
        root = jsondata.root_data()
        sql = f"UPDATE user_xiuxian SET power=round(exp*?*?,0) WHERE user_id=?"
        cur.execute(sql, (root[UserMessage.root_type]["type_speeds"], level[UserMessage.level]["spend"], user_id))
        self.conn.commit()

    def update_ls(self, user_id, price, key):
        """更新灵石  1为增加，2为减少"""
        cur = self.conn.cursor()

        if key == 1:
            sql = f"UPDATE user_xiuxian SET stone=stone+? WHERE user_id=?"
            cur.execute(sql, (price, user_id))
            self.conn.commit()
        elif key == 2:
            sql = f"UPDATE user_xiuxian SET stone=stone-? WHERE user_id=?"
            cur.execute(sql, (price, user_id))
            self.conn.commit()


    def get_ls_rank(self):
        """灵石排行榜"""
        sql = f"SELECT user_id,stone FROM user_xiuxian  WHERE stone>0 ORDER BY stone DESC LIMIT 5"
        cur = self.conn.cursor()
        cur.execute(sql,)
        result = cur.fetchall()
        return result


    def singh_remake(self):
        """重置签到"""
        sql = f"UPDATE user_xiuxian SET is_sign=0"
        cur = self.conn.cursor()
        cur.execute(sql, )
        self.conn.commit()

    def update_user_name(self,user_id,user_name):
        """更新用户道号"""
        cur = self.conn.cursor()
        get_name = f"select user_name from user_xiuxian where user_name=?"
        cur.execute(get_name, (user_name,))
        result = cur.fetchone()
        if result:
            return "已存在该道号！"
        else:
            sql = f"UPDATE user_xiuxian SET user_name=? where user_id=?"

            cur.execute(sql,(user_name, user_id))
            self.conn.commit()
            return '道友的道号更新成功拉~'

    def updata_level_cd(self,user_id):
        """更新破镜CD"""
        sql = f"UPDATE user_xiuxian SET level_up_cd=? where user_id=?"
        cur = self.conn.cursor()
        now_time = datetime.datetime.now()
        cur.execute(sql, (now_time, user_id))
        self.conn.commit()

    def updata_level(self,user_id,level_name):
        """更新境界"""
        sql = f"UPDATE user_xiuxian SET level=? where user_id=?"
        cur = self.conn.cursor()
        cur.execute(sql, (level_name, user_id))
        self.conn.commit()

    def get_user_cd(self, user_id):
        """
        获取用户操作CD
        :param user_id: QQ
        """
        sql = f"SELECT * FROM user_cd  WHERE user_id=?"
        cur = self.conn.cursor()
        cur.execute(sql, (user_id,))
        result = cur.fetchone()
        if result:
            return UserCd(*result)
        else:
            self.insert_user_cd(user_id,)
            return None

    def insert_user_cd(self, user_id) -> None:
        """
        添加用户至CD表
        :param user_id: qq
        :return:
        """
        sql = f"INSERT INTO user_cd (user_id) VALUES (?)"
        cur = self.conn.cursor()
        cur.execute(sql, (user_id,))
        self.conn.commit()

    def in_closing(self,user_id, the_type):
        """
        更新用户操作CD
        :param user_id: qq
        :param the_type: 0:无状态  1：闭关中  2：历练中
        :param the_time: 本次操作的时长
        :return:
        """
        if the_type == 1:
            now_time = datetime.datetime.now()
        elif the_type == 0:
            now_time = 0
        elif the_type == 2:
            now_time = datetime.datetime.now()
        # scheduled_time = datetime.datetime.now() + datetime.timedelta(minutes=int(the_time))
        sql = f"UPDATE user_cd SET type=?,create_time=? where user_id=?"
        cur = self.conn.cursor()
        cur.execute(sql, (the_type, now_time, user_id))
        self.conn.commit()

    def out_closing(self,user_id, the_type):
        """出关状态更新"""
        pass

    def update_exp(self,user_id,exp):
        """增加修为"""
        sql = f"UPDATE user_xiuxian SET exp=exp+? where user_id=?"
        cur = self.conn.cursor()
        cur.execute(sql, (exp, user_id))
        self.conn.commit()

    def update_j_exp(self,user_id,exp):
        """减少修为"""
        sql = f"UPDATE user_xiuxian SET exp=exp-? where user_id=?"
        cur = self.conn.cursor()
        cur.execute(sql, (exp, user_id))
        self.conn.commit()


    def realm_top(self):
        """境界排行榜"""
        sql = f"""SELECT user_name,level,exp FROM user_xiuxian 
        WHERE user_name is NOT NULL
        ORDER BY CASE
        WHEN level = '渡劫境圆满' THEN '01'
        WHEN level = '渡劫境中期' THEN '02'
        WHEN level = '渡劫境初期' THEN '03'
        WHEN level = '大乘境圆满' THEN '04'
        WHEN level = '大乘境中期' THEN '05'
        WHEN level = '大乘境初期' THEN '06'
        WHEN level = '合体境圆满' THEN '07'
        WHEN level = '合体境中期' THEN '08'
        WHEN level = '合体境初期' THEN '09'
        WHEN level = '炼虚境圆满' THEN '10'
        WHEN level = '炼虚境中期' THEN '11'
        WHEN level = '炼虚境初期' THEN '12'
        WHEN level = '化神境圆满' THEN '13'
        WHEN level = '化神境中期' THEN '14'
        WHEN level = '化神境初期' THEN '15'
        WHEN level = '元婴境圆满' THEN '16'
        WHEN level = '元婴境中期' THEN '17'
        WHEN level = '元婴境初期' THEN '18'
        WHEN level = '结丹境圆满' THEN '19'
        WHEN level = '结丹境中期' THEN '20'
        WHEN level = '结丹境初期' THEN '21'
        WHEN level = '筑基境圆满' THEN '22'
        WHEN level = '筑基境中期' THEN '23'
        WHEN level = '筑基境初期' THEN '24'
        WHEN level = '练气境圆满' THEN '25'
        WHEN level = '练气境中期' THEN '26'
        WHEN level = '练气境初期' THEN '27'
        WHEN level = '江湖好手' THEN '28'
        ELSE level END ASC,exp DESC LIMIT 10"""
        cur = self.conn.cursor()
        cur.execute(sql, )
        result = cur.fetchall()
        mess = f"✨位面境界排行榜TOP10✨\n"
        num = 0
        for i in result:
            num += 1
            mess += f"第{num}位 {i[0]} {i[1]},修为{i[2]}\n"

        return mess

    def stone_top(self):
        sql = f"SELECT user_name,stone FROM user_xiuxian WHERE user_name is NOT NULL ORDER BY stone DESC LIMIT 10"
        cur = self.conn.cursor()
        cur.execute(sql, )
        result = cur.fetchall()
        mess = f"✨位面灵石排行榜TOP10✨\n"
        num = 0
        for i in result:
            num += 1
            mess += f"第{num}位  {i[0]}  灵石：{i[1]}枚\n"

        return mess

    def power_top(self):
        """战力排行榜"""
        sql = f"SELECT user_name,power FROM user_xiuxian WHERE user_name is NOT NULL ORDER BY power DESC LIMIT 10"
        cur = self.conn.cursor()
        cur.execute(sql, )
        result = cur.fetchall()
        mess = f"✨位面战力排行榜TOP10✨\n"
        num = 0
        for i in result:
            num += 1
            mess += f"第{num}位  {i[0]}  战力：{i[1]}\n"

        return mess

    def do_work(self,user_id, the_type, sc_time=None):
        """
        更新用户操作CD
        :param sc_time: 任务
        :param user_id: qq
        :param the_type: 0:无状态  1：闭关中  2：历练中
        :param the_time: 本次操作的时长
        :return:
        """
        now_time = None
        if the_type == 1:
            now_time = datetime.datetime.now()
        elif the_type == 0:
            now_time = 0
        elif the_type == 2:
            now_time = datetime.datetime.now()

        sql = f"UPDATE user_cd SET type=?,create_time=?,scheduled_time=? where user_id=?"
        cur = self.conn.cursor()
        cur.execute(sql, (the_type, now_time, sc_time, user_id))
        self.conn.commit()



class XiuxianJsonDate:
    def __init__(self):
        self.root_jsonpath = DATABASE / "灵根.json"
        self.level_jsonpath = DATABASE / "突破概率.json"
        self.do_work_jsonpath = DATABASE / "悬赏令.json"


    def beifen_linggen_get(self):
        with open(self.root_jsonpath, 'r', encoding='utf-8') as e:
            a = e.read()
            data = json.loads(a)
            lg = random.choice(data)
            return lg['name'], lg['type']

    def level_rate(self, level):
        with open(self.level_jsonpath, 'r', encoding='utf-8') as e:
            a = e.read()
            data = json.loads(a)
            return data[0][level]


    def linggen_get(self):
        """获取灵根信息"""
        # with open(self.root_jsonpath, 'r', encoding='utf-8') as e:
        #     file_data = e.read()
        #     data = json.loads(file_data)
        data = jsondata.root_data()
        rate_dict = {}
        for i, v in data.items():
            rate_dict[i] = v["type_rate"]
        lgen = OtherSet().calculated(rate_dict)
        if data[lgen]["type_flag"]:
            flag = random.choice(data[lgen]["type_flag"])
            root = random.sample(data[lgen]["type_list"], flag)
            msg = ""
            for j in root:
                if j == root[-1]:
                    msg += j
                    break
                msg += (j + "、")

            return msg + '属性灵根', lgen
        else:
            root = random.choice(data[lgen]["type_list"])
            return root, lgen


    def do_work(self,key,work_list=None,name=None):
        """悬赏令获取"""
        # with open(self.do_work_jsonpath, 'r', encoding='utf-8') as e:
        #     a = e.read()
        #     data = json.loads(a)
        data = jsondata.reward_that_data()
        print("111",data)
        print(type(data))
        if key == 0:   # 如果没有获取过，则返回悬赏令
            get_work_list = []
            for i in data:
                name = random.choice(list(data[i].keys()))
                get_work_list.append([name, data[i][name]["rate"], data[i][name]["succeed_thank"], data[i][name]["time"]])
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


            if random.randint(1, 100) <= work_event["rate"]:
                return random.choice(work_event["succeed"]), work_event["succeed_thank"]
            else:
                return random.choice(work_event["fail"]), work_event["fail_thank"]


class OtherSet(XiuConfig):

    def __init__(self):
        super().__init__()

    def set_closing_type(self,user_level):
        list_all = len(self.level) - 1
        now_index = self.level.index(user_level)
        if list_all == now_index:
            return "道友已是最高境界，无法修炼了！"
        is_updata_level = self.level[now_index + 1]
        need_exp = XiuxianDateManage().get_level_power(is_updata_level)
        return need_exp

    def get_type(self,user_exp,rate,user_level):
        list_all = len(self.level) - 1
        now_index = self.level.index(user_level)
        if list_all == now_index:
            return "道友已是最高境界，无法突破！"

        is_updata_level = self.level[now_index + 1]
        need_exp = XiuxianDateManage().get_level_power(is_updata_level)

        #判断修为是否足够突破
        if user_exp >= need_exp:
            pass
        else:
            return "道友的修为不足以突破！距离下次突破需要{}修为！突破境界为：{}".format(need_exp-user_exp,is_updata_level)

        success_rate = True if random.randint(0, 100) < rate else False

        if success_rate:

            return [self.level[now_index + 1]]
        else:
            return '失败'

    def calculated(self,rate: dict) -> str:
        """
        根据概率计算，轮盘型
        :rate:格式{"数据名"："获取几率"}
        :return: 数据名
        """

        get_list = []  # 概率区间存放

        n = 1
        for name, value in rate.items():  # 生成数据区间
            value_rate = int(value)
            list_rate = [_i for _i in range(n, value_rate + n)]
            get_list.append(list_rate)
            n += value_rate

        now_n = n - 1
        get_random = random.randint(1, now_n)  # 抽取随机数

        index_num = None
        for list_r in get_list:
            if get_random in list_r:  # 判断随机在那个区间
                index_num = get_list.index(list_r)
                break

        return list(rate.keys())[index_num]

    def date_diff(self,new_time,old_time):
        """计算日期差"""
        if isinstance(new_time,datetime.datetime):
            pass
        else:
            new_time = datetime.datetime.strptime(new_time, '%Y-%m-%d %H:%M:%S.%f')

        if isinstance(old_time,datetime.datetime):
            pass
        else:
            old_time = datetime.datetime.strptime(old_time, '%Y-%m-%d %H:%M:%S.%f')

        day = (new_time - old_time).days
        sec = (new_time - old_time).seconds

        return (day * 24 * 60 * 60) + sec

    def fight(self,player1=None,player2=None):
        player1 = {'HP': 100,
                   "ROOT_RATE": 1,
                   "LEVEL_RATE": 1,
                   "COMBO": 0,
                   "ATK": 12,
                   "AC": 20}

        player2 = {'HP': 100,
                   "ROOT_RATE": 1.2,
                   "LEVEL_RATE": 1,
                   "COMBO": 0,
                   "ATK": 10,
                   "AC": 19}

        HP_SEND = True
        while HP_SEND is True:
            player1_gj = (random.randint(1, 10) + player1['ATK']) * player1["ROOT_RATE"] * player1["LEVEL_RATE"]
            player2_gj = (random.randint(1, 10) + player2['ATK']) * player2["ROOT_RATE"] * player2["LEVEL_RATE"]

            player2['HP'] = player2['HP'] - (int(player1_gj) - player2["AC"])
            print(player2['HP'])
            HP_SEND = False
        else:
            print('222')
            
    def get_power_rate(self, mind, other):
        power_rate = mind / (other + mind)
        if power_rate >= 9.5:
            return "道友偷窃小辈实属天道所不齿！"
        elif power_rate <= 0.05:
            return "道友请不要不自量力！"
        else:
            return int(power_rate * 100)



if __name__ == '__main__':
    print(OtherSet().date_diff("2022-09-08 00:42:56.740255","2022-09-08 00:42:56.740255"))
    # paths = r"G:\yuzi_bot\yuzi_bot\data\xiuxian\悬赏令.json"
    # with open(paths, 'r', encoding='utf-8') as e:
    #     a = e.read()
    #     data = json.loads(a)
    #     get_work_list = []
    #     for i in data:
    #         name = random.choice(list(data[i].keys()))
    #         get_work_list.append([name,data[i][name]["rate"],data[i][name]["succeed_thank"]])
    #     print(get_work_list)
    #
    #     work_event = None
    #     for i, v in data.items():
    #         for vk, vv in v.items():
    #             if vk == get_work_list[0][0]:
    #                 work_event = vv
    #
    #     print(work_event["rate"])
    #     if random.randint(1, 100) <= work_event["rate"]:
    #         print(random.choice( work_event["succeed"]), work_event["succeed_thank"])
    #     else:
    #         print (random.choice(work_event["fail"]), work_event["fail_thank"])

#     apath = r"G:\yuzi_bot\yuzi_bot\data\xiuxian\xiuxian.db"
#     conn = sqlite3.connect(apath)
#     sql = f"""SELECT user_name,level,exp FROM user_xiuxian
# WHERE user_name is NOT NULL
# ORDER BY CASE
# WHEN level = '筑基境圆满' THEN '1'
# WHEN level = '筑基境中期' THEN '2'
# WHEN level = '筑基境初期' THEN '3'
# WHEN level = '练气境圆满' THEN '4'
# WHEN level = '练气境中期' THEN '5'
# WHEN level = '练气境初期' THEN '6'
# WHEN level = '江湖好手' THEN '7'
# ELSE level END ASC,exp DESC LIMIT 5"""
#     cur = conn.cursor()
#     cur.execute(sql,)
#     result = cur.fetchall()
#     mess = f"位面境界排行榜TOP5\n"
#     num=0
#     for i in result:
#         num+=1
#         mess += F"TOP{num}:{i[0]},境界：{i[1]},修为：{i[2]}\n"
#
#     print(mess)
