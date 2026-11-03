---
type: project-note
status: growing
created: 2026-11-03
updated: 2026-11-03
tags:
  - cs
  - loop-agent
  - source-book
sources:
  - https://github.com/masterroland13/loop-agent/blob/main/docs/design/loop-agent-book/ch09-compaction.md
confidence: 0.75
review_after: 2026-12-03
---

# 第 9 章：上下文压缩 —— 对话太长时怎么切、怎么摘要、怎么上树

> 本章只讲超限之后。系统提示、瘦身、检索在第 8 章。读完你应该能说出：什么情况下一条摘要会写进树，什么情况下故意不写。

## 1. 目标

跨轮交接要达到「本地压一下还能接着干」的程度，而不是把算法焊进 `loop.py`。漏斗是：

```text
全文永不丢（transcript.jsonl）
    → 进模型的路径可以变短，而且变短的结果写回树
        → 耐久的 system / 记忆 / Skills 不进这一刀
            → 丢掉的细节用 search_session 按摘录拉回
```

入口只有 `compress_messages_if_needed`（`services/compress.py`）。环和手动 compact 都走它。

## 2. 什么时候真的压

```text
if not auto_compress and not force:
    return 原样, compressed=False
tokens = 字符估算
threshold = context_limit - reserve   # reserve 默认 1024
if tokens <= threshold and not force:
    return 原样, compressed=False
```

`auto_compress` 默认关。普通发送在预算内什么都不做。

`force=True` 是手动 `POST /api/sessions/{id}/compact`。可以带 `focus`：摘要的 Critical / Next 偏向这些词。空会话 400，不改工作区文件。

`tail_trim` 也返回 `compressed=True`，但 **不上树**。它只是「太短、切不出一段旧对话」时丢掉最老的几条，留下尾巴。`compaction_persist` 只接受 method 为 `llm` 或 `extractive`。tail_trim 写上树会变成一条没有摘要正文的假节点。

## 3. 切点：`find_cut_index`

先把消息拆成三堆：

- 普通 system（契约、记忆所在的那些）留下。
- Goal 的 system 块拿掉，改由 `preserve_goal` 在压完后重新钉上。避免旧目标块和新摘要打架。
- 其余 `rest` 才参与切。

从 `rest` 的尾巴往前累加估算 token，直到够 `keep_recent_tokens`。切点再往前挪，直到落在 `user` 或 `assistant` 上。不能把一段的第一句切成 `tool`，否则模型看到孤儿 tool 结果。

`keep_recent` 是「最近原话保留」。更老的进 `older`，变成摘要。

切不出来（整段 rest 都在预算里）且不是 force：若 rest 很短，走 `tail_trim`。force 且几乎没得切时，尽量留最后两条，保证手动按钮有可见效果。

## 4. 摘要正文：先抽取，再让模型改写

对 `older`：

1. `find_previous_summary`：若旧区间里已经有一条摘要，抽出来供增量合并，避免一次次摘要把更早的决定洗没。
2. `serialize_messages_for_summary`：把旧消息收成有长度帽的文本，供模型读。
3. `build_extractive_summary`：不调模型，按规则抽出六节。这是兜底，也是评判模型摘要的尺子。
4. 若传入了 `summarize` 回调（窗口用当前会话的档案调一次短完成），用它改写。失败、超时、结构太烂，就留抽取版。`method` 记成 `llm` 或 `extractive`。

六节标题固定：

```text
## Goal
## Constraints
## Progress
## Key Decisions
## Next Steps
## Critical Context
```

`coerce_six_sections`：

- 模型正文里「（见原文）」出现太多次，整段丢掉，用抽取版。
- 模型没写出至少三节，用抽取版的骨架，把模型自由文本塞进 Progress，避免一份散文替换掉结构。
- Goal 节若只是把 `preserve_goal` 复读一遍（回声），用抽取版的 Goal 换掉。`_section_echoes_goal` 看归一化后的重叠。
- 抽取版会丢掉「元问题」（「你刚才说了什么」这种 follow-up）、假的空闲进度、大段看起来像摘要倾倒的用户粘贴。Next Steps 要留下还没做的事，而不是把用户的提问再贴一遍。

摘要消息的 content 带 `【对话压缩摘要】`。前面还有交接说明：这是交接，不是复述。`preserve_goal` 非空时，压完再 `inject_goal_into_messages`，把目标作为独立 system 钉回去。自动压缩不能把 Turn Goal 洗掉。Goal 关着不钉。

## 5. 被折掉的 user 原话留一段

