



<div align="center">
    <img src="https://s4.ax1x.com/2022/03/05/bw2k9A.png" alt="bw2k9A.png" border="0"/>
    <h1>nonebot_plugin_setu</h1>
    <b>基于nonebot2、loliconApi的涩图插件</b>
    <br/>
    <a href="https://github.com/ayanamiblhx/nonebot_plugin_setu/stargazers"><img alt="GitHub stars" src="https://img.shields.io/github/stars/ayanamiblhx/nonebot_plugin_setu?color=%09%2300BFFF&style=flat-square"></a>
    <a href="https://github.com/ayanamiblhx/nonebot_plugin_setu/issues"><img alt="GitHub issues" src="https://img.shields.io/github/issues/ayanamiblhx/nonebot_plugin_setu?color=Emerald%20green&style=flat-square"></a>
    <a href="https://github.com/ayanamiblhx/nonebot_plugin_setu/network"><img alt="GitHub forks" src="https://img.shields.io/github/forks/ayanamiblhx/nonebot_plugin_setu?color=%2300BFFF&style=flat-square"></a>
    <a href="https://github.com/ayanamiblhx/nonebot_plugin_setu/blob/main/LICENSE"><img alt="GitHub license" src="https://img.shields.io/github/license/ayanamiblhx/nonebot_plugin_setu?color=Emerald%20green&style=flat-square"></a>
</div>

## 安装及更新

- 安装

```bash
nb plugin install nonebot_plugin_setu
```
或者
```bash
pip install nonebot_plugin_setu
```
推荐使用`nb`进行安装
- 更新

```bash
nb plugin update nonebot_plugin_setu
```
或者
```bash
pip install nonebot_plugin_setu -U
```
- 导入插件
  
  在`pyproject.toml`里的`[tool.nonebot]`中添加`plugins = ["nonebot_plugin_setu"]`
  
  **注**：如果你使用`nb`安装插件，则不需要设置此项


## 使用方式

<p align="center">
    <a href="https://asciinema.org/a/488190">
    <img src="https://bucket-1305806783.cos.ap-shanghai.myqcloud.com/setu_config.svg?q-sign-algorithm=sha1&q-ak=AKIDvdo-c-KtUVpgaidaLfg_guqXoNtIQPnCvJCwhSN_F2OyTjimJ2fpWlfpJWXaBj1F&q-sign-time=1686313421;1686317021&q-key-time=1686313421;1686317021&q-header-list=host&q-url-param-list=&q-signature=4d72847f10844e73e3c4887bd7b51c642fc65aae&x-cos-security-token=IntmoJTcUBDUbESzoQ06PJ24O5uj7qTaf3ec5b16fc5234af818f0ba4c00572a3w0u_kXF-8SZ6EeZc6NWKAuv14yL93dy0jiGCcdQmi5jBELN5evsVkYx_0FJ1UAXIqlU8wLM03ES2SClWaNDEHMRa6Za6HQTGTvetNNXLuLJyhNb6nTrz7-Knh9F24jJKup1llke-Z-EZIidVMCS8Lv68syeqF_dpGSwF86mgK7LR-rXmJv3yKO_-ADzNan1y7k-G2pqeQzX8jXMwWeRToQ" />
    </a>
</p>


首先运行一遍robot，然后在robot目录的data目录下修改setu_config.json配置文件，然后重启robot  
-->  
更改为直接去pixiv通过tag搜图返图  
在pixiv抓包cookie填入`setu_config.json`中  
魔改过，部分命令设置或许无效，明确的有往数据库写入返图信息，相关代码已被注释
新增热度排序功能，仅限tag搜索且使用的是会员`cookie`

### 添加配置

- **在你的setu_config.json文件中修改如下配置：**

  SUPERUSERS = ["主人的qq号"]，可添加多个

  PROXIES_HTTP = 'HTTP魔法地址(例如`http://127.0.0.1:7890`)，这与你使用的魔法有关'

  PROXIES_SOCKS = 'SOCKS5魔法地址(例如`socks5://127.0.0.1:10808`)，这与你使用的魔法有关'

  **注**：若没有魔法或者不会设置可不填



### 正式使用

