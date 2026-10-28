# 数据来源与署名

本项目转换并合并数据，不声称拥有上游数据。代码的 MIT 许可不用于重新授权第三方规则。

- **MetaCubeX / meta-rules-dat**：`meta` 分支的 `geo/geosite/category-ai-!cn.list`。原项目采用 GPL-3.0，完整许可保留在 [licenses/MetaCubeX-GPL-3.0.txt](licenses/MetaCubeX-GPL-3.0.txt)。[项目与来源说明](https://github.com/MetaCubeX/meta-rules-dat)。转换：`+.` 后缀表达式转为 Loon DOMAIN-SUFFIX，裸域名转为 DOMAIN。
- **models.dev / Anomaly**：`dev` 分支中 `providers/*/provider.toml` 的明确 API 主机名。原项目采用 MIT，完整许可保留在 [licenses/models.dev-MIT.txt](licenses/models.dev-MIT.txt)。[原项目](https://github.com/anomalyco/models.dev)。转换：仅保留主机名为 DOMAIN，按配置筛选。
- **可莉 / KeLee / luestr**：`snapshots/KeLee-AI-20261028.list` 来自仓库所有者本地 Loon 已加载的 AI.lsr 缓存，按所有者要求于 2026-10-28 导出。原订阅地址为 `https://kelee.one/Tool/Loon/Lsr/AI.lsr`，原项目说明见 [ProxyResource](https://github.com/luestr/ProxyResource)。该快照保留规则内容与逻辑条件，没有冒充可莉官方实时更新。上游仓库现说明仅配置模板开源，本项目不将其模板许可证推定为 AI.lsr 的授权，也不为该快照声明新的许可。

生成文件仅做格式规范化、精确去重及与手工补充合并。第三方材料应遵循其原作者条款。

## WiFi Calling、运营商与银行来源

- 迁入的 26 份自维护规则原来由仓库所有者的 COS 订阅提供；原始 URL 和注释保留在对应 `overrides/` 文件中。英国银行合集原来订阅自 **iniwex5/tools**，保留快照并继续同步 [UK.list](https://github.com/iniwex5/tools/blob/main/rules/UK.list)。
- **HenryChiao/the_clash_ruleset**：按国家补充 WiFi Calling，保留 [GPL-3.0 许可](licenses/HenryChiao-GPL-3.0.txt)。具体筛选见 [整理说明](docs/rule-organization.md)。
- **blackmatrix7/ios_rule_script**：PayPal 经过域名筛选，OKX 按对应类别合并；保留 [GPL-2.0 许可](licenses/blackmatrix7-GPL-2.0.txt)。
- **MetaCubeX/meta-rules-dat**：另使用 Kraken 分类，来源许可见上文。
- **xOS/Config**、**LeiyuG/Surge**：分别使用 N26、Coinbase/Bitget 的公开规则，并进行域名或类型筛选；原项目链接见 [整理说明](docs/rule-organization.md)。这些来源及 iniwex5/tools 的仓库 API 未标示许可证，本仓库不为它们另行授予 MIT 许可。

各分类输出保留来源署名链接；没有将第三方规则整体重新授权为本项目原创代码的许可。
