from re import I

from nonebot import on_command, on_message, on_regex
from nonebot.adapters.onebot.v11 import (
    PRIVATE_FRIEND,
    GROUP,
)
from nonebot.permission import SUPERUSER
from nonebot_plugin_guild_patch import (
    GUILD,
    GUILD_OWNER,
    GUILD_ADMIN,
    GUILD_SUPERUSER,
    GuildMessageEvent)

run_xiuxian = on_command("我要修仙", priority=5)
restart = on_command("再入仙途", aliases={"重新修仙", "重入仙途"}, priority=5)
package = on_command("我的纳戒", aliases={"升级纳戒"}, priority=5)
sign_in = on_command("修仙签到", priority=5)
help_in = on_command("修仙帮助", priority=5)
rank = on_command("排行榜", aliases={"修仙排行榜", "灵石排行榜", "战力排行榜", "境界排行榜", "宗门排行榜"}, priority=5)
remaname = on_command("改名", priority=5)
level_up = on_command("突破", priority=5)
in_closing = on_command("闭关", priority=5)
give_stone = on_command("送灵石", priority=5)
qq_binding = on_command('绑定QQ', aliases={"绑定qq", "QQ绑定", "qq绑定"}, priority=5)
# dufang = on_regex(
#     r"(金银阁)\s?(\d+)\s?([大|小|奇|偶|猜])?\s?(\d+)?",
#     flags=I,
#     permission=PRIVATE_FRIEND | GROUP,
# )
steal_stone = on_command("偷灵石", aliases={"飞龙探云手"}, priority=5)
gm_command = on_command("神秘力量", permission=SUPERUSER | GUILD_SUPERUSER, priority=5)
gmm_command = on_command("未知力量", permission=SUPERUSER | GUILD_SUPERUSER, priority=5)
rob_stone = on_command("抢劫", aliases={"抢灵石"}, priority=5)
restate = on_command("重置状态", permission=SUPERUSER | GUILD_SUPERUSER, priority=5)
open_robot = on_command("开启抢灵石", aliases={'关闭抢灵石'}, permission=SUPERUSER | GUILD_SUPERUSER, priority=5)
open_xiuxian = on_command("启用修仙功能", aliases={'禁用修仙功能'}, permission=SUPERUSER | GUILD_SUPERUSER, priority=5)
user_leveluprate = on_command('我的突破概率', priority=5)