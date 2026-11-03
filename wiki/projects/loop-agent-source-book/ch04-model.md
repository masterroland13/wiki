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
  - https://github.com/masterroland13/loop-agent/blob/main/docs/design/loop-agent-book/ch04-model.md
confidence: 0.75
review_after: 2026-12-03
---

# 第 4 章：模型调用 —— 一套客户端，按会话选网关

> 本章讲 loop-ai：档案存在哪、一次 Turn 怎么选 client、流式结果怎么收成环能吃的 dict、网关抽风时用户看到什么。不讲压缩，那是第 9 章。

## 1. 我们没有 Pi 那种 30 家适配器

Pi 的 `pi-ai` 为 Anthropic、OpenAI、Google、Bedrock 各写一套请求。Loop Agent 只做 **OpenAI Chat Completions 兼容**：

```text
openai.AsyncOpenAI(api_key=..., base_url=...)
client.chat.completions.create(...)
```

Kimi、DeepSeek、百炼、OpenRouter、自建网关，只要路径兼容，就建一条档案，不写新的 provider 类。LiteLLM 也只是「某条档案的 base_url 指向 LiteLLM」，不是架构前提。

代价是：不兼容的字段（思考轨迹的名字、工具 schema 的挑剔、视觉内容的格式）要在 `LLMProvider` 里做归一，而不是假设每家都和官方 OpenAI 一样。

## 2. 档案，不是进程级单例

早期实现是一个全局 `LLM_API_KEY` / `LLM_BASE_URL` / `LLM_MODEL`。两个会话一切换模型，另一个会话的下一轮就会打到错误网关。

现在的真源是 Model Registry（`services/model_registry.py`）：

- 用户数据目录里一份 JSON。
- 每条档案有 `id`、显示名、`base_url`、`api_key`、`model_id`、是否启用。
- 全局还有温度、`max_tokens`。
- 设置里可以从预置开卡（`provider_presets.py`：Moonshot、DeepSeek、OpenRouter 等）。预置只填地址和模型名，密钥用户自己贴。

会话表上有 `profile_id` 和 `model_id`（`models.py` 的 `Session`）。新会话抄当前激活档案。顶栏改模型，写的是**这一条会话**，不是全局。

`LLMProvider` 里有两套 client，用途不同：

| 方法 | 用途 | 会不会改全局 |
|------|------|----------------|
| `_sync_client` | 设置页测试、拉模型列表 | 会把「当前激活档案」同步到 `self.client` |
| `_client_for_profile(profile_id)` | 真正的一轮对话 | 不会。缓存是 `profile_id -> (url, key, client)` |
| `profile_is_ready` | 发送前检查 | 只看这条档案有没有 url 和 key |
| `is_available` | 旧的「进程有没有配模型」 | 只看激活档案 |

`send_message_endpoint` 在开 SSE 之前调用 `_bind_turn_model`，得到这一轮的 `model` 和 `profile_id`。producer 里 `turn_profile_id.set(...)`，让 `chat_complete` 在异步调用栈上拿到档案，而不把档案 id 塞进每一个函数参数。两个并行会话各 set 各的 contextvar，client 缓存在字典里，不会互相覆盖。

发送前若 `profile_is_ready` 为假，直接 503，不进环。

## 3. 一轮里 model 字符串还可能被附件改写

`_bind_turn_model` 得到会话绑定的模型名之后，还有 `resolve_model_for_attachments`：

- 纯文本：用绑定的模型。
- 图片：若当前模型不能看图，且设置里有 `vision_model`，改用视觉模型。
- 需要视觉但没有视觉模型：`AttachmentError` code `VISION_MODEL_REQUIRED`，HTTP 400，不编造「我看到了图片」。

图片像素在 `build_user_chat_message` 里变成多模态 content。系统提示明确说：图片不要再调 `read_attachment`。文本附件才用 `read_attachment`。PDF 不自动抽文本。

## 4. `chat_complete` 对环的契约

环不碰 SDK 对象。`provider.chat_complete(working, tools, model)` 返回普通 dict（第 3 章列过的键）。

实现上大致是：

1. 用 contextvar 里的 profile 拿 client。没有 key 就抛，由环收成 `LLM_PROVIDER_ERROR`。
2. 温度和 max_tokens 用档案全局，不写死在环里。
3. `tools` 为空或 `None`（软着陆）时不传 tools 字段。
4. 流式聚合：正文增量、工具参数增量拼成完整 `tool_calls`。思考增量若网关放在 `reasoning_content` 或兼容字段，收成 `reasoning_content`，并记耗时。
5. 网关对 tools schema 直接 400：重试一次不带 tools，返回 `tools_fallback=True`。环发 `tools_disabled`，并禁止这轮声称写文件成功。

