---
name: review
description: Review, consolidate, and reconnect this wiki's knowledge—and spark new ideas from what you already captured. Use when the user says /review, 回顾 wiki, 复习整理, weekly review, 复盘, 整理 inbox, review_after 到期, or wants inspiration from existing notes. Complements /wiki (capture/archive), /query (answer from existing pages), /teacher (learn new material), /lint (mechanical link/nav fix)—not a substitute for any of them.
---

# review

对 wiki 知识库做 **Review（再整理、再连接、再激活）**：把 Capture 落下的碎片变成可复利资产，并从已有笔记里 **激发新连接与新问题**。

## 先读

1. `AGENTS.md`
2. `wiki/WIKI_SCHEMA.md`（两段式工作流、frontmatter、`review_after`，以及「行为记忆与写入路由」）
3. `wiki/index.md`
4. **行为记忆层（复盘之前必读）**：`wiki/projects/learning-progress/README.md`（写入路由），然后 `wiki/projects/learning-progress/index.md`，再按需 `learner-profile.md`。这是偏好、纠错、教学进度，不是主题事实，也不是主题索引
5. 按需：`wiki/inbox.md`、用户指定的 map / project

发现的偏好、纠错、「下次怎么教」写回 `wiki/projects/learning-progress/`。**禁止**写进 topic、entity、paper 的正文。可复用事实仍进 `topics/` / `entities/`。不要求 Mem0、Letta 或云端记忆。合成对照：事实 `wiki/topics/x-demo-fact-vs-preference.md`，偏好 `wiki/projects/learning-progress/preferences/demo-hint-first.md`。

## 与其它技能的分工

| 技能 | 何时用 |
|------|--------|
| **/wiki** | 新 URL、新对话、新截图 → Raw + topic + 导航 |
| **/query** | 用已有页回答；引用仓库路径。找不到就说 I can't find，不在这里整理 inbox |
| **/review** | 已有 inbox / growing / stale / 到期页 → 提炼、互链、复盘、灵感 |
| **/teacher** | 还不会、要推导、要练题 → 教练式学习 |
| **/lint** | 坏链、孤岛页、frontmatter 格式、changelog 机械补全 |

**review 做语义与结构判断；lint 做体检。** 发现纯链接错误时可建议用户 `/lint`，但 review 会话里可顺手修明显坏链。

## 路由（按用户意图）

```
输入
 ├─ 「inbox / 待办清单」→ references/triage-checklist.md § Inbox
 ├─ 「某主题 / 某 map / 某 project」→ references/modes.md § Topic sweep
 ├─ 「到期 / stale / growing」→ references/triage-checklist.md § Due pages
 ├─ 「复习 / 考我 / 回忆」→ references/modes.md § Recall
 ├─ 「灵感 / 还能写什么 / 缺什么」→ references/inspiration.md
 └─ 未指定 → references/modes.md § Weekly（默认）
```

## 核心问题（每页必过）

Review 时对每个候选页问：

1. **主张是什么？** — 一句话可引用结论；说不清 → 降级为 seed 或退回 inbox
2. **证据在哪？** — `sources` / Raw 路径 / 可复现链接
3. **边界在哪？** — 何时不成立、与哪条旧结论冲突。冲突时**禁止静默覆盖**：写 `## Contradictions`，或用 `supersedes` / `superseded_by` 更换阅读入口。不裁定谁对。见 `wiki/WIKI_SCHEMA.md`「矛盾与取代」

摘抄堆、无主张 → **不归档**，留在 inbox 或标 `status: seed` + 补 Open Questions。

## 通用流程

### 1. 定范围与时间盒

- 默认 **weekly：15–30 分钟**
- 用户说「快速」→ 只扫 inbox + 最多 3 条 due 页
- 用户说「深度」→ 一个 map 全扫 + inspiration pass

### 2. 收集候选

按 `references/triage-checklist.md` 拉清单：

- `wiki/inbox.md` 未处理项
- `review_after` ≤ 今天（或用户指定窗口）
- `status: growing` / `stale`
- 用户点名的 map / project / tag

### 3. 逐项处理

对每条候选，输出简短判定（可表格）：

| 项 | 主张 | 动作 |
|----|------|------|
| … | … | promote / merge / link / defer / drop |

**动作词典：**

- **promote** — inbox → `topics/` / `entities/` / `maps/` 草稿
- **merge** — 并入已有 topic 的重复表述。主张冲突时禁止用 merge 删掉或改写一方；改走矛盾块或 supersession 字段。旧页留重定向，或在确认无冲突后再删冗余
- **link** — 补 Related、map、index 入口；不新建页
- **defer** — 仍有价值但未成熟 → 更新 `review_after`、`confidence`
- **drop** — 无复用价值，从 inbox 移除（说明理由）

候选若是学习者偏好、纠错或教学进度：写入 `wiki/projects/learning-progress/`，不要 promote 进 topic 正文。候选若是可复用事实：仍 promote 到 `topics/` / `entities/` / `maps/`，不要写进行为记忆层冒充事实。

### 4. 更新 frontmatter

- `growing` / `stale` → 补或调 `confidence`、`review_after`
- 结论收敛 → 考虑 `stable`
- 始终更新 `updated`
- 冲突或更换阅读入口时，高价值页才补 `supersedes` / `superseded_by`（相对路径）。两个字段都可以空着。不要新造 status 来表示取代
- 带 `superseded_by` 的页从 `wiki/index.md` 主表移出，保留页面，由后继页链入。不要为了清掉 lint warning 而删页或改写主张

### 5. Inspiration pass（默认开启，可 `--no-spark` 跳过）

读 `references/inspiration.md`：找矛盾、空白 map、可合并簇、跨 topic 桥梁、**3 条可 Capture 的新问题**（写进 inbox 或口头给用户）。

### 6. 收口

- 结构性变更（新 map、大合并）→ `wiki/changelog.md`
- 输出：**本次处理 N 条 · 新建/合并 M 页 · 下次建议 review 日期 · 灵感清单**
- 机械问题多 → 建议下一轮 `/lint`

## 输出风格

- 像 **编辑复盘**，不是聊天摘要
- 每条结论带 **路径**（`wiki/topics/...`）
- 灵感要 **可行动**（一句 Capture 提示），不要空泛「可以多想想」
- 尊重 stop-slop：短句、具体、少口号

## bundled references

| 文件 | 内容 |
|------|------|
| `references/modes.md` | Weekly / Topic / Recall / Quick 模式 |
| `references/triage-checklist.md` | inbox、due 页、frontmatter 扫描 |
| `references/inspiration.md` | 激发新连接与 Capture 线索 |
