from ..data_source import *


class reward(JsonDate):
    
    def __init__(self):
        self.Reward_that_jsonpath = DATABASE / "悬赏令test.json"