`humanize_provider_error` 把常见英文错误收成中文短句。上下文超限会变成「对话上下文超出模型限制。请新开一个会话重试。」压缩钩子本应在超限前动手；这句是最后的网关错误，不是压缩本身。

## 5. 思考轨迹为什么要回放

部分兼容网关（尤其带 reasoning 的模型）要求：assistant 消息如果产生过 `reasoning_content`，下一轮必须原样带上，否则拒绝请求。

所以 `_run_one_turn` 在追加带 tool_calls 的 assistant 时：

```text
if reasoning:
    assistant_msg["reasoning_content"] = reasoning
```

前端另收一条 `thought` 事件（phase=end，带 text 和 duration_ms）。空 reasoning 不发。UI 不编造「正在思考」。

`thought` 进 trace，供活动时间线使用。它不是一种新的 `AgentMessage` role。进模型的仍是 assistant 上的字段。

## 6. 错误时用户看到的代码

环把供应商异常收成 SSE：

| code | 何时 |
|------|------|
| `LLM_PROVIDER_ERROR` | `chat_complete` 抛了 |
| `TURN_CANCELLED` | `cancel_event` 在等待模型或工具时被置位 |
| `EMPTY_RESPONSE` | 没工具、没正文 |
| `TOOL_LOOP_LIMIT` | 软着陆也拿不到可展示的文字 |

`race_with_cancel` 包住 `chat_complete` 和软着陆那一次调用。取消不是杀掉线程，而是竞态：事件先到就抛 `TurnCancelled`。工具执行中的取消同样看这个 event（第 5 章）。

窗口侧同一会话已有回合会 409 `SESSION_BUSY`（`try_begin_turn`）。这不是模型错误。SSE 生产结束的 `finally` 里 `end_turn`，把忙标志清掉。浏览器断开时 `_sse_detach_producer` 让生成继续跑完落库，避免「用户关了标签，占位 assistant 永远是空的、会话永远忙」。

## 7. 密钥放哪

档案 JSON 在用户数据目录，不进工作区，不进 git。开发用的 `backend/.env` 只给本机狗粮。桌面进程保存模型时不把密钥写回仓库 `.env`。

检索 `search_session` 不扫 `.env`。JSONL 追加前 `redact_value` 打码密钥字段。这些是第 8、第 10 章的事，但模型层要知道：密钥不是 prompt 的一部分，也不是工具结果的一部分。

## 8. 和 Pi 第 4 章的差别

| Pi | Loop Agent |
|----|------------|
| 每家一个 stream 适配器 | 只认 Chat Completions |
| `models.json` 在 `~/.pi/agent` | Registry 在用户数据目录，会话上挂 `profile_id` |
| 会话中途 `/model` 切换，底层做有损交接 | 顶栏改的是这条会话的档案；不在一条 working 列表中途换协议 |
| 浏览器也能跑 pi-ai | 调用只在后端。前端拿不到 key |

我们不做跨供应商的思考签名回放。只回放本网关返回的 `reasoning_content`。换档案等于下一轮用新 client，历史文本还在，思考字段能否被新网关接受不保证。所以产品上切换模型是「这条会话以后用新档案」，不是「同一条请求里热切换」。

## 9. 对着读的文件

- `services/provider.py`：`LLMProvider`、`humanize_provider_error`、`turn_profile_id`
- `services/model_registry.py`：`resolve_credentials`、`resolve_active_handle`
- `services/provider_presets.py`：预置列表
- `api/routes.py`：`_bind_turn_model`、`test_model_profile_endpoint`
- `services/attachments.py`：`resolve_model_for_attachments`、`build_user_chat_message`
- 测试：`tests/test_llm_config.py`、`tests/test_session_model_binding.py`、`tests/test_attachments_vision.py`

下一章讲这些 `tools` 数组里的函数从哪注册、执行时谁决定要不要等用户点 Apply。

## Related

- 上一篇：[ch03-agent-loop.md](./ch03-agent-loop.md)
- 手册目录：[README](./README.md)
- 下一篇：[ch05-tools.md](./ch05-tools.md)
- 源码仓库：[masterroland13/loop-agent](https://github.com/masterroland13/loop-agent)
