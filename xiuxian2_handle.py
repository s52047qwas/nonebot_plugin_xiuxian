import sqlite3
import time

from collections import namedtuple
from enum import Enum
from functools import wraps
from inspect import signature
from pathlib import Path
from typing import List
import json
import random

DATABASE =Path() / "data" / "xiuxian"

xiuxian_data = namedtuple("xiuxian_data", ["no", "user_id", "linggen", "level"])

UserDate = namedtuple("UserDate",["id","user_id","stone","root","root_type","level","power","create_time","is_sign","exp","user_name"])


def linggen_get():
    path_lg = DATABASE / "灵根.json"
    with open(path_lg,'r', encoding='utf-8') as e:
        a = e.read()
        data = json.loads(a)
        lg = random.choice(data)
        return lg['name'],lg['type']


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

    def close(self):
        self.conn.close()
        print("数据库关闭！")

    # def _create_file(self):
    #     """创建数据库文件"""
    #     c = self.conn.cursor()
    #     c.execute('''''')
    #     c.execute('''''')
    #     c.execute('''''')
    #     self.conn.commit()

    def _get_id(self):
        """获取下一个id"""
        cur = self.conn.cursor()
        cur.execute('select id from user_xiuxian')
        result = cur.fetchall()
        print(result)
        return len(result) + 1

    @classmethod
    def close_dbs(cls):
        XiuxianDateManage().close()

    def _create_user(self, user_id: str,root:str,type:str,power:str,create_time,user_name) -> None:
        """在数据库中创建用户并初始化"""
        new_id = self._get_id()
        c = self.conn.cursor()
        sql = f"INSERT INTO user_xiuxian (id,user_id,stone,root,root_type,level,power,create_time,user_name) VALUES (?,?,0,?,?,'江湖好手',?,?,?)"
        c.execute(sql, (new_id, user_id,root,type,power,create_time,user_name))
        self.conn.commit()


    def get_user_message(self,user_id):
        '''获取用户信息'''
        cur = self.conn.cursor()
        sql = f"select * from user_xiuxian where user_id=?"
        cur.execute(sql, (user_id,))
        result = cur.fetchone()
        if not result:
            return None
        else:
            return UserDate(*result)

    def create_user(self,user_id,*args):
        cur = self.conn.cursor()
        sql = f"select * from user_xiuxian where user_id=?"
        cur.execute(sql, (user_id,))
        result = cur.fetchone()
        if not result:
            self._create_user(user_id,args[0],args[1],args[2],args[3],args[4])
            self.conn.commit()
            return '欢迎进入修仙世界的，你的灵根为：{},类型是：{},你的战力为：{},当前境界：江湖好手'.format(args[0], args[1], args[2],args[3])
        else:
            return '您已迈入修仙世界，输入我的修仙信息，获取数据吧！'

    def get_sign(self,user_id):
        '''获取用户签到信息'''
        cur = self.conn.cursor()
        sql = f"select is_sign from user_xiuxian where user_id=?"
        cur.execute(sql, (user_id,))
        result = cur.fetchone()
        if not result:
            return '修仙界没有你的足迹，输入 我要修仙 加入修仙世界吧！'
        elif result[0]==0:
            ls = random.randint(1,100)
            exp = random.randint(100,500)
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
        if result[0]>=100:
            sql = f"UPDATE user_xiuxian SET root=?,root_type=?,stone=stone-100 WHERE user_id=?"
            cur.execute(sql, (lg, type,user_id))
            self.conn.commit()

            self.update_power(user_id)
            return "逆天之行，重获新生，新的灵根为：{}，类型为：{}".format(lg,type)
        else:
            return "你的灵石还不够呢，快去赚点灵石吧！"

    def get_type_power(self,name):
        """获取灵根或境界的战力和倍率"""
        cur = self.conn.cursor()
        sql = f"SELECT power FROM level WHERE name=?"
        cur.execute(sql, (name,))
        result = cur.fetchone()
        return result[0]

    def update_power(self,user_id) -> None:
        """更新战力"""
        UserMessage = self.get_user_message(user_id)
        cur = self.conn.cursor()
        sql = f"UPDATE user_xiuxian SET power=(SELECT power FROM level WHERE name=?)*(SELECT power FROM level WHERE name=?) WHERE user_id=?"
        cur.execute(sql, (UserMessage.root_type, UserMessage.level, user_id))
        self.conn.commit()

    def update_ls(self, user_id, price,key):
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
        sql = f"UPDATE user_xiuxian SET user_name=? where user_id=?"
        cur = self.conn.cursor()
        cur.execute(sql,(user_name,user_id) )
        self.conn.commit()
        return '道友的道号更新成功拉~'


if __name__ == '__main__':
    # a=r'G:'
    # print(a)
    # conn = sqlite3.connect(a)
    # cur = conn.cursor()
    # sql = f"SELECT user_id,stone FROM user_xiuxian  WHERE stone>0 ORDER BY stone DESC LIMIT 5"
    # cur.execute(sql,)
    # result = cur.fetchall()
    # print(result)

    a = XiuxianDateManage()
    print(a.database_path)
    a.get_ls_rank()