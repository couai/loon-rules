# 本次归档

- Claude-NetCoffee、Claude-NTP、Oracle-Loon 原样迁入；客户端只替换 URL，保留策略、标签和相对顺序。
- 15 条公开网站、银行/钱包补充迁入独立列表；保持原策略，在订阅区开头按原本地顺序排列。保留会覆盖广告插件的本地例外、个人端点、DNS 引导与场景网段。
- 删除两个冗余本地项：`fh-static.bycsi.com` 已被 `bycsi.com` 覆盖；`metaaivm.com` 已被 AI-Combined 覆盖。
- 按用户选择，以 UK-Banks 替换旧 UK：银行域名白名单 + 原有银行品牌关键词/IP，移除共享服务、`co.uk` 和已有独立订阅的重复服务。旧 URL 留在仓库兼容，不再推荐使用。
- Stripe 原订阅（含 DOMAIN-KEYWORD,stripe）提到 OpenAI 前；保持原手动选择策略，避免 OpenAI 列表继续抢先匹配。
- 发布前检查规则完整性与生成测试；切换前备份完整配置（只保存在本机）；切换后核对公开文件、Loon 加载内容与迁移前后的真实请求记录。
