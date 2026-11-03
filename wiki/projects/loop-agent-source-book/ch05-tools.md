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
  - https://github.com/masterroland13/loop-agent/blob/main/docs/design/loop-agent-book/ch05-tools.md
confidence: 0.75
review_after: 2026-12-03
---

# 第 5 章：工具系统 —— 注册、执行、审批从工具里拆出去

> 本章回答：模型看到的 tools 列表怎么来的；`propose_edit` 为什么不直接写磁盘；YOLO / Trusted / Strict 差在哪一行；读工具和写工具为什么不是同一种返回。

## 1. 注册表

`tools/registry.py` 一个进程级 `registry`。`ToolSpec` 四字段：`name`、`description`、`parameters`（JSON Schema）、`handler`。

`get_openai_tools()` 收成：

```text
{ "type": "function", "function": { "name", "description", "parameters" } }
```

环在 `run_agent_loop` 开头 `import agent_window.tools`。包的 `__init__` 调用各组 `register_*`。没这个 import，列表是空的，模型只能聊天。

设置里的 `disabled_tools` 在交给模型之前滤掉。滤掉的工具不会出现在 schema 里，模型不应该能点名调用。系统提示里的工具名列表来自 `registry.list_names()`，和滤掉之前的全集可能不一致——以环实际传入的 `tools` 为准。提示词若仍提到被禁用的名字，模型可能点名失败，工具管道会返回失败 JSON，而不是静默成功。

## 2. 现在有哪些工具

| 名字 | 文件 | 副作用 | 和审批的关系 |
|------|------|--------|----------------|
| `list_dir` / `read_file` / `grep` | `fs_tools.py` | 只读工作区 | 不进门控。结果直接回 |
| `propose_edit` / `propose_delete` | `edit_tools.py` | 生成补丁，等 Apply 才落盘 | 门控 kind=patch |
| `propose_shell` | `shell_tools.py` | 校验 argv 后等待，再 subprocess | 门控 kind=shell |
| `propose_memory` | `memory_tools.py` | 改 USER.md 或 MEMORY.md | 门控 kind=memory |
| `search_session` | `session_tools.py` | 只读本会话 JSONL / spill | 只读 |
| `read_attachment` | `attachment_tools.py` | 只读本会话附件文本 | 只读。图片不要用它 |
| `ping` / `get_weather` | `builtin.py` | 外部 HTTP | 只读演示 |

读路径一律 `resolve_in_workspace`。相对路径相对工作区根。逃出根是错误，不是「读到了家目录」。

`propose_shell` 的 argv 是字符串数组，不是一条 shell 字符串。`validate_argv` 拒绝管道和重定向。解释器优先用环境里的 Python（`python_for_package` / `resolve_loop_python`），避免工作区里没有 `python` 时模型自己发明绝对路径。

删除文件走 `propose_delete`，不走 `rm`。系统提示把这句话写死了。

## 3. 工具不决定要不要等人

宪章：审批是 Preset，不是工具的人格。handler 可以返回「我准备好了一份补丁」，但「现在就写还是等点击」由 `before_tool_call` 决定。

`core/preset_hooks.py`：

| Preset | `GatePresetDecision` |
|--------|----------------------|
| YOLO | `action=allow`，`auto_apply=True`。写、shell、记忆直接落，审计仍记 |
| Trusted | `action=wait`。写和 shell 等 UI/CLI。记忆还看设置 `confirm_memory` |
| Strict | `action=wait`，且 `force_confirm_memory=True`。记忆也必须确认，忽略 `confirm_memory=False` |

`before_tool_call_preset` 只看 `config.preset`，不看工具名。工具管道再解释：读工具没有 `AWAIT_*` 标记，allow 和 wait 对它都是直接跑 handler。写工具的 handler 创建 `PendingPatch` / `PendingShell` / `PendingMemory`，返回带等待标记的 JSON。管道看到标记，再按 decision：

- `allow`：不等待，直接 apply。
- `wait`：`wait_for_*_decision`，SSE 发 `await_approval`，前端或 `loop approve` / `loop reject` 解开。
- `block`：不执行，把 reason 当失败结果。钩子可以返回 `{action:"block", reason}`。默认 Preset 不 block。

`normalize_gate_decision` 把钩子的各种返回（dataclass、dict、缺字段）收成同一种 `GatePresetDecision`，避免环里写三套 if。

Strict 和 Trusted 的第一处行为差是记忆：Trusted 可以在设置里把记忆改成自动写；Strict 不行。写文件两边都是 wait。YOLO 两边都是 allow。

## 4. 管道在环里的位置

`_run_one_turn` 不调用 handler。它调用 `run_tool_steps(name, raw_args, config, cancel_event)`。

管道的职责：

1. `resolve_gate_decision(config, phase="pre")`。
2. block 则立刻失败结果。
3. 找到 spec，调 handler。
4. 若结果是等待标记且 decision 是 wait：把 diff/shell 卡片事件 yield 出去，然后 await 用户决定。取消事件置位则按拒绝/取消收场。
5. 决定是 apply 还是 reject 之后，yield `_tool_result` 和可能的 `_gate_meta`。

环看到 `_gate_meta` 才把 `write_gate_seen` 等设为真。所以「YOLO 自动 apply」也算见过门。终稿再说「我改了文件」是诚实的。反过来，handler 没走到门（参数错误、路径出界）不算见过门，嘴上说改了仍会挂未验证警告。

