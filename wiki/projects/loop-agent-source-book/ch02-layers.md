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
  - https://github.com/masterroland13/loop-agent/blob/main/docs/design/loop-agent-book/ch02-layers.md
confidence: 0.75
review_after: 2026-12-03
---

# 第 2 章：项目结构与分层 —— 谁可以调用谁

> 本章回答：仓库为什么看起来是一个 Python 包，却要说成四层；改代码时什么样的 import 是错的；三个目录和四层是两套正交的轴。

## 1. 为什么要分层

早期形态是一条双向缠绕：`routes.py` 既拼提示词、又跑环、又等审批；`loop.py` 直接碰补丁、记忆和供应商。功能能跑，但每加一个模式（Goal、Preset、压缩）都会在 `loop.py` 里再写一个 `if`。

宪章把这件事说成依赖方向，不说成「文件必须搬进四个文件夹」：

```text
loop-window     React · FastAPI · SQLite · CLI · 桌面壳
      ↑
loop-coding     读改文件、shell、记忆、Skills、压缩、检索、落盘
      ↑
loop-agent-core 环、LoopConfig、会话树路径、Goal/Preset 钩子
      ↑
loop-ai         Model Registry、OpenAI 兼容 Client、流式、错误归一
```

箭头只向上。底层不知道上层的存在。

- `loop-ai` 不知道什么是 Goal，也不知道 FastAPI。
- `loop-agent-core` 可以调模型、可以调度工具，但不能 `import agent_window.api` 或 `agent_window.models`。
- `loop-coding` 做事。它不决定「这次要不要弹审批」。
- `loop-window` 组装一次请求：从库里取出路径、装上钩子、把环的事件写成 SSE。

允许 coding / core 使用 ai 的原子类型（消息 dict、模型名）。禁止反向：ai 去 import 会话 ORM。

物理包名仍是 `agent_window`。不要单独开一个「全文替换成 loop_*」的 PR。改名跟着绞杀走。验收看 `backend/tests/test_layer_boundaries.py`：`agent_window.core` 存在，且不 import `api` / `models`。

## 2. 今天文件落在哪一层

| 逻辑层 | 目录 / 文件 | 一句话 |
|--------|-------------|--------|
| loop-ai | `services/provider.py`、`services/model_registry.py`、`services/llm_config.py`、`services/provider_presets.py` | 按档案拿 client，发 chat completion |
| loop-agent-core | `core/` 全部、`agent/loop.py`、`agent/goal.py`、`agent/checkpoint.py`、`agent/exploration.py`、`agent/observation.py`、`agent/loop_exit.py`、`agent/turn_event.py` | 环和策略。`session_tree.py` 用鸭子类型读 `parent_id`，不 import ORM |
| loop-coding | `tools/*`、`services/patches.py`、`shell.py`、`memory.py`、`skills.py`、`workspace.py`、`compress.py`、`compaction_persist.py`、`session_transcript.py`、`session_search.py`、`context_transform.py` | 副作用和上下文塑形 |
| loop-window | `api/routes.py`、`models.py`、`schemas.py`、`cli/`、前端 `src/`、`main.py` | HTTP、表、界面 |

有几处看起来「跨层」，其实是故意的接缝，不是破例：

- `services/context_transform.py` 住在 coding，因为压缩算法不能进 core。`loop.py` 只调用 `apply_transform_context(config, working)`。core 不 import `compress.py`。
- `services/compaction_persist.py` 要写 SQLite，所以它 import `models`。它属于 window/coding 的持久化，不属于环。环压完只在内存里的 `working` 上继续；上树是窗口在钩子回调里做的。
- `core/session_tree.py` 的注释写明：对 ORM 行做鸭子类型（`role` / `content` / `id` / `parent_id` / `entry_type`），这样 core 不用认识 `Message` 类。

## 3. `LoopConfig` 是层与层之间的插座

`core/loop_config.py` 是一个 dataclass，不是服务。一次运行一份配置。字段都是可选钩子：

| 钩子 | 谁安装 | 环什么时候拉 |
|------|--------|----------------|
| `convert_to_llm` | 缺省就是 `default_convert_to_llm` | 窗口在进环前把树上的行翻成 dict；环内 working 已经是 dict |
| `transform_context` | `install_context_transform` | 每一轮 `_run_one_turn` 调模型之前 |
| `before_tool_call` | `install_preset_hooks` | 工具管道决定 allow / wait / block |
| `after_tool_call` | Goal 或观察 | 单个工具之后 |
| `after_tool_batch` | Goal ON 时 | 这一批 tool call 全部有了 tool 消息之后 |
| `on_turn_start` | Goal ON 时 | `run_agent_loop` 开头注入目标 |
| `get_steering_messages` | `bind_steering` | 每一轮开始前抽走用户插队 |
| `get_follow_up_messages` | 字段在，默认没人填 | 外环续命，还没接 |
| `should_stop_after_turn` | 可选 | 一轮结束要不要停 |
| `on_final_reply` | 可选 | 终稿出来时 |

工厂方法把「模式」收成拷贝，而不是在环里分支：

- `LoopConfig.default()`：Goal 关 + YOLO。先装基础工具钩子（观察瘦身），再装 Preset。
- `from_settings(goal_mode, preset)`：`default()` 再 `with_goal_mode`、`with_preset`。
- `with_goal_mode(False)` 会清掉 Goal 钩子。所以关 Goal 不是「钩子里再 if 一次」，而是钩子槽位为空。
- `with_preset` 只换 `before_tool_call`，不去清 Goal 钩子。两套策略正交。

