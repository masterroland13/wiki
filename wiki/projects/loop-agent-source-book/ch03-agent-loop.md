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
  - https://github.com/masterroland13/loop-agent/blob/main/docs/design/loop-agent-book/ch03-agent-loop.md
confidence: 0.75
review_after: 2026-12-03
---

# 第 3 章：Agent Loop —— 模型怎么反复想和做

> 本章把 `backend/src/agent_window/agent/loop.py` 走完。读完你应该能手画出：一次用户消息里有几次 LLM 调用、什么时候算一轮结束、什么时候整个 agent 结束、Goal 关着时环里还剩下什么。

## 1. 两种「轮」不要混

| 名字 | 谁说的 | 含义 |
|------|--------|------|
| 用户回合 | 窗口 | 用户按一次发送，到这条 assistant 占位被写完。HTTP 上是一次 SSE |
| Turn | 环 | 一次 `chat_complete`，加上这次返回的全部 tool call。`turn_start` 到 `turn_end` |
| Trace | 环 | 一次 `run_agent_loop`。`agent_start` 到 `agent_end`。里面有 1..N 个 Turn |

用户说「帮我改这个函数并跑测试」，模型可能先读文件（Turn 0），再 `propose_edit`（Turn 1），再 `propose_shell`（Turn 2），最后用文字收尾（Turn 3）。这是一次 Trace、四次 Turn、一次用户回合。

`core/turn.py` 里的 `TurnOutcome` 只有三个值：

- `CONTINUE`：这轮跑了工具，外层 for 再来一次。
- `DONE`：终稿已经发出（`token` + `done`），或者门控决定结束。
- `STOP`：取消、供应商错误、空响应。外层必须 return，不能再调模型。

## 2. 外层：`run_agent_loop`

签名（简化）：

```text
run_agent_loop(messages, model, cancel_event, goal, previous_goal, config, emit, session_id)
```

`messages` 是窗口已经准备好的 OpenAI 风格 dict 列表（system、历史、本轮 user）。环把它复制进 `AgentLoopState.working`，后面只改这份列表。

入口做这些事：

1. `cfg = config or LoopConfig.default()`。
2. `emit` 缺省是空的 `EventSink`。每个对外事件先 `_pub`：既 yield 给 SSE，也 `sink.emit` 给旁路观察者。
3. `import agent_window.tools`，触发各 `register_*`，否则 registry 是空的。
4. 读设置：`disabled_tools`、`max_tool_iters`（夹到 8..64）、检查点间隔、探索阈值。
5. `registry.get_openai_tools()` 去掉被禁用的，得到本轮 `tools` 数组。
6. `effective_goal = turn_goal if cfg.goal_mode else None`。关 Goal 时，软着陆横幅也不会拿目标说事。钩子本身在 `with_goal_mode(False)` 时已经卸掉。

然后：

```text
yield agent_start
若 on_turn_start：注入目标，yield 它返回的事件（通常是 turn_goal）
state = AgentLoopState(working, ...)

for turn_index in range(max_tool_iters):
    若已取消：error TURN_CANCELLED，return
    抽 steering，追加成 user，yield steer_inject
    yield turn_start
    async for event in _run_one_turn(...): yield
    yield turn_end {outcome}
    若 outcome 是 STOP 或 DONE：return
    # CONTINUE 则下一圈

# for 用尽还在 CONTINUE
soft_land 一轮（不带 tools）
finally:
    yield agent_end
```

`agent_end` 在 `finally` 里，所以取消和异常路径也会发出。窗口用它知道这条 SSE 可以收尾。

### 2.1 插队（steering）

用户在生成过程中 `POST /api/sessions/{id}/steer`。`core/steering.py` 把文本放进该会话的队列。每一轮开始前 `drain_steering` 抽空，包一层说明后追加为 `{"role":"user"}`。这是内层插队：插在下一次 LLM 调用之前，不新开 HTTP 回合。

`get_follow_up_messages` 是外层续命（模型说完了，系统再塞一句「继续」）。字段在 `LoopConfig` 上，产品路径没接。不要在 `loop.py` 里临时写一个 while。

## 3. 内层：`_run_one_turn`

一轮的骨架：

```text
working, compressed, meta = apply_transform_context(...)   # 进模型前塑形
turn = chat_complete(working, tools, model)                # 可被 cancel 打断
若有 reasoning：yield thought
若有挂起的 checkpoint：yield progress_checkpoint（有正文就当 reply，否则 settled）
若 tools_fallback：yield tools_disabled

若有 tool_calls：
    把 assistant+tool_calls 追加进 working（带 reasoning_content 回放）
    按顺序跑完每一个工具
    after_tool_batch
    outcome = CONTINUE
    return

若没有 tool_calls：
    处理「声称写过但没门控」「输出被 max_tokens 截断」「该改仓库却没调 propose_edit」
    有终稿：yield token + done，outcome = DONE
    空响应且已跑过工具：用模板合成一句，再 token + done
    空响应且没跑过工具：error EMPTY_RESPONSE，outcome = STOP
```

