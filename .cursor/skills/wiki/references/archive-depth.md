# 归档深度：L0 / L1 / L2

默认由 Agent 根据输入判断档位；用户可说「只要 Raw」「标准 wiki」「深挖」覆盖。

## 档位对照

| 档位 | 典型输入 | Raw | Wiki | 导航 | 外链互证 |
|------|----------|-----|------|------|----------|
| **L0 片段** | 单图/单段、无 URL、补一条事实 | 必做（图+结构化转写） | 短段落并入已有 topic，或 seed topic（TL;DR+来源） | 仅当新主题 | 不主动 |
| **L1 标准** | URL、文章摘要、用户 `/wiki` 默认 | 长/杂/重要来源时必做 | `topic-ingest` 或对应模板 | index 或 map；结构性新增写 changelog | 1–2 源即可 |
| **L2 深读** | 「深挖」、TrendRadar S 档、高价值技术文 | 全文或精读摘录 | 完整 ingest（Assessment、Boundary、Actionable） | index + map + changelog | 多源交叉验证 |

## 合并 vs 新建 topic

1. `grep` / 读 `wiki/index.md` 是否已有同主题页
2. **extend** 已有 topic：新增段落 + 更新 `updated` + 补 `sources`
3. **新建** topic：主题独立、会反复检索、或 L2 深读

## confidence 粗算（`growing` / `stale` 页）

| 来源组合 | 建议 confidence |
|----------|-----------------|
| 仅用户截图/聊天、无一手 URL | ≤ 0.70 |
| 截图/摘要 + ≥2 独立二次文献一致 | 0.65–0.75 |
| 一手 URL / 官方文档 + 本地 Raw | ≥ 0.80 |
| 二手解读、无源码核对 | 0.55–0.65 |

在 `Source Snapshot` 或 frontmatter 注明：`primary_screenshot` / `primary_url` / `secondary_corroboration`；缺 primary URL 时在 Open Questions 留坑，并询问用户是否可补链。
