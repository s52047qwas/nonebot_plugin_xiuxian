import json
from pathlib import Path
import os
import datetime
from .riftmake import Rift


class OLD_RIFT_INFO(object):
    def __init__(self):
        self.dir_path = Path(__file__).parent
        self.data_path = os.path.join(self.dir_path, "rift_info.json")
        try:
            with open(self.data_path, 'r', encoding='utf-8') as f:
                self.data = json.load(f)
        except:
            self.info = {}
            data = json.dumps(self.info, ensure_ascii=False, indent=4)
            with open(self.data_path, mode="x", encoding="UTF-8") as f:
                f.write(data)
                f.close()
            with open(self.data_path, 'r', encoding='utf-8') as f:
                self.data = json.load(f)

    def __save(self):
        """
        :return:保存
        """
        with open(self.data_path, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, cls=MyEncoder, ensure_ascii=False, indent=4)

    def save_rift(self, group_rift):
        """
        保存rift
        :param group_rift:
        """
        self.data = {}
        for x in group_rift:
            rift_data = {str(x): {"name": group_rift[x].name,
                                  "rank": group_rift[x].rank,
                                  "count": group_rift[x].count,
                                  "l_user_id": group_rift[x].l_user_id,
                                  "time": group_rift[x].time
                                  }
                         }
            self.data.update(rift_data)
        self.__save()
        return True

    def read_rift_info(self):
        """
        读取rift信息
        """
        group_rift = {}
        for x in self.data:
            rift = Rift()
            rift.name = self.data[x]["name"]
            rift.rank = self.data[x]["rank"]
            rift.count = self.data[x]["count"]
            rift.time = self.data[x]["time"]
            rift.l_user_id = self.data[x]["l_user_id"]
            group_rift[int(x)] = rift
        self.data = {}
        self.__save()
        return group_rift


old_rift_info = OLD_RIFT_INFO()


class MyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.strftime("%Y-%m-%d %H:%M:%S")
        if isinstance(obj, bytes):
            return str(obj, encoding='utf-8')
        if isinstance(obj, int):
            return int(obj)
        elif isinstance(obj, float):
            return float(obj)
        else:
            return super(MyEncoder, self).default(obj)