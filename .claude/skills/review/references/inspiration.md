# Inspiration pass

Review 不只是「整理干净」，还要从 **已有图** 里发现新边、新问题、新 map。

默认在 Weekly / Topic sweep 结束时跑一遍（Quick 模式可跳过）。

## 六类信号

| 信号 | 问什么 | 典型产出 |
|------|--------|----------|
| **矛盾** | 哪两个 topic 结论打架？ | 在相关页写 `## Contradictions`（对方路径、两边主张、各自来源）。可以另开一页讨论，但禁止静默覆盖：不得删改双方主张。不要只改 `confidence` 就算调和完。更换阅读入口用 `supersedes` / `superseded_by`。见 `wiki/WIKI_SCHEMA.md`「矛盾与取代」 |
| **空白** | map 上列了但没链的 topic？ | inbox 一条 Capture |
| **簇** | 3+ 页同 tag 却无 map？ | 提议新 `wiki/maps/...` |
| **桥梁** | A 领域结论能否解释 B？ | Related 互链 + 一句跨域主张 |
| **过时** | Raw 比 topic 新很多？ | stale + 重读任务 |
| **重复** | 两页讲同一件事？ | merge 建议 |

## 输出格式

至少 **3 条可 Capture 线索**，每条：

```markdown
- **[主题]** 问题：… → 建议动作：inbox 一句 / 新开 topic 草稿 / 读 Raw `path`
```

## 禁止

- 发现冲突时禁止静默覆盖。写入 `## Contradictions` 或 supersession 字段，不裁定谁对
- 不要编造 wiki 里不存在的页（先 grep 确认）
- 不要因为散文里出现了名字，或脚本未达 ≥2 个不同页的门槛，就新建 entity。Weekly 的缺失 entity 以 `python3 scripts/check_missing_entities.py` 和用户当次点名为准
- 不要为空学科建空 topic。没有笔记的分区留在 inbox
- 不要空泛「可以多读论文」— 要具体到 map/topic/URL
- 不要用 inspiration 代替 teacher：这里是 **从库存生问题**，不是教新课

## 与 teacher 的衔接

若灵感暴露 **知识缺口** 且用户想学会：

> 「这条可以开 `/teacher` 专门推 Derivation；review 先把问题写进 inbox。」
