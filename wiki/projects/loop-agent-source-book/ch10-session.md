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
  - https://github.com/masterroland13/loop-agent/blob/main/docs/design/loop-agent-book/ch10-session.md
confidence: 0.75
review_after: 2026-12-03
---

# 第 10 章：会话管理 —— 存、恢复、分叉、落盘

> 本章把第 6 章的树放回「一次会话的一生」。读完你应该能回答：刷新页面之后模型还能看见什么，删不掉的是哪一份文件，regenerate 为什么不是覆盖。

## 1. 会话是什么

`models.Session` 一行：

| 字段 | 作用 |
|------|------|
| `id` | UUID |
| `user_id` | 现在基本是默认用户 |
| `title` / `title_locked` | 侧栏标题。锁定后自动起的标题不能覆盖 |
| `data_path` | 这个会话在用户数据目录下的文件夹 |
| `workspace_root` | 当时绑定的工作区。工具实际用的是进程级当前工作区；这个字段记下会话创建/更新时的根，避免列表里失去上下文 |
| `goal_mode` / `pinned_goal` | Goal 开关和固定目标。固定目标覆盖自动抽取 |
| `leaf_id` | 当前路径的尖端 |
| `profile_id` / `model_id` | 这条会话用哪条模型档案 |
| `last_prompt_at` | 侧栏时钟，只随用户指令更新 |
| `messages` | 一对多，删会话级联删消息 |

库文件是用户数据目录里的 `agent_window.db`。`init_db` 用 `create_all` 再补列（trace、attachments、parent_id、leaf_id、goal、模型绑定等）。老库靠这些 `_migrate_*` 升级，不要求用户删库。

## 2. 创建

`create_session`（`services/storage.py`）：

- 生成 id 和 `data_path`（文件名做了 sanitize）。
- 标题可以先是占位，首条用户消息之后再自动起标题，除非 `title_locked`。
- 新会话的 `profile_id` / `model_id` 抄当前激活档案。之后顶栏修改只写这一行。
- `goal_mode` 默认假。

首次没有工作区时，桌面向导不创建「空聊再让工具去猜路径」。先模型，再文件夹，绑定成功才进主界面。开发进程如果 `.env` 已经指向一份有工作区的 `backend/data`，不会走这步向导。

## 3. 恢复

打开一条旧会话：

1. `GET /api/sessions/{id}` 元数据。
2. `GET .../messages?view=active` 或 `all`。active 用 `build_path_from_session`。all 按时间列出全部行，包括兄弟枝和被折掉、但 parent 已经不在叶子链上的旧消息。
3. `GET .../context` 给占用百分比。
4. 前端把 assistant 的 `trace` 画成活动线。不重新请求模型。

刷新不重跑环。占位 assistant 若进程死在 finalize 之前，可能留下空 content。JSONL 在中断路径会补 assistant；进程被 kill -9 时可能少最后一条。这是已知边界。

`leaf_id` 丢了或指向已删 id：`_fallback_leaf_id` 用 sequence 最大的一条。这是恢复，不是「最新的用户意图」。若最大 sequence 在一条被放弃的枝上，恢复结果可能和用户记得的叶子不一致。所以删消息和移动叶子必须成对写，单改 sequence 是错的。

## 4. 发送时叶子怎么移动

第 6 章写过插入顺序。这里从会话生命周期再看一次：

```text
旧 leaf = A
用户发送
  user.parent = A
  assistant 占位.parent = user
  leaf = 占位
生成结束
  更新占位的 content / trace
  leaf 仍是这条 assistant
```

下一轮用户消息的 parent 就是这条 assistant。链是 user → assistant → user → assistant。工具不在链上。

同一会话 `try_begin_turn` 失败则 409。不要两路 SSE 同时移动叶子。

## 5. 分叉：regenerate 和回退

**regenerate**（`regenerate_endpoint`）：不插入新 user。找到当前路径上的最后一条 user，新建一条 assistant，`parent_id` 指向它，`leaf_id` 指向新 assistant。旧 assistant 变成兄弟。

```text
        user
       /    \
  old asst   new asst   ← leaf
```

两条回答都在 `view=all`。模型下一次只看见 new。要回到 old，把 leaf 指回 old asst。不删 new。

**回退 / 从中间改问**（若 UI 提供）：新的 user 挂在选中节点上，leaf 跟着新枝走。旧枝留着。我们没有 Pi 的 `/tree` 全套 UI，数据模型已经是树。切支界面仍是产品缺口，不要用「删掉后面所有消息」假装回退。删了就没有兄弟可回。

被放弃的枝不会自动做五节摘要（C7）。它们占数据库，不占下一轮 token。

