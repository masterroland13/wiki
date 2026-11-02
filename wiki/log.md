# Wiki Operations Log

时序操作记录（**ingest / query / lint**）。最新条目在顶部。

本文件**不是**结构性变更日志。目录约定、schema、技能体系写在 [`changelog.md`](./changelog.md)。不要把 changelog 改成操作日志，也不要把每一次小补丁写进 changelog。

## 条目前缀

标题必须能被 grep。动词三选一，不要把 `ingest|query|lint` 原样写进标题：

```text
## [YYYY-MM-DD] ingest | 标题
## [YYYY-MM-DD] query | 标题
## [YYYY-MM-DD] lint | 标题
```

模式：`## [YYYY-MM-DD] ingest|query|lint | title`（日期、一个动词、空格、竖线、空格、一行标题）。

| 动词 | 何时写 |
|------|--------|
| `ingest` | **L2 compile 必写**。默认 L1 / L0 **不写** |
| `query` | 每次 `/query` 结束写一条，包括找不到 |
| `lint` | 每次 `/lint` 结束写一条，带上 error / warning 数量 |

默认归档深度是 **L1**。用户不说「L2」「深挖」「compile」「级联」，就停在小步归档：不级联 entity / map / index，也不写 `ingest` 条目。

L2 只额外碰**相关** entity、**相关** map、[`index.md`](./index.md)，并在本文件顶部追加一条 `ingest`。不改无关阅读笔记正文，不凑 10–15 页。不存在的预期路径用反引号，不要写成链接（本文件仍做相对链接检查，但没有知识页 frontmatter）。

规则见 [`WIKI_SCHEMA.md`](./WIKI_SCHEMA.md)「操作日志与 changelog」。

## 条目

## [2026-11-02] ingest | L2 dry-run — synthetic example-widget

协议演练，**未执行写入**。用来核对 L2 的 log 标题和预期触达。没有新建下面的 topic / entity，也没有改 [`index.md`](./index.md) 的知识分区、任何 map 正文，或《妥协社会》阅读笔记。

- depth: L2（须明示；未说则仍是 L1，本条不会出现）
- 样例来源：虚构「example-widget」。不是一次真实投喂
- 预期触达（真做 L2 时只做这些；路径尚不存在，故用反引号）：
  - topic（L1 也会写的那一页）：`wiki/topics/cs-example-widget.md`
  - entity：`wiki/entities/entity-example-widget.md`（短定义 + 链到 topic，不搬笔记正文）
  - map：`wiki/maps/learning-spine.md`（加一行链接，不改其它阶段的段落）
  - index：`wiki/index.md` 理工分区加一行
  - log：本条
- 明确不碰：`wiki/changelog.md`（这次不是结构变更）、`wiki/topics/phil-han-palliative-society-*.md`、其它 map 的正文
- 停在 L1 时：只写或补一篇 topic，必要时一条 index 或 map 入口；不写本文件，不级联 entity
