
from pathlib import Path
import json
import yaml

DATABASE = Path() / "data" / "xiuxian"

class XiuConfig:

    def __init__(self):
        self.config_yamlpath = DATABASE / "config.yaml"
        config_data = self._config_data()

        self.level = config_data['level']
        self.level_up_cd = config_data["level_up_cd"]  # 境界突破CD 单位分钟
        self.closing_exp = config_data['closing_exp']  # 闭关每分钟增加的修为
        self.closing_exp_upper_limit = config_data['closing_exp_upper_limit']  # 闭关可获取修为上限（下一个境界需要的修为的1.5倍）
        self.level_punishment_floor = config_data['level_punishment_floor']  # 突破失败扣除修为，惩罚下限(当前实例：1%)
        self.level_punishment_limit = config_data['level_punishment_limit']  # 突破失败扣除修为，惩罚上限(当前实例：10%)
        self.level_up_probability = config_data['level_up_probability']  # 突破失败增加当前境界突破概率的比例
        self.sign_in_lingshi_lower_limit = config_data['sign_in_lingshi_lower_limit']  # 每日签到灵石下限
        self.sign_in_lingshi_upper_limit = config_data['sign_in_lingshi_upper_limit']  # 每日签到灵石上限
        self.sign_in_xiuwei_lower_limit = config_data['sign_in_xiuwei_lower_limit']  # 每日签到修为下限
        self.sign_in_xiuwei_upper_limit = config_data['sign_in_xiuwei_upper_limit']  # 每日签到修为上限
        self.tou = config_data['tou']  # 偷灵石惩罚
        self.tou_lower_limit = config_data['tou_lower_limit']  # 偷灵石下限
        self.tou_upper_limit = config_data['tou_upper_limit']  # 偷灵石上限
        self.remake = config_data['remake']  # 重入仙途的消费
        self.sect_min_level = config_data['sect_min_level']  # 创建宗门的最低修为等级要求
        self.sect_create_cost = config_data['sect_create_cost']  # 创建宗门的最低修为等级要求
        self.user_info_cd = config_data['user_info_cd']  # 我的修仙信息查询cd
        self.user_info_cd_msg = config_data['user_info_cd_msg']
        self.dufang_cd = config_data['dufang_cd']  # 金银阁cd
        self.dufang_cd_msg = config_data['dufang_cd_msg']
        self.tou_cd = config_data['tou_cd']  # 偷灵石CD
        # self.ggg = config_data['ggg']

        self.sql_table = config_data['sql_table']
        self.sql_user_xiuxian = config_data['sql_user_xiuxian']


    def _config_data(self):
        """配置数据"""
        with open(self.config_yamlpath, 'r', encoding='utf-8') as e:
            a = e.read()
            data = yaml.safe_load(a)
            return data


class JsonConfig:
    def __init__(self):
        self.config_jsonpath = DATABASE / "config.json"


    def read_data(self):
        """配置数据"""
        with open(self.config_jsonpath, 'r', encoding='utf-8') as e:
            data = json.load(e)
            return data

    def write_data(self, key):
        """
        说明：设置抢灵石开启或关闭
        参数：
            key：1为开启，2为关闭
        """

        json_data = self.read_data()

        if key == 1:
            json_data['qiang'] = True
        if key == 2:
            json_data['qiang'] = False

        with open(self.config_jsonpath, 'w', encoding='utf-8') as f:
            json.dump(json_data, f)



if __name__ == '__main__':
    name = XiuConfig()._config_data()
    for i in name:
        print(i)