## 6. 磁盘上的四份东西

| 位置 | 内容 | 谁写 | 卸载是否删除 |
|------|------|------|----------------|
| `agent_window.db` | 会话和气泡、审计 | SQLAlchemy | 否 |
| `{data_path}/transcript.jsonl` | 全文追加 | `session_transcript` | 否 |
| `{data_path}/turns/` | 大工具结果 | spill | 否 |
| 工作区文件 | 用户项目。propose_edit apply 之后才变 | 补丁服务 | 否 |

`loop uninstall` 只删 `~/.local/lib/loop-agent` 和入口、桌面项。

JSONL 一行一个事件。user/assistant 消息、SSE 里值得留的工具与门控、成功的 compact。只追加。读的时候坏行跳过。

附件文件在会话目录，库里的 `attachments` 列是 JSON（id、文件名、类型）。JSONL 只记 id 和文件名，不把文件字节再写一遍。下载走 `download_attachment_endpoint`。

## 7. 删除

`delete_session` 删库行（消息级联）并清理会话目录。不删工作区，不删 USER.md（那是跨会话的）。MEMORY.md 也是用户数据级，不是某个会话私有。删一条聊天不应该忘掉「这个用户偏好中文」。

取消进行中的回合要先停环再删，否则 SSE 的 finalize 会写到已经删掉的 id。

## 8. 和模型档案、Goal 的绑定

切换顶栏模型：更新这条 session 的 `profile_id` 和 `model_id`。下一次 `chat_complete` 用 `_client_for_profile`。已经在飞的那一轮用的是开始时 set 的 contextvar，不会半路换 client。

Goal 开关：`update_session_goal_mode`。下一轮 `LoopConfig.from_settings` 才装上或卸下钩子。已经在飞的那一轮用的是开始时的 config，不会半路把检查点打开。

固定目标：`pinned_goal`。`resolve_session_goal` 优先用它，空则从用户句子抽取。变更打 `goal.change` 审计。

## 9. CLI 和窗口看的是同一份会话

`loop ask`、`loop status`、`loop approve`、`loop reject` 走 HTTP 客户端打到正在跑的后端，不是另开一份 SQLite。审批卡片因此在窗口和终端都能解。

`loop shell` 的后端数据目录是 `~/.local/share/loop-agent`。开发用的 `backend/data` 是另一份库。两边的会话列表不会混。排查「我的聊天不见了」时先看连的是 8000 还是 8765。

## 10. 和 Pi 第 10 章的差别

| Pi | Loop Agent |
|----|------------|
| 会话是一个 JSON/JSONL 树文件 | SQLite 树 + 旁边一份 JSONL 全文 |
| `/tree` 在 TUI 里跳节点 | 数据有 leaf；切支 UI 不完整 |
| 分支切换可触发分支摘要 | 未做 |
| 换模型走 pi-ai 的有损交接 | 换的是会话档案，下一轮新 client |

我们把「气泡」和「全文」拆开，是因为工具草稿太吵，不适合每条都当气泡，但压缩后又必须能找回。树负责产品上的分叉；JSONL 负责不丢。

## 11. 对着读的文件

- `models.py`：`Session`、`Message`、`init_db`
- `services/storage.py`：`create_session`、`add_message`、`set_session_leaf`、`delete_session`
- `core/session_tree.py`
- `services/session_transcript.py`、`services/session_search.py`
- `api/routes.py`：`create_session_endpoint`、`get_messages_endpoint`、`regenerate_endpoint`、`delete_session_endpoint`
- `cli/main.py`：`ask` / `approve` / `shell`
- 测试：`tests/test_checkpoint.py`（树与叶子相关的一并在 session 测试里）、`tests/test_session_model_binding.py`、`tests/test_compaction_persist.py`

## 12. 十章之后如果要改代码

按这个顺序动手，不容易把层焊回去：

1. 行为先写成失败的 pytest（断言事件或 HTTP 里有没有某段文字）。
2. 策略放进钩子；机制才动 `loop.py`。
3. 动了树或压缩，同时看 JSONL 是否只在成功后追加。
4. `CHANGELOG.md` 的 `[Unreleased]` 写为什么。
5. 动了 Goal、Preset、压缩漏斗或分层，再改 `docs/foundation-status.md`。宪章级的取舍才改 `docs/architecture-charter.md`。

短速查仍是 `docs/design/loop-agent-manual.md`。这两套冲突时，以宪章和测试为准，再回来改手册。

## Related

- 上一篇：[ch09-compaction.md](./ch09-compaction.md)
- 手册目录：[README](./README.md)
- 源码仓库：[masterroland13/loop-agent](https://github.com/masterroland13/loop-agent)
