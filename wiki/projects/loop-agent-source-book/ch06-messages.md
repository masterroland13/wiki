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
  - https://github.com/masterroland13/loop-agent/blob/main/docs/design/loop-agent-book/ch06-messages.md
confidence: 0.75
review_after: 2026-12-03
---

# 第 6 章：消息系统 —— 三套表示，一条路径

> 本章回答：SQLite 里的一行、树上的路径、发给模型的 dict，为什么不能是同一个结构。读完再看压缩和分叉才不会把 `sequence` 当成对话顺序。

## 1. 三套表示

| 表示 | 谁持有 | 长什么样 | 谁能看见 |
|------|--------|----------|----------|
| ORM `Message` | SQLite | `role` 只有 user/assistant/system；另有 `parent_id`、`entry_type`、`sequence`、`trace`、`attachments` | 窗口、回放、`view=all` |
| `AgentMessage` | 进程内，进模型前一跳 | `role` 可以是 `compaction_summary` | `messages_to_agent_messages` |
| OpenAI dict | `working` / HTTP body | `user` / `assistant` / `system` / `tool`，assistant 上可带 `tool_calls` | 网关 |

Pi 内部有更丰富的 AgentMessage（thinking、toolCall 分类型）。我们把「思考」放在 assistant dict 的 `reasoning_content` 和 SSE 的 `thought` 上，不给 ORM 加一种 role。ORM 的 role 枚举保持三个值，树才能简单。

`entry_type` 默认 `message`。压缩摘要是 `compaction_summary`。role 仍然是 assistant 或按写入时的 Role 存——真正让模型把它当摘要的，是转成 `AgentMessage` 时看 `entry_type`，不是看 role 字符串。`messages_to_agent_messages`：

```text
entry == compaction_summary → AgentMessage.role = compaction_summary
否则 → role 用 ORM 的 user/assistant/system
```

`default_convert_to_llm` 再把 `compaction_summary` 收成：

```text
{ "role": "user", "content": "【对话压缩摘要】\n" + 正文 }
```

模型没有 `compaction_summary` 这个 role。前缀让它知道这是交接，不是用户刚说的话。未知 role 也收成 user，避免整段被丢掉。

空字符串在 `build_llm_messages` 里丢掉。占位 assistant（刚 `add_message` 时 content 是空）不会进历史。当前这条空占位的 parent 是本轮 user，但它自己还没内容，`prior_path` 在插入它之前就取好了，所以历史路径里本来就没有它。

## 2. 树：认父不认子

`Session.leaf_id` 指向当前尖端。`Message.parent_id` 指向父。

`walk_to_root`：从叶子沿 `parent_id` 走到没有父，用 `seen` 防环，再 reverse，得到根到叶。

`build_path_from_session`：

1. 用传入的 leaf，否则 `session.leaf_id`。
2. 叶子不在字典里，退到 `sequence` 最大的那条（`_fallback_leaf_id`）。
3. 走 `walk_to_root`。

兄弟节点都在库里。`view=all` 列出全部行，给回放和调试。`view=active` 只走叶子路径，这才是下一轮模型该看见的。

`sequence` 只表示插入顺序，用来分配新行的序号、在 leaf 损坏时找一条「最新」。它不是对话顺序。分叉之后，sequence 更大的消息可能在被放弃的枝上。

## 3. 一次发送怎么挂到树上

`send_message_endpoint`：

```text
prior_path = build_path_from_session(session)   # 还不包含本轮
parent_for_user = session.leaf_id
user = add_message(..., parent_id=parent_for_user)
assistant = add_message(..., content="", parent_id=user.id)  # 占位
```

`add_message` 会把 `leaf_id` 移到新行。所以占位 assistant 一插入，叶子就是它。生成过程中前端已经能拿着这个 id 往 trace 上贴事件。结束时更新这行的 content 和 trace，而不是再 insert 一条 assistant。

regenerate 不插新的 user。它在同一条 user 下再挂一条 assistant 兄弟，把叶子指到新兄弟。旧 assistant 还在，`view=all` 能看见。这就是「同一句用户话，两条回答」。

回退（把叶子移到更早的节点）不删行。下一轮 `build_path` 走新叶子，被放弃的枝不进模型。被放弃的枝也不会自动摘要（C7 没做）。全文仍在 JSONL 里。

## 4. 从路径到 `chat_messages`

```text
chat_messages = build_llm_messages(
    prior_path,
    convert_to_llm=loop_cfg.convert_to_llm,
    system_prompt=_system_prompt(session_id),
)
chat_messages.append(build_user_chat_message(...))  # 本轮，可能是多模态
```

