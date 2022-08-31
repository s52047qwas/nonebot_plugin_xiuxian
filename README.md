# nonebot_plugin_xiuxian

_:tada::tada::tada:修仙模拟器！:tada::tada::tada:_

## 简介

本插件主要为实现群聊修仙功能，战斗系统to do中。

## 特色功能

--已实装功能：<br>
--指令：<br>
  --1、我要修仙：进入修仙模式<br>
  --2、我的修仙信息：获取修仙数据<br>
  --3、修仙签到：获取灵石及修为<br>
  --4、重入仙途：重置灵根数据，每次100灵石<br>
  --5、#金银阁：猜大小，赌灵石<br>
  --6、改名xx：修改你的道号，暂无用户，待排行榜使用<br>
  --7、其他功能to do中<br>


## 安装

- 使用脚手架安装(推荐位git处拉取源码使用)

```
pip install nonebot-plugin-xiuxian
```

- 然后在bot.py文件中添加

```
nonebot.load_plugin('nonebot-plugin-xiuxian')
```

## 功能展示

- 使用 `/我要修仙` 指令触发机器人，机器人创建用户信息，生成灵根，境界等信息。
- 发送突破，当修为足够时，可突破境界。
- 发送修仙签到，获取每日初始化的灵石及修为。

![image](https://user-images.githubusercontent.com/44226600/187607785-3ea934f4-2b5c-418e-9b99-e8a8e5562125.png)

## 一些问题

- 当前首次使用，未自动创建json文件及sql文件，请在[githut](https://github.com/s52047qwas/nonebot_plugin_xiuxian)处，目录nonebot_plugin_xiuxian ——>xiuxian
处下载文件，放置于bot目录，data -> xiuxian文件夹处

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
或者联系我：578043031

## 许可证
本项目使用 [MIT](https://choosealicense.com/licenses/mit/) 作为开源许可证。

