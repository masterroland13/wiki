# Loop Agent 源码学习

> 对照 [Pi Agent Book](https://dgzhuya.com/modules/ch01-overview) 的十章结构，按 [loop-agent](https://github.com/masterroland13/loop-agent) 仓库 2026-11-03 的代码讲。  
> 产品名只称 Loop Agent。  
> 和宪章冲突时以 [`docs/architecture-charter.md`](https://github.com/masterroland13/loop-agent/blob/main/docs/architecture-charter.md) 为准。  
> 短速查仍用 [`docs/design/loop-agent-manual.md`](https://github.com/masterroland13/loop-agent/blob/main/docs/design/loop-agent-manual.md)。

每一章都回答三层：是什么、源码怎么走、为什么这样而不是那样。源码讲解用我们开发时的说法：文件路径、函数名、钩子名、SSE 事件名，按一次真实请求的调用顺序往下走。

物理包名仍是 `agent_window`。下面说的 loop-ai / loop-agent-core / loop-coding / loop-window 是逻辑层，不是四个已发布的 pip 包。

| 章 | 文件 | 回答的问题 |
|----|------|------------|
| 1 | [ch01-overview.md](ch01-overview.md) | Loop Agent 是什么，和 Pi / Cursor 差在哪 |
| 2 | [ch02-layers.md](ch02-layers.md) | 四层和三个运行时目录怎么分工 |
| 3 | [ch03-agent-loop.md](ch03-agent-loop.md) | `run_agent_loop` 怎么让模型反复想和做 |
| 4 | [ch04-model.md](ch04-model.md) | 一套 OpenAI 兼容客户端怎么按会话选网关 |
| 5 | [ch05-tools.md](ch05-tools.md) | 工具怎么注册、审批怎么从工具里拆出去 |
| 6 | [ch06-messages.md](ch06-messages.md) | 库里的行、树上的路径、进模型的 dict 三套表示 |
| 7 | [ch07-events.md](ch07-events.md) | SSE、EventSink、TurnTrace 各管什么 |
| 8 | [ch08-context.md](ch08-context.md) | 系统提示、记忆快照、Skills、观察瘦身怎么省窗口 |
| 9 | [ch09-compaction.md](ch09-compaction.md) | 超限之后怎么切、怎么摘要、怎么上树 |
| 10 | [ch10-session.md](ch10-session.md) | 会话怎么存、怎么恢复、怎么分叉、全文落在哪 |

建议按顺序读前六章。第 7 章起可以跳读，但第 9 章依赖第 6 章和第 8 章。

读代码的最短路径：

1. `backend/src/agent_window/core/loop_config.py`
2. `backend/src/agent_window/core/session_tree.py`
3. `backend/src/agent_window/agent/loop.py` 里的 `run_agent_loop` / `_run_one_turn`
4. `backend/src/agent_window/api/routes.py` 里的 `send_message_endpoint`
5. `backend/src/agent_window/services/context_transform.py` → `compress.py` → `compaction_persist.py`