`select_folded_user_originals`：在 `older` 里只挑真实 user。跳过摘要自己、空 user、assistant、tool。

从近到远累加，默认大约 8K token。**最近一条 user 一定留**。一旦更早的一条放不下，停，不再跳过它去捞更早的短句。这是 C2 审查定的：跳着捞会让「中间那句关键要求」消失，只剩下更老的短句。

这些 user 挂在摘要和近端之间。assistant 不会被改成 user。下一轮叶子路径仍能看见用户原话，而不只看见模型对原话的改写。

上树用的 token 帽必须和这次压缩用的是同一个数。内存里按 8K 选了，树上不能再按另一个默认多挂几条。

## 6. 上树：`persist_compaction_on_tree`

被折的原文留在 SQLite 和 JSONL。叶子路径绕开它们：

```text
摘要.parent_id = 被折的第一段原来的 parent
被保留的第一段.parent_id = 摘要.id
leaf_id 不动
```

`update_leaf=False`。当前尖端仍是用户正在看的那条，不会跳到摘要上。

对齐：

- `meta.method` 必须是 `llm` 或 `extractive`。
- `summary_content` 非空。
- `cut_index` 落在路径行数中间。
- `rest_count` 必须等于「压之前的可持久化路径 + 本轮 user」的行数。对不齐就 **跳过**，不猜一个切点硬写。`strict_align` 为真时如此。

relink 中途失败：`_rollback_persist` 删掉刚插入的摘要，把已经改过的 `parent_id` 改回去。不留半条链。

环内 working 比树长（里面有 tool 消息）时，不能把 working 的 cut 套到树上。`persist_compaction_from_tree` 在当前叶子路径上重新 `find_cut_index`，摘要正文仍用刚生成的那份。这是 C3。

JSONL 的 compact 事件只在上树成功之后追加。上树失败，前端不能显示「已压缩」。

## 7. 手动 compact 和自动压的差别

| | 自动 | 手动 |
|--|------|------|
| 开关 | `auto_compress` | `force=True` |
| 预算 | 超阈值才动 | 尽量压，即使还没超 |
| focus | 无 | 有则偏向 Critical / Next |
| Goal | 钩子传入的 `preserve_goal` | Goal 开时同样钉目标 |
| 上树 | `on_compressed` | compact 端点自己调 persist |

两条路的六节和切点是同一套函数。不要在路由里复制一份摘要提示词。

## 8. 估算不是账单

`approx_tokens` 用字符数除以 4。中文会偏乐观或偏悲观，和网关 tokenizer 不一致。所以阈值留了 `reserve`。真超限时 `humanize_provider_error` 仍可能告诉用户新开会话。压缩是尽力，不是保证。

## 9. 已知没做

- C6：在 `after_tool_batch` 里再压一次的专门策略。现在是每 Turn 开头压，工具批中间不压。
- C7：对放弃的兄弟枝做摘要。现在兄弟只是留在库里，不进叶子路径。
- 并发：两个请求同时 compact 同一会话没有单独的锁（发送本身有 SESSION_BUSY，compact 端点要单独看它是否也占这个锁）。

## 10. 和 Pi 第 9 章的差别

Pi 的 compaction 也是「旧消息变成结构化摘要，留在会话文件里」。我们多了三条约定：

1. 摘要是树上的 `entry_type`，模型侧才变成带标记的 user。
2. 被折 user 的近端原话按预算留下，不是全部交给模型改写。
3. 默认不自动压。全文在 JSONL。Pi 更倾向于在阈值到了就压，因为它的会话文件就是唯一真源。

## 11. 对着读的文件

- `services/compress.py`：`find_cut_index`、`select_folded_user_originals`、`build_extractive_summary`、`coerce_six_sections`、`compress_messages_if_needed`
- `services/compaction_persist.py`：`persist_compaction_on_tree`、`persist_compaction_from_tree`
- `services/context_transform.py`：`on_compressed`
- `api/routes.py`：`compact_session_endpoint`、`_session_context_usage`
- 测试：`tests/test_compress.py`、`tests/test_compaction_persist.py`、`tests/test_compact_api.py`
- 手测剧本：`docs/dogfood/section-7-compress-playbook.md`

下一章把会话作为整体：创建、恢复、分叉、删掉之后磁盘上还剩什么。

## Related

- 上一篇：[ch08-context.md](./ch08-context.md)
- 手册目录：[README](./README.md)
- 下一篇：[ch10-session.md](./ch10-session.md)
- 源码仓库：[masterroland13/loop-agent](https://github.com/masterroland13/loop-agent)
