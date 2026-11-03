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
  - https://github.com/masterroland13/loop-agent/blob/main/docs/design/loop-agent-book/ch07-events.md
confidence: 0.75
review_after: 2026-12-03
---

# 第 7 章：事件 —— SSE、EventSink、Trace 各管一条管道

> 本章回答：为什么环里到处是 `yield {"type": ...}`；浏览器、审计、落盘为什么不能都直接绑在 yield 上；断开连接之后回合为什么还要跑完。

## 1. 三种消费者

同一次工具调用，三方需要不同的东西：

| 消费者 | 要什么 | 管道 |
|--------|--------|------|
| 浏览器 | 立刻画字、画 diff、画审批卡 | SSE：`yield` 出去的 dict 被收成 `data: {...}` |
| 旁路 | 审计、测试里的记录器，失败不能弄断环 | `EventSink`（Pipe A） |
| 事后回放 | 刷新页面还能看到这轮干了什么 | assistant 行上的 `trace` + `transcript.jsonl` |

环的 docstring 把 yield 的事件列成一份契约。窗口只应该依赖这份名字，不要去读 `working`。

## 2. 生命周期事件

`core/event_sink.py` 把四类标成 `LIFECYCLE_TYPES`：

- `agent_start` / `agent_end`：一次 `run_agent_loop`。
- `turn_start` / `turn_end`：一次 LLM + 它的工具批。`turn_end` 带 `index` 和 `outcome`（continue / done / stop）。

`agent_end` 在 `finally`，所以取消也会到。`turn_end` 在软着陆的 `finally` 里也会到。前端用它们关「正在生成」，而不是只等 `done`。`done` 表示有终稿；取消路径可能只有 `error`，没有 `done`。

## 3. 环会 yield 的业务事件

| type | 何时 | 前端大致做什么 |
|------|------|----------------|
| `turn_goal` | Goal 开且抽出了目标 | 目标条 |
| `steer_inject` | 插队文本已进 working | 可显示「已插入」 |
| `thought` | 供应商返回了 reasoning | 活动线「思考」 |
| `tool_start` | 开始一个工具 | 活动线一行 |
| `tool_result` | 工具结束 | 收起、标状态 |
| `diff` / `shell` / `await_approval` | 门控卡片 | 审批 UI |
| `progress_checkpoint` | Goal 批末 | 进度；`settled` 时不要空等 |
| `edit_nudge` | 戳了一次「你还没 propose_edit」 | 一般不单独气泡 |
| `soft_land` | 触顶收口 | 横幅：未完成 |
| `tools_disabled` | 网关拒绝 tools | 提示换模型 |
| `token` | 终稿全文（不是逐 token 的唯一来源，见下） | 写入 assistant 气泡 |
| `done` | 终稿结束 | 停止转圈 |
| `error` | 取消、空响应、供应商、触顶失败 | 错误态 |
| `context_compressed` | 窗口在压缩成功后另发 | 占用变化。环自己不发这个名字 |

说明：`token` 事件的 `content` 在当前实现里经常是**整段终稿**，不是必须逐字增量。流式增量如果在 `chat_complete` 内部聚合完才返回，环就一次 yield。UI 要能接受「一条 token 就是全文」。思考和工具才是过程事件。

`_tool_result`、`_gate_meta` 以下划线开头，是管道给环的内部事件，环不会把它们原样 `_pub` 出去。

## 4. EventSink：旁路失败不能杀死环

```text
def _pub(ev):
    sink.emit(ev)
    return ev
```

`emit` 先 `deepcopy`，再逐个 subscriber。subscriber 抛错只打日志。测试可以 subscribe 收集事件，不必解析 SSE 文本。

生产路径上，主消费者仍是 yield。Sink 是 Pipe A：火忘。不要在 subscriber 里写数据库事务还假设失败会回滚整轮——失败被吞了。要落库的逻辑放在窗口的消费循环里，那里失败要看得见。

`_run_one_turn` 内部的 yield 在外层 for 里是 `sink.emit(event)` 再 yield。软着陆和外层生命周期走 `_pub`。两条路都会进 sink。不要假设「只有 `_pub` 的才进 sink」。

## 5. 窗口怎么把事件变成 SSE

`_agent_turn_event_stream` 包住 `run_agent_loop`。它还负责：

