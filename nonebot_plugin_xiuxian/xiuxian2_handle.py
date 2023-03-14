import datetime
import json
import random
import sqlite3
from collections import namedtuple
from pathlib import Path

from nonebot.log import logger

from .data_source import jsondata
from .xiuxian_config import XiuConfig

DATABASE = Path() / "data" / "xiuxian"

xiuxian_data = namedtuple("xiuxian_data", ["no", "user_id", "linggen", "level"])

UserDate = namedtuple("UserDate",
                      ["id", "user_id", "stone", "root", "root_type", "level", "power", "create_time", "is_sign", "exp",
                       "user_name", "level_up_cd", "level_up_rate", "sect_id", "sect_position", "hp", "mp", "atk", "atkpractice",
                       "sect_task", "sect_contribution", "sect_elixir_get", "blessed_spot_flag", "blessed_spot_name"])

UserCd = namedtuple("UserCd", ["user_id", "type", "create_time", "scheduled_time"])

SectInfo = namedtuple("SectInfo",
                      ["sect_id", "sect_name", "sect_owner", "sect_scale", "sect_used_stone", "sect_fairyland",
                       "sect_materials", "mainbuff", "secbuff", "elixir_room_level"])
BuffInfo = namedtuple("BuffInfo",
                      ["id", "user_id", "main_buff", "sec_buff", "faqi_buff", "fabao_weapon", "armor_buff", "atk_buff", "blessed_spot"])

back = namedtuple("back", ["user_id", "goods_id", "goods_name", "goods_type", "goods_num", "create_time", "update_time",
                           "remake", "day_num", "all_num", "action_time", "state", "bind_num"])

num = '578043031'


