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
  - https://github.com/masterroland13/loop-agent/blob/main/docs/design/loop-agent-book/ch01-overview.md
confidence: 0.75
review_after: 2026-12-03
---

# 第 1 章：开篇 —— Loop Agent 是什么，为什么按源码读

> 本章不钻进某一个函数。读完你应该能说出：产品要解决什么、默认行为是什么、哪些能力是模式而不是脊柱、后面九章各自落在哪一层。

## 1. 一句话

Loop Agent 是一台跑在你自己机器上的编码 Agent 外壳：窗口（React）+ 本地后端（FastAPI）+ 一条薄的 Agent 环。模型通过 OpenAI 兼容接口调用。改文件、跑命令、写记忆都走工具，默认在你选中的工作区里做，不把仓库安装树当沙箱。

宪章里的原话是：

> Loop Agent = 可拆分的编码 Agent 外壳（Window + CLI）+ 薄而稳的 Agent 环 + 可选 Goal 模式 + Hermes 式可进化记忆。

拆开这四块，后面每一章都有落点：

| 块 | 用户看到的 | 源码主落点 | 哪一章 |
|----|------------|------------|--------|
| 外壳 | 聊天窗、设置、CLI `loop`、桌面 `loop shell` | `src/`、`api/routes.py`、`cli/` | 2、7、10 |
| 薄环 | 模型说话、调工具、再说话，直到不再调工具 | `agent/loop.py` + `LoopConfig` | 3 |
| Goal | 输入框旁的 Goal 开关，亮了才死抱目标 | `core/goal_hooks.py` | 3、8 |
| 记忆 | USER.md / MEMORY.md，有字数帽，每轮用冻结快照 | `services/memory.py` | 5、8 |

## 2. 它不是什么

读源码时最容易走偏的是把「我们做过的功能」当成「环的定义」。下面几件事都在仓库里，但都不是脊柱：

**不是强审批产品。** 审批还在，Preset 有三档：YOLO、Trusted、Strict。默认是 YOLO：本地可信工作区直接执行，仍然记审计。Trusted 写操作要人点，读自动放行。Strict 全部门控，并且记忆也强制确认。策略挂在 `LoopConfig.before_tool_call`，不写进 `propose_edit` 函数体里。产品首页不再把「弹窗」当差异化。

**不是默认 Goal 产品。** Goal 按钮不亮时，环就是最简循环：观察瘦身、写盘诚实（模型嘴上说写了但本轮没有 gate 事件，就挂未验证警告）。不注入 Turn Goal，不跑检查点，不跑探索收敛。亮了才装上 `install_goal_hooks`。`loop.py` 里不允许散落 `if goal_mode`。

**不是又一个聊天网页。** 会话不是按 `sequence` 排成一条直线塞给模型。每条消息有 `parent_id`，会话有 `leaf_id`。当前要送给模型的历史，是从叶子走到根再反过来的那条路径。回退和 regenerate 是移动叶子，旧枝留着。这是第 6 章和第 10 章的主题。

**不是 Pi 的逐行移植。** Pi 是终端里的四个 TypeScript 包，默认 YOLO、极短系统提示、四个核心工具。我们向它学分层、会话树、`transformContext`、压缩上树。我们比它厚：diff / hunk、附件、Skills、审计、窗口、CLI。厚的部分必须挂在 coding 和 window，不能把 `loop.py` 焊成第二个 `routes.py`。

## 3. 一次发送，先建立地图

用户在输入框按发送之后，后端 `send_message_endpoint`（`api/routes.py`）做的事可以压成这条链。后面几章都是把其中一段拆开。

```text
1. try_begin_turn          同一会话不能两轮并行（409 SESSION_BUSY）
2. build_path_from_session  取当前 leaf 到根的路径，作为「这一轮之前」的历史
3. add_message USER         parent = 旧 leaf
4. add_message ASSISTANT    先插一条空占位，parent = 这条 user；trace 先是 []
5. _system_prompt           工作区提示 + 冻结记忆 + Skills 目录 + AGENTS.md
6. LoopConfig.from_settings goal_mode 来自会话，preset 来自设置
7. build_llm_messages       路径 → AgentMessage → OpenAI dict，再前置 system
8. 本轮 user 再 append       图片会变成多模态 content，不走纯文本
9. 解析 Turn Goal           Goal OFF 时目标是空的
10. install transform       压缩钩子绑上；超限才压，默认 auto_compress 关
11. SSE                     run_agent_loop 吐事件；前端按事件画气泡和工具卡
12. finalize                占位 assistant 写上正文和 trace；JSONL 只追加
```

环自己不知道 HTTP，也不知道 SQLite。它收到的是已经拼好的 `messages` 和一个 `LoopConfig`。窗口负责把树变成列表，环负责在这份列表上迭代。

## 4. 三个运行时目录（先记住，第 2 章展开）

| 目录 | 默认 | 里面有什么 |
|------|------|------------|
| 安装目录 | `~/.local/lib/loop-agent` | 界面、窗口程序、后端 venv。`loop uninstall` 只删这里 |
| 用户数据 | `APP_DATA_DIR` 或 `~/.local/share/loop-agent` | SQLite、模型档案、记忆、`transcript.jsonl`、过大工具结果 spill |
| 工作区 | 用户选的文件夹 | 读改文件、shell 的根。没绑定，工具没有根 |