| 命令                               | 举例                                | 说明                                                                                   |
|----------------------------------|-----------------------------------|:-------------------------------------------------------------------------------------|
| 下载涩图/色图+数量                       | 下载涩图12345、下载色图12345               | 下载涩图：下载非涩涩图片；下载色图：下载色色图片                                                             |
| 涩图、setu、无内鬼、色图                   | setu                              | 发送图片                                                                                 |
| @用户cd+时间（秒）                      | @张三cd12345                        | 指定用户cd                                                                               |
| 群cd+时间（秒）                        | 群cd12345                          | 指定群cd                                                                                |
| 开启/关闭在线发图                        | 开启在线发图                            | 在线发图开启之后，图片将不再从本地发送而是从网上下载后在线发送，不会占用服务器存储资源                                          |
| 开启/关闭魔法                          | 关闭魔法                              | 魔法关闭之后，图片的下载以及在线发送将不再通过魔法而是通过镜像来完成，如果没有魔法或者不会设置推荐关闭                                  |
| 涩图tagA和B和C（最多指定三个tag）            | 涩图tag碧蓝航线、涩图tag公主连结和白丝            | 为了保证尽可能多地获取tag指定的内容，tag指定的图片都会在线获取而不从本地寻找，是否存储依然遵循在线发图开关                             |
| 撤回间隔+时间（秒）                       | 撤回间隔20、撤回间隔0                      | 设置撤回间隔之后，机器人将会在指定间隔后撤回发送的图片，撤回间隔为0时，机器人将不会进行撤回。同时撤回间隔以群聊为单位，每个群都能设置不同的间隔，私聊将不会触发撤回操作 |
| 涩图api、设置api地址+`服务器ip地址或域名:机器人端口` | 涩图api、设置api地址`123.456.789.0:8080` | 设置api并开放防火墙端口之后，就能把服务器中的图库数据转为api供他人调用，本地api调试请访问`http://localhost:机器人端口/setu/docs`  |
| 开启涩涩、开启私聊涩涩、关闭涩涩、关闭私聊涩涩          | 开启涩涩、开启私聊涩涩                       | 开启涩涩之后，机器人将会发送色色图片，涩涩以群聊为单位，支持不同群是否开启                                                |
| 涩图帮助                             | 涩图帮助                              | 获取命令列表                                                                               |
| 涩图转发者名字                          | 涩图转发者名字bot                        | 修改发送转发消息时的转发者名字                                                                      |
| 添加/删除ban                             | 添加/删除ban3d                        | 添加/删除禁止匹配自定义tag的插画                                                                             |
| 查看ban                           | 查看ban                      | 查看当前被ban的tag                                                           |
| 涩榜(数字）                 |榜涩榜、涩榜50                                              |查看今日排行榜 ，带数字查看排行榜位置
| 开/关图           |开图、关图                   |开关群聊发图权限         |
| 涩榜排序        |涩榜  |图片 排序：最新、旧、热度 ！需要注意只有使用会员账号才可选择按热度排序，否则还是会按最新排序

#### 注：

- 用户cd和群cd同时存在时，以用户cd为准
- 群cd默认3600s
- 开放api时请保证机器人监听的地址为0.0.0.0
- 仅好友才能私聊发图，私聊发图时若未指定用户cd，则默认cd3600s

## TODO

- [ ] 数据可视化



## 更新日志

### 2023/1/9

- 修复无法捕获异常bug
- 优化图片下载以及异常通知
- 修复发送的图片为空白的bug

### 2022/12/27

- 将图片发送方式改为转发
- 新增修改转发者名字

### 2022/7/29[v1.1.2]

- 增加帮助，修复下载图片失败bug

### 2022/4/2[v1.0.14]

- 新增自动撤回
- 新增自建图库与图库api
- 新增涩涩模式



### 2022/3/19[v1.0.11]

- 新增指定tag，可指定tag进行发图，tag最多指定三个



### 2022/3/17[v1.0.9]

- 新增在线发图开关，图片可以在线发送而不占用服务器存储空间
- 新增魔法开关，没有魔法也能够正常使用

注：旧版本用户请删除setu_config.json然后重新配置一遍



### 2022/3/13[v1.0.5]

- 删除SETU_CD，修改cd配置，不再依赖userscd.json，转为依赖数据库文件
- 添加用户cd和群cd，可由管理员进行指定和更改
- 引入数据库存储图片信息，修改图片存储格式从jpg转为图片原本对应样式

注：旧版本用户请删除setu_config.json然后重新配置一遍



### 2022/3/9[v1.0.4]

- 更改异常捕获范围，修复无法捕获异常的bug



### 2022/3/8[v1.0.3]

- 删除配置：SETU_NUM，可下载指定数量的图片
- 新增下载图片进度条



### 2022/3/5 [v1.0.1]

- 支持nonebot[v2.0.0-beta2]，请更新至最新版nonebot使用
- 更改图片的名字为对应pid
- 更改文件的配置方式，不再依赖.env文件



### 2022/1/26 [v1.0.0a1]

- 支持nonebot[v2.0.0-beta1]，beta1之前的请使用0.0.6版本
