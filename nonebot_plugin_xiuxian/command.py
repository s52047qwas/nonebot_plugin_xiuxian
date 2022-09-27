from re import I

from nonebot import on_command, on_message, on_regex, on_fullmatch
from nonebot.adapters.onebot.v11 import (
    PRIVATE_FRIEND,
    GROUP,
)
from nonebot.permission import SUPERUSER

run_xiuxian = on_fullmatch("我要修仙", priority=5)
xiuxian_message = on_command("我的修仙信息", aliases={"我的存档"}, priority=5)
restart = on_command("再入仙途", aliases={"重新修仙", "重入仙途"}, priority=5)
package = on_command("我的纳戒", aliases={"升级纳戒"}, priority=5)
sign_in = on_fullmatch("修仙签到", priority=5)
help_in = on_fullmatch("修仙帮助", priority=5)
remaker = on_fullmatch("重入仙途", priority=5)

use = on_fullmatch("#使用", priority=5)
buy = on_fullmatch("#购买", priority=5)
rank = on_command("排行榜", aliases={"修仙排行榜", "灵石排行榜", "战力排行榜", "境界排行榜", "宗门排行榜"}, priority=5)
time_mes = on_message(priority=999)
remaname = on_command("改名", priority=5)
level_up = on_fullmatch("突破", priority=5)
in_closing = on_fullmatch("闭关", priority=5)
out_closing = on_command("出关", aliases={"灵石出关"}, priority=5)
give_stone = on_command("送灵石", priority=5)
do_work = on_command("悬赏令", priority=5)
dufang = on_regex(
    r"(金银阁)\s?(\d+)\s?([大|小|猜])?\s?(\d+)?",
    flags=I,
    permission=PRIVATE_FRIEND | GROUP,
)

steal_stone = on_command("偷灵石", aliases={"飞龙探云手"}, priority=5)
gm_command = on_command("神秘力量", permission=SUPERUSER, priority=5)

my_sect = on_command("我的宗门", aliases={"宗门信息"}, priority=5)
create_sect = on_command("创建宗门", priority=5)
join_sect = on_command("加入宗门", priority=5)
sect_position_update = on_command("宗门职位变更", priority=5)
sect_donate = on_command("宗门捐献", priority=5)
sect_out = on_command("退出宗门", priority=5)
sect_kick_out = on_command("踢出宗门", priority=5)
sect_owner_change = on_command("宗主传位", priority=5)

rob_stone = on_command("抢劫", aliases={"抢灵石"}, priority=5)

