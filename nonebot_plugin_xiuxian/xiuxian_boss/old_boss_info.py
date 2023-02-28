import ujson as json
from pathlib import Path
import os

PATH = Path(__file__).parent


class OLD_BOSS_INFO(object):
    def __init__(self):
        self.dir_path = PATH
        self.data_path = os.path.join(self.dir_path, "boss_info.json")
        try:
            with open(self.data_path, 'r', encoding='utf-8') as f:
                self.data = json.load(f)
        except:
            self.info = {}
            data = json.dumps(self.info, ensure_ascii=False, indent=4)
            with open(self.data_path, mode="x", encoding="UTF-8") as f:
                f.write(data)
            with open(self.data_path, 'r', encoding='utf-8') as f:
                self.data = json.load(f)

    def __save(self):
        """
        :return:保存
        """
        with open(self.data_path, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=4)

    def save_boss(self, boss_data):
        """
        保存boss
        :param boss_data:
        """
        self.data = {}
        self.data.update(boss_data)
        self.__save()
        return True

    def read_boss_info(self):
        """
        读取boss信息
        """
        tp = self.data
        self.__save()
        return tp


old_boss_info = OLD_BOSS_INFO()
