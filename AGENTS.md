# wiki — 个人知识库维护说明（单一事实来源）

**Claude Code** 通过根目录 `CLAUDE.md` 的 `@AGENTS.md` 导入本文件。**Cursor** 直接读本文件与 `wiki/WIKI_SCHEMA.md`；技能在 `.cursor/skills/`。**Codex** 以本文件为项目正文（技能在 `.codex/skills/`）。

修改项目级约定时**优先改本文件**；`CLAUDE.md` 仅作 Claude Code 的跳转与 `@` 导入。

## 启动时阅读顺序

1. **本文件 (`AGENTS.md`)** — 项目说明、技能路径、知识库分层；**下文「仓库文档索引」**。
2. **`wiki/WIKI_SCHEMA.md`** — `wiki/` 与 `references/` 的目录归档与轻量维护习惯。
3. **`wiki/index.md`** — 主题导航入口。

若任务落在 `wiki/` 内，默认顺序：`AGENTS.md` → `wiki/WIKI_SCHEMA.md` → `wiki/index.md` → 相关 map / project / topic。

**`/teacher`、`/teacher-cs`、`/review` 在讲课或复盘之前再读行为记忆层** [`wiki/projects/learning-progress/`](wiki/projects/learning-progress/README.md)：先 README 的写入路由，再 hub 与 learner profile，场景页按需。事实仍去 `wiki/topics/` 与 `wiki/entities/`。本层不是主题索引，也不是知识单一真相源。不要求 Mem0、Letta 或云端记忆。写入路由的契约在 [`wiki/WIKI_SCHEMA.md`](wiki/WIKI_SCHEMA.md)「行为记忆与写入路由」。

## 仓库文档索引

| 优先级 | 路径 | 用途 | 何时读 |
|--------|------|------|--------|
| P0 | **`AGENTS.md`** | 项目正文、技能、Wiki 分层、**本索引** | 任何维护任务启动时 |
| P0 | **`wiki/WIKI_SCHEMA.md`** | 目录分工、Raw/URL/图片与维护约定 | 动 `wiki/` 或 `references/raw/` 时 |
| P1 | **`wiki/index.md`** | 复利知识库主题索引 | 查找、复习、归档后更新导航时 |
| P1 | **`wiki/maps/wiki-teaching-usage-handbook.md`** | 教学与使用手册（人类上手） | 第一次使用、对齐工作流时 |
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
| Wiki | `wiki/` | Agent 与人类共同维护的 Markdown 知识网。事实在 topics / entities / papers / maps |
| Memory | `wiki/projects/learning-progress/` | 行为记忆：偏好、纠错、教学进度。不是主题事实的单一真相源，也不是主题索引。写入路由见 [`wiki/WIKI_SCHEMA.md`](wiki/WIKI_SCHEMA.md)「行为记忆与写入路由」与该目录 [`README.md`](wiki/projects/learning-progress/README.md)。不要求 Mem0 / 云记忆 |
| Schema | `wiki/WIKI_SCHEMA.md` + 本文件 | 约定与导航 |

**知识检索优先级**：默认以 `wiki/` 的主题页（topics / entities / maps）+ `references/raw/` 为单一真相源。行为记忆只回答「怎么教、纠正过什么、进度到哪」，不代替事实页。

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
| **/review** | inbox 分拣、到期页复盘、灵感连接。启动先读行为记忆层；偏好不写入 topic 正文。Weekly 跑缺失 entity 扫描（≥2 个不同页，或用户点名） | `.agents/skills/review/SKILL.md` |
| **/teacher** | 教练式学习：推导、复习、系统掌握（通用 + CS）。启动先读行为记忆层；偏好不写入 topic 正文 | `.agents/skills/teacher/SKILL.md` |
| **/teacher-cs** | CS 别名：算法、LeetCode、面试（必读 domain-cs.md） | `.agents/skills/teacher-cs/SKILL.md` |

| 环境 | wiki | query | lint | review | teacher | teacher-cs |
|------|------|-------|------|--------|---------|------------|
| **Cursor** | 说「投喂 wiki / /wiki / 归档进 wiki」 | 说「/query / 问 wiki / 根据笔记回答」 | 说「整理 wiki / lint 一下」 | 说「/review / 复盘 inbox」 | `/teacher` / 教练式学习 | `/teacher-cs` / 教我做题 / 算法教练 |
| **Claude Code** | `/wiki` | `/query` | `/lint` | `/review` | `/teacher` | `/teacher-cs` |
| **Codex** | `$wiki` | `$query` | `$lint` | `$review` | `$teacher` | `$teacher-cs` |

宿主副本：`.cursor/skills/`、`.claude/skills/`、`.codex/skills/` 是 `.agents/skills/` 的镜像，不是第二份真相源。**只改 `.agents/skills/`，再把同一内容同步到这三个目录。** 不要在某一宿主副本里单独发明分歧。校验：`python3 scripts/check_skill_sync.py`（一致退出码 0；漂移退出码 1，并打印路径）。详见 `wiki/WIKI_SCHEMA.md`「技能正文的单一真相源」。

冲突与取代的可选字段（`supersedes` / `superseded_by`）、`## Contradictions` / `## Superseded`，以及**禁止静默覆盖**，写在 `wiki/WIKI_SCHEMA.md`「矛盾与取代」。`/wiki` 与 `/review` 必须照做。字段不是必填。

实体页的可选字段（`kind`、`aliases`、`people`、`works`）和建页门槛写在 `wiki/WIKI_SCHEMA.md`「实体页」。`/review` 的 weekly 必须跑 `python3 scripts/check_missing_entities.py`。未达 ≥2 个不同 wiki 页、用户也没有点名时，不要新建 entity，也不要为空学科建空 topic。字段不是必填，lint 不因此失败。
