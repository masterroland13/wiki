# 实体页（Entities）

**实体** = 可反复引用的稳定节点：人、作品、专辑、概念、工具等。

## 何时建 entity

| 问题 | 动作 |
|------|------|
| 「这是谁 / 哪部 / 哪个概念？」 | 建 `wiki/entities/entity-*.md` |
| 「我怎么理解 / 比较？」 | 建 `wiki/topics/<prefix>-*.md` |
| 单次读/观/听记录 | 写在 **entity 页** 的「个人笔记」小节 |

## 命名

- 文件：`entity-<slug>.md`（如 `entity-author-orwell.md`）
- 与 `topics/` 互链；**一个概念 hub** 避免多学科各写一篇重复 entity

## 模板

[`../templates/entity-template.md`](../templates/entity-template.md)

## 索引

在 [`../index.md`](../index.md) 的 **实体** 分区补链接。
