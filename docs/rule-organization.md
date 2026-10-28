# 规则整理与上游选择

2026-10-28：迁移现有 WiFi Calling、运营商 App、银行/支付订阅。配置只更换 URL，保留每条订阅的策略、标签和顺序。每项保持独立文件，不把不同国家或不同出口的规则合成一个订阅。

## 目录与维护

| 内容 | 生成目录 | 来源 |
|---|---|---|
| AI | `rules/AI-Combined.list` | MetaCubeX、models.dev、可莉快照与手工补充 |
| WiFi Calling 英国/香港/德国/美国 | `rules/wificall/` | 现有规则 + HenryChiao 对应国家规则 |
| 香港运营商 App | `rules/carrier/` | 现有自维护规则 |
| 英国银行精简合集 | `rules/bank/UK-Banks.list` | 原快照 + iniwex5，限定银行域名；原有银行品牌关键词/IP |
| 各银行、支付与交易服务 | `rules/bank/` | 现有规则 + 按服务筛选的公开上游 |

迁入的自维护内容放在 `overrides/<分类>/`，保留原注释和来源。原英国合集放在 `snapshots/`。每次构建合并这些文件与公开来源；公开来源每 6 小时刷新，自维护文件需要自行编辑。数量、来源贡献和跳过原因见 [manifest](../reports/manifest.json)。

## 采用和筛选的公开来源

- [HenryChiao WiFi Calling](https://github.com/HenryChiao/the_clash_ruleset/tree/main/The_Location_rule-set/Wi-Fi_Calling_rule-set)：按 UK/HK/DE/US 合并。英国源中的 MCC 230 域名与错误 CIDR `62.141.11.56/24` 明确排除；德国源夹带的 N26、tech26 银行域名排除，避免抢走银行策略。新增检查会阻止跨国家 MCC 混入。
- [blackmatrix7 PayPal](https://github.com/blackmatrix7/ios_rule_script/tree/master/rule/Loon/PayPal)：只选择配置中列出的 PayPal/Braintree 服务域名；没有整体引入其数百个历史或防御性注册域名、其他支付品牌和 USER-AGENT 规则。
- [blackmatrix7 OKX](https://github.com/blackmatrix7/ios_rule_script/tree/master/rule/Loon/OKX)、[MetaCubeX Kraken](https://github.com/MetaCubeX/meta-rules-dat/blob/meta/geo/geosite/kraken.list)：合并对应服务的公开列表。
- [xOS N26](https://github.com/xOS/Config/blob/Her/RuleSet/N26.list)：选择精确域名与域名后缀，不采用 `*26.de` 通配规则。
- [LeiyuG Coinbase](https://github.com/LeiyuG/Surge/blob/main/rules/Coinbase.list)、[Bitget](https://github.com/LeiyuG/Surge/blob/main/rules/Bitget.list)：选择明确的服务/CDN 域名，排除本次未确认范围的共享分析、认证域名及泛关键词。
- [iniwex5 UK](https://github.com/iniwex5/tools/blob/main/rules/UK.list)：新 UK-Banks 只同步 50 个已审核的银行/金融服务域名及子域名，另保留 9 条银行品牌关键词和 1 条原 IP 规则。旧 UK 保留兼容，不再用于本机。

没有采用 xOS Bybit 的泛通配及共享 `rudderlabs.com`：这些会扩大匹配范围，现有 Bybit 规则也明确把一批类似域名列在待确认注释中。需要真实请求记录支持后再增补。

## 仍需留意的现有重叠

以下重叠需要区分处理：

- 旧 `UK.list` 的 90 条精简为 `UK-Banks.list` 的 60 条：删除 `co.uk`、Stripe、LemFi、Trading212、共享统计/验证服务等 30 条，保留银行域名、品牌关键词与原 IP 规则。Stripe 使用现有独立订阅并放在 OpenAI 前；LemFi、Trading212 使用各自独立订阅。不要同时启用新旧 UK 列表。
- 香港运营商 App 列表包含 `googleapis.com`、`gstatic.com`、Appsflyer、Branch、Adjust 等共享域名，并且位于 WiFi Calling 和银行规则前；其中 `wlan.three.com.hk` 会优先走运营商 App 的策略。
- WiFi Calling US 包含一些 App/统计辅助域名。此次保留原有覆盖，未擅自缩减。

以后收窄这些范围时，应作为独立分流调整，先用实际流量验证，避免把地址迁移和出口行为变更混在一起。

## Claude 与 Oracle 订阅

Claude-NetCoffee、Claude-NTP、Oracle-Loon 已迁入独立 `rules/ai/`、`rules/services/` 文件，分别保留 34、116、25 条规则；客户端原位置替换 URL，保留原策略。

单条网站和钱包补充由客户端 `[Rule]` 管理，仓库不保留拆分文件或生成配置。本地广告例外、个人端点、DNS 引导和场景网段也由客户端维护。Loon 的本地 > 插件 > 订阅来源优先级见 [官方说明](https://nsloon.app/docs/Rule/)。

Claude-NTP 是通用时间服务列表，含国内和国外地址，并非只有 Claude 或海外服务；继续沿用原人工智能策略，未擅自删减。Claude-NetCoffee 保留原第三方域名/关键词、IP-ASN 与 no-resolve；Oracle 保留 `.java` 和 `.oracle` 顶级域名后缀。它们是自维护快照，编辑 overrides 后由六小时工作流重建；不会自动重新抓取 NetCoffee 网页。

Oracle-Loon 与本机另一份 Oracle.lsr 的当前 25 条内容相同。保留两份及原顺序后，请求可继续先命中 Oracle.lsr 的 DIRECT；以新订阅实际加载内容确认迁移生效，不声称它一定抢先命中。

验证包括公开订阅可读取、每项保留原规则、Loon 实际加载内容及代表性分流请求。WiFi Calling 的分流验证不等于 SIM 注册或实际通话成功。