停止条件是「这个 completion 里没有 tool call」，不是模型文本里出现「完成了」。

### 3.1 进模型前的塑形

`apply_transform_context` 在 `services/context_transform.py`。钩子空则原样返回。默认钩子是压缩（第 9 章）。这里只要记住：`working` 可能在这一刻变短，`state.working` 要指到新列表。压缩失败不应把环弄崩；算法在 coding 层。

### 3.2 `chat_complete` 返回什么

环只认这些键：

- `content`：正文。
- `tool_calls`：`[{id, name, arguments}, ...]`。
- `tools_fallback` / `tools_fallback_reason`：网关拒绝 tools schema，这轮改成纯文本。
- `finish_reason`：`length` 或 `max_tokens` 时追加截断说明。
- `reasoning_content`、`reasoning_duration_ms`、`reasoning_source`：有才发 `thought`。空的不编造。

有 tool call 时，assistant 消息会把 `reasoning_content` 原样放回去。有的网关下一轮要求把思考轨迹带上，丢掉会 400。

### 3.3 一批工具必须按序跑完

`for tc in tool_calls` 不是并发。原因：

- 后一个工具可能依赖前一个的结果（先读再改）。
- 审批卡片按顺序出，用户才看得懂。
- 取消时要知道哪些 id 已经有了 tool 消息。

每个工具：

1. 若是 `propose_memory`，先把 `memory_gate_seen = True`。重复提案在真正落地前也算「尝试过记忆门」，避免终稿又被未验证警告打一遍。
2. `yield tool_start`。
3. `run_tool_steps` 异步吐事件。内部事件 `_tool_result`、`_gate_meta` 不直接给前端。其余（`diff`、`await_approval`、`shell`）原样 yield。
4. `_gate_meta.kind` 为 patch / shell / memory 时，置上对应的 `*_gate_seen`。这是写盘诚实的账本，不是审批本身。
5. `resolve_gate_outcome` 把工具结果收成四种动作（见 3.4）。
6. 观察瘦身：`_observe_tool` → `observe_tool_result`。SSE 给用户看的可以是全文；放进 `working` 的 `role=tool` 是瘦身后的 `model_payload`。大块 spill 到 `turns/`。

一批之中禁止插入新的 user 消息。检查点和探索收敛的提示，要等每个 `tool_call_id` 都有了 tool 消息，才由 `after_tool_batch` 追加。取消时 `_append_missing_tool_results` 给没跑到的 id 补 `status=cancelled`。门控提前结束则补 `status=skipped`。

### 3.4 门控结果的四种动作

`resolve_gate_outcome`（`agent/loop_exit.py` 一带）把「工具返回了什么」收成：

| 动作 | 环做什么 |
|------|----------|
| `STOP_CANCELLED` | 补齐 tool 消息，`error TURN_CANCELLED`，`STOP` |
| `END_TURN` | 补齐，把说明当 `token` + `done`，`DONE`。用户拒绝且不该再让模型改口时走这里 |
| `CONTINUE_LOOP` | tool 消息进 working，记 `gate_retry_used`，继续本批剩下的工具。拒绝后允许模型再试一次时走这里 |
| 普通完成 | tool 消息进 working，继续本批 |

`gate_retry_used` 保证「拒绝后再试」不会变成无限循环。

### 3.5 没有 tool call 时的诚实

终稿路径上有四道检查，全是字符串层面的，不靠模型自觉：

**工具被网关关掉。** `tools_fallback` 为真。正文空就换成「当前模型不支持工具」；正文像是在声称写过，就追加同一句。模型不能在降级轮假装 `propose_edit` 成功。

**声称写过但本轮没有门。** `_WRITE_CLAIM_RE` 扫正文。命中前 48 个字符里有否定（「不要说已经写入」）则跳过。三个 `*_gate_seen` 都是假，追加 `_UNVERIFIED_WRITE_NOTE`。系统提示里要求「必须调工具」这句话本身含有「写入」字样，所以否定窗口是必须的，否则每轮终稿都会被自己的规则打中。

**输出被截断。** `finish_reason` 是 `length` 或 `max_tokens`，追加截断说明。不把半截当完整答案。

**该改仓库却只说不改。** `working_requests_repo_edit` 看目标和历史像不像「要改文件」。还没见过写门、这轮 nudge 没用过、正文还是空的：往 working 追加一条 user nudge，`yield edit_nudge`，`CONTINUE`。只用一次（`edit_nudge_used`）。下一轮模型若仍然不调工具，就不再 nudge，改走模板回复，避免死循环。

**真的什么都没有。** 没正文、也没跑过工具：`error EMPTY_RESPONSE`，`STOP`。跑过工具但模型最后一轮空：`synthesize_tools_only_reply` 用目标、是否见过写门、是否已经 nudge 过，拼一段不假装成功的收尾。

