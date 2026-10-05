# Logan 开屏广告保守订阅

基于 https://github.com/oklazeno/gkd-subscription 的规则，经保守筛选。原作者包括 Lin-arm、ganlinte、MengNianxiaoyao、aoguai、oklazeno。上游许可说明原样保存在 UPSTREAM-LICENSE.md；本项目不对其许可解释作额外保证。

## 安全边界

仅保留应用专属开屏广告组，且每条规则必须明确匹配“跳过 / 跳過 / skip”文字。排除敏感应用、系统组件、敏感词规则、坐标操作、非普通点击和跨规则依赖。删除所有全局规则与其他分类；每组限启动前 10 秒、最多一次点击。关键词过滤会遗漏风险，也会误删正常规则；不能保证零误触。

JSON5 可以使用标准 JSON 语法。本版本未在实际手机上验证选择器兼容性和跳广告效果。请先在普通应用上验证，发现误触立即停用对应组。

## 导入与更新

上传 gkd.json5 到自己的 GitHub 仓库后，复制该文件的 Raw 链接，在 GKD 中添加订阅。停用或移除旧的上游订阅，避免旧规则仍然运行。

文件未设置 updateUrl/checkUpdateUrl，GKD 使用你添加时填写的链接更新。因此始终导入自己仓库的 Raw 地址。每次修改需保持 id 不变并增加 version。没有自动同步上游工作流；不要直接用上游文件覆盖本文件。

订阅地址：https://raw.githubusercontent.com/LoganMrSUN/gkd-safe-subscription/main/gkd.json5

部署路径：仓库根目录 gkd.json5。仓库需要公开才能使用无需认证的 Raw 链接；不要把 GitHub token 写进订阅链接。

## 文件

- gkd.json5：可直接导入的保守版本。
- audit.json：源文件 SHA256、移除原因及完整移除清单。
- build.py：可复现筛选脚本，需要 Python json5；输入为父目录 upstream.json5。
- UPSTREAM-LICENSE.md：上游许可与署名说明。
