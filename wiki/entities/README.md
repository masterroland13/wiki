# 实体页（Entities）

**实体** = 可反复引用的稳定节点：人、作品、专辑、概念、工具等。

## 何时建 entity

| 问题 | 动作 |
|------|------|
| 「这是谁 / 哪部 / 哪个稳定节点？」并且达到下面的门槛 | 建 `wiki/entities/entity-*.md` |
| 「我怎么理解 / 比较？」 | 建 `wiki/topics/<prefix>-*.md` |
| 单次读/观/听记录 | 写在 **entity 页** 的「个人笔记」小节 |

**门槛**：至少 2 个不同的 wiki 页链向同一个还不存在的 `entity-*.md`，或用显式 wiki 链接 / `entity:名字` 提及它。同一页写两次只算 1 页。散文里反复出现的名字不算。用户在当次 `/review` 里点名，可以建，这不把门槛改成 1。没达门槛且没有点名，不要新建。不为空学科建空 topic。

Weekly 报告：

```bash
python3 scripts/check_missing_entities.py
```

脚本只打印候选，不建页。字段约定见 [`../WIKI_SCHEMA.md`](../WIKI_SCHEMA.md)「实体页」。

## 命名

- 文件：`entity-<slug>.md`（如 `entity-author-orwell.md`）
- 与 `topics/` 互链；**一个概念 hub** 避免多学科各写一篇重复 entity

## 模板

[`../templates/entity-template.md`](../templates/entity-template.md)

## 索引

在 [`../index.md`](../index.md) 的 **实体** 分区补链接。
