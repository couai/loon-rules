# WiFi Calling 与运营商 App 核查记录

核查及实施日期：2026-10-28。按确认方案补充 3 个网关、增加 UK/DE 两份 App 合集，继续复用六小时构建任务。

## WiFi Calling 补充

| 地区 | 补充与依据 |
|---|---|
| 香港 SmarTone | `DOMAIN-SUFFIX,epdg.epc.mnc006.mcc454.pub.3gppnetwork.org`；[TP-Link 官方参考](https://support.omadanetworks.com/en/document/120222/)明确列出，Google/Cloudflare DNS 均可解析。 |
| 香港 CMHK | `DOMAIN-SUFFIX,epdg.epc.mnc012.mcc454.pub.3gppnetwork.org`；[ITU 分配表](https://www.itu.int/dms_pub/itu-t/opb/sp/T-SP-OB.1218-2021-OAS-PDF-E.pdf)将 454-12 分配给 CMHK，按 [ETSI §19.4.2.9.2](https://www.etsi.org/deliver/etsi_ts/123000_123099/123003/14.07.00_60/ts_123003v140700p.pdf)命名，两家 DNS 返回有效地址。这是编号、标准和 DNS 支持的补充，尚未验证实卡注册。 |
| 美国 Verizon | `DOMAIN-SUFFIX,wo.vzwwo.com`；[HPE 官方模式](https://arubanetworking.hpe.com/techdocs/CLI-Bank/Content/instant/sh-wifical-dns-patrns.htm)及 TP-Link 均列出该网关。 |

修改前以上三者的本机 UDP 500 请求均落到 `FINAL,DIRECT`。英国 EE 的 `mnc030.mcc234`、`mnc034.mcc234` 已实际命中 `DOMAIN-KEYWORD,mcc234`，不重复添加。美国现有列表已覆盖 [T-Mobile 企业网络要求](https://www.t-mobile.com/support/coverage/wi-fi-calling-on-a-corporate-network)中的主要网段。

香港 `mnc015.mcc454`、`mnc017.mcc454` 标准 ePDG 域名本次解析到 `127.0.0.1`；AT&T 的 `vtc.epdg.att.ericsson.net`、`cnc.epdg.att.ericsson.net`、文档中的 `cnc.epdg.att.erricson.net` 及旧 Sprint `primgw.vowifi2.spcsdns.net` 返回 NXDOMAIN，因此暂不加入。不按 MNC 分配表穷举网关，也不增加笼统 `mcc454` 关键词。

## 英国 App：6 条

以下官网支持账户、账单、充值或 App 管理，按运营商根域收录：

- `ee.co.uk`：[EE App](https://ee.co.uk/download-ee-app)。
- `giffgaff.com`：[giffgaff App](https://www.giffgaff.com/mobile-app?app=1)。
- `voxi.co.uk`：[VOXI 账户](https://www.voxi.co.uk/help/account)。
- `vodafone.co.uk`：[My Vodafone](https://www.vodafone.co.uk/login)。
- `o2.co.uk`：[My O2 App](https://www.o2.co.uk/help/products-and-services/o2-services-and-apps/my-o2-app)。
- `three.co.uk`：[Three 账户指南](https://www.three.co.uk/support/account/manage-your-account/registration-and-login-help)。

前 3 个根域从 UK WiFi 移入 App 合集；`ct.ee.co.uk` 原兼容条目继续留在 WiFi。CMLink UK 的[登录](https://www.cmlink.com/uk/en/login/)和[充值](https://www.cmlink.com/uk/en/topup/)与香港使用同一主机不同路径，域名规则无法区分 `/uk/`。保留现行香港 `cmlink.com` 规则，不重复加入英国表。

## 德国 App：7 条

- `DOMAIN-SUFFIX,telekom.de`：[MeinMagenta](https://www.telekom.de/apps/meinmagenta-app)。
- 精确主机 `accounts.login.idm.telekom.com`：[Telekom 官方登录说明](https://www.telekom.de/datenschutzhinweise/view-plain/047.pdf)。
- 精确主机 `account.idm.telekom.com`、`meinkonto.telekom-dienste.de`、`meinmagenta.go.link`：MeinMagenta 官方页面直接链接。不扩大到 `telekom.com` 或共享 `go.link` 根域。
- `DOMAIN-SUFFIX,vodafone.de`：[MeinVodafone](https://www.vodafone.de/hilfe/meinvodafone.html)，从 DE WiFi 移入。
- `DOMAIN-SUFFIX,o2online.de`：[Mein O2](https://www.o2online.de/mein-o2/)。本机后续按用户要求移除「个人自建」本地覆盖，现由 DE App 订阅使用德国手动策略。

## 顺序、例外与验证

四份 WiFi 按 UK/HK/DE/US 原顺序在前，随后 HK/UK/DE 三份 App 合集。UK App 使用英国手动选择，DE App 使用德国手动策略，HK App 保留香港手动策略；其他既有策略和订阅相对顺序不变。WiFi override 与 `exclude_rules` 同步调整，防止上游重新带回迁出的 App 根域；新增网关由 `required_rules` 保留。

保留 ePDG/IMS、现有 IP、`ct.ee.co.uk`、德国网络基础设施域名和既有 eSIM 开通辅助。`mzstatic.com` 等共享服务继续排除。英国 `go-esim.com` 后续可参考 [EE](https://business.ee.co.uk/help/ee-getting-started/setting-up-your-esim/)与 [BT](https://business.bt.com/help/article/bt-mobile/esim-and-sim-cards/esim-on-samsung-devices/)官方资料，按实际开通主机收窄；本次不修改。

本次预期数量：UK/HK/DE/US WiFi 分别 29/20/21/52 条，HK/UK/DE App 分别 22/6/7 条。验证包括构建、既有回归检查、远端内容与本地加载比对、UDP 500/4500 和 App 请求的实际规则命中。网络探测只验证分流，不能替代对应 SIM 的注册、短信和真实通话验证。
