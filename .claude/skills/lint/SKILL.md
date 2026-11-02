---
name: lint
description: Light maintenance for this wiki—navigation, links, frontmatter, and changelog. Always run python3 scripts/lint_wiki.py before any semantic check. Use when the user says 整理 wiki, 维护知识库, 补导航, lint 一下, or wants a mechanical health pass (not semantic review—that is /review).
---

# lint

对 **本仓库** `wiki/` 做轻量维护整理。机械规则的真源是 `scripts/lint_wiki.py`（见 `wiki/WIKI_SCHEMA.md`「机器规则子集」）。本技能不代替脚本，也不做语义矛盾判断。

先读：`AGENTS.md` → `wiki/WIKI_SCHEMA.md` → `wiki/index.md`。

适用：用户说「整理 wiki / 维护知识库 / 补导航 / 收口一下 / lint 一下」。

## 顺序（第 1 步不可跳过）

1. **先跑机器 lint**，在任何导航或语义判断之前：

   ```bash
   python3 scripts/lint_wiki.py
   ```

   若当前环境里 Python 3 的命令是 `python`，用 `python` 代替 `python3`。

   退出码：有 error 为 **1**；仅 warning 为 **0**；`--strict` 把 warning 也当成失败（退出码 1）；用法或环境错误为 **2**。报告里的路径就是问题页。脚本退出码为 1 时，不要把体检说成通过。

2. 按报告处理：
   - error（缺字段、非法枚举、坏相对链接、坏 `sources` 路径、非法日期）先修
   - warning（orphan 候选、`growing` / `stale` 缺 `review_after`）能小修就修
   - 不要为了清掉 warning 去改写既有阅读笔记正文；历史页可以暂时留着 warning

3. 脚本不管、仍要人看的项：
   - `wiki/index.md` 和相关 map 能否找到新增内容
   - 页面是否落在合适目录
   - 结构性变更需要时补 `wiki/changelog.md`
   - 是否贴近 `wiki/templates/` 的结构目标（至少结论 + 来源 + Related）
   - `growing` / `stale` 的 `confidence`（0.0–1.0）

4. 图片断链已包含在脚本的相对链接检查里。要单独验收某个文件时，仍可跑 `scripts/wiki_verify_images.sh`。

`lint` 是机械体检。语义整理、inbox 复盘、矛盾是否成立，用 **`/review`**。

本技能不改 ingest 默认深度，不引入检索栈，也不把 Obsidian 当成写入真相源。

技能正文只改 `.agents/skills/lint/SKILL.md`，再同步到 `.cursor/skills/lint/`、`.claude/skills/lint/`、`.codex/skills/lint/`。
