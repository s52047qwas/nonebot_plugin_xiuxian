# nonebot_plugin_xiuxian

_:tada::tada::tada:修仙模拟器！:tada::tada::tada:_

## 简介

本插件主要为实现群聊修仙功能，国庆预计更新，宗门，背包，装备，丹药，技能，战斗系统，大佬请一起来写吧，群号：760517008

## 设定征集中，有好的想法可以推送给我哦~~~
todo的功能，
1、修炼室
2、坊市
3、装备，丹药，背包
4、排行榜
5、秘境

## 特色功能

--已实装功能：<br>
--指令：<br>
## 9月27更新配置文件，请下载最新config.yaml文件
  1、我要修仙：进入修仙模式<br>
  2、我的修仙信息：获取修仙数据<br>
  3、修仙签到：获取灵石及修为<br>
  4、重入仙途：重置灵根数据，每次100灵石<br>
  5、金银阁：猜大小，赌灵石<br>
  6、改名xx：修改你的道号，暂无用户，待排行榜使用<br>
  7、突破：修为达到要求后，可突破境界<br>
  8、闭关，出关，灵石出关：挂机进行修炼，增加修为<br>
  9、送灵石：送灵石+数量+道号或者艾特某人即可<br>
  10、排行榜功能，境界排行榜，灵石排行榜，战力排行榜<br>
  11、悬赏令功能：指令：悬赏令，悬赏令接取+编号，悬赏令结算<br>
  12、偷灵石@对应用户：偷取对应用户灵石<br>
  13、神秘力量+灵石数量+@对应人  实例：神秘力量100@xx  给对应用户增加灵石,当为神秘力量100这样时，为全体用户增加灵石<br>
  14、宗门系统：发送“宗门帮助”获取信息<br>
  15、抢灵石：抢灵石@xxx，对应为根据气血，法术，攻击力进行回合制战斗<br>
  16、开启/关闭抢灵石：开启或关闭抢灵石功能<br>
  17、我的突破概率：查询当前的突破概率<br>
  18、世界boss：发送“世界boss帮助”获取信息<br>
  19、坊市：查询商店信息，当前商品为用户自行上架拍卖<br>
  20、重置状态：不艾特人时，重置所有用户HP,MP,ATK信息，艾特用户时，重置对应用户状态<br>
  21、钱庄：发送“钱庄帮助”获取信息<br>
  22、启用/禁用修仙功能：启用或禁用，对某个群聊的修仙模组<br>
  23、我的功法：功法系统，当前获取途径：宗门处<br>
  24、炼丹系统：发送“炼丹帮助”获取对应操作指令，对应炼丹炉，可在世界boss处获取。<br>



## 安装

- 使用脚手架安装(推荐github处拉取源码使用)

```
pip install nonebot-plugin-xiuxian
```
## 更新
```
pip install nonebot-plugin-xiuxian -U或者pip install nonebot-plugin-xiuxian --upgrade
```

- 然后在bot.py文件中添加

```
nonebot.load_plugin('nonebot_plugin_xiuxian')
```

## 功能展示

- 使用 `/我要修仙` 指令触发机器人，机器人创建用户信息，生成灵根，境界等信息。
- 发送突破，当修为足够时，可突破境界。
- 发送修仙签到，获取每日初始化的灵石及修为。

![image](https://user-images.githubusercontent.com/44226600/187607785-3ea934f4-2b5c-418e-9b99-e8a8e5562125.png)

## 一些问题

- 当前首次使用，未自动创建json文件及sql文件，请在[githut](https://github.com/s52047qwas/nonebot_plugin_xiuxian)处，目录nonebot_plugin_xiuxian ——>xiuxian
处下载文件，放置于bot目录，data -> xiuxian文件夹处
- 当为放置为plugins目录使用时，请修改根目录下__init__.py文件中的42行：src=''中的内容，填写的是存放插件的目录，一般情况下 src='src.plugins.'  如有不同请按照格式修改
  


## 更新
#2022/10/06
新增抢灵石功能;
新增气血，法术，攻击力;
新增回合制战斗系统;

# 2022/09/20
新增了宗门功能
优化更新了悬赏令功能
注意下载json数据更新

# 2022/09/13
新增灵石出关功能，消耗对应灵石增加修为
调整重入仙途为配置处调整消耗，XiuConfig.py
新增偷灵石功能
更新版本0.3.3
调整存档显示，修复排行榜缺失，新增GM权限
pip install nonebot-plugin-xiuxian==0.3.3

# 2022/09/09
部分境界信息从数据库分离为json文件，调整各项配置文件，更新各个json格式，需替换更新，新增Xiuconfig.py配置文件，配置CD等信息

# 2022/09/07
新增悬赏令功能，初版临时作为获取灵石的途径，后续待优化玩法<br>
# 2022/09/04
突破：修为达到要求后，可突破境界<br>
闭关，出关：挂机进行修炼，增加修为<br>
送灵石：送灵石+数量+道号或者艾特某人即可<br>
排行榜功能<br>

## 特别感谢

- [NoneBot2](https://github.com/nonebot/nonebot2)：本插件实装的开发框架。
- [go-cqhttp](https://github.com/Mrs4s/go-cqhttp)：稳定完善的 CQHTTP 实现。

## 插件依赖

- nonebot2
- nonebot-adapter-onebot
- go-cqhttp

## 支持

大家喜欢的话可以给这个项目点个star

有bug、意见和建议都欢迎提交 [Issues](https://github.com/s52047qwas/nonebot_plugin_xiuxian/issues) 
或者联系进入QQ交流群：760517008

## 许可证
本项目使用 [MIT](https://choosealicense.com/licenses/mit/) 作为开源许可证