## 4. 触顶：软着陆

`for` 跑满 `max_tool_iters` 仍是 `CONTINUE`（最后一轮还在调工具），进入软着陆，不再给工具：

1. `yield soft_land`，带上次数、已跑工具数、目标。
2. working 追加 `soft_land_user_prompt`：要求对照目标说进度和没做完的部分，不要假装完成。
3. `chat_complete(..., tools=None)`。
4. 有正文：前面加 `soft_land_banner`（「已提前收口，任务未完成」），`token` + `done`。
5. 没正文但跑过工具：`synthesize_soft_land_reply`。
6. 都没有：`error TOOL_LOOP_LIMIT`。

软着陆自己也有 `turn_start` / `turn_end`，index 等于 `max_tool_iters`。失败在 `finally` 里仍发 `turn_end`，再由外层 `finally` 发 `agent_end`。

## 5. Goal 开着时，环多出来的只有钩子

`goal_mode` 为真时 `with_goal_mode` 装上：

- `on_turn_start` → `apply_goal_start`：把目标注入 working，发 `turn_goal`。目标变了会带 `previous_goal`。
- `after_tool_batch` → `flush_goal_after_batch`：本批工具都落完之后，才增加检查点计数、决定要不要 `progress_checkpoint`、把探索收敛的 user 提示追加进 working。
- 探索计数在单个工具之后只更新数字（`note_exploration_tool`），不在批中间插 user。同一工具连着读（默认阈值 6）才在批末要求收敛。

检查点默认每 4 个工具一次（设置可改）。模型下一轮若先写了一段进度再带工具，这段被 `clip_checkpoint_reply` 收成 `progress_checkpoint.reply`。若模型直接调工具不说话，事件带 `settled: true`，UI 不要停在「等待说明」。

Goal 关着：这些钩子是 `None`。`_run_one_turn` 里 `if config.after_tool_batch` 为假，只累加 `tools_since_checkpoint`（没人读它）。观察瘦身仍然做，那是 F4，和 Goal 无关，装在 `install_base_tool_hooks`。

目标文本从哪来，是窗口的事：`resolve_session_goal` 看 pinned goal，否则从用户句子里抽。抽和变更审计在 routes，不在环中。

## 6. `AgentLoopState` 里每个字段为什么存在

| 字段 | 跨 Turn 保留的原因 |
|------|-------------------|
| `working` | 对话真源（这一次 Trace 内） |
| `turn_goal` | 软着陆和 nudge 要引用；Goal 关着是 None |
| `write_gate_seen` / `shell_gate_seen` / `memory_gate_seen` | 终稿诚实。一旦本 Trace 里出现过门，后面的文字收尾不再被打成「未验证」 |
| `gate_retry_used` | 拒绝后只自动再试一轮 |
| `tools_since_checkpoint` / `pending_checkpoint` | Goal 检查点 |
| `exploration_*` | Goal 探索收敛 |
| `tools_ran` | 空终稿和软着陆要知道有没有工具结果可总结 |
| `edit_nudge_used` | 缺 `propose_edit` 只戳一次 |
| `outcome` | 外层 for 看它决定 return 还是继续 |

## 7. 和 Pi 第 3 章对齐的部分

Pi 把环收成「最简循环 + 一组函数钩子」。我们也是：最简循环在 `_run_one_turn` 的 if tool_calls / else；Goal、Preset、压缩、插队都是钩子。

Pi 用工具上的 `terminate` 也可以停。我们没有这个标志。停只看「这轮没有 tool call」或门控动作 `END_TURN` / `STOP`。

Pi 的 follow-up 外环我们留了字段。不要在没设计「谁有权续命」之前接上，否则用户会看到 Agent 自己说个不停。

## 8. 对着读的文件

- `agent/loop.py`：`run_agent_loop`、`_run_one_turn`、`soft_land_*`、`_looks_like_write_claim`
- `core/turn.py`：`TurnOutcome`、`AgentLoopState`
- `core/loop_config.py`：工厂
- `core/goal_hooks.py`：`apply_goal_start`、`flush_goal_after_batch`
- `core/steering.py`：`drain_steering`
- `agent/loop_exit.py`：`resolve_gate_outcome`、`should_nudge_missing_edit`
- 测试：`tests/test_loop_exit.py`、`tests/test_gate_continue.py`、`tests/test_empty_response.py`

下一章讲 `chat_complete` 背后的 client：为什么两个会话不能共用一个全局网关。

## Related

- 上一篇：[ch02-layers.md](./ch02-layers.md)
- 手册目录：[README](./README.md)
- 下一篇：[ch04-model.md](./ch04-model.md)
- 源码仓库：[masterroland13/loop-agent](https://github.com/masterroland13/loop-agent)
