# Wiki Changelog

Newest entries at the top.

## 2026-11-02

- **Slice H**：entity 模板补上可选类型字段（`kind`：`book` | `person` | `work` | `org` | `concept` | `album` | `tool`；`aliases`；`people` / `works` 为相对路径列表）。旧页不必回填，lint 不把这些字段当必填。契约在 [`WIKI_SCHEMA.md`](WIKI_SCHEMA.md)「实体页」。
- Weekly `/review` 跑 `scripts/check_missing_entities.py`。候选要来自至少 2 个不同的 wiki 页（缺页的 `entity-*.md` 链接，或显式双括号 / `entity:` 提及）。散文里的人名不算。用户当次点名可以建。脚本不建页，也不能把门槛调到 1 以下。不为空学科建空 topic。
- [`index.md`](index.md) 文艺、理工、跨学科不再留「待 ingest」空表，改为指向 [`inbox.md`](inbox.md)。未改《妥协社会》阅读笔记正文。未改 L1 默认。未做 Slice G、J。

- 上手手册的阅读入口改为 [`maps/wiki-teaching-usage-handbook.md`](maps/wiki-teaching-usage-handbook.md)（标题「wiki教学与使用手册」）。[`maps/wiki-user-guide.md`](maps/wiki-user-guide.md) 留短跳转并标 `superseded_by`，不再从 [`index.md`](index.md) 主推。

- **Slice I**：技能正文的单一真相源是 `.agents/skills/`。新增 `scripts/check_skill_sync.py`，按文件 SHA-256 对照 `.cursor/skills/`、`.claude/skills/`、`.codex/skills/`。只改 canonical 再同步镜像；宿主副本不是第二份原文。漂移退出码 1 并打印路径；一致为 0。`/lint` 把它列为可选附加检查，不改变 `lint_wiki.py` 的契约。未做 Slice G、H、J。未改 L1 默认、`log.md` 协议、source-clock 与行为记忆路由。

- **Slice F**：`wiki/projects/learning-progress/` 定为行为记忆层（偏好、纠错、教学进度）。事实仍在 topics / entities。写入路由在 [`WIKI_SCHEMA.md`](WIKI_SCHEMA.md)「行为记忆与写入路由」，并链到 [`projects/learning-progress/README.md`](projects/learning-progress/README.md)。`/teacher` 与 `/review` 启动时先读该层。禁止把偏好写进 topic 正文。不要求 Mem0 / Letta / 云记忆。索引只在「项目」轻链 hub，偏好页不进主题分区。
- 合成示例：事实 [`topics/x-demo-fact-vs-preference.md`](topics/x-demo-fact-vs-preference.md)（北窗焦点块 3.2 与 2.1 项/小时）；偏好 [`projects/learning-progress/preferences/demo-hint-first.md`](projects/learning-progress/preferences/demo-hint-first.md)（先提示、限时、先用中文纠正）。未改《妥协社会》阅读笔记正文。未改 L1 默认、`log.md` 协议与 source-clock。未做 Slice G–J。
- lint：该目录存在但缺少 README 或标题 `## 写入路由` 时 warning，不因此失败。

- **Slice E**：source-clock stale。知识页 `sources` 指向仓库内、`wiki/` 外的已存在文件时，`scripts/lint_wiki.py` 把该文件 mtime 的本地日历日期与页 `updated` 比较。源日期更晚则 warning，建议考虑 `status: stale`，不写回页面。纯 URL 与非路径标签跳过；`wiki/` 内互链不参与比较。未改 L1 默认，也未改 `log.md` 协议。未做 Slice F–J。未改《妥协社会》笔记正文。

- **Slice D**：新增 [`log.md`](log.md) 作为操作日志（ingest / query / lint）。条目前缀 `## [YYYY-MM-DD] ingest|query|lint | title`。`changelog.md` 仍只记结构性变更。默认归档深度仍是 **L1**；L2 compile 须用户说出「L2 / 深挖 / compile / 级联」，且只级联相关 entity、相关 map、index，并写一条 `ingest`。`log.md` 与 changelog 一样不要求知识页 frontmatter。未改阅读笔记正文。未做 Slice E–J。

- **Slice C**：矛盾与取代协议。模板增加 `## Contradictions` 与 `## Superseded`；frontmatter 的 `supersedes` / `superseded_by` 可选，只给高价值页，不回填旧页。`/wiki` 与 `/review` 禁止静默覆盖。lint 在 `superseded_by` 页仍被 `wiki/index.md` 直接链接时报 warning，不裁定谁对。
- 合成示例：[`topics/x-demo-contradiction-coexistence.md`](topics/x-demo-contradiction-coexistence.md)（两条虚构主张并存）。被取代的归档页不从 index 主推。未改《妥协社会》阅读笔记正文。未做 Slice D–J。

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
