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
  - https://github.com/masterroland13/loop-agent/blob/main/docs/design/loop-agent-book/ch08-context.md
confidence: 0.75
review_after: 2026-12-03
---

# 第 8 章：上下文工程 —— 窗口有限，信息源很多

> 本章讲「进模型之前有哪些层在裁、在组织」。六节摘要和上树是第 9 章。这里先把每一层解决的问题分开，避免把所有省 token 的事都叫成压缩。

## 1. 一次请求里有哪些信息源

`send_message_endpoint` 拼出来的 `chat_messages`，加上环内继续追加的 tool，来源是：

```text
系统提示 _system_prompt
├── 默认契约，或工作区 SYSTEM.md 整段替换
├── APPEND_SYSTEM.md
├── 冻结的 MEMORY.md / USER.md（有字符帽）
└── AGENTS.md 全文 + Skills 目录（不是正文）
历史路径（叶子到根，摘要已经变成带标记的 user）
本轮 user（文本，或文本+图片）
环内追加
├── steering / Goal 注入 / nudge / 软着陆提示
├── assistant + tool_calls
└── role=tool 的瘦身结果
```

随便一项都能撑爆窗口：`grep` 命中几百行、`read_file` 整文件、测试日志、多轮工具。网关超限是硬错误。上下文工程是在这之前分层处理。

## 2. 总图

```text
每次工具返回
  观察瘦身 + spill          services/observation、tool_hooks
每轮拼系统提示
  工作区契约、记忆快照、Skills 目录、AGENTS.md
进模型前（每 Turn）
  transform_context
    ├── 未超限：原样
    └── 超限且 auto_compress 或 force：第 9 章的压缩
模型觉得摘要丢了细节
  search_session            只拉短摘录，不把 JSONL 整份塞回
```

| 层 | 触发 | 默认开吗 |
|----|------|----------|
| 观察瘦身 | 每个工具结果 | 开 |
| 系统提示分桶 | 每次发送 | 开 |
| 自动压缩 | 估算 token 超过 `context_limit - reserve` | **关**（`auto_compress` 默认 false） |
| 手动压缩 | 菜单或 `POST .../compact` | 用户触发 |
| 检索 | 模型调用 `search_session` | 工具在，模型自己决定 |

自动压缩默认关，是因为摘要会丢细节。产品先把全文留在 JSONL，让用户看见占用条，再手动压。开了自动压，算法和第 9 章一样。

占用条：`GET /api/sessions/{id}/context`。估算是字符数除以 4，不是网关账单。超了只是提示，不单独构成压缩。

## 3. 系统提示里什么是耐久的，什么不是

`_system_prompt` 把耐久上下文放在 system，不放进会被折掉的对话桶：

**工作区契约。** 有根：告诉模型根路径、必须用 propose_*、路径相对根。无根：不要编文件内容。

**记忆。** `session_id` 存在时读冻结快照（`get_frozen_user_md` / `get_frozen_memory_md`），标题写 `frozen this session`。没有 session 时读活文件。超过字符帽的部分截断，并写明要用 `propose_memory` 去删。记忆不进压缩的「被摘要对话」。下一轮系统提示仍带同一份快照，直到会话重新冻结。

**AGENTS.md。** 全文。这是项目规则，和 Pi 把多层 CLAUDE.md 拼进系统提示是同一类决定：规则稳定，值得占 token。

**Skills。** 只有目录行：`id: name — description`。正文让模型 `read_file`。避免十个技能的全文每轮都付税。

**检索提示。** 固定一句：摘要里缺路径或原话时调 `search_session`，不要猜，不要把整份日志倒回来。

`SYSTEM.md` 替换的是默认契约那一段。记忆和 Skills 仍接在返回值末尾。替换之后若没写 propose_edit 规则，模型更容易嘴上说改完。环上的未验证警告还在，但体验会变差。

## 4. 观察瘦身（输入侧，每次工具）

`observe_for_working` → `observe_tool_result`。

