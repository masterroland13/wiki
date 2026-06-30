---
type: map
status: seed
created: 2026-05-16
updated: 2026-05-16
tags:
  - workflow
  - wiki
  - capture
sources:
  - https://stephango.com/vault
  - ../WIKI_SCHEMA.md
---

# Capture -> Review -> Archive

一句话：先低摩擦记录，再周期性整理，让结构通过链接和属性自然涌现。

## Scope

- 适用于日常输入新材料、新想法、新会议记录
- 目标是减少“该放哪”的决策开销
- 与 `wiki/index.md`、`wiki/WIKI_SCHEMA.md` 配合使用

## Workflow

| Stage | Goal | Default place | Time budget |
|------|------|------|------|
| Capture | 先把想法落地 | `wiki/inbox.md` | 10-60s |
| Review | 补属性、补链接、判断价值 | `wiki/inbox.md` + 目标页草稿 | 15-30min / week |
| Archive | 沉淀为长期资产 | `wiki/topics/` `wiki/maps/` `wiki/entities/` | 按需 |

## Capture Rules

1. 新内容优先“写下来”，不要先纠结分类。
2. 至少补一个来源（`sources`）或一个上下文线索。
3. 如果能想到关联对象，立即加一个内部链接。

## Review Checklist (Weekly)

- 把高价值条目从 inbox 提升到对应目录
- 统一 frontmatter 字段名（`kind/project/people/date/rating/status`）
- 检查是否写清“主张-证据-边界”（避免只做摘抄）
- 修复断链，补关键互链（topic <-> map <-> entity）
- 需要时在 `wiki/changelog.md` 记录结构变更

## Archive Heuristics

- 可复用知识 -> `wiki/topics/`
- 导航或编排页 -> `wiki/maps/`
- 稳定术语定义 -> `wiki/entities/`
- 单篇论文笔记 -> `wiki/papers/`
- 项目私有经验 -> `wiki/projects/<project>/`

## Minimal Example

```yaml
---
type: topic
status: seed
kind: reference
project: []
people: []
date: 2026-06-30
sources:
  - ../../references/raw/example-clip.md
---
```

这个流程追求的不是“立刻整洁”，而是“长期低摩擦 + 可持续复用”。
