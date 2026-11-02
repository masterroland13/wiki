---
type: map
status: growing
created: 2026-06-30
updated: 2026-11-02
tags:
  - wiki
  - index
sources: []
confidence: 0.5
review_after: 2026-07-15
---

# wiki 索引

本目录是个人 **长期复利知识库**：Markdown 按 `maps/`、`topics/` 等组织。  
原件在 `references/raw/`（及可选 `references/papers/`）。规则见 [`WIKI_SCHEMA.md`](./WIKI_SCHEMA.md)。

**默认阅读顺序**：本页 → 相关 map / project → 具体 topic / entity。

## Start Here

| 页面 | 用途 |
|------|------|
| [**wiki教学与使用手册**](./maps/wiki-teaching-usage-handbook.md) | 完整上手说明：工作流、技能、模板、归档 |
| [Schema](./WIKI_SCHEMA.md) | 目录布局、前缀、维护习惯 |
| [Changelog](./changelog.md) | 结构性变更记录 |
| [操作日志](./log.md) | ingest / query / lint 时序。默认 L1 不写 ingest 条目 |
| [Inbox](./inbox.md) | 待归档队列 |
| [Capture → Review → Archive](./maps/capture-review-archival-workflow.md) | 低摩擦录入工作流 |
| [Learning spine（跨学科主轴）](./maps/learning-spine.md) | 阶段化学习导航 |

## 文艺（文学 · 影像 · 音乐）

| 笔记 | 说明 |
|------|------|
| *（待 ingest）* | 文学：`lit-` 前缀 → `topics/` |
| *（待 ingest）* | 电影：`film-` 前缀 → `topics/`；作品用 `entities/` |
| *（待 ingest）* | 音乐：`music-` 前缀 → `topics/`；专辑/艺人用 `entities/` |

## 人文

| 笔记 | 说明 |
|------|------|
| [《妥协社会》· 纯划线 37 条](./topics/phil-han-palliative-society-highlights.md) | 原文 + 上下文 / 解读 |
| [《妥协社会》· 阅读笔记索引](./maps/phil-han-palliative-society-reading-index.md) | 27 条想法 + Agent 点评（全书） |
| [《妥协社会》· 笔记 11–27](./topics/phil-han-palliative-society-notes-11-27.md) | 无意义 → 伦理学 |
| [《妥协社会》· 笔记 5–10](./topics/phil-han-palliative-society-notes-05-10.md) | 幸福强制 / 生存 |
| [《妥协社会》· 笔记 1–4](./topics/phil-han-palliative-society-ch01-algophobia-notes.md) | 痛苦恐惧症 |
| [《妥协社会》实体](./entities/entity-book-palliative-society.md) | 书目 hub |

## 理工

| 笔记 | 说明 |
|------|------|
| *（待 ingest）* | 计算机：`cs-` → `topics/` |
| *（待 ingest）* | 物理：`phys-` → `topics/` |
| *（待 ingest）* | 天文：`astro-` → `topics/` |

## 跨学科

| 笔记 | 说明 |
|------|------|
| *（待 ingest）* | 桥梁主题：`x-` → `topics/` |

## 实体（Entities）

| 页面 | 说明 |
|------|------|
| [实体页说明](./entities/README.md) | 何时建 entity、命名约定 |

## 项目（Projects）

| 项目 | 说明 |
|------|------|
| [Learning progress](./projects/learning-progress/index.md) | 行为记忆 hub（偏好 / 纠错 / 进度）。不是主题索引，也不是事实的单一真相源 |

## 协议示例

合成页，用来演示两条主张可以同时留下。不是阅读笔记。

| 笔记 | 说明 |
|------|------|
| [矛盾并存（合成）](./topics/x-demo-contradiction-coexistence.md) | 当天重读与间隔复习两条虚构主张同页保留；不裁定谁对 |
| [事实与偏好分家（合成）](./topics/x-demo-fact-vs-preference.md) | 测量留在 topic。偏好在 learning-progress，不链进本表 |

## 维护技能

| 技能 | 触发 |
|------|------|
| `/wiki` | 投喂 URL、截图、聊天 → 归档 |
| `/query` | 按已有笔记回答；金标见 [retrieval cases](./evals/retrieval-cases.md) |
| `/review` | 复盘 inbox、到期页 |
| `/lint` | 坏链、导航、frontmatter；`superseded_by` 页仍被本页主推时 warning |
