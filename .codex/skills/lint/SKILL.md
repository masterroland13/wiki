---
name: lint
description: Light maintenance for this wiki—navigation, links, frontmatter, and changelog. Use when the user says 整理 wiki, 维护知识库, 补导航, lint 一下, or wants a mechanical health pass (not semantic review—that is /review).
---

# lint

对 **本仓库** `wiki/` 做轻量维护整理。

先读：`AGENTS.md` → `wiki/WIKI_SCHEMA.md` → `wiki/index.md`。

适用：用户说「整理 wiki / 维护知识库 / 补导航 / 收口一下 / lint 一下」。

顺序：

1. 检查 `wiki/index.md` 和相关 map 是否能找到新增内容
2. 检查页面是否落在合适目录
3. 检查相对链接、图片路径、frontmatter 是否明显有错
4. 需要时补 `wiki/changelog.md`
5. 检查是否匹配 `wiki/templates/` 的结构目标（至少结论 + 来源 + Related）
6. 检查 frontmatter：`growing`/`stale` 补 `confidence`/`review_after`；`seed`/`stable` 避免空可选字段

可选：`scripts/wiki_verify_images.sh`。

`lint` 是机械体检；语义整理与 inbox 复盘用 **`/review`**。
