---
type: entity
status: seed
created: 2026-05-16
updated: 2026-05-16
tags:
  - template
  - entity
sources: []
project: []
confidence:
review_after:
# 可选，仅高价值页。相对本页的路径。不裁定对错，也不必回填旧页。
supersedes: []
superseded_by: []
# 可选。仅 entity 页的类型。省略或留空都可以，lint 不检查。
# book | person | work | org | concept | album | tool
kind: book
aliases: []
# 相关人物 / 作品的 entity 页，相对本页的路径。没有就空着，不要为了填字段建空页。
people: []
works: []
# 出版、生卒、首演等自由文本。不是 lint 的 YYYY-MM-DD。
date:
# 个人评分，可空。
rating:
---

# Entity Name

复制后改标题。下面的类型字段都可选，旧页不必回填。建页门槛：至少 2 个不同的 wiki 页链向或显式提及这个名字，或者用户在当次 `/review` 里点名。未达门槛不要新建。散文里反复出现的人名不算。脚本：`python3 scripts/check_missing_entities.py`。

## Identity

与 frontmatter 对齐。没有的项留空。

- **kind**：`book` | `person` | `work` | `org` | `concept` | `album` | `tool`
- **aliases**：译名、原题、简称
- **date**：
- **rating**：

## People

相关人物。每条是已经存在的 `wiki/entities/entity-*.md`，写相对本页的路径。没有就不写。

- 

## Works

相关作品（书、专辑、影片或其它 work）。同样只链已经存在的 entity。没有就留空。

- 

## Working Definition

用 1-3 句话定义这个实体，不追求百科全书式完整，优先可复用。

## Inclusion / Exclusion

- **属于这个实体**：哪些情况算
- **不属于这个实体**：哪些情况不算

## Why It Matters

说明这个实体在当前仓库语境下的作用边界。

## Signals

如何在实际任务里识别“该实体正在起作用”。

- signal one
- signal two

## Related Notes

- [Related topic](../topics/example-topic.md)
- [Related map](../maps/example-map.md)

## Contradictions

与其它页冲突、且还没有取代关系时写在这里。两边都保留，不删改对方正文，也不裁定谁对。普通页留空。

- 对方页：
- 对方主张：
- 本页主张：
- 各自来源：

## Superseded

只在更换「先读哪一页」时填写，并同步 frontmatter 的 `supersedes` / `superseded_by`（相对本页的路径，可空）。这不表示旧主张为假。旧页留着。

- 本页取代：
- 本页被谁取代：
- 留下旧页的原因：

## Adjacent Entities

| Entity | Relationship | Common confusion |
|------|------|------|
| [Adjacent entity](./example-entity.md) | 互补/上位/下位 | 容易混淆点 |
| [Adjacent entity](./another-entity.md) | 互补/上位/下位 | 容易混淆点 |

## Open Questions

- 哪些边界仍然模糊
- 下一次更新要补什么证据