- 占位 assistant 已经在发送前插入。
- 流中把 trace 增量写回这行（`TurnTraceWriter`）。
- 终稿 `finalize`：content、trace、耗时。
- 中断 `finalize_interrupted`：也要留下 assistant，JSONL 也追加。审查要求中断轮次不能少 assistant，否则检索和回放对不齐。
- 压缩成功且上树成功，才追加 JSONL 的 compact 事件。上树失败不能假装 compact 成功。

`_sse_detach_producer`：客户端断开后，生产者继续，直到 `end_turn`。否则用户一刷新，会话卡在 BUSY，占位气泡永远空。

响应头 `Cache-Control: no-cache`，`media_type=text/event-stream`。

## 6. Trace 和 JSONL 不是同一份

| | `Message.trace` | `transcript.jsonl` |
|--|-----------------|-------------------|
| 粒度 | 这一条 assistant 气泡的过程 | 会话级追加日志：user、assistant、tool、gate、compact |
| 用途 | 刷新后画活动线 | 压缩后 `search_session` 找回原文；审计级留档 |
| 体积 | 过大工具结果换成 spill 引用 | 同样打码；附件只记 id 和文件名 |
| 删除 | 删消息/删会话会跟着走 | 删会话时应一起处理会话目录；`loop uninstall` 不删 |

`append_transcript_event` 只追加。不改历史行。密钥字段走 `redact_value`。`data_path` 若逃出用户数据目录，拒绝写。坏行在读取时跳过，不让一行损坏拖垮检索。

`search_session` 不读 SQLite 当后备。库是气泡，JSONL 才是全文。混用会搜到不该搜的列。

## 7. 审计是第三条更粗的管道

`services/audit.py` 的 `emit_audit` 写 `audit_events` 表。事件类型如 `goal.change`、门控 apply/reject。它不是 SSE。设置页和审计面板读它。

Goal 变更在 routes 里用 `goal_change_audit_event` 发出，不在环中。因为「目标变了」是会话状态，不是某一次 tool call。

YOLO 的 diff/shell/memory 也要记成 gate。自动执行不是「没发生」。

## 8. 取消的事件顺序

用户点停止：`cancel_session_endpoint` 置位 `cancel_event`。

可能发生的顺序：

1. 若卡在 `chat_complete`：`race_with_cancel` 抛 `TurnCancelled`，yield `error TURN_CANCELLED`，outcome STOP，然后 `turn_end`、`agent_end`。
2. 若卡在工具批中间：当前工具看到取消，`STOP_CANCELLED`，没跑的 tool_call 补 stub，再同样的 error。
3. 窗口 `finalize_interrupted`，JSONL 有这条 assistant。

不会出现「error 发出去了但 working 里 assistant 的 tool_call 没有 tool 消息」这种半截。下一次用户发送会重新 `build_path`，不会把半截 working 留到下一轮 HTTP。working 是这一次 Trace 的内存。

## 9. 和 Pi 第 7 章的差别

Pi 的 Agent 是 EventEmitter，UI 和扩展都 subscribe。我们的主路径是异步生成器，因为 FastAPI 的 SSE 就是 `StreamingResponse` 吃异步迭代器。EventSink 是额外的旁路，不是唯一总线。

扩展系统还没有。所以没有「订阅 `turn_end` 再触发下一轮」这种 Pi 扩展写法。续命要接 `get_follow_up_messages`，而不是在前端收到 `done` 之后自动再 POST。前端自动再 POST 会绕过环的停止规则。

## 10. 对着读的文件

- `agent/loop.py` 文件头 docstring 的事件列表
- `core/event_sink.py`
- `services/turn_trace.py`：`TurnTraceWriter`、`is_turn_in_progress`
- `services/session_transcript.py`：`append_message_event`、`append_sse_event`、`redact_value`
- `api/routes.py`：`_agent_turn_event_stream`、`_sse_detach_producer`、`cancel_session_endpoint`
- 前端：`src/utils/turnTrace.ts`、`src/api/agent.ts`
- 测试：`tests/test_sse_detach.py`、`tests/test_audit.py`、`tests/test_session_transcript.py`

下一章把「进模型之前谁在裁上下文」按层摊开。压缩算法本身留到第 9 章。

## Related

- 上一篇：[ch06-messages.md](./ch06-messages.md)
- 手册目录：[README](./README.md)
- 下一篇：[ch08-context.md](./ch08-context.md)
- 源码仓库：[masterroland13/loop-agent](https://github.com/masterroland13/loop-agent)
