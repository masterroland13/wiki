# Template Design Rationale

这个文档说明：为什么当前模板采用“低摩擦 Capture + 批判性 Deepen”的结构。

## 目标问题

旧模板常见问题：

- 结构好看但不逼迫思考，容易变成信息搬运
- 字段过多且一次性必填，创建成本高
- 只有结论没有证据，几周后难以判断可信度

## 证据来源（方法论）

- 深度加工优于机械转录：`levels of processing` 与生成效应相关研究强调“用自己的话重构”比逐字记录更利于长期记忆。
- 结构化提问可提升长期保留：近期 note-taking 研究在真实教学环境中显示，结构化方法（如 Cornell）对长期保留有优势，且动机是稳定相关变量。
- 原子化与链接：Zettelkasten 强调“一条笔记一个核心想法 + 有意义链接”，降低后续组合和复用成本。
- 渐进式总结：Progressive Summarization 强调不是每条都精修，而是按价值逐层加深，符合现实维护成本。

参考链接：

- https://www.frontiersin.org/journals/psychology/articles/10.3389/fpsyg.2025.1697151/full
- https://howtothink.ai/learn/note-taking-as-information-processing
- https://zettelkasten.de/atomicity/guide/
- https://fortelabs.com/blog/progressive-summarization-a-practical-technique-for-designing-discoverable-notes

## 设计决策映射

| 设计决策 | 解决的问题 | 对应模板结构 |
|------|------|------|
| 两阶段写作（先 Capture，后 Deepen） | 一上来写太重导致弃用 | 每个模板保留 `TL;DR` + 可选深度区块 |
| 主张-证据分离 | 只抄摘要、缺可验证性 | `Core Claim` + `Evidence` / `My Assessment` |
| 显式边界和反例 | 过度泛化、错误迁移 | `Boundaries / Counterexamples` |
| 记录不确定性 | 结论僵化、难迭代 | `Open Questions / Next Verification` + `confidence` |
| 冲突显式化，取代只留痕 | 静默改掉旧主张 | `## Contradictions`、`## Superseded`；可选 `supersedes` / `superseded_by` |
| 强制互链 | 知识孤岛 | `Related` 区块 |

## 使用建议（务实版）

1. 首轮写作只完成：`TL;DR` + `sources` + `Related`。
2. 仅对高价值页面补写 `Evidence` 与 `Boundaries`。
3. 每周回顾时补 `confidence` 和 `review_after`，而不是创建当天写完所有字段。
4. `supersedes` / `superseded_by` 保持空白，直到这一页真的要记录冲突或更换阅读入口。见 [`WIKI_SCHEMA.md`](../WIKI_SCHEMA.md)「矛盾与取代」。
