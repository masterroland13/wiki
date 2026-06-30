---
name: review
description: Review, consolidate, and reconnect this wiki's knowledge—and spark new ideas from what you already captured. Use when the user says /review, 回顾 wiki, 复习整理, weekly review, 复盘, 整理 inbox, review_after 到期, or wants inspiration from existing notes. Complements /wiki (capture/archive), /lint (mechanical link/nav fix)—not a substitute for either.
---

# review

对 wiki 知识库做 **Review（再整理、再连接、再激活）**：把 Capture 落下的碎片变成可复利资产，并从已有笔记里 **激发新连接与新问题**。

## 先读

1. `AGENTS.md`
2. `wiki/WIKI_SCHEMA.md`（两段式工作流、frontmatter、`review_after`）
3. `wiki/index.md`
4. 按需：`wiki/inbox.md`、用户指定的 map / project

## 与其它技能的分工

| 技能 | 何时用 |
|------|--------|
| **/wiki** | 新 URL、新对话、新截图 → Raw + topic + 导航 |
| **/review** | 已有 inbox / growing / stale / 到期页 → 提炼、互链、复盘、灵感 |
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
3. **边界在哪？** — 何时不成立、与哪条旧结论冲突

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
- **merge** — 并入已有 topic，旧页留重定向或删冗余
- **link** — 补 Related、map、index 入口；不新建页
- **defer** — 仍有价值但未成熟 → 更新 `review_after`、`confidence`
- **drop** — 无复用价值，从 inbox 移除（说明理由）

### 4. 更新 frontmatter

- `growing` / `stale` → 补或调 `confidence`、`review_after`
- 结论收敛 → 考虑 `stable`
- 始终更新 `updated`

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