class XiuxianDateManage:
    global num
    _instance = {}
    _has_init = {}

    def __new__(cls):
        if cls._instance.get(num) is None:
            cls._instance[num] = super(XiuxianDateManage, cls).__new__(cls)
        return cls._instance[num]

    def __init__(self):
        if not self._has_init.get(num):
            self._has_init[num] = True
            self.database_path = DATABASE
            if not self.database_path.exists():
                self.database_path.mkdir(parents=True)
                self.database_path /= "xiuxian.db"
                self.conn = sqlite3.connect(self.database_path)
                # self._create_file()
            else:
                self.database_path /= "xiuxian.db"
                self.conn = sqlite3.connect(self.database_path)
            logger.info(f"数据库已连接！")
            self._check_data()

    def close(self):
        self.conn.close()
        logger.info(f"数据库关闭！")

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

        for i in XiuConfig().sql_table:
            if i == "user_xiuxian":
                try:
                    c.execute(f"select count(1) from {i}")
                except sqlite3.OperationalError:
                    c.execute("""CREATE TABLE "user_xiuxian" (
      "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
      "user_id" INTEGER NOT NULL,
      "stone" integer DEFAULT 0,
      "root" TEXT,
      "root_type" TEXT,
      "level" TEXT,
      "power" integer DEFAULT 0,
      "create_time" integer,
      "is_sign" integer DEFAULT 0,
      "exp" integer DEFAULT 0,
      "user_name" TEXT DEFAULT NULL,
      "level_up_cd" integer DEFAULT NULL,
      "level_up_rate" integer DEFAULT 0
    );""")
            elif i == "user_cd":
                try:
                    c.execute(f"select count(1) from {i}")
                except sqlite3.OperationalError:
                    c.execute("""CREATE TABLE "user_cd" (
  "user_id" INTEGER NOT NULL,
  "type" integer DEFAULT 0,
  "create_time" integer DEFAULT NULL,
  "scheduled_time" integer,
  PRIMARY KEY ("user_id")
);""")
            elif i == "sects":
                try:
                    c.execute(f"select count(1) from {i}")
                except sqlite3.OperationalError:
                    c.execute("""CREATE TABLE "sects" (
  "sect_id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
  "sect_name" TEXT NOT NULL,
  "sect_owner" integer,
  "sect_scale" integer NOT NULL,
  "sect_used_stone" integer,
  "sect_fairyland" integer
);""")
            elif i == "back":
                try:
                    c.execute(f"select count(1) from {i}")
                except sqlite3.OperationalError:
                    pass
                    c.execute("""CREATE TABLE "back" (
  "user_id" INTEGER NOT NULL,
  "goods_id" INTEGER NOT NULL,
  "goods_name" TEXT,
  "goods_type" TEXT,
  "goods_num" INTEGER,
  "create_time" TEXT,
  "update_time" TEXT,
  "remake" TEXT,
  "day_num" INTEGER DEFAULT 0,
  "all_num" INTEGER DEFAULT 0,
  "action_time" TEXT,
  "state" INTEGER DEFAULT 0
);""")

            elif i == "BuffInfo":
                try:
                    c.execute(f"select count(1) from {i}")
                except sqlite3.OperationalError:
                    c.execute("""CREATE TABLE "BuffInfo" (
  "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
  "user_id" integer DEFAULT 0,
  "main_buff" integer DEFAULT 0,
  "sec_buff" integer DEFAULT 0,
  "faqi_buff" integer DEFAULT 0,
  "fabao_weapon" integer DEFAULT 0
);""")
                    

        for i in XiuConfig().sql_user_xiuxian:
            try:
                c.execute(f"select {i} from user_xiuxian")
            except sqlite3.OperationalError:
                sql = f"ALTER TABLE user_xiuxian ADD COLUMN {i} INTEGER DEFAULT 0;"
                print(sql)
                c.execute(sql)
        
        for s in XiuConfig().sql_sects:
            try:
                c.execute(f"select {s} from sects")
            except sqlite3.OperationalError:
                sql = f"ALTER TABLE sects ADD COLUMN {s} INTEGER DEFAULT 0;"
                print(sql)
                c.execute(sql)
        
        for m in XiuConfig().sql_buff:
            try:
                c.execute(f"select {m} from BuffInfo")
            except sqlite3.OperationalError:
                sql = f"ALTER TABLE BuffInfo ADD COLUMN {m} INTEGER DEFAULT 0;"
                print(sql)
                c.execute(sql)
                
        for b in XiuConfig().sql_back:
            try:
                c.execute(f"select {b} from back")
            except sqlite3.OperationalError:
                sql = f"ALTER TABLE back ADD COLUMN {b} INTEGER DEFAULT 0;"
                print(sql)
                c.execute(sql)

        self.conn.commit()

    @classmethod
    def close_dbs(cls):
        XiuxianDateManage().close()

    def _create_user(self, user_id: str, root: str, type: str, power: str, create_time, user_name) -> None:
        """在数据库中创建用户并初始化"""
        c = self.conn.cursor()
        sql = f"INSERT INTO user_xiuxian (user_id,stone,root,root_type,level,power,create_time,user_name,exp) VALUES (?,0,?,?,'江湖好手',?,?,?,100)"
        c.execute(sql, (user_id, root, type, power, create_time, user_name))
        self.conn.commit()

    def get_user_message(self, user_id):
        """根据USER_ID获取用户信息，不获取功法加成"""
        cur = self.conn.cursor()
        sql = f"select * from user_xiuxian where user_id=?"
        cur.execute(sql, (user_id,))
        result = cur.fetchone()
        if not result:
            return None
        else:
            return UserDate(*result)

    def get_user_real_info(self, user_id):
        """根据USER_ID获取用户信息，获取功法加成"""
        cur = self.conn.cursor()
        sql = f"select * from user_xiuxian where user_id=?"
        cur.execute(sql, (user_id,))
        result = cur.fetchone()
        if not result:
            return None
        else:
            return UserDate(*final_user_data(result))


    def get_sect_info(self, sect_id):
        """
        通过宗门编号获取宗门信息
        :param sect_id: 宗门编号
        :return:
        """
        cur = self.conn.cursor()
        sql = f"select * from sects where sect_id=?"
        cur.execute(sql, (sect_id,))
        result = cur.fetchone()
        if not result:
            return None
        else:
            return SectInfo(*result)

    def get_user_message2(self, user_id):
        '''根据user_name获取用户信息'''
        cur = self.conn.cursor()
        sql = f"select * from user_xiuxian where user_name=?"
        cur.execute(sql, (user_id,))
        result = cur.fetchone()
        if not result:
            return None
        else:
            return UserDate(*result)

    def create_user(self, user_id, *args):
        """校验用户是否存在"""
        cur = self.conn.cursor()
        sql = f"select * from user_xiuxian where user_id=?"
        cur.execute(sql, (user_id,))
        result = cur.fetchone()
        if not result:
            self._create_user(user_id, args[0], args[1], args[2], args[3], args[4])
            self.conn.commit()
            return '欢迎进入修仙世界的，你的灵根为：{},类型是：{},你的战力为：{},当前境界：江湖好手'.format(args[0], args[1], args[2], args[3])
        else:
            return '您已迈入修仙世界，输入【我的修仙信息】获取数据吧！'

    def get_sign(self, user_id):
        '''获取用户签到信息'''
        cur = self.conn.cursor()
        sql = f"select is_sign from user_xiuxian where user_id=?"
        cur.execute(sql, (user_id,))
        result = cur.fetchone()
        if not result:
            return '修仙界没有你的足迹，输入 我要修仙 加入修仙世界吧！'
        elif result[0] == 0:
            ls = random.randint(XiuConfig().sign_in_lingshi_lower_limit, XiuConfig().sign_in_lingshi_upper_limit)
            exp = random.randint(XiuConfig().sign_in_xiuwei_lower_limit, XiuConfig().sign_in_xiuwei_upper_limit)
            sql2 = f"UPDATE user_xiuxian SET is_sign=1,stone=stone+?,exp=exp+? WHERE user_id=?"
            cur.execute(sql2, (ls, exp, user_id))
            self.conn.commit()
            return '签到成功，获取{}块灵石,修为增加{}！'.format(ls, exp)
        elif result[0] == 1:
            return '贪心的人是不会有好运的！'

    def ramaker(self, lg, type, user_id):
        """洗灵根"""
        cur = self.conn.cursor()

        # 查灵石
        sql_s = f"SELECT stone FROM user_xiuxian WHERE user_id=?"
        cur.execute(sql_s, (user_id,))
        result = cur.fetchone()
        if result[0] >= XiuConfig().remake:
            sql = f"UPDATE user_xiuxian SET root=?,root_type=?,stone=stone-? WHERE user_id=?"
            cur.execute(sql, (lg, type, XiuConfig().remake, user_id))
            self.conn.commit()

            self.update_power2(user_id)
            return "逆天之行，重获新生，新的灵根为：{}，类型为：{}".format(lg, type)
        else:
            return "你的灵石还不够呢，快去赚点灵石吧！"

    def get_root_rate(self, name):
        """获取灵根倍率"""
        data = jsondata.root_data()
        return data[name]['type_speeds']

    def get_level_power(self, name):
        """获取境界倍率"""
        data = jsondata.level_data()
        return data[name]['power']

    def update_power2(self, user_id) -> None:
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

    def update_root(self, user_id, key):
        """更新灵根  1为混沌，2为融合，3为超，4为龙，5为天"""
        cur = self.conn.cursor()
        print(user_id)
        print(key)

        if int(key) == 1:
            sql = f"UPDATE user_xiuxian SET root=?,root_type=? WHERE user_id=?"
            cur.execute(sql, ("全属性灵根", "混沌灵根", user_id))
            self.conn.commit()
        elif int(key) == 2:
            sql = f"UPDATE user_xiuxian SET root=?,root_type=? WHERE user_id=?"
            cur.execute(sql, ("融合万物灵根", "融合灵根", user_id))
            self.conn.commit()
        elif int(key) == 3:
            sql = f"UPDATE user_xiuxian SET root=?,root_type=? WHERE user_id=?"
            cur.execute(sql, ("月灵根", "超灵根", user_id))
            self.conn.commit()
        elif int(key) == 4:
            sql = f"UPDATE user_xiuxian SET root=?,root_type=? WHERE user_id=?"
            cur.execute(sql, ("言灵灵根", "龙灵根", user_id))
            self.conn.commit()
        elif int(key) == 5:
            sql = f"UPDATE user_xiuxian SET root=?,root_type=? WHERE user_id=?"
            cur.execute(sql, ("金灵根", "天灵根", user_id))
            self.conn.commit()            
            
    def update_ls_all(self, price):
        """所有用户增加灵石"""
        cur = self.conn.cursor()
        sql = f"UPDATE user_xiuxian SET stone=stone+?"
        cur.execute(sql, (price,))
        self.conn.commit()


    def get_ls_rank(self):
        """灵石排行榜"""
        sql = f"SELECT user_id,stone FROM user_xiuxian  WHERE stone>0 ORDER BY stone DESC LIMIT 5"
        cur = self.conn.cursor()
        cur.execute(sql, )
        result = cur.fetchall()
        return result

    def singh_remake(self):
        """重置签到"""
        sql = f"UPDATE user_xiuxian SET is_sign=0"
        cur = self.conn.cursor()
        cur.execute(sql, )
        self.conn.commit()

    def update_user_name(self, user_id, user_name):
        """更新用户道号"""
        cur = self.conn.cursor()
        get_name = f"select user_name from user_xiuxian where user_name=?"
        cur.execute(get_name, (user_name,))
        result = cur.fetchone()
        if result:
            return "已存在该道号！"
        else:
            sql = f"UPDATE user_xiuxian SET user_name=? where user_id=?"

            cur.execute(sql, (user_name, user_id))
            self.conn.commit()
            return '道友的道号更新成功拉~'

    def updata_level_cd(self, user_id):
        """更新破镜CD"""
        sql = f"UPDATE user_xiuxian SET level_up_cd=? where user_id=?"
        cur = self.conn.cursor()
        now_time = datetime.datetime.now()
        cur.execute(sql, (now_time, user_id))
        self.conn.commit()

    def updata_level(self, user_id, level_name):
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
            self.insert_user_cd(user_id, )
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

    def create_sect(self, user_id, sect_name) -> None:
        """
        创建宗门
        :param user_id:qq
        :param sect_name:宗门名称
        :return:
        """
        sql = f"INSERT INTO sects(sect_name, sect_owner, sect_scale, sect_used_stone) VALUES (?,?,0,0)"
        cur = self.conn.cursor()
        cur.execute(sql, (sect_name, user_id))
        self.conn.commit()

    def get_sect_info_by_qq(self, user_id):
        """
        通过用户qq获取宗门信息
        :param user_id:
        :return:
        """
        cur = self.conn.cursor()
        sql = f"select * from sects where sect_owner=?"
        cur.execute(sql, (user_id,))
        result = cur.fetchone()
        if not result:
            return None
        else:
            return SectInfo(*result)

    def get_sect_info_by_id(self, sect_id):
        """
        通过宗门id获取宗门信息
        :param sect_id:
        :return:
        """
        cur = self.conn.cursor()
        sql = f"select * from sects where sect_id=?"
        cur.execute(sql, (sect_id,))
        result = cur.fetchone()
        if not result:
            return None
        else:
            return SectInfo(*result)

    def update_usr_sect(self, user_id, usr_sect_id, usr_sect_position):
        """
        更新用户信息表的宗门信息字段
        :param user_id:
        :param usr_sect_id:
        :param usr_sect_position:
        :return:
        """
        sql = f"UPDATE user_xiuxian SET sect_id=?,sect_position=? where user_id=?"
        cur = self.conn.cursor()
        cur.execute(sql, (usr_sect_id, usr_sect_position, user_id))
        self.conn.commit()

    def get_all_sect_id(self):
        """获取全部宗门id"""
        sql = f"SELECT sect_id FROM sects"
        cur = self.conn.cursor()
        cur.execute(sql, )
        result = cur.fetchall()
        return result

    def in_closing(self, user_id, the_type):
        """
        更新用户操作CD
        :param user_id: qq
        :param the_type: 0:无状态  1：闭关中  2：历练中
        :return:
        """
        now_time = None
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

    def out_closing(self, user_id, the_type):
        """出关状态更新"""
        pass

    def update_exp(self, user_id, exp):
        """增加修为"""
        sql = f"UPDATE user_xiuxian SET exp=exp+? where user_id=?"
        cur = self.conn.cursor()
        cur.execute(sql, (exp, user_id))
        self.conn.commit()

    def update_j_exp(self, user_id, exp):
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
        WHEN level = '太乙境圆满' THEN '11'
        WHEN level = '太乙境中期' THEN '12'
        WHEN level = '太乙境初期' THEN '13'
        WHEN level = '金仙境圆满' THEN '14'
        WHEN level = '金仙境中期' THEN '15'
        WHEN level = '金仙境初期' THEN '16'
        WHEN level = '真仙境圆满' THEN '17'
        WHEN level = '真仙境中期' THEN '18'
        WHEN level = '真仙境初期' THEN '19'
        WHEN level = '半步真仙' THEN '20'
        WHEN level = '渡劫境圆满' THEN '21'
        WHEN level = '渡劫境中期' THEN '22'
        WHEN level = '渡劫境初期' THEN '23'
        WHEN level = '大乘境圆满' THEN '24'
        WHEN level = '大乘境中期' THEN '25'
        WHEN level = '大乘境初期' THEN '26'
        WHEN level = '合体境圆满' THEN '27'
        WHEN level = '合体境中期' THEN '28'
        WHEN level = '合体境初期' THEN '29'
        WHEN level = '炼虚境圆满' THEN '30'
        WHEN level = '炼虚境中期' THEN '31'
        WHEN level = '炼虚境初期' THEN '32'
        WHEN level = '化神境圆满' THEN '33'
        WHEN level = '化神境中期' THEN '34'
        WHEN level = '化神境初期' THEN '35'
        WHEN level = '元婴境圆满' THEN '36'
        WHEN level = '元婴境中期' THEN '37'
        WHEN level = '元婴境初期' THEN '38'
        WHEN level = '结丹境圆满' THEN '39'
        WHEN level = '结丹境中期' THEN '40'
        WHEN level = '结丹境初期' THEN '41'
        WHEN level = '筑基境圆满' THEN '42'
        WHEN level = '筑基境中期' THEN '43'
        WHEN level = '筑基境初期' THEN '44'
        WHEN level = '练气境圆满' THEN '45'
        WHEN level = '练气境中期' THEN '46'
        WHEN level = '练气境初期' THEN '47'
        WHEN level = '江湖好手' THEN '48'
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

    def get_exp_rank(self, user_id):
        """修为排行"""
        sql = f"select rank from(select user_id,exp,dense_rank() over (ORDER BY exp desc) as 'rank' FROM user_xiuxian) where user_id=?"
        cur = self.conn.cursor()
        cur.execute(sql, (user_id,))
        result = cur.fetchone()
        return result

    def get_stone_rank(self, user_id):
        """灵石排行"""
        sql = f"select rank from(select user_id,stone,dense_rank() over (ORDER BY stone desc) as 'rank' FROM user_xiuxian) where user_id=?"
        cur = self.conn.cursor()
        cur.execute(sql, (user_id,))
        result = cur.fetchone()
        return result
      
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

    def scale_top(self):
        """
        宗门建设度排行榜
        :return:
        """
        sql = f"SELECT sect_id, sect_name, sect_scale FROM sects WHERE sect_owner is NOT NULL ORDER BY sect_scale DESC"
        cur = self.conn.cursor()
        cur.execute(sql, )
        result = cur.fetchall()
        mess = f"✨位面宗门建设排行榜TOP10✨\n"
        num = 0
        for i in result:
            num += 1
            mess += f"第{num}位  {i[1]}  建设度：{i[2]}\n"
            if num == 10:
                break
        return mess, result

    def get_all_scale(self):
        """
        获取所有宗门信息
        :return:
        """
        sql = f"SELECT * FROM sects WHERE sect_owner is NOT NULL"
        cur = self.conn.cursor()
        cur.execute(sql, )
        result = cur.fetchall()
        results = []
        for r in result:
            results.append(SectInfo(*r))
        return results
    
    def get_top1_user(self):
        """
        获取修为第一的用户
        """
        cur = self.conn.cursor()
        sql = f"select * from user_xiuxian ORDER BY exp DESC LIMIT 1"
        cur.execute(sql)
        result = cur.fetchone()
        if not result:
            return None
        else:
            return UserDate(*result)

    def donate_update(self, sect_id, stone_num):
        """宗门捐献更新建设度及可用灵石"""
        sql = f"UPDATE sects SET sect_used_stone=sect_used_stone+?,sect_scale=sect_scale+? where sect_id=?"
        cur = self.conn.cursor()
        cur.execute(sql, (stone_num, stone_num * 10, sect_id))
        self.conn.commit()

    def update_sect_materials(self, sect_id, sect_materials, key):
        """更新资材  1为增加，2为减少"""
        cur = self.conn.cursor()

        if key == 1:
            sql = f"UPDATE sects SET sect_materials=sect_materials+? WHERE sect_id=?"
            cur.execute(sql, (sect_materials, sect_id))
            self.conn.commit()
        elif key == 2:
            sql = f"UPDATE sects SET sect_materials=sect_materials-? WHERE sect_id=?"
            cur.execute(sql, (sect_materials, sect_id))
            self.conn.commit()

    def get_all_sects_id_scale(self):
        """
        获取所有宗门信息
        :return
        :result[0] = sect_id   
        :result[1] = 建设度 sect_scale,
        :result[2] = 丹房等级 elixir_room_level 
        """
        sql = f"SELECT sect_id, sect_scale, elixir_room_level FROM sects WHERE sect_owner is NOT NULL ORDER BY sect_scale DESC"
        cur = self.conn.cursor()
        cur.execute(sql, )
        result = cur.fetchall()
        return result
    
    def get_all_users_by_sect_id(self, sect_id):
        """
        获取宗门所有成员信息
        :return: 成员列表
        """
        sql = f"SELECT * FROM user_xiuxian WHERE sect_id = ?"
        cur = self.conn.cursor()
        cur.execute(sql, (sect_id,))
        result = cur.fetchall()
        results = []
        for user in result:
            results.append(UserDate(*user))
        return results
    
    def do_work(self, user_id, the_type, sc_time=None):
        """
        更新用户操作CD
        :param sc_time: 任务
        :param user_id: qq
        :param the_type: 0:无状态  1：闭关中  2：历练中  3：探索秘境中
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
        elif the_type == 3:
            now_time = datetime.datetime.now()

        sql = f"UPDATE user_cd SET type=?,create_time=?,scheduled_time=? where user_id=?"
        cur = self.conn.cursor()
        cur.execute(sql, (the_type, now_time, sc_time, user_id))
        self.conn.commit()

    def update_levelrate(self, user_id, rate):
        """更新突破成功率"""
        sql = f"UPDATE user_xiuxian SET level_up_rate=? where user_id=?"
        cur = self.conn.cursor()
        cur.execute(sql, (rate, user_id))
        self.conn.commit()

    def update_user_attribute(self,user_id, hp, mp, atk):
        """更新用户HP,MP,ATK信息"""
        sql = f"UPDATE user_xiuxian SET hp=?,mp=?,atk=? where user_id=?"
        cur = self.conn.cursor()
        cur.execute(sql, (hp, mp, atk, user_id))
        self.conn.commit()

    def update_user_hp_mp(self,user_id, hp, mp):
        """更新用户HP,MP信息"""
        sql = f"UPDATE user_xiuxian SET hp=?,mp=? where user_id=?"
        cur = self.conn.cursor()
        cur.execute(sql, (hp, mp, user_id))
        self.conn.commit()
        
    def update_user_sect_contribution(self, user_id, sect_contribution):
        """更新用户宗门贡献度"""
        sql = f"UPDATE user_xiuxian SET sect_contribution=? where user_id=?"
        cur = self.conn.cursor()
        cur.execute(sql, (sect_contribution, user_id))
        self.conn.commit()

    def update_user_hp(self,user_id):
        """重置用户状态信息"""
        sql = f"UPDATE user_xiuxian SET hp=exp/2,mp=exp,atk=exp/10 where user_id=?"
        cur = self.conn.cursor()
        cur.execute(sql, (user_id,))
        self.conn.commit()

    def restate(self, user_id=None):
        """restate重置所有用户状态或重置对应人状态"""
        if user_id is None:
            sql = f"UPDATE user_xiuxian SET hp=exp/2,mp=exp,atk=exp/10"
            cur = self.conn.cursor()
            cur.execute(sql,)
            self.conn.commit()
        else:
            sql = f"UPDATE user_xiuxian SET hp=exp/2,mp=exp,atk=exp/10 where user_id=?"
            cur = self.conn.cursor()
            cur.execute(sql, (user_id,))
            self.conn.commit()

    def get_back_msg(self, user_id):
        """获取用户背包信息"""
        sql = f"SELECT * FROM back where user_id=? and goods_num >= 1"
        cur = self.conn.cursor()
        cur.execute(sql, (user_id,))
        result = cur.fetchall()
        # msg = f"你的背包\n"
        # for i in result:
        #     msg += f"{i},"
        results = []
        if result == []:
            results = None
        for r in result:
            results.append(back(*r))
        return results

    def goods_num(self, user_id, goods_id):
        """
        判断用户物品数量
        :param user_id: 用户qq
        :param goods_id: 物品id
        :return: 物品数量
        """
        sql = f"SELECT num FROM back where user_id=? and goods_id=?"
        cur = self.conn.cursor()
        cur.execute(sql, (user_id, goods_id))
        result = cur.fetchone()
        if result:
            return result[0]
        else:
            return 0
        
    def get_all_user_exp(self, level):
        """查询所有对应大境界玩家的修为"""
        sql = f"SELECT exp FROM user_xiuxian  WHERE level like '{level}%'"
        cur = self.conn.cursor()
        cur.execute(sql, )
        result = cur.fetchall()
        return result

    def update_user_atkpractice(self,user_id, atkpractice):
        """更新用户攻击修炼等级"""
        sql = f"UPDATE user_xiuxian SET atkpractice={atkpractice} where user_id=?"
        cur = self.conn.cursor()
        cur.execute(sql, (user_id,))
        self.conn.commit()

    def update_user_sect_task(self,user_id, sect_task):
        """更新用户宗门任务次数"""
        sql = f"UPDATE user_xiuxian SET sect_task=sect_task+? where user_id=?"
        cur = self.conn.cursor()
        cur.execute(sql, (sect_task, user_id))
        self.conn.commit()
    
    def sect_task_reset(self):
        """重置宗门任务次数"""
        sql = f"UPDATE user_xiuxian SET sect_task=0"
        cur = self.conn.cursor()
        cur.execute(sql, )
        self.conn.commit()

    def update_sect_scale_and_used_stone(self, sect_id, sect_used_stone, sect_scale):
        """更新宗门灵石、建设度"""
        sql = f"UPDATE sects SET sect_used_stone=?,sect_scale=? where sect_id=?"
        cur = self.conn.cursor()
        cur.execute(sql, (sect_used_stone, sect_scale, sect_id))
        self.conn.commit()
    
    def update_sect_elixir_room_level(self, sect_id, level):
        """更新宗门丹房等级"""
        sql = f"UPDATE sects SET elixir_room_level=? where sect_id=?"
        cur = self.conn.cursor()
        cur.execute(sql, (level, sect_id))
        self.conn.commit()
    
    def update_user_sect_elixir_get_num(self, user_id):
        """更新用户每日领取丹药领取次数"""
        sql = f"UPDATE user_xiuxian SET sect_elixir_get=1 where user_id=?"
        cur = self.conn.cursor()
        cur.execute(sql, (user_id,))
        self.conn.commit()
    
    def sect_elixir_get_num_reset(self):
        """重置宗门丹药领取次数"""
        sql = f"UPDATE user_xiuxian SET sect_elixir_get=0"
        cur = self.conn.cursor()
        cur.execute(sql, )
        self.conn.commit()
    
    

    def update_sect_mainbuff(self, sect_id, mainbuffid):
        """更新宗门当前的主修功法"""
        sql = f"UPDATE sects SET mainbuff=? where sect_id=?"
        cur = self.conn.cursor()
        cur.execute(sql, (mainbuffid, sect_id))
        self.conn.commit()
    
    def update_sect_secbuff(self, sect_id, secbuffid):
        """更新宗门当前的神通"""
        sql = f"UPDATE sects SET secbuff=? where sect_id=?"
        cur = self.conn.cursor()
        cur.execute(sql, (secbuffid, sect_id))
        self.conn.commit()
        
    
    def initialize_user_buff_info(self, user_id):
        """初始化用户buff信息"""
        sql = f"INSERT INTO BuffInfo (user_id,main_buff,sec_buff,faqi_buff,fabao_weapon) VALUES (?,0,0,0,0)"
        cur = self.conn.cursor()
        cur.execute(sql, (user_id,))
        self.conn.commit()
        
    def get_user_buff_info(self, user_id):
        """获取用户buff信息"""
        sql = f"select * from BuffInfo where user_id =?"
        cur = self.conn.cursor()
        cur.execute(sql, (user_id,))
        result = cur.fetchone()
        if not result:
            return None
        else:
            return BuffInfo(*result)
    
    def updata_user_main_buff(self, user_id, id):
        """更新用户主功法信息"""
        sql = f"UPDATE BuffInfo SET main_buff = ? where user_id = ?"
        cur = self.conn.cursor()
        cur.execute(sql, (id, user_id,))
        self.conn.commit()
    
    def updata_user_sec_buff(self, user_id, id):
        """更新用户副功法信息"""
        sql = f"UPDATE BuffInfo SET sec_buff = ? where user_id = ?"
        cur = self.conn.cursor()
        cur.execute(sql, (id, user_id,))
        self.conn.commit()
        
    def updata_user_faqi_buff(self, user_id, id):
        """更新用户法器信息"""
        sql = f"UPDATE BuffInfo SET faqi_buff = ? where user_id = ?"
        cur = self.conn.cursor()
        cur.execute(sql, (id, user_id,))
        self.conn.commit()
    
    def updata_user_fabao_weapon(self, user_id, id):
        """更新用户法宝信息"""
        sql = f"UPDATE BuffInfo SET fabao_weapon = ? where user_id = ?"
        cur = self.conn.cursor()
        cur.execute(sql, (id, user_id,))
        self.conn.commit()
    
    def updata_user_armor_buff(self, user_id, id):
        """更新用户防具信息"""
        sql = f"UPDATE BuffInfo SET armor_buff = ? where user_id = ?"
        cur = self.conn.cursor()
        cur.execute(sql, (id, user_id,))
        self.conn.commit()
        
    def updata_user_atk_buff(self, user_id, buff):
        """更新用户永久攻击buff信息"""
        sql = f"UPDATE BuffInfo SET atk_buff=atk_buff+? where user_id = ?"
        cur = self.conn.cursor()
        cur.execute(sql, (buff, user_id,))
        self.conn.commit()
    
    def updata_user_blessed_spot(self, user_id, blessed_spot):
        """更新用户洞天福地等级"""
        sql = f"UPDATE BuffInfo SET blessed_spot=? where user_id = ?"
        cur = self.conn.cursor()
        cur.execute(sql, (blessed_spot, user_id,))
        self.conn.commit()
    
    def update_user_blessed_spot_flag(self, user_id):
        """更新用户洞天福地是否开启"""
        sql = f"UPDATE user_xiuxian SET blessed_spot_flag=1 where user_id=?"
        cur = self.conn.cursor()
        cur.execute(sql, (user_id,))
        self.conn.commit()
        
    def update_user_blessed_spot_name(self, user_id, blessed_spot_name):
        """更新用户洞天福地的名字"""
        sql = f"UPDATE user_xiuxian SET blessed_spot_name=? where user_id=?"
        cur = self.conn.cursor()
        cur.execute(sql, (blessed_spot_name, user_id,))
        self.conn.commit()
    
    def day_num_reset(self):
        """重置丹药每日使用次数"""
        sql = f"UPDATE back SET day_num=0 where goods_type='丹药'"
        cur = self.conn.cursor()
        cur.execute(sql, )
        self.conn.commit()

    def sect_owner_update(self, sect_id, sect_owner):
        """更改宗主"""
        sql = f"UPDATE sects SET sect_owner=? where sect_id=?"
        cur = self.conn.cursor()
        cur.execute(sql, (sect_owner, sect_id,))
        self.conn.commit()

    def send_back(self, user_id, goods_id, goods_name, goods_type, goods_num, bind_flag=0):
        """
        插入物品至背包
        :param user_id: 用户qq
        :param goods_id: 物品id
        :param goods_name: 物品名称
        :param goods_type: 物品类型
        :param goods_num: 物品数量
        :param bind_flag: 是否绑定物品，0-非绑定，1-绑定
        :return: None
        """
        now_time = datetime.datetime.now()
        # 检查物品是否存在，存在则update
        cur = self.conn.cursor()
        back = self.get_item_by_good_id_and_user_id(user_id, goods_id)
        if back:
            # 判断是否存在，存在则update
            if bind_flag == 1:
                bind_num = back.bind_num + goods_num
            else:
                bind_num = back.bind_num
            goods_nums = back.goods_num + goods_num
            sql = f"UPDATE back set goods_num=?,update_time=?,bind_num={bind_num} WHERE user_id=? and goods_id=?"
            cur.execute(sql, (goods_nums, now_time, user_id, goods_id))
            self.conn.commit()
        else:
            # 判断是否存在，不存在则INSERT
            if bind_flag == 1:
                bind_num = goods_num
            else:
                bind_num = 0
            sql = """
                    INSERT INTO back (user_id, goods_id, goods_name, goods_type, goods_num, create_time, update_time, bind_num)
            VALUES (?,?,?,?,?,?,?,?)"""
            cur.execute(sql, (user_id, goods_id, goods_name, goods_type, goods_num, now_time, now_time, bind_num))
            self.conn.commit()
            
    def get_item_by_good_id_and_user_id(self, user_id, goods_id):
        """根据物品id、用户id获取物品信息"""
        sql = f"select * from back where user_id=? and goods_id=?"
        cur = self.conn.cursor()
        cur.execute(sql, (user_id, goods_id))
        result = cur.fetchone()
        if not result:
            return None
        else:
            return back(*result)

    # def update_back(self, user_id, goods_id, msg):
    #     """使用物品"""
    #     check_sql = f"select goods_num from back where user_id=? and goods_id=?"
    #     cur = self.conn.cursor()
    #     cur.execute(check_sql, (user_id, goods_id))
    #     result = cur.fetchone()
        
    def update_back_equipment(self, sql_str):
        """更新背包，传入sql"""
        print(f"执行的sql：{sql_str}")
        cur = self.conn.cursor()
        cur.execute(sql_str)
        self.conn.commit()
        
    def update_back_j(self, user_id, goods_id, num=1, use_key=0):
        """
        使用物品
        :num 减少数量  默认1
        :use_key 是否使用，丹药使用才传 默认0
        """
        back = self.get_item_by_good_id_and_user_id(user_id, goods_id)
        if back.goods_type == "丹药" and use_key == 1:#丹药要判断耐药性、日使用上限
            if back.bind_num >= 1:
                bind_num = back.bind_num - num#优先使用绑定物品
            else:
                bind_num = back.bind_num
            day_num = back.day_num + num
            all_num = back.all_num + num
        else:
            bind_num = back.bind_num
            day_num = back.day_num
            all_num = back.all_num
        goods_num = back.goods_num - num
        now_time = datetime.datetime.now()
        sql_str = f"UPDATE back set update_time='{now_time}',action_time='{now_time}',goods_num={goods_num},day_num={day_num},all_num={all_num},bind_num={bind_num} WHERE user_id={user_id} and goods_id={goods_id}"
        cur = self.conn.cursor()
        cur.execute(sql_str)
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


    def do_work(self, key, work_list=None, name=None):
        """悬赏令获取"""
        # with open(self.do_work_jsonpath, 'r', encoding='utf-8') as e:
        #     a = e.read()
        #     data = json.loads(a)
        data = jsondata.reward_that_data()
        print("111", data)
        print(type(data))
        if key == 0:  # 如果没有获取过，则返回悬赏令
            get_work_list = []
            for i in data:
                name = random.choice(list(data[i].keys()))
                get_work_list.append(
                    [name, data[i][name]["rate"], data[i][name]["succeed_thank"], data[i][name]["time"]])
            return get_work_list

        if key == 1:  ##返回对应的悬赏令信息
            for i in data:
                try:
                    return data[i][name]['time']
                except:
                    pass

        elif key == 2:  # 如果是结算，则获取结果
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

    def set_closing_type(self, user_level):
        list_all = len(self.level) - 1
        now_index = self.level.index(user_level)
        if list_all == now_index:
            return "道友已是最高境界，无法修炼了！"
        is_updata_level = self.level[now_index + 1]
        need_exp = XiuxianDateManage().get_level_power(is_updata_level)
        return need_exp

    def get_type(self, user_exp, rate, user_level):
        list_all = len(self.level) - 1
        now_index = self.level.index(user_level)
        if list_all == now_index:
            return "道友已是最高境界，无法突破！"

        is_updata_level = self.level[now_index + 1]
        need_exp = XiuxianDateManage().get_level_power(is_updata_level)

        # 判断修为是否足够突破
        if user_exp >= need_exp:
            pass
        else:
            return "道友的修为不足以突破！距离下次突破需要{}修为！突破境界为：{}".format(need_exp - user_exp, is_updata_level)

        success_rate = True if random.randint(0, 100) < rate else False

        if success_rate:

            return [self.level[now_index + 1]]
        else:
            return '失败'

    def calculated(self, rate: dict) -> str:
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

    def date_diff(self, new_time, old_time):
        """计算日期差"""
        if isinstance(new_time, datetime.datetime):
            pass
        else:
            new_time = datetime.datetime.strptime(new_time, '%Y-%m-%d %H:%M:%S.%f')

        if isinstance(old_time, datetime.datetime):
            pass
        else:
            old_time = datetime.datetime.strptime(old_time, '%Y-%m-%d %H:%M:%S.%f')

        day = (new_time - old_time).days
        sec = (new_time - old_time).seconds

        return (day * 24 * 60 * 60) + sec

    def fight(self, player1=None, player2=None):
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
        if power_rate >= 0.95:
            return "道友偷窃小辈实属天道所不齿！"
        elif power_rate <= 0.05:
            return "道友请不要不自量力！"
        else:
            return int(power_rate * 100)

    def player_fight(self, player1: dict, player2: dict, type_in: 1):
        """
        回合制战斗
        type_in : 1 为完整返回战斗过程（未加）
        2：只返回战斗结果
        数据示例：
        {"道号": None, "气血": None, "攻击": None, "真元": None, '会心':None}
        """
        msg1 = "{}发起攻击，造成了{}伤害\n"
        msg2 = "{}发起攻击，造成了{}伤害\n"

        play_list = []
        suc = None

        while True:
            player1_gj = int(round(random.uniform(0.95, 1.05), 2) * player1['攻击'])
            if random.randint(0, 100) <= player1['会心']:
                player1_gj = int(player1_gj * 1.5)
                msg1 = "{}发起会心一击，造成了{}伤害\n"

            player2_gj = int(round(random.uniform(0.95, 1.05), 2) * player2['攻击'])
            if random.randint(0, 100) <= player2['会心']:
                player2_gj = int(player2_gj * 1.5)
                msg2 = "{}发起会心一击，造成了{}伤害\n"

            # 造成的伤害
            # play1_sh: int = int(player1_gj) - player2['防御']
            # play2_sh: int = int(player2_gj) - player1['防御']
            play1_sh: int = int(player1_gj)
            play2_sh: int = int(player2_gj)

            # print(msg1.format(player1['道号'], play1_sh))
            play_list.append(msg1.format(player1['道号'], play1_sh))

            player2['气血'] = player2['气血'] - play1_sh
            # print(f"{player2['道号']}剩余血量{player2['气血']}")
            play_list.append(f"{player2['道号']}剩余血量{player2['气血']}")
            XiuxianDateManage().update_user_hp_mp(player2['user_id'], player2['气血'], player2['真元'])

            if player2['气血'] <= 0:
                # print("{}胜利".format(player1['道号']))
                play_list.append("{}胜利".format(player1['道号']))
                suc = f"{player1['道号']}"

                XiuxianDateManage().update_user_hp_mp(player2['user_id'], 1, player2['真元'])
                break

            # print(msg2.format(player2['道号'], play2_sh))
            play_list.append(msg2.format(player2['道号'], play2_sh))

            player1['气血'] = player1['气血'] - play2_sh
            # print(f"{player1['道号']}剩余血量{player1['气血']}\n")
            play_list.append(f"{player1['道号']}剩余血量{player1['气血']}\n")
            XiuxianDateManage().update_user_hp_mp(player1['user_id'], player1['气血'], player1['真元'])

            if player1['气血'] <= 0:
                # print("{}胜利".format(player2['道号']))
                play_list.append("{}胜利".format(player2['道号']))
                suc = f"{player2['道号']}"

                XiuxianDateManage().update_user_hp_mp(player1['user_id'], 1, player1['真元'])
                break

            if player1['气血'] <= 0 or player2['气血'] <= 0:
                play_list.append("逻辑错误！！！")
                break

        return play_list, suc

    def send_hp_mp(self, user_id, hp, mp):
        user_msg = XiuxianDateManage().get_user_message(user_id)
        max_hp = int(user_msg.exp/2)
        max_mp = int(user_msg.exp)

        msg = []
        hp_mp = []

        if user_msg.hp < max_hp:
            if user_msg.hp + hp < max_hp:
                new_hp = user_msg.hp + hp
                msg.append(',回复气血：{}'.format(hp))
            else:
                new_hp = max_hp
                msg.append(',气血已回满！')
        else:
            new_hp = user_msg.hp
            msg.append('')

        if user_msg.mp < max_mp:
            if user_msg.mp + mp < max_mp:
                new_mp = user_msg.mp + mp
                msg.append(',回复真元：{}'.format(mp))
            else:
                new_mp = max_mp
                msg.append(',真元已回满！')
        else:
            new_mp = user_msg.mp
            msg.append('')

        hp_mp.append(new_hp)
        hp_mp.append(new_mp)
        hp_mp.append(user_msg.exp)

        return msg, hp_mp

from .read_buff import UserBuffDate
from .item_json import Items
items = Items()
def final_user_data(user_data):
    """传入用户当前信息、buff信息，返回最终信息"""
    user_data = list(user_data)
    user_buff_data = UserBuffDate(user_data[1]).BuffInfo
    if int(user_buff_data.faqi_buff) == 0:
        weapon_atk_buff = 0
    else:
        weapon_info = items.get_data_by_item_id(user_buff_data.faqi_buff) 
        weapon_atk_buff = weapon_info['atk_buff']
    main_buff_data = UserBuffDate(user_data[1]).get_user_main_buff_data()
    main_hp_buff = main_buff_data['hpbuff'] if main_buff_data != None else 0
    main_mp_buff = main_buff_data['mpbuff'] if main_buff_data != None else 0
    main_atk_buff = main_buff_data['atkbuff'] if main_buff_data != None else 0
    user_data[15] = int(user_data[15] * (1 + main_hp_buff))#hp 
    user_data[16] = int(user_data[16] * (1 + main_mp_buff))#mp
    user_data[17] = int(user_data[17] * (user_data[18] * 0.04 + 1) * (1 + main_atk_buff) * (1 + weapon_atk_buff)) + user_buff_data.atk_buff#每级+10%攻击
    user_data = tuple(user_data)
    return user_data
    
    
if __name__ == '__main__':
    print(OtherSet().date_diff("2022-09-08 00:42:56.740255", "2022-09-08 00:42:56.740255"))

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
