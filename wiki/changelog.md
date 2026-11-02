# Wiki Changelog

Newest entries at the top.

## 2026-11-02

- **Slice B**：新增 `/query`（`.agents/skills/query/SKILL.md`，并同步 Cursor / Claude / Codex）。流程是 index → map/topic，答案引用仓库路径；找不到必须说 **I can't find**，不编造路径。高价值答案只提议回写。
- 新增 [`evals/retrieval-cases.md`](evals/retrieval-cases.md)（15 题，含释义问法与故意缺失）和 `scripts/check_retrieval_cases.py`。不引入向量库，不把 `references/raw/` 当默认检索源。
- `wiki/evals/` 不参与 frontmatter / orphan 检查，仍检查相对链接。未做 Slice C–J，未改阅读笔记正文。

- 落盘前沿调研、升级计划与切片审查手册，索引见 [`docs/README.md`](../docs/README.md)。
- **Slice A**：新增 `scripts/lint_wiki.py`（frontmatter、相对链接、orphan 候选、`growing`/`stale` 缺 `review_after`）与 `scripts/test_lint_wiki.py`。机器规则写在 `WIKI_SCHEMA.md`。`/lint` 改为先跑脚本。
- 补齐 `wiki/projects/learning-progress/` 两页所缺必填 frontmatter。未改阅读笔记正文。`growing` 且缺 `review_after` 的既有页保持 warning。

## 2026-07-08

- 从 [caapapx/teacher](https://github.com/caapapx/teacher) 安装 **`/teacher`** skill（含 `references/`、`evals/`）；`letsgo` 语境改为 **wiki 仓库**。
- 新增 **`/teacher-cs`** 兼容别名（路由至 `teacher` + `domain-cs.md`）；同步 `.cursor/`、`.claude/`、`.codex/` 副本。
- 新增 `wiki/projects/learning-progress/` 骨架；更新 `AGENTS.md`、`review` skill 分工表。

## 2026-07-07

- 新增《妥协社会》**纯划线 37 条**（原文 + 上下文/解读）；更新阅读索引与实体页。
- 完成《妥协社会》阅读笔记 **11–27**；新增 [阅读笔记索引](maps/phil-han-palliative-society-reading-index.md)（全书 27 条）。
- 新增《妥协社会》阅读笔记 **5–10**（幸福强制、生存）；更新书目实体链入。
- 新增韩炳哲《妥协社会》实体页与 **痛苦恐惧症** 章节阅读笔记（原文 / 想法 / 点评 / 理解）；`index.md` 人文分区链入。

## 2026-06-30

- 新增 [`wiki/maps/wiki-user-guide.md`](maps/wiki-user-guide.md)（Wiki 使用手册）；`index.md` Start Here 链入。
- **初始化**：从 [letsgo](https://github.com/caapap/letsgo) **方案 A 骨架** 创建本仓库（`WIKI_SCHEMA`、`templates`、`wiki/lint/review` skills、空 `index`/`inbox`）；**不含** letsgo 知识正文。
- 远程：`https://github.com/masterroland13/wiki`；本地 `~/wiki`（WSL）。
