# Loon Rules

[![Update Loon rules](https://github.com/couai/loon-rules/actions/workflows/update.yml/badge.svg)](https://github.com/couai/loon-rules/actions/workflows/update.yml)

将公开上游、现有规则快照和少量手工补充合并为 Loon 规则订阅。Python 3.11+，仅使用标准库。

## 订阅

[AI-Combined.list](https://raw.githubusercontent.com/couai/loon-rules/main/rules/AI-Combined.list)

放在 Loon 的 `[Remote Rule]` 中，策略名按实际配置填写：

```ini
https://raw.githubusercontent.com/couai/loon-rules/main/rules/AI-Combined.list, policy=人工智能策略, tag=AI-Combined, enabled=true
```

替换原 AI.lsr 时保留原来的策略绑定和顺序，放在 China、GEOIP 和 FINAL 等通用规则前面。原有 OpenAI、Claude、Gemini、Claude-Coffee、Claude-NTP 等专用规则可以继续保留。仓库只提供规则，不包含节点或完整个人配置。

## 来源与覆盖

### WiFi Calling、运营商与银行规则

已迁入的 WiFi Calling、运营商和银行规则：[WiFi Calling](rules/wificall/)（UK/HK/DE/US）、[香港运营商 App](rules/carrier/)、[银行与支付](rules/bank/)。每份保持独立，方便继续绑定原来的地区策略。另外提供 [Claude 专项](rules/ai/) 和 [Oracle 规则](rules/services/Oracle-Loon.list)。英国银行推荐使用精简的 [UK-Banks.list](rules/bank/UK-Banks.list)，旧 UK.list 仅保留兼容。目录、公开上游筛选与重叠项见 [规则整理说明](docs/rule-organization.md)。

单条网站和钱包补充在客户端 `[Rule]` 中维护，不生成独立订阅。

维护已迁移的规则请编辑 `overrides/` 对应分类；公开来源由 `sources.json` 管理，使用现有的六小时更新任务。不要直接编辑 `rules/` 下的生成文件。

### AI

| 来源 | 用途 | 更新方式 |
|---|---|---|
| [MetaCubeX category-ai-!cn](https://github.com/MetaCubeX/meta-rules-dat/blob/meta/geo/geosite/category-ai-!cn.list) | AI 网站及配套域名 | 每次构建拉取 |
| [models.dev](https://github.com/anomalyco/models.dev/tree/dev/providers) | 提取 provider.toml 中明确声明的 API 主机名 | 每次构建拉取 |
| [KeLee 本地快照](snapshots/KeLee-AI-20261028.list) | 保留原可莉 AI 规则的覆盖 | 固定于 2026-10-28，手工更新 |
| [手工补充](overrides/AI.list) | Muse、Lovable、v0、Augment | 手工维护 |

初次合并生成 **439 条**规则。原本地可莉缓存有 245 条，精确去重后 243 条；这 243 条全部保留，包括 3 条 AND 条件与 IPv4/IPv6 规则。两个公开上游单独使用时仍有 34 条原规则未被覆盖，所以快照是必要补充。当前数量与各源贡献见 [manifest](reports/manifest.json)。

models.dev 是模型目录，不是分流规则库。本项目仅提取明确的 API 主机名为 `DOMAIN`，不抓文档域名、不把 URL 路径扩大成域名后缀。跳过 SDK 默认端点、用户自定义主机、localhost/IP 地址，并通过 `sources.json` 排除部分国内 API 和共享管理端点；跳过原因记录在 manifest。该筛选不是完整的地域识别系统，也不会删除旧快照已有的规则。

合并只做格式转换和精确去重，不把 AND 拆开，不将 `.ai`、`azurefd.net`、`run.app` 等泛化为全局匹配。相互覆盖但不完全相同的规则会保留。

## 自动更新

GitHub Actions 默认在北京时间 **02:17、08:17、14:17、20:17** 运行；也支持 Actions 页面手动运行和源配置变更触发。流程：测试 → 拉取全部来源 → 解析与校验 → 合并 → 有变更才提交。

任何上游失败、内容为空、数量低于配置门槛或出现不支持的规则语法，整次更新失败，已发布规则保持不变。没有用旧下载缓存冒充成功更新；可莉快照本身是明确列出的静态来源。

工作流使用仓库自带的 `GITHUB_TOKEN`，不需要个人令牌。PR 只运行测试，不拥有发布权限。失败可在 Actions 查看；通知由 GitHub 账号的 Actions 通知设置控制。

[GitHub 定时任务](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#schedule)可能延迟；公开仓库连续 60 天没有活动时，定时任务可能被自动停用，可在 Actions 页面重新启用。

## 本地运行与扩展

```sh
python3 -m unittest discover -s tests -v
python3 scripts/build.py
```

同一类增加上游：在 `sources.json` 的 `collections.AI-Combined.sources` 中添加来源。新增其他类别：增加一个 collection，设置不同的 `output`，仍复用同一脚本和工作流。例如：

```json
{
  "Example": {
    "output": "rules/Example.list",
    "sources": [
      {"name": "Local example", "path": "overrides/Example.list", "format": "loon", "min_rules": 1}
    ]
  }
}
```

把 `Example` 对象放进现有 `collections`，并创建对应的本地规则文件即可。远程来源把 `path` 换成 `url`。

支持 `loon`、`domain-list` 和 `models-tar`。`loon` 支持 DOMAIN、DOMAIN-SUFFIX、DOMAIN-KEYWORD、IP-CIDR、IP-CIDR6、IP-ASN、GEOIP、PROTOCOL、SRC-PORT、DEST-PORT 和 AND/OR 组合；规则不含策略。`domain-list` 将 `+.example.com` 转为后缀规则，裸域名转为精确匹配。其他格式或规则类型需要先扩展解析器与测试。

`exclude_rules` 按规范化后的完整规则精确排除；`required_rules` 可指定必须存在的规则。自定义补充放在 `overrides/`，不要直接编辑生成文件。

单个上游还可设置 `exclude_lines`（解析前排除已确认错误项）、`include_rule_types`、`include_domains`（仅接受这些域名及子域名）。筛选仅作用于该来源，不会删除本地补充；跳过内容和原因会记录在 manifest。

## 署名与许可

本项目原创脚本、测试和工作流采用 [MIT](LICENSE)。第三方规则与数据保留各自来源、署名与条款，详见 [NOTICE](NOTICE.md) 和 `licenses/`。
