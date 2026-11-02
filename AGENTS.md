# wiki — 个人知识库维护说明（单一事实来源）

**Claude Code** 通过根目录 `CLAUDE.md` 的 `@AGENTS.md` 导入本文件。**Cursor** 直接读本文件与 `wiki/WIKI_SCHEMA.md`；技能在 `.cursor/skills/`。**Codex** 以本文件为项目正文（技能在 `.codex/skills/`）。

修改项目级约定时**优先改本文件**；`CLAUDE.md` 仅作 Claude Code 的跳转与 `@` 导入。

## 启动时阅读顺序

1. **本文件 (`AGENTS.md`)** — 项目说明、技能路径、知识库分层；**下文「仓库文档索引」**。
2. **`wiki/WIKI_SCHEMA.md`** — `wiki/` 与 `references/` 的目录归档与轻量维护习惯。
3. **`wiki/index.md`** — 主题导航入口。

若任务落在 `wiki/` 内，默认顺序：`AGENTS.md` → `wiki/WIKI_SCHEMA.md` → `wiki/index.md` → 相关 map / project / topic。

## 仓库文档索引

| 优先级 | 路径 | 用途 | 何时读 |
|--------|------|------|--------|
| P0 | **`AGENTS.md`** | 项目正文、技能、Wiki 分层、**本索引** | 任何维护任务启动时 |
| P0 | **`wiki/WIKI_SCHEMA.md`** | 目录分工、Raw/URL/图片与维护约定 | 动 `wiki/` 或 `references/raw/` 时 |
| P1 | **`wiki/index.md`** | 复利知识库主题索引 | 查找、复习、归档后更新导航时 |
| P1 | **`wiki/maps/learning-spine.md`** | 跨学科学习主轴（阶段 → Wiki 链接） | 规划长期学习、补 topic 时 |
| P2 | **`CLAUDE.md`** | `@AGENTS.md` + 索引镜像 | Claude Code 会话 |
| P2 | **`ROADMAP.md`** | 仓库工程 Backlog（可选） | 评估工具、记 Icebox 时 |
| P2 | **`docs/README.md`** | 调研、施工计划、切片审查 | 做仓库工程升级（Slice）时 |

**维护约定**

1. 改「先读谁、P0/P1」：只改 **`AGENTS.md` 本节**，并同步 **`CLAUDE.md`**。
2. 流程与分层：只定义在 **`wiki/WIKI_SCHEMA.md`**。
3. 结构性变更：在 **`wiki/changelog.md`** 记一笔。每一次小补丁、每一次 L1 归档不必写。
4. 操作流水：ingest / query / lint 写在 **`wiki/log.md`**（前缀 `## [YYYY-MM-DD] ingest|query|lint | title`）。**默认 L1 不写 ingest 条目**。只有用户明示「L2 / 深挖 / compile / 级联」才做 L2 compile（相关 entity、相关 map、index，并写一条 `ingest`）。不要把 changelog 改成操作日志。

## LLM 维护的知识库（无 Obsidian）

| 层 | 路径 | 说明 |
|----|------|------|
| Raw | `references/raw/` | 原始资料收件箱；Agent 默认只读。可只投喂 URL，由 Agent 或 `scripts/ingest_url_to_raw.py` 写入 Raw 后再归档到 Wiki。 |
| Papers | `references/papers/` | PDF 与论文原件（可选） |
| Wiki | `wiki/` | Agent 与人类共同维护的 Markdown 知识网 |
| Schema | `wiki/WIKI_SCHEMA.md` + 本文件 | 约定与导航 |

**知识检索优先级**：默认以 `wiki/` + `references/raw/` 为单一真相源。

## 跨宿主、跨会话的边界

同一远程上可能有多宿主 Agent 的提交：**先拉取再大改**；冲突以合并结果为准。Wiki 的单一真相在仓库里，不在聊天记录中。

- 默认分支：**`master`**
- 远程：`https://github.com/masterroland13/wiki`

## Custom Skills

| 技能 | 用途 | Canonical 路径 |
|------|------|----------------|
| **/wiki** | 投喂 URL、截图、聊天 → Raw + Wiki。**默认 L1**；L2 compile 须明示 | `.agents/skills/wiki/SKILL.md` |
| **/query** | 按已有 wiki 页回答，引用仓库路径；找不到就明说 | `.agents/skills/query/SKILL.md` |
| **/lint** | 坏链、导航、frontmatter 机械体检（先跑 `scripts/lint_wiki.py`） | `.agents/skills/lint/SKILL.md` |
| **/review** | inbox 分拣、到期页复盘、灵感连接 | `.agents/skills/review/SKILL.md` |
| **/teacher** | 教练式学习：推导、复习、系统掌握（通用 + CS） | `.agents/skills/teacher/SKILL.md` |
| **/teacher-cs** | CS 别名：算法、LeetCode、面试（必读 domain-cs.md） | `.agents/skills/teacher-cs/SKILL.md` |

| 环境 | wiki | query | lint | review | teacher | teacher-cs |
|------|------|-------|------|--------|---------|------------|
| **Cursor** | 说「投喂 wiki / /wiki / 归档进 wiki」 | 说「/query / 问 wiki / 根据笔记回答」 | 说「整理 wiki / lint 一下」 | 说「/review / 复盘 inbox」 | `/teacher` / 教练式学习 | `/teacher-cs` / 教我做题 / 算法教练 |
| **Claude Code** | `/wiki` | `/query` | `/lint` | `/review` | `/teacher` | `/teacher-cs` |
| **Codex** | `$wiki` | `$query` | `$lint` | `$review` | `$teacher` | `$teacher-cs` |

宿主副本：`.cursor/skills/`、`.claude/skills/`、`.codex/skills/` 与 `.agents/skills/` 保持同步。

冲突与取代的可选字段（`supersedes` / `superseded_by`）、`## Contradictions` / `## Superseded`，以及**禁止静默覆盖**，写在 `wiki/WIKI_SCHEMA.md`「矛盾与取代」。`/wiki` 与 `/review` 必须照做。字段不是必填。
