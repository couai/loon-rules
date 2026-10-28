# 规则整理与上游选择

2026-10-28：迁移现有 WiFi Calling、运营商 App、银行/支付订阅。配置只更换 URL，保留每条订阅的策略、标签和顺序。每项保持独立文件，不把不同国家或不同出口的规则合成一个订阅。

## 目录与维护

| 内容 | 生成目录 | 来源 |
|---|---|---|
| AI | `rules/AI-Combined.list` | MetaCubeX、models.dev、可莉快照与手工补充 |
| WiFi Calling 英国/香港/德国/美国 | `rules/wificall/` | 现有规则 + HenryChiao 对应国家规则 |
| 香港运营商 App | `rules/carrier/` | 现有自维护规则 |
| 英国银行合集 | `rules/bank/UK.list` | 原 UK 快照 + iniwex5 实时来源 |
| 各银行、支付与交易服务 | `rules/bank/` | 现有规则 + 按服务筛选的公开上游 |

迁入的自维护内容放在 `overrides/<分类>/`，保留原注释和来源。原英国合集放在 `snapshots/`。每次构建合并这些文件与公开来源；公开来源每 6 小时刷新，自维护文件需要自行编辑。数量、来源贡献和跳过原因见 [manifest](../reports/manifest.json)。

## 采用和筛选的公开来源

- [HenryChiao WiFi Calling](https://github.com/HenryChiao/the_clash_ruleset/tree/main/The_Location_rule-set/Wi-Fi_Calling_rule-set)：按 UK/HK/DE/US 合并。英国源中的 MCC 230 域名与错误 CIDR `62.141.11.56/24` 明确排除；德国源夹带的 N26、tech26 银行域名排除，避免抢走银行策略。新增检查会阻止跨国家 MCC 混入。
- [blackmatrix7 PayPal](https://github.com/blackmatrix7/ios_rule_script/tree/master/rule/Loon/PayPal)：只选择配置中列出的 PayPal/Braintree 服务域名；没有整体引入其数百个历史或防御性注册域名、其他支付品牌和 USER-AGENT 规则。
- [blackmatrix7 OKX](https://github.com/blackmatrix7/ios_rule_script/tree/master/rule/Loon/OKX)、[MetaCubeX Kraken](https://github.com/MetaCubeX/meta-rules-dat/blob/meta/geo/geosite/kraken.list)：合并对应服务的公开列表。
- [xOS N26](https://github.com/xOS/Config/blob/Her/RuleSet/N26.list)：选择精确域名与域名后缀，不采用 `*26.de` 通配规则。
- [LeiyuG Coinbase](https://github.com/LeiyuG/Surge/blob/main/rules/Coinbase.list)、[Bitget](https://github.com/LeiyuG/Surge/blob/main/rules/Bitget.list)：选择明确的服务/CDN 域名，排除本次未确认范围的共享分析、认证域名及泛关键词。
- [iniwex5 UK](https://github.com/iniwex5/tools/blob/main/rules/UK.list)：原有英国银行上游，继续同步，保留原分类范围。

没有采用 xOS Bybit 的泛通配及共享 `rudderlabs.com`：这些会扩大匹配范围，现有 Bybit 规则也明确把一批类似域名列在待确认注释中。需要真实请求记录支持后再增补。

## 仍需留意的现有重叠

以下是迁移前已有的行为，本次保持不变：

- `UK.list` 含 `co.uk`、Stripe、LemFi、Trading212 和部分共享服务，且位于独立银行订阅前。因此它可能优先命中这些请求；各订阅的策略名相近也不代表完全相同。
- 香港运营商 App 列表包含 `googleapis.com`、`gstatic.com`、Appsflyer、Branch、Adjust 等共享域名，并且位于 WiFi Calling 和银行规则前；其中 `wlan.three.com.hk` 会优先走运营商 App 的策略。
- WiFi Calling US 包含一些 App/统计辅助域名。此次保留原有覆盖，未擅自缩减。

以后收窄这些范围时，应作为独立分流调整，先用实际流量验证，避免把地址迁移和出口行为变更混在一起。

## 本地规则后续归档建议

| 类别 | 适合进入公共仓库的内容 | 处理建议 |
|---|---|---|
| 现有自维护远程列表 | Claude-NetCoffee、Claude-NTP、Oracle-Loon | 可继续迁入独立 `rules/ai/`、`rules/services/`，保持各自策略 |
| 银行与钱包补充 | Zopa、PetaFuel、MetaMask、WalletConnect、Bycsi | 可按服务建补充列表；迁移前核对与现有银行订阅的覆盖和优先级 |
| 通用公开网站 | Linux.do、V2EX、NodeSeek、Railway、Grokipedia 等 | 按用途建小列表；出口策略继续由客户端指定 |
| AI 本地补丁 | `metaaivm.com` | AI-Combined 已包含；可评估删除重复项 |
| 重复后缀 | `fh-static.bycsi.com` 与 `bycsi.com` | 两者当前策略一致，前者已被后者覆盖，可在单独清理时删去 |
| 本机与个人网络 | 家庭/公司网段、场景策略、自建服务、DNS 引导与出口 | 留在客户端，不放入公共规则仓库 |

本地规则优先级高于订阅规则，因此把 `[Rule]` 项移动到远程订阅可能改变实际命中。此次只迁移已经是远程订阅的 27 项，其余作为后续整理建议，未改动本地规则。参考 [Loon 匹配优先级](https://nsloon.app/docs/Rule/)。

验证包括公开订阅可读取、每项保留原规则、Loon 实际加载内容及代表性分流请求。WiFi Calling 的分流验证不等于 SIM 注册或实际通话成功。
