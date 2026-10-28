# 数据来源与署名

本项目转换并合并数据，不声称拥有上游数据。代码的 MIT 许可不用于重新授权第三方规则。

- **MetaCubeX / meta-rules-dat**：`meta` 分支的 `geo/geosite/category-ai-!cn.list`。原项目采用 GPL-3.0，完整许可保留在 [licenses/MetaCubeX-GPL-3.0.txt](licenses/MetaCubeX-GPL-3.0.txt)。[项目与来源说明](https://github.com/MetaCubeX/meta-rules-dat)。转换：`+.` 后缀表达式转为 Loon DOMAIN-SUFFIX，裸域名转为 DOMAIN。
- **models.dev / Anomaly**：`dev` 分支中 `providers/*/provider.toml` 的明确 API 主机名。原项目采用 MIT，完整许可保留在 [licenses/models.dev-MIT.txt](licenses/models.dev-MIT.txt)。[原项目](https://github.com/anomalyco/models.dev)。转换：仅保留主机名为 DOMAIN，按配置筛选。
- **可莉 / KeLee / luestr**：`snapshots/KeLee-AI-20261028.list` 来自仓库所有者本地 Loon 已加载的 AI.lsr 缓存，按所有者要求于 2026-10-28 导出。原订阅地址为 `https://kelee.one/Tool/Loon/Lsr/AI.lsr`，原项目说明见 [ProxyResource](https://github.com/luestr/ProxyResource)。该快照保留规则内容与逻辑条件，没有冒充可莉官方实时更新。上游仓库现说明仅配置模板开源，本项目不将其模板许可证推定为 AI.lsr 的授权，也不为该快照声明新的许可。

生成文件仅做格式规范化、精确去重及与手工补充合并。第三方材料应遵循其原作者条款。
