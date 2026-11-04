# 过夜审计（2026-11-04）

对象：`masterroland13/wiki` @ `c0cec48`。仓库可访问，不是空库（`wiki/` 45 个 Markdown）。任务称呼 Mo（崔君凯）。库内没有这个名字的人物页，本文件不补。

本刀只加这份报告。知识页、技能、脚本都没改，也没删任何原文。

## 结论

`python3 scripts/lint_wiki.py`：`scanned=45`，`errors=0`，`warnings=2`。两条都是 source-clock（手册与旧使用指南的 `sources` 含 `AGENTS.md`，文件日期 2026-11-04 晚于页 `updated` 2026-11-02）。按契约不要为此改 `status`。

`check_missing_entities.py`：候选 0。`check_skill_sync.py`：20 文件，漂移 0。

最大缺口：Loop Agent 十章只从 [`wiki/index.md`](wiki/index.md) 理工区链到 [`projects/loop-agent-source-book/README.md`](wiki/projects/loop-agent-source-book/README.md)。项目区、[`learning-spine`](wiki/maps/learning-spine.md)、教学手册、changelog、检索金标都没有这条链。十章 `sources` 指向的上游目录在 loop-agent 仓库里不存在。

## 索引

[`wiki/index.md`](wiki/index.md) `updated: 2026-11-03`，`review_after: 2026-07-15`（已过期；lint 只查缺字段）。文艺 / 跨学科空区指向 inbox，没有空 topic，这点是对的。人文区《妥协社会》簇完整。实体表只有 [`entities/README.md`](wiki/entities/README.md)，书目实体只出现在人文区。

项目区只有 learning-progress。十章放在 `wiki/projects/loop-agent-source-book/`，类型 `project-note`，hub 是 `README.md`。手册写的 hub 文件名是 `projects/<name>/index.md`（learning-progress 确有 `index.md`）。按手册找十章的 `index.md` 会落空。

[`learning-spine`](wiki/maps/learning-spine.md) 计算机行没有链接，「当前缺口」仍写没有 topic。`topics/` 里确实没有 `cs-` 页；理工区已经有这本项目手册。主轴 `updated` 是 2026-11-02，十章是 2026-11-03。

[`wiki/evals/retrieval-cases.md`](wiki/evals/retrieval-cases.md) q14（动态规划）仍应判缺失。它的 note 写「理工区没有计算机笔记」，和 index 现况不一致。

根 [`README.md`](README.md) 切片表写 Slice H 未做。[`docs/README.md`](docs/README.md)、[`ROADMAP.md`](ROADMAP.md)、[`wiki/changelog.md`](wiki/changelog.md) 写 Slice H 已实现。changelog 停在 2026-11-02，没有十章入库这一笔。`wiki/log.md` 无对应 ingest；默认 L1 可以不写。

## 断链

`wiki/` 内相对链接：lint 0 条。模板里的 `example-*.md` 按契约豁免，不要当成断链去建页。

真断、且 lint 不扫：

| 位置 | 问题 |
|------|------|
| [`references/raw/README.md`](references/raw/README.md) | `../wiki/WIKI_SCHEMA.md` 落到 `references/wiki/`。应是 `../../wiki/WIKI_SCHEMA.md` |
| [`references/image-ingest.md`](references/image-ingest.md) | `../../../../wiki/...` 逃出仓库。同文在 `.agents/skills/wiki/references/` 四层上到根，链接是通的。`references/` 下四份与技能正文逐字节相同，这份副本深度错了 |
| `screenshot-only.md`（`references/` 与三份技能镜像） | 范例链向不存在的 `references/raw/claude-code-bashtool-20-security-checks-2026-05-31.md` 与 `wiki/topics/cs-claude-code-bashtool-20-security-checks.md`。初始化说明不含 letsgo 正文。不要为修链建这两页 |

外部（2026-11-04，`curl -I -L` + `gh api` 列 `docs/design/`）：

- 200：Pi Agent Book `ch01-overview`、loop-agent 仓库根、`docs/architecture-charter.md`、`docs/design/loop-agent-manual.md`
- 404：`docs/design/loop-agent-book/ch01-overview.md`、`ch10-session.md`
- `docs/design/` 只有 `loop-agent-manual.md` 与 `v1-7-headless-cli-design.md`，没有 `loop-agent-book/`。十章 frontmatter 的 `sources` 都是这个前缀，lint 不查 URL

上游另有、本库未链、本审计未读正文：`docs/research/pi-agent-ch06-messages.md`、`docs/research/pi-agent-ch08-context-engineering.md`。只记路径在，不当成十章的替稿。

`references/raw/` 只有 README 与 `assets/`。`references/papers/` 空。`wiki/papers/`、`wiki/roadmaps/` 目录不存在；schema 写了角色，目前没有指向具体文件的死链。有稿再创建。

## Loop Agent 交叉链

目录外链入 hub 的只有 index 理工区那一行。

书内：README 有十章表。「第 9 章依赖第 6 章和第 8 章」是散文，没有链接。章的 Related 基本是上一篇 / 下一篇。ch01、ch10 能回目录；ch02–ch09 不能。散文点到别章但 Related 没链的：ch01→第 6、10 章；ch03→第 9 章；ch04→第 3、5、8、9、10 章；ch05→第 8 章；ch06、ch07→第 9 章；ch09 缺第 6 章；ch10→第 6 章。章不回 index，不回 learning-spine。宪章和 manual 只在 README 里，那两条是通的。

不要建 `entity-loop-agent`。扫描器计的是缺席的 `entity-*.md` 或显式 `entity:`，散文里的产品名不算。十章已经是项目笔记。

## 建议信息架构（下一刀，本 PR 不做）

一条 hub：继续用 `wiki/projects/loop-agent-source-book/README.md`。不要把十章拆进 index，也不要复制一份 map。

1. index 项目区加一行，链这个 README。理工区留短指针，写明这是项目手册，不是 `cs-` topic。两行同一目标。
2. learning-spine 计算机行链到同一 README。缺口改成：尚无 `cs-` topic；已有这本手册。
3. 手册补一句：项目 hub 可以是 `README.md` 或 `index.md`。不要为对齐文件名再写一份章节表。
4. 修上面三处真断链。范例路径改成反引号，写明本库没有那两页。
5. 十章 `sources` 的 404 URL 改成本页，或改成仍存在的 manual / charter，并注明 2026-11-04 上游无 `loop-agent-book/`。不要到另一个仓库补文件。
6. 金标加一题「十章目录在哪」→ README；改 q14 的 note。changelog 补 2026-11-03 一条。根 README 的 Slice H 改成与 docs / ROADMAP 一致。
7. 章间只补链接：README 的依赖句、ch09→ch06、ch10→ch06、中间章回目录。不改主张。
8. 下次碰 index 时把 `review_after` 拨到未来。source-clock 两条留着。实体表可加已有的《妥协社会》实体一行，不新写页。

不做：空 topic、空学科页、未点名的 entity、把手册改成 `stale`、改《妥协社会》正文。
