class XiuConfig:

    def __init__(self):
        self.level = ["江湖好手",
                      "练气境初期",
                      "练气境中期",
                      "练气境圆满",
                      "筑基境初期",
                      "筑基境中期",
                      "筑基境圆满",
                      "结丹境初期",
                      "结丹境中期",
                      "结丹境圆满",
                      "元婴境初期",
                      "元婴境中期",
                      "元婴境圆满",
                      "化神境初期",
                      "化神境中期",
                      "化神境圆满",
                      "炼虚境初期",
                      "炼虚境中期",
                      "炼虚境圆满",
                      "合体境初期",
                      "合体境中期",
                      "合体境圆满",
                      "大乘境初期",
                      "大乘境中期",
                      "大乘境圆满",
                      "渡劫境初期",
                      "渡劫境中期",
                      "渡劫境圆满"]  # 最高境界设定
        self.level_up_cd = 60  # 境界突破CD 单位分钟
        self.closing_exp = 10  # 闭关每分钟增加的修为
        self.closing_exp_upper_limit = 1.5  # 闭关可获取修为上限（下一个境界需要的修为的1.5倍）
        self.level_punishment_floor = 1  # 突破失败扣除修为，惩罚下限(当前实例：1%)
        self.level_punishment_limit = 5  # 突破失败扣除修为，惩罚上限(当前实例：10%)
        self.level_up_probability = 0.3  # 突破失败增加当前境界突破概率的比例
        self.sign_in_lingshi_lower_limit = 100  # 每日签到灵石下限
        self.sign_in_lingshi_upper_limit = 300  # 每日签到灵石上限
        self.sign_in_xiuwei_lower_limit = 1000  # 每日签到修为下限
        self.sign_in_xiuwei_upper_limit = 3000  # 每日签到修为上限
        self.tou = 30  # 偷灵石惩罚
        self.remake = 200  # 重入仙途的消费
        self.sect_min_level = "化神境圆满"  # 创建宗门的最低修为等级要求
        self.sect_create_cost = 50  # 创建宗门的最低修为等级要求
        self.user_info_cd = 30  # 我的修仙信息查询cd
        self.user_info_cd_msg = '你急啥呢？{cd_msg}后再查询吧'
        self.dufang_cd = 15  # 金银阁cd
        self.dufang_cd_msg = '你急啥呢？{cd_msg}后再来吧'

        self.sql_table = ["user_xiuxian", "user_cd", "sects"]
        self.sql_user_xiuxian = ["level_up_rate", "sect_id", "sect_position"]
