# 行为记忆层

本目录是**行为记忆**：偏好、纠错、教学进度。可复用事实在 `wiki/topics/`、`wiki/entities/`、`wiki/papers/`。本目录不是知识的单一真相源，也不是 `wiki/index.md` 的主题主入口。索引可以在「项目」里轻链 [hub](index.md)。

不要求 Mem0、Letta 或任何云端记忆。本层就是仓库里的 Markdown。

契约定义在 [`wiki/WIKI_SCHEMA.md`](../../WIKI_SCHEMA.md)「行为记忆与写入路由」。下表与该节同一路由。若两处不一致，以 schema 为准。

`/teacher`、`/teacher-cs`、`/review` 在讲课或复盘之前读本页，再读 [hub](index.md) 与 [learner profile](learner-profile.md)。

**禁止**把行为偏好写进 topic、entity、paper 的正文。

## 写入路由

| 写什么 | 写到哪里 | 不要写到哪里 |
|--------|----------|----------------|
| 可复用事实、概念、读书结论、可引用主张 | `wiki/topics/`、`wiki/entities/`、`wiki/papers/`；导航在 `wiki/maps/` 与 `wiki/index.md` | 本目录 |
| 学习者偏好（节奏、语言、要提示还是要结论、纠错口吻） | 本目录（[learner-profile.md](learner-profile.md) 或 `preferences/`） | topic / entity / paper 正文 |
| 纠错与「下次怎么教」 | 本目录 | topic / entity / paper 正文 |
| 教学进度、场景水平、未完成任务 | 本目录（hub，以及已有的 `scenes/` 等） | topic / entity / paper 正文 |
| 原始材料 | `references/raw/` 或 `references/papers/` | 不把偏好改写成 raw，也不把 raw 改成偏好 |
| 一次 ingest / query / lint | `wiki/log.md`（不新增动词；默认 L1 仍不写 ingest） | 不把偏好当成一条 log |
| 目录约定或 schema 变更 | `wiki/changelog.md` | 不把一次教学偏好写成结构性变更 |

## 示例

事实与偏好拆开。两边都是虚构的，不是阅读笔记。

| 侧 | 页 | 写的是什么 |
|----|----|------------|
| 事实 | [北窗焦点块的小时完成数](../../topics/x-demo-fact-vs-preference.md) | 合成测量：25/5 为 3.2 项/小时，连续 90 分钟为 2.1 |
| 偏好 | [先提示、限时、先用中文纠正](preferences/demo-hint-first.md) | 怎么教这个学习者，不是测量结果 |
