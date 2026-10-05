# Logan 广告与应用管理保守订阅

导入地址： https://raw.githubusercontent.com/LoganMrSUN/gkd-safe-subscription/main/gkd.json5

## 当前版本 2026100502

原有 41 个开屏广告组保留；参考 Lin-arm/GKD_subscription v602 新增 21 个经过逐组静态审查的应用管理组。

- 界面管理：8 组默认开启。ChatGPT Plus 营销提示关闭、Kimi/Photoshop Express/QQ音乐/X/小红书的评价提示关闭、知乎评论氛围评价关闭、小红书截屏分享提示关闭。
- 阅读辅助：13 组默认关闭。DeepSeek完成思考后折叠、GitHub PR展开、Facebook/Instagram/Reddit/X翻译、X更多帖子与读取失败重试、知乎展开、小红书展开回复、QQ查看原图。

在 GKD 中按需单独打开“阅读辅助”规则。翻译可能产生网络请求，QQ原图增加流量，自动展开会改变阅读界面。每个新增组及规则设置至少 3 秒冷却；界面管理每次进入应用最多一次，阅读辅助每次进入应用最多三次。限次会降低自动化覆盖率。

## 风险评估

默认新增规则：低风险，但布局变化可能造成误触或误关提示。阅读辅助：低至中风险，主要是界面变化和流量；默认关闭。以上是静态判断，不代表已在手机验证。

不导入上游其他功能。排除付款、银行/证券、安装与风险绕过、权限授权、文件夹授权、登录批准、删除、系统设置、重发消息，以及自动隐藏安全/账号警告。所有全局规则保持为空。Instagram翻译删去首页坐标规则，只保留点击文字按钮的规则。保留既有开屏广告规则。

## 更新

订阅 id 保持 159916922；version 递增。没有上游自动同步、updateUrl或checkUpdateUrl，GKD从导入时填写的本仓库地址更新。停用旧的上游订阅，以免其规则继续运行。

## 审查与复现

- audit.json：首版筛选记录。
- enhancement-audit.json：本次新增规则清单、默认状态、风险及来源哈希。
- build.py：旧版开屏广告筛选脚本；单独运行不能生成增强版。
- enhance.py：增强版允许清单。下载 Lin-arm 原始 JSON5 后运行 `python enhance.py gkd.json5 lin-arm.json5 rebuilt.json5`，需要 Python json5。重建时版本号递增。

## 来源

原版来自 oklazeno/gkd-subscription；其来源及许可说明见 UPSTREAM-LICENSE.md。新增规则来自 https://github.com/Lin-arm/GKD_subscription ，作者 👻。保留原始选择器来源截图链接。版权归各原作者，本仓库不对上游许可解释作额外保证。