`build_llm_messages` 的顺序：

1. 路径上的行 → `AgentMessage` 列表。
2. `convert_to_llm`（缺省 `default_convert_to_llm`）。
3. 丢掉 content 为空的。
4. 若有 system_prompt，插到最前。

本轮 user 不走 `prior_path`，是因为插库时的 content 是 `build_content_for_model`（给纯文本模型的扁平字符串，附件变成文末说明），而发给视觉模型的是 `build_user_chat_message`（图片是 image_url）。两条都要留：库里的是可回放文本，请求里的是这一轮模型真正要看的。

历史里的 user 已经是当初入库的字符串。旧轮的图片不会在下一轮再次变成多模态像素，除非当初把 data URL 写进了 content。当前实现是像素只在当轮请求里注入。这是有意的：避免每一轮都重传大图。

## 5. 环内的 `working` 比树更肥

树上没有 `role=tool`，也没有带 `tool_calls` 的 assistant。那些只活在这一次 Trace 的 `working` 里。

原因：工具回合可能很多，如果每条 tool 都 insert 进 SQLite 的消息树，叶子路径会变成几十个节点，压缩切点、regenerate、回放都会变复杂。我们把一轮用户回合收成一对：一条 user、一条 assistant。工具过程进 assistant 的 `trace` JSON，以及 `transcript.jsonl` 的追加事件。

后果：环中间 `transform_context` 压的是 `working`（含 tool），上树时不能拿 working 的下标去改 `parent_id`。`persist_compaction_from_tree` 在**当前树的叶子路径**上重算切点，摘要正文仍用刚压出来的那份。这是 C3 审查修过的坑。第 9 章会再走一遍。

`working` 里中途插入的 steering、nudge、软着陆 user、Goal 检查点提示，同样不逐条上树。它们影响这一次 Trace 的模型，不成为可回放的用户气泡。用户真正打的字才是树上的 user。

## 6. trace 不是消息

`Message.trace` 是 JSON 文本，默认 `[]`。`TurnTraceWriter` 在生成过程中把 `tool_start`、`thought`、`diff` 等写进去。前端 `turnTrace.ts` 用它画活动线，不把它拼回 prompt。

`is_turn_in_progress`：有工具 trace 但没有正文也没有收尾，才算还在跑。历史会话若误判成 in progress，计时会用「现在 − 开始时间」，出现上千小时。收尾条件是有正文或收尾事件。没有 `elapsed_ms` 时用 trace 起止间隔，不用墙上时钟。

## 7. 收藏、标题、时间

- `is_favorite` 在消息上。收藏列表不改变叶子。
- `title_locked`：用户改过标题之后，自动标题不能覆盖。
- `last_prompt_at`：侧栏时钟只跟用户指令走，不跟 assistant 更新走。

这些是窗口字段。环不读它们。

## 8. 和 Pi 第 6 章的差别

Pi 的消息类型更细，`convertToLlm` 是明确的翻译边界。我们也有这道边界，但更窄：只特殊处理 `compaction_summary`，其余 role 透传。tool 消息不经过 `AgentMessage`，因为它们不进 ORM。

Pi 把整段会话（含工具）放进同一个树文件。我们把「用户看得见的气泡」放进树，把「模型这一轮用过的工具草稿」放进 working + trace + JSONL。回放工具过程靠 trace 和 JSONL，不靠把 tool role 塞进 `Role` 枚举。

## 9. 对着读的文件

- `models.py`：`Session`、`Message`、`init_db` 里的 parent/leaf/entry_type 迁移
- `core/messages.py`：`AgentMessage`、`default_convert_to_llm`、`COMPACTION_SUMMARY_MARKER`
- `core/session_tree.py`：`build_path_from_session`、`build_llm_messages`
- `services/storage.py`：`add_message`、`set_session_leaf`
- `api/routes.py`：`send_message_endpoint` 前半、`get_messages_endpoint`、`regenerate_endpoint`
- 测试：`tests/test_session_transcript.py`、`tests/test_turn_goal.py`

下一章讲这些消息变化时，前端是靠哪几种事件知道的。

## Related

- 上一篇：[ch05-tools.md](./ch05-tools.md)
- 手册目录：[README](./README.md)
- 下一篇：[ch07-events.md](./ch07-events.md)
- 源码仓库：[masterroland13/loop-agent](https://github.com/masterroland13/loop-agent)
