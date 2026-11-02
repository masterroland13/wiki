---
name: query
description: Answer from this wiki by reading wiki/index.md, then maps and topics, and citing repo paths. Use when the user says /query, 问 wiki, 根据笔记回答, 库里有没有, or wants an answer grounded in existing pages. If the pages are not there, say "I can't find" and do not invent paths. Not for ingest (/wiki), mechanical lint (/lint), inbox review (/review), or coaching (/teacher).
---

# query

用**已经写在 wiki 里的页**回答问题。检索顺序是索引 → 地图或项目 → 叶子页。不新开一套检索服务。

## 何时用

用户说「/query」「问 wiki」「根据笔记回答」「库里有没有」「查一下我的笔记」。

不要用本技能代替：

- 投喂新材料 → `/wiki`
- 坏链和 frontmatter → `/lint`（先跑 `python3 scripts/lint_wiki.py`）
- inbox、到期页、语义整理 → `/review`
- 推导、练题、系统学习 → `/teacher` 或 `/teacher-cs`

## 流程（按顺序，不跳步）

1. 读 `wiki/index.md`。
2. 从索引里选出相关的 `wiki/maps/` 或 `wiki/projects/`，读完再打开 `wiki/topics/`、`wiki/entities/` 等叶子页。
3. 只根据**实际打开过**的页面作答。
4. 答案里列出读过的**仓库路径**（相对仓库根，例如 `wiki/topics/foo.md`）。没打开的文件不要写进引用。

金标与路径检查见 `wiki/evals/retrieval-cases.md`。抽检目标：至少 70% 的题打开期望页，或者明确说找不到。编造路径算失败。`python3 scripts/check_retrieval_cases.py` 只检查金标格式和期望路径是否存在，它不回答问题。

## 失败协议

仓库里没有能支撑回答的页面时，停下来，写明：

**I can't find this in the wiki.**（找不到。）

然后：

- 不编造来源路径，不把没读过的文件说成已读
- 列出已经读过的路径，并说明缺的是哪一类页（例如「理工分区仍是待 ingest」）
- 不调用 embedding、向量库、QMD、GraphRAG，或任何外部检索服务
- 不把 `references/raw/` 或 `references/papers/` 当成默认真相源去补答。只有某张 wiki 页已经指向一份 raw，且问题明确要核对那份原文时，才打开那一份
- 可以指出 `wiki/inbox.md`，或建议下一轮用 `/wiki` 归档。不要在这次回答里大改 wiki

## 答案形状

```
## 答案
（结论，以及它来自哪一页的哪一节）

## 读过
- `wiki/index.md`
- `wiki/maps/...` 或 `wiki/projects/...`
- `wiki/topics/...` 或 `wiki/entities/...`

## 回写（可选，先提议）
- 建议写入的路径和一句结论
- 未执行
```

找不到时把「答案」换成失败协议那一句，并保留「读过」。多页才够回答时，列出用到的每一条路径。页面彼此冲突时并列引用，不要静默选边。落盘时走 `wiki/WIKI_SCHEMA.md`「矛盾与取代」：写 `## Contradictions` 或 `supersedes` / `superseded_by`，不要改写对方页来消掉冲突。

## 回写

高价值答案（会反复被问，或补上了索引里没有的稳定结论）可以**提议**写回 wiki：目标路径、要补的一句结论、要动的 index 或 map。

- 先提议，用户同意后再写
- 不自动全库改写
- 与已有页冲突时禁止静默覆盖；按 schema 写矛盾块或 supersession 字段
- 不借这次回答改写既有阅读笔记正文（例如《妥协社会》各篇）

## 不做

- 不引入 embedding / 向量库 / QMD / GraphRAG
- 不默认对 `references/raw/` 做 RAG
- 不把金标脚本当成答题器

技能正文只改 `.agents/skills/query/SKILL.md`，再同步到 `.cursor/skills/query/`、`.claude/skills/query/`、`.codex/skills/query/`。
