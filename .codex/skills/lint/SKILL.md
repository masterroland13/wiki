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
   - warning（orphan 候选、`growing` / `stale` 缺 `review_after`、`superseded_by` 仍被 `wiki/index.md` 直接链接）能小修就修
   - 最后一种：从 `wiki/index.md` 拿掉该链接，保留页面，让后继页链入。不要删页，不要清空字段来消掉 warning，也不要改写主张。哪一边为真不在本技能。规则见 `wiki/WIKI_SCHEMA.md`「矛盾与取代」和「机器规则子集」
   - source-clock warning 不要自动修。`wiki/` 外的 source 文件，其 mtime 的本地日历日期晚于页 `updated` 时，消息是 `source '<path>' is newer than updated (YYYY-MM-DD > YYYY-MM-DD); consider status: stale`。它只建议人考虑 `status: stale`。不要为了消掉它去改 `status`、`updated` 或正文。URL、非路径标签和 `wiki/` 内互链不会触发。规则见 `wiki/WIKI_SCHEMA.md`「Source-clock」
   - `learning-progress` 缺 `README.md` 或标题 `## 写入路由` 只是 warning（`learning-progress README.md is missing (write-routing table)` 或 `learning-progress README.md is missing the write-routing table`）。目录不存在则不查。不要为此把路由表写进 topic，也不要把全库判失败。规则见 `wiki/WIKI_SCHEMA.md`「行为记忆路由表（存在性）」
   - 不要为了清掉 warning 去改写既有阅读笔记正文；历史页可以暂时留着 warning

3. 脚本不管、仍要人看的项：
   - `wiki/index.md` 和相关 map 能否找到新增内容
   - 页面是否落在合适目录
   - 结构性变更需要时补 `wiki/changelog.md`
   - 是否贴近 `wiki/templates/` 的结构目标（至少结论 + 来源 + Related）
   - `growing` / `stale` 的 `confidence`（0.0–1.0）

4. 图片断链已包含在脚本的相对链接检查里。要单独验收某个文件时，仍可跑 `scripts/wiki_verify_images.sh`。

5. 收尾时在 `wiki/log.md` **顶部**追加一条，不要为此再跑一轮 lint，也不要写进 `wiki/changelog.md`：

   ```text
   ## [YYYY-MM-DD] lint | 本次范围的一行说明

   - errors: N
   - warnings: N
   ```

   `wiki/log.md` 与 `wiki/changelog.md` 一样不是知识页：没有 frontmatter 也不算 error。结构性变更仍只在需要时写 changelog。

`lint` 是机械体检。语义整理、inbox 复盘、矛盾是否成立，用 **`/review`**。

本技能不改 ingest 默认深度，不引入检索栈，也不把 Obsidian 当成写入真相源。

## 可选附加检查（不改变上面的契约）

机器 lint 的退出码只来自 `scripts/lint_wiki.py`。改过技能正文后，可以再跑：

```bash
python3 scripts/check_skill_sync.py
```

它对照 `.agents/skills/` 与 `.cursor/skills/`、`.claude/skills/`、`.codex/skills/` 的文件哈希。一致退出码 0；漂移退出码 1，并打印不一致路径。这不是 `lint_wiki.py` 的 warning，也不要把它算进 `wiki/log.md` 的 lint 计数。规则见 `wiki/WIKI_SCHEMA.md`「技能正文的单一真相源」。

技能正文只改 `.agents/skills/`（本文件是 `.agents/skills/lint/SKILL.md`），再同步到 `.cursor/skills/`、`.claude/skills/`、`.codex/skills/`。不要在某一宿主副本里单独改。