开发时 `backend/.env` 里 `APP_DATA_DIR=./data`，狗粮库在仓库里。`loop shell` 不读这份 `.env`，端口 8765，避开开发用的 8000 / 5173。

环不拼安装路径。工具不读安装树。这是为了避免「Agent 改到自己的源码」在用户机器上变成默认行为。

## 5. 和 Pi 十章的对应，以及我们多出来的东西

Pi 的教材按「开篇、分层、环、模型、工具、消息、事件、上下文工程、压缩、会话」排。本手册沿用这个顺序，因为这十个问题是任何编码 Agent 都要回答的。差别在答案：

| Pi 的答案 | Loop Agent 的答案 |
|-----------|-------------------|
| 四个包，可以单独 import | 一个 Python 包 `agent_window`，用 import 方向模拟四层；`tests/test_layer_boundaries.py` 守住 core / ai 不碰 FastAPI 和 SQLAlchemy |
| 系统提示极短，能力靠扩展 | 系统提示在 `_system_prompt` 里写清工具契约（必须调 propose_edit，不许嘴上说写过）。工作区可放 `SYSTEM.md` 整段替换，`APPEND_SYSTEM.md` 追加 |
| 工具就是 read/write/edit/bash | 读是 `list_dir` / `read_file` / `grep`；写是 `propose_edit` / `propose_delete`；命令是 `propose_shell`；记忆是 `propose_memory`。写和跑默认仍可能要人点 Apply，取决于 Preset |
| 压缩是环内策略 | 压缩在 `services/compress.py`，经 `transform_context` 钩子进入环。摘要写成树上的 `compaction_summary`，模型看到的是带「【对话压缩摘要】」的 user |
| 终端 TUI | React 窗口 + SSE。事件类型和环的生命周期是同一套名字（`agent_start`、`turn_start`、`tool_start`、`token`、`done`） |

## 6. 默认好用，靠几条硬规则而不是靠功能清单

这些规则在源码里是可测的行为，不是文案：

1. **停不停，看有没有 tool call。** `_run_one_turn` 里 `if tool_calls:` 就执行完这一批再 `CONTINUE`。没有 tool call，才把正文当终稿，发 `token` + `done`。模型说「我已经改好了」但没调工具，不算做完。
2. **嘴上说写过，本轮没有 gate，要挂警告。** `_looks_like_write_claim` 扫终稿。否定句（「不要声称已写入」这类）不算。命中且 `write_gate_seen` / `shell_gate_seen` / `memory_gate_seen` 都是假，就在正文后追加未验证说明。
3. **同一轮里的 tool call 必须配齐 tool 结果，才能再插入 user。** 取消或门控提前结束时，`_append_missing_tool_results` 给剩下的 id 补 stub。否则下一轮请求会因为「assistant 的 tool_call 没有 tool 消息」被网关拒绝。
4. **工具次数有顶。** `max_tool_iters` 来自设置，夹在 8 到 64。用尽后不是假装完成，而是 `soft_land`：再调一次**不带工具**的模型，横幅写明任务未完成。
5. **全文不进窗口，也不丢。** `transcript.jsonl` 只追加。进模型的路径可以被压缩。模型要用细节时调 `search_session`，只搜本会话的 JSONL 和 spill，不搜别的会话、不搜工作区、不搜 `.env`。

## 7. 读这套手册时怎么对源码

每一章末尾有「对着读的文件」。建议的用法：

- 先读章，在脑子里走完一次发送。
- 再打开对应函数，对照本章里的分支（取消、空响应、工具降级、软着陆）。
- 行为以 pytest 为准。改环的测试在 `backend/tests/test_loop_exit.py`、`test_gate_*.py`、`test_compress.py`、`test_checkpoint.py` 这一带。断言写的是「输出里有没有某事件」，不是内部变量名。

模型会不会乖乖调工具，测试测不了。那类改动要写手测步骤。前端没有自动化测试，UI 改动靠 `npx tsc -b` 和手点。

## 8. 本章没展开、后面会展开的缺口

这些是已知边界，不是本章的疏漏：

- 物理包还没拆成四个发布包。逻辑层已经分开。
- `LoopConfig.get_follow_up_messages` 字段在，无人值守的外环还没接上。插队用的是 `get_steering_messages`（`POST .../steer`）。
- 被放弃分支的摘要（Pi 的 branch summary，我们内部叫 C7）没做。
- 占用百分比是 `chars/4` 估算，不是网关账单。
- 进程被杀掉时，JSONL 可能少最后一条 assistant。

下一章把「谁可以 import 谁」和「文件落在哪个目录」讲死。不先分清这两件事，读 `loop.py` 会以为它应该自己去打开数据库。

## Related

- 上一篇：[手册目录](./README.md)
- 手册目录：[README](./README.md)
- 下一篇：[ch02-layers.md](./ch02-layers.md)
- 源码仓库：[masterroland13/loop-agent](https://github.com/masterroland13/loop-agent)