给模型的 payload 要短、可执行：状态、路径、错误码、diff 统计。全文测试输出、大文件内容写到 `turns/`，payload 留引用。SSE 仍可带更全的文本，用户在活动线里能看见。

spill 回调通过 `LoopConfig.extra["observe_spill"]` 注入（`with_observe_spill`）。core 不自己拼数据目录。

这一层 Goal 关着也做。它解决的是「单次工具结果」，不是「十轮对话加起来太长」。

## 5. 工具定义本身也占窗口

`get_openai_tools()` 的 description 和 parameters 每一轮都发。所以工具说明要短，契约的长文放系统提示一处，不要两处各写一遍还互相矛盾。

`disabled_tools` 直接不发给模型，是最干净的裁剪。

## 6. 附件不进历史像素

当轮图片在 `build_user_chat_message` 里。历史回放用的是入库的文本说明。下一轮不会自动重传图片。模型要再看图，用户得再附一次，或当轮已经描述过。

文本附件不把文件全文拼进 user。系统提示要求 `read_attachment`。这样大 PDF/文本的体积受工具瘦身控制，而不是塞进不可裁的 user 气泡。PDF 明确不抽：不要让模型写脚本假装抽出了正文。

## 7. `transform_context` 在这一章的位置

`install_context_transform` 把 `auto_compress`、`context_limit`、摘要函数、`on_compressed` 绑进钩子。`apply_transform_context` 每 Turn 调一次。

钩子返回 `(messages, compressed, meta)`。环只把 messages 放回 `state.working`。`compressed is True` 时，窗口的 `on_compressed` 负责上树（第 9 章）。环不写库。

`preserve_goal` 传进压缩，是为了摘要的 Goal 节不要把系统提示里的目标复读一遍（回声）。Goal 关着时 `preserve_goal` 为空，不注入目标块。

手动 `POST .../compact` 走同一套 `compress_messages_if_needed(..., force=True, focus=...)`，不是另一套摘要器。

## 8. 检索是压缩的退路，不是第二份上下文

`search_session`（`services/session_search.py`）：

- 只在本会话根下找 `transcript.jsonl` 和 spill。
- 根必须在用户数据目录内。
- 不搜其它会话、不搜工作区源码、不搜 `*.env`、不把 SQLite 当 JSONL 后备。
- 命中是短摘录，有条数帽和总字数帽。返回里带 name/path，方便模型引用。
- 坏的 `max_hits` 直接拒绝。

模型把它当工具。结果进 working 时同样走观察瘦身。所以「找回细节」也不会一次灌回 50KB。

## 9. 和 Pi 第 8 章的四层对照

| Pi | Loop Agent |
|----|------------|
| 工具输出 truncateHead/Tail | 观察瘦身 + spill |
| 系统提示组装 + Skills 懒加载 | `_system_prompt` + catalog |
| Compaction | 第 9 章，且默认不自动 |
| 切换分支时摘要被放弃的枝 | **没做**（C7） |

我们多了一层 Pi 默认没有的：耐久记忆和对话分桶。USER.md 不参与「被折进六节」的那一刀，避免用户偏好在压缩时丢掉或被摘要改写。

## 10. 对着读的文件

- `api/routes.py`：`_system_prompt`
- `services/skills.py`：`skill_context_blocks`
- `services/memory.py`：`freeze_user_md_for_session`、字符帽
- `core/tool_hooks.py`、`agent/observation.py`
- `services/context_transform.py`
- `services/session_search.py`
- 测试：`tests/test_system_prompt.py`、`tests/test_context_transform.py`、`tests/test_session_search.py`

下一章只讲超限之后那一刀：切在哪、六节怎么来、怎么挂回树上。

## Related

- 上一篇：[ch07-events.md](./ch07-events.md)
- 手册目录：[README](./README.md)
- 下一篇：[ch09-compaction.md](./ch09-compaction.md)
- 源码仓库：[masterroland13/loop-agent](https://github.com/masterroland13/loop-agent)
