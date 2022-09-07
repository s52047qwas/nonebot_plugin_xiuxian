from datetime import datetime




class gamebingo:

    def __init__(self):
        self.player = []
        self.start = 0
        self.price = 0
        self.time = 0

    def add_player(self,user_id):
        self.player.append(user_id)

    def get_player_len(self):
        return len(self.player)

    def start_change(self, key):
        self.start = key

    def add_price(self,pr):
        self.price = pr

    def end_game(self):
        self.player = []
        self.start = 0
        self.price = 0
        self.time = 0


class do_is_work:
    def __init__(self,user_id):
        self.user = user_id
        self.time = 0
        self.msg = 0
        self.world = []


class time_msg:
    def __init__(self):
        self.time = 0
