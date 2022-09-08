from pathlib import Path
import json

DATABASE = Path() / "data" / "xiuxian"


class JsonDate:
    """处理JSON数据"""

    def __init__(self):
        """json文件路径"""
        self.root_jsonpath = DATABASE / "灵根.json"
        self.level_rate_jsonpath = DATABASE / "突破概率.json"
        self.Reward_that_jsonpath = DATABASE / "悬赏令.json"
        self.level_jsonpath = DATABASE / "境界.json"

    def level_data(self):
        """境界数据"""
        with open(self.level_jsonpath, 'r', encoding='utf-8') as e:
            a = e.read()
            data = json.loads(a)
            return data

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

jsondata = JsonDate()


if __name__ == '__main__':
    # P =r"G:\yuzi_bot\yuzi_bot\data\xiuxian\境界.json"
    # a = JsonDate().my_test_file(pathfile=P)
    # from pprint import pprint
    # pprint(a["结丹境圆满"]["power"])
    from datetime import datetime
    print(datetime.now())
    if isinstance("2022-09-08 00:42:50.279352", datetime):
        print('11')