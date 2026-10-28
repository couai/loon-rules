# 规则整理与上游选择

2026-10-28：迁移现有 WiFi Calling、运营商 App、银行/支付订阅。最初迁移只更换 URL；随后按下述审核结果收窄运营商规则并调整优先级，保留策略。每项保持独立文件，不把不同国家或不同出口的规则合成一个订阅。

## 目录与维护

| 内容 | 生成目录 | 来源 |
|---|---|---|
| AI | `rules/AI-Combined.list` | MetaCubeX、models.dev、可莉快照与手工补充 |
| WiFi Calling 英国/香港/德国/美国 | `rules/wificall/` | 现有规则 + HenryChiao 对应国家规则 |
| 香港/英国/德国运营商 App | `rules/carrier/` | 运营商专属域名；移除泛关键词和共享服务 |
| Claude 与时间服务 | `rules/ai/Claude.lsr`、`rules/ai/Claude-NTP.list` | NetCoffee、v2fly 与原有补充快照 |
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
- 客户端银行规则先放各服务的独立订阅，最后放 `UK-Banks.list` 作为英国银行补充（当前位于 Sumsub 后、GitHub 前），保留英国手动选择策略。当前合集与独立银行列表没有发现域名或完整规则重叠；该顺序也便于以后增加专用规则。

## 运营商范围与优先级

四份 WiFi Calling 按 UK、HK、DE、US 的原顺序放在 HK/UK/DE-Carrier-App 前，各自保留原地区策略。这样 `wlan.three.com.hk` 先命中香港 WiFi Calling，随后 `three.com.hk` 才覆盖运营商 App。域名规则仍遵循 Loon 的类型和来源优先级，提前订阅不会使 IP 规则越过域名规则。

香港补充 SmarTone `mnc006.mcc454` 与 CMHK `mnc012.mcc454` 的 ePDG 后缀，美国补充 Verizon `wo.vzwwo.com`，均由 override 和 `required_rules` 保留。CMHK 依据编号、命名标准与 DNS 核查，仍需实卡验证。英国 EE 的 `mnc030`、`mnc034` 已由现有 `mcc234` 覆盖。依据及待核查项见 [运营商核查记录](wifi-carrier-review-proposal.md)。

UK-Carrier-App 收录 6 条，DE-Carrier-App 收录 7 条。UK WiFi 的 `ee.co.uk`、`giffgaff.com`、`voxi.co.uk` 与 DE WiFi 的 `vodafone.de` 迁入对应 App 合集，并在 WiFi 合并后排除以避免上游重新带回。保留 `ct.ee.co.uk`、ePDG/IMS、现有 IP 与开通辅助规则。新合集分别使用英国手动选择、德国手动策略；本机已移除 `o2online.de` 的个人自建覆盖规则，现由 DE App 订阅使用德国手动策略；香港 App 继续使用香港手动策略。CMLink 英港共用主机，保留现行香港规则，不将整个 `cmlink.com` 重复加入英国合集。

德国列表补充 `DOMAIN-SUFFIX,epdg.epc.mnc001.mcc262.pub.3gppnetwork.org`，修复该网关原先落到 FINAL 的遗漏，继续使用德国手动策略。此项由本地补充源及 `required_rules` 保留，不扩大为匹配全部 `mcc262` 的关键词。

HK-Carrier-App 保留 22 条明确域名，移除 11 个泛关键词、8 个共享服务后缀与 2 个已被父域名覆盖的子域名。MyLink 使用 `mylinkapp.hk` 及精确主机 `mylink.komect.com`，不扩大到整个 `komect.com`；依据 CMHK 的 [MySIM 文件](https://www.hk.chinamobile.com/upload/onlineshop/2026-04-15/5g-mysim-local-package-sc.pdf)和 [MyLink 活动文件](https://www.hk.chinamobile.com/upload/onlineshop/2026-01-15/tnc_slash_5G_Student_Referral_Program_115.pdf)。Appsflyer、Branch、Adjust、Crashlytics、Firebase、Google API/静态资源等共享平台交由其他规则处理。

WiFi Calling UK 移除 `gspe1-ssl.ls.apple.com`；US 移除 `mzstatic.com`、`cohere.com`、`ip-api.com`、`optimizely.com`、`crashlytics.com`、`mobilefuse.com`、`inmobi.com`、`kochava.com`、`agkn.com`、`inner-active.mobi`。这仅撤销强制地区出口，不添加拦截；Apple 资源、AI 与通用服务恢复由后续规则匹配。`exclude_rules` 对合并后的全部来源生效，测试防止这些共享服务重新混入。ePDG/IMS、运营商认证、现有 IP 和国家 UDP 条件继续保留。

## Claude 与 Oracle 订阅

`Claude.lsr` 由原 Claude-NetCoffee 重命名，完整保留 34 条规则及人工智能策略，在客户端替换原 NetCoffee 位置；移除另一个重复的可莉 Claude.lsr。`Claude-NTP.list` 保留 116 条及原位置。

Oracle 仅保留可莉 `https://rule.kelee.one/Loon/Oracle.lsr`，使用原 DIRECT 策略；仓库内重复的 Oracle-Loon 输出、来源和生成配置已删除。GoogleVoice、AppStore、OneDrive 继续保留。

单条网站和钱包补充由客户端 `[Rule]` 管理，仓库不保留拆分文件或生成配置。本地广告例外、个人端点、DNS 引导和场景网段也由客户端维护。Loon 的本地 > 插件 > 订阅来源优先级见 [官方说明](https://nsloon.app/docs/Rule/)。

Claude-NTP 是通用时间服务列表，含国内和国外地址，并非只有 Claude 或海外服务；继续沿用原人工智能策略，未擅自删减。Claude.lsr 保留原第三方域名/关键词、IP-ASN 与 no-resolve。Claude 文件是自维护快照，编辑 overrides 后由六小时工作流重建；不会自动重新抓取 NetCoffee 网页。


验证包括公开订阅可读取、每项保留原规则、Loon 实际加载内容及代表性分流请求。WiFi Calling 的分流验证不等于 SIM 注册或实际通话成功。