用户拒绝时，`resolve_gate_outcome` 可能 `END_TURN`（把拒绝写成这轮的最终回复）或 `CONTINUE_LOOP`（把拒绝作为 tool 结果还给模型，让它改一版再提案）。后者受 `gate_retry_used` 限制，避免无限拒绝-重试。

## 5. 观察瘦身：给模型的和给用户的不是同一份

`observe_tool_result`（`agent/observation.py`）在工具结果进 `working` 之前跑，Goal 关着也跑。

- SSE / trace 保留更全的原文，活动时间线才看得懂。
- `working` 里的 `role=tool` 用短 JSON。超长的全文 spill 到会话 `turns/`，payload 里留 `full_ref`。
- 下一轮模型若要细节，靠引用或 `search_session`，而不是把 8000 行测试日志永远留在上下文里。

这是第 8 章「每次工具调用都裁」的那一层。环只调用 `_observe_tool`，不自己截断字符串。

## 6. 写盘诚实，从工具名开始

系统提示（`_system_prompt`）要求：

- 改文件必须 `propose_edit`，等结果里 `status=applied` 才能说写过。
- 跑命令必须 `propose_shell`。
- 被拒绝后用户说「再试一次」，必须再次调用同一工具，不能改口成纯文字。
- 只有附件、没有明确「保存到工作区」时，默认只读：文本走 `read_attachment` 后口头摘要，图片直接描述。不要发明脚本把附件抠进仓库。
- 用户明确说保存附件，才 `read_attachment`（文本）再 `propose_edit`。

环上的 `_looks_like_write_claim` 是提示词的执法：提示词会被忽略，正则不会。否定句排除是为了不误伤提示词自己。

partial apply（hunk 级勾选）在补丁服务和前端 Diff 面板，不在环里。环只看到最终 tool 结果字符串。

## 7. 记忆工具为什么单独一条

`propose_memory` 的 target 是 `user` 或 `memory`。

- USER.md：跨会话的使用者偏好。
- MEMORY.md：这个工作区/项目的教训。

两者都有字符硬上限（`get_user_md_char_limit` / `get_memory_md_char_limit`）。超限要 replace/remove，不是无限追加。

操作是条目级：add / replace / remove，不是每次整文件覆盖（也支持 mode=replace）。重复条目会在提案阶段失败。

每轮进系统提示的是**冻结快照**（`freeze_*_for_session`），不是「工具刚写完立刻把新文件再注入本轮 system」。本轮内模型通过 tool 结果知道写进去了；下一轮用户消息才会在新的快照里看到。这样压缩对话桶不会和「正在变长的记忆文件」缠在一起。第 8 章细讲。

## 8. Skills 不是工具注册，是目录

`services/skills.py` 扫描工作区 `skills/*/SKILL.md`。系统提示只放 id、名字、一句话描述。正文由模型用 `read_file` 按需拉。这是 Pi 的 progressive disclosure，我们没有单独的 `skill` 工具。

`AGENTS.md` 例外：项目规则全文进系统提示（工作区一份，另有全局候选路径）。它是规则，不是可选技能。

`SYSTEM.md` 若存在，**整段替换**默认系统提示。`APPEND_SYSTEM.md` 追加。记忆块和 Skills 目录仍接在后面。替换默认提示时，工具契约那一大段会消失，除非 `SYSTEM.md` 自己写上。这是给高级用户的杠杆，也是踩坑点。

## 9. 和 Pi 第 5 章的差别

Pi 的核心工具是 read / write / edit / bash，写是真写。审批是约 50 行扩展，默认没有。

我们把写和 bash 收成 propose_*，因为产品要保留 diff、hunk、审计。为了不把审批焊进工具，Preset 才存在。YOLO 时用户体感和 Pi 接近（直接落盘），Trusted/Strict 时才等卡片。

我们没有 TypeBox。参数是手写 JSON Schema。校验失败由 handler 返回错误 JSON，模型下一轮能看见。

我们没有热重载扩展。新工具是改 `tools/` 并重启进程。Skills 的正文是 markdown，改完下一轮 `read_file` 就能读到，不必重启。这是「知识热更新」，不是「工具热更新」。

## 10. 对着读的文件

- `tools/registry.py`、`tools/__init__.py`
- `tools/fs_tools.py`、`edit_tools.py`、`shell_tools.py`、`memory_tools.py`
- `core/preset_hooks.py`：`decide_gate_preset`
- `services/shell.py`：`validate_argv`、`wait_for_shell_decision`
- `services/memory.py`：提案和字符帽
- `services/workspace.py`：`resolve_in_workspace`
- 测试：`tests/test_cli_gates.py`、`tests/test_write_claim.py`、`tests/test_hunk_apply.py`、`tests/test_shell_python.py`

下一章讲这些工具结果和用户句子在进模型之前长什么样：库里的行、树上的路径、dict 三套表示。

## Related

- 上一篇：[ch04-model.md](./ch04-model.md)
- 手册目录：[README](./README.md)
- 下一篇：[ch06-messages.md](./ch06-messages.md)
- 源码仓库：[masterroland13/loop-agent](https://github.com/masterroland13/loop-agent)