`send_message_endpoint` 里的实际装配是：

```text
loop_cfg = LoopConfig.from_settings(
    goal_mode=session.goal_mode,
    preset=agent_cfg["loop_preset"],  # 缺省当 yolo
)
loop_cfg = _bind_turn_transform(...)  # 把压缩回调绑上去
```

环的签名是 `run_agent_loop(messages, model, cancel_event, goal, previous_goal, config, emit, session_id)`。没有 `db` 参数。这就是分层在函数签名上的样子。

## 4. 运行时三个目录，和 import 无关

分层回答「代码谁调用谁」。目录回答「字节落在哪」。环不解析安装路径。

### 4.1 安装目录

`loop install` 把构建好的界面、窗口程序、一份后端虚拟环境放进 `~/.local/lib/loop-agent`。命令入口 `~/.local/bin/loop` 用这份环境里的解释器。桌面项 `~/.local/share/applications/loop-agent.desktop` 的 Exec 写绝对路径，不依赖当前 PATH。

`loop uninstall` 只删程序。用户数据和工作区留下。已经装好的 `loop` 再执行 `install` 会停下来，要从仓库里跑。

### 4.2 用户数据目录

`Settings.app_data_dir`。环境变量 `APP_DATA_DIR` 优先，否则 `~/.local/share/loop-agent`。不默认成进程当前目录，也不把 `backend/data` 自动拷进去。

这里有：

- `agent_window.db`：会话、消息、审计。外键打开（`PRAGMA foreign_keys=ON`）。
- 模型档案（Registry 的 JSON）。
- USER.md / MEMORY.md（有字符硬上限）。
- 每个会话目录下的 `transcript.jsonl`（只追加）。
- `turns/`：大工具结果 spill 出去的文件。SQLite 的 trace 里留引用，working 里留瘦身版。

CLI 的 `~/.config/loop-agent` 只服务命令行，不和用户数据合并。

### 4.3 工作区

`workspace.json` 记在用户数据目录里，指向用户选的文件夹。`services/workspace.py` 的 `resolve_in_workspace` 把工具拿到的相对路径解析到这个根下面，拒绝逃出根。

没绑定时，`_system_prompt` 会告诉模型：本地文件不要编，让用户先在「此电脑」里选文件夹。记忆工具仍然可用。

桌面壳第一次打开、还没有工作区时，向导先收集一个模型（Base URL、API Key、Model ID），再选或新建文件夹。新建只在当前浏览目录下建子文件夹，点「使用此文件夹」才绑定。新建接口拒绝相对父路径，避免落到进程 cwd。

## 5. 进程有两套，不要混

| | 开发 | 装好之后的桌面 |
|--|------|----------------|
| 后端 | `uvicorn agent_window.main:app --port 8000` | `loop shell` 拉起，端口 8765 |
| 前端 | `npm run dev -- --host 0.0.0.0 --port 5173` | 安装目录里的构建产物，由 8765 托管 |
| 数据 | `backend/.env` 的 `APP_DATA_DIR=./data` | `~/.local/share/loop-agent` |
| 读不读 `.env` | 开发进程读 | `loop shell` 不读 `backend/.env` |

8765 已被占用时不开第二份，避免接到别人的后端。`/health` 必须是 200 才算起来。关窗后子进程停掉。

## 6. 前端在这一层里是什么

`src/` 全部算 loop-window。它不实现环。它做的是：

- `src/api/agent.ts`：HTTP / SSE 客户端。
- `src/components/ChatInput.tsx`：发送、停止、附件、Goal 开关、模型芯片。
- `src/App.tsx`：会话列表、消息流、把 SSE 事件摊进气泡。
- `src/utils/turnTrace.ts`：把后端 trace 画成活动时间线。

前端没有自动化测试。改 UI 的验收是 `npx tsc -b` 加上手点。后端逻辑改动必须带 `backend/tests/test_*.py`。

## 7. 一条依赖规则怎么在代码审查里用

看到一个 PR，先问三句：

1. 这个 `if` 是策略还是机制？策略进钩子（Goal、Preset、压缩）。机制（配齐 tool 消息、空响应、软着陆）留在 `loop.py`。
2. 这个 import 是不是从 core 指向上层？`from agent_window.models` 出现在 `core/` 或 `agent/loop.py` 里就是错的。`session_tree` 用 `getattr(msg, "parent_id")` 就是为了躲开这个 import。
3. 这个路径是不是安装目录或工作区混用？写用户数据用 `app_data_dir`。读写项目文件用 `require_root()`。

## 8. 和 Pi 第 2 章的差别

Pi 的 `pi-ai`、`pi-agent-core`、`pi-coding-agent`、`pi-tui` 是四个 npm 包，可以只装下面两层在自己的程序里跑环。我们还没有这个发布形态。分层承诺已经写进宪章和测试，运行时的「可拆」体现在：

- 环函数不接收数据库会话。
- 压缩算法不在 `loop.py`。
- 审批不在工具 handler 里写死。
- UI 通过 SSE 事件消费环，环不 import React。

下一章进入心脏：`run_agent_loop` 和 `_run_one_turn`。

## Related

- 上一篇：[ch01-overview.md](./ch01-overview.md)
- 手册目录：[README](./README.md)
- 下一篇：[ch03-agent-loop.md](./ch03-agent-loop.md)
- 源码仓库：[masterroland13/loop-agent](https://github.com/masterroland13/loop-agent)
