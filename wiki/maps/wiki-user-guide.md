---
type: map
status: growing
created: 2026-06-30
updated: 2026-11-02
tags:
  - wiki
  - guide
  - onboarding
sources:
  - ../WIKI_SCHEMA.md
  - ../../AGENTS.md
confidence: 0.85
review_after: 2026-08-01
---

# Wiki 使用手册

本页是 **个人复利知识库** 的完整使用说明：面向人类读者，也供 Agent 在维护任务前快速对齐约定。

> **TL;DR**：新材料先低摩擦 Capture → 每周 `/review` 整理 → 值得反复查找的页从 `index.md` 链入；投喂 URL/截图时说「归档进 wiki」或 `/wiki`。

## 目录

1. [这是什么](#这是什么)
2. [仓库分层](#仓库分层)
3. [目录结构](#目录结构)
4. [快速上手](#快速上手)
5. [三段式工作流](#三段式工作流)
6. [Agent 技能](#agent-技能)
7. [写一页 Wiki](#写一页-wiki)
8. [命名与分类](#命名与分类)
9. [Raw 与 URL 归档](#raw-与-url-归档)
10. [图片处理](#图片处理)
11. [归档深度 L0 / L1 / L2](#归档深度-l0--l1--l2)
12. [导航与互链](#导航与互链)
13. [Topic 与 Entity 怎么选](#topic-与-entity-怎么选)
14. [模板选择](#模板选择)
15. [脚本与验收](#脚本与验收)
16. [Git 与多宿主协作](#git-与多宿主协作)
17. [常见场景速查](#常见场景速查)
18. [延伸阅读](#延伸阅读)

---

## 这是什么

本仓库是一个 **Git + Markdown + Agent** 维护的个人知识库：

- **Wiki**（`wiki/`）：经过提炼、可复用的结论与导航
- **Raw**（`references/raw/`）：原始剪藏、长文备份、截图转写——默认不改写正文
- **Schema**（`AGENTS.md` + `wiki/WIKI_SCHEMA.md`）：约定与维护规则

设计目标：

- 不依赖 Obsidian 也能长期维护（Obsidian 仅作可选浏览器）
- 人类与 Agent 共用同一套目录与 frontmatter
- 结构通过 **链接 + 索引** 涌现，而非事先建满文件夹

**单一真相源**：检索与维护时，以 `wiki/` + `references/raw/` 为准，不在聊天记录里找结论。

---

## 仓库分层

| 层 | 路径 | 用途 | 谁写 |
|----|------|------|------|
| **Raw** | `references/raw/` | 剪藏、备份、长文、草稿、截图 assets | Agent 抓取或人类粘贴；Agent 默认只读 |
| **Papers** | `references/papers/` | PDF 与论文原件（可选） | 人类 |
| **Wiki** | `wiki/` | 长期笔记、导航、项目知识 | 人类 + Agent |
| **Schema** | `AGENTS.md`、`wiki/WIKI_SCHEMA.md` | 项目说明与目录约定 | 人类（改约定时同步 changelog） |

**阅读优先级**（Agent 与人类相同）：

1. `AGENTS.md`
2. `wiki/WIKI_SCHEMA.md`
3. `wiki/index.md`
4. 相关 map / project / topic

---

## 目录结构

### `wiki/` 子目录

| 路径 | 作用 |
|------|------|
| `wiki/index.md` | **总入口**：主题索引表 |
| `wiki/changelog.md` | 结构性变更记录（非每笔必写；不要改成操作日志） |
| `wiki/log.md` | ingest / query / lint 时序。默认 L1 不写 ingest 条目 |
| `wiki/inbox.md` | 可选：尚未归档的待办清单 |
| `wiki/maps/` | 主题地图、学习路线、工作流说明（**本手册在此**） |
| `wiki/roadmaps/` | 细分路线（如某学科子路线） |
| `wiki/topics/` | 主题笔记：概念、方法、读书记录 |
| `wiki/entities/` | 术语 / 作品 / 人物等短定义页 |
| `wiki/papers/` | 单篇论文阅读笔记 |
| `wiki/projects/` | 按项目归档的知识 hub。`learning-progress/` 是行为记忆（偏好 / 纠错 / 进度），不是主题事实 |
| `wiki/templates/` | 新页骨架 |
| `wiki/references/` | Wiki 侧参考（如图片处理指南） |

### 默认导航协议

```
wiki/index.md
    ↓
wiki/maps/ 或 wiki/projects/
    ↓
wiki/topics/、wiki/entities/、wiki/papers/
```

不要跳过 index 直接乱建叶子页——否则容易变成「孤岛页」。

`/teacher` 与 `/review` 在讲课或复盘之前，再读 [`learning-progress`](../projects/learning-progress/README.md)。那是行为记忆，不是本索引的主题主入口。偏好不要写进 topic 正文。写入路由见 [`WIKI_SCHEMA.md`](../WIKI_SCHEMA.md)。

---

## 快速上手

### 第一次使用

1. 打开 [`wiki/index.md`](../index.md) 熟悉分区（文艺 / 人文 / 理工 / 跨学科 / 实体 / 项目）
2. 读 [`Capture → Review → Archive`](./capture-review-archival-workflow.md) 了解日常节奏
3. 有材料要归档时，对 Agent 说：**「投喂 wiki」** 或 **`/wiki`**，附上 URL / 截图 / 聊天摘要

### 30 秒录入一条想法

打开 [`wiki/inbox.md`](../inbox.md)，在合适分区追加一行：

```markdown
- [ ] 某文章 URL — 想提炼「XXX 结论」
```

不必立刻分类；每周 `/review` 时再 promote 到 `topics/`。

### 第一次写正式 topic

1. 复制 [`wiki/templates/topic-template.md`](../templates/topic-template.md) 或 [`topic-ingest-template.md`](../templates/topic-ingest-template.md)
2. 保存到 `wiki/topics/<prefix>-<slug>.md`（见 [命名与分类](#命名与分类)）
3. 填 frontmatter + 一句 TL;DR + 来源 + ≥2 个 Related
4. 在 [`wiki/index.md`](../index.md) 对应分区加一行链接

---

## 三段式工作流

核心流程：**Capture → Review → Archive**。详见 [`capture-review-archival-workflow.md`](./capture-review-archival-workflow.md)。

| 阶段 | 目标 | 默认位置 | 时间预算 |
|------|------|----------|----------|
| **Capture** | 先把想法落地，降低分类决策 | `wiki/inbox.md` 或临时页 | 10–60 秒 |
| **Review** | 补属性、互链、判断价值 | inbox + 目标页草稿 | 15–30 分钟 / 周 |
| **Archive** | 沉淀为长期资产 | `topics/`、`maps/`、`entities/` | 按需 |

### Capture 规则

1. **先写下来**，不要先纠结放哪个文件夹
2. 至少补一个 **来源**（`sources` 或 Raw 路径）或上下文线索
3. 能想到关联对象，立刻加一个内部链接

### Review 每周清单

- [ ] 把高价值 inbox 项 promote 到对应目录
- [ ] 检查 frontmatter 是否完整（尤其 `growing`/`stale` 的 `confidence`、`review_after`）
- [ ] 每页是否写清 **主张 → 证据 → 边界**（避免只做摘抄）
- [ ] 修复断链，补 topic ↔ map ↔ entity 互链
- [ ] 结构性变更写入 [`wiki/changelog.md`](../changelog.md)

### Archive 启发式

| 内容类型 | 去向 |
|----------|------|
| 可复用知识、方法、机制 | `wiki/topics/` |
| 导航、学习路径、知识编排 | `wiki/maps/` |
| 稳定术语 / 人物 / 作品定义 | `wiki/entities/` |
| 单篇论文笔记 | `wiki/papers/` |
| 某项目专属决策与经验 | `wiki/projects/<project>/` |
| 学习者偏好、纠错、教学进度 | `wiki/projects/learning-progress/`（不要写进 topic 正文） |

---

## Agent 技能

本仓库有六个定制技能。Canonical 只在 `.agents/skills/`。只改这里，再同步到 `.cursor/skills/`、`.claude/skills/`、`.codex/skills/`。不要把某一宿主副本当成另一份原文。核对：`python3 scripts/check_skill_sync.py`。

### 技能对照表

| 技能 | 用途 | Cursor 怎么说 | Claude Code | Codex |
|------|------|---------------|-------------|-------|
| **/wiki** | 新 URL、截图、聊天 → Raw + topic + 导航 | 「投喂 wiki」「归档进 wiki」 | `/wiki` | `$wiki` |
| **/query** | 用已有页回答，引用仓库路径；找不到就明说 | 「/query」「问 wiki」「根据笔记回答」 | `/query` | `$query` |
| **/review** | inbox 分拣、到期页复盘、灵感连接 | 「/review」「复盘 inbox」 | `/review` | `$review` |
| **/lint** | 坏链、孤岛页、frontmatter 机械体检 | 「lint 一下」「整理 wiki」 | `/lint` | `$lint` |
| **/teacher** | 教练式学习：推导、复习、系统掌握 | `/teacher` / 教练式学习 | `/teacher` | `$teacher` |
| **/teacher-cs** | CS 别名：算法、LeetCode、面试 | `/teacher-cs` / 教我做题 | `/teacher-cs` | `$teacher-cs` |

### 分工原则

```
新输入 ──→ /wiki（归档）
已有笔记要答案 ──→ /query（引用路径；找不到就说 I can't find）
还不会/要推导 ──→ /teacher 或 /teacher-cs（CS）
已有笔记要整理 ──→ /review（语义整理、互链、灵感）
机械问题 ──→ /lint（链接、导航、格式）
```

- **query 只读已有页并引用路径**；**review 做判断**；**lint 做体检**。
- 六个技能 **不是** 重型 compile loop：优先小步归档、必要导航、可追溯来源。没有向量库，也不把 `references/raw/` 当默认答案源。

### `/wiki` 典型输入

| 输入 | Agent 行为 |
|------|------------|
| 文章 URL | 默认 L1：必要时 Raw → 一篇 topic → index 或 map 一条入口。说出「L2 / 深挖 / compile / 级联」才级联 entity + map + index，并写 `wiki/log.md` |
| 截图 / 幻灯片（无 URL） | 几乎总是 Raw + 结构化转写 |
| 聊天摘要 / JD / 论文摘要 | 按 archive-depth 定档 |
| TrendRadar 摘要 | 走专用路由，不随意开 deep-dive topic |

### `/review` 典型模式

| 你说 | Agent 做什么 |
|------|--------------|
| 「复盘 inbox」 | 逐项 promote / merge / link / defer / drop |
| 「到期页 / stale / growing」 | 扫 `review_after` ≤ 今天 |
| 「复习 / 考我」 | Recall 模式 |
| 「还能写什么」 | Inspiration pass：矛盾、空白、跨 topic 桥梁 |
| 未指定 | 默认 Weekly（15–30 分钟） |

### `/query` 怎么问

1. 先读 `wiki/index.md`，再打开相关 map / project，然后打开 topic / entity
2. 答案列出读过的仓库路径
3. 没有页就说 **I can't find**（找不到），不编造路径
4. 值得留下的答案只提议写回，不自动改完整库

金标在 [`wiki/evals/retrieval-cases.md`](../evals/retrieval-cases.md)。检查期望路径是否存在：

```bash
python3 scripts/check_retrieval_cases.py
```

### `/lint` 检查项

先跑机器 lint（规则见 [`WIKI_SCHEMA.md`](../WIKI_SCHEMA.md)「机器规则子集」）：

```bash
python3 scripts/lint_wiki.py
```

脚本之后再看它不管的部分：

1. `wiki/index.md` 和相关 map 能否找到新内容
2. 页面是否落在合适目录
3. 是否满足模板 MVP：结论 + 来源 + Related
4. 结构性变更才补 `wiki/changelog.md`。`/lint` 收尾另写一条 `wiki/log.md`（`lint`），不要把操作流水写进 changelog
5. `growing` / `stale` 的 `confidence` 仍人工看；缺 `review_after` 由脚本报 warning
6. 带 `superseded_by` 仍被 `wiki/index.md` 直接链接时，脚本报 warning。从 index 拿掉链接并保留该页。不要删页，也不要改写主张来消掉这条 warning
7. source-clock：`wiki/` 外的 source 文件，mtime 的本地日历日期晚于 `updated` 时，脚本 warning 并建议考虑 `status: stale`。不要为了消掉它去改 `status`、`updated` 或正文。URL 与 `wiki/` 内互链不触发。细则见 Schema「Source-clock」

---

## 写一页 Wiki

### Frontmatter 必填

```yaml
---
type: topic          # topic | map | paper | entity | project-note
status: seed         # seed | growing | stable | stale
created: 2026-06-30
updated: 2026-06-30
tags:
  - cs
sources:
  - https://example.com/article
  - ../../references/raw/example-clip.md
---
```

### 按 status 补充

| status | 建议 |
|--------|------|
| `seed` | 初稿，可省略 confidence |
| `growing` | 补 `confidence`（0.0–1.0）和 `review_after` |
| `stable` | 结论已收敛 |
| `stale` | 可能过时，必须设 `review_after` 以便复盘 |

### 页面 MVP（首轮完成标准）

1. **一句可复用结论**（30 秒内读懂）
2. **至少一条可信来源**（`sources` 或 Raw 链）
3. **至少两条 Related 链接**
4. **至少一个不确定性 / 待验证点**（Open Questions 或 Boundaries）

### 高价值 ingest 页额外要求

使用 [`topic-ingest-template.md`](../templates/topic-ingest-template.md) 时，补全：

- **Claims from Source** — 原文主张
- **My Assessment** — 你的判断（不照抄）
- **Boundaries / Failure Cases** — 何时不成立
- **Actionable Moves** — 可执行下一步

### 矛盾与取代（可选，高价值页）

规则在 [`WIKI_SCHEMA.md`](../WIKI_SCHEMA.md)「矛盾与取代」。普通页和旧页不用填。

- 两条主张冲突：写 `## Contradictions`，两边都留着。不要删改已有句子来显得一致，也不要裁定谁对。
- 只是更换先读哪一页：旧页写 `superseded_by`，新页写 `supersedes`（相对本页的路径）。旧页留在仓库里。这不表示旧主张为假。
- 带 `superseded_by` 的页不要留在 [`index.md`](../index.md) 的主表里。`/lint` 对这种情况报 warning，不会因此让全库失败。从 map 或本手册链过去不算主推。
- 合成示例：[`矛盾并存`](../topics/x-demo-contradiction-coexistence.md)。被取代的归档建议仍在 [`x-demo-superseded-filing.md`](../topics/x-demo-superseded-filing.md)，index 不链它。

Review 时对每页过三问：

1. **主张是什么？** — 说不清 → 降级为 seed 或退回 inbox
2. **证据在哪？** — sources / Raw / 可复现链接
3. **边界在哪？** — 与哪条旧结论冲突。冲突时按「矛盾与取代」写明，禁止静默覆盖

---

## 命名与分类

### 学科 slug 前缀

| 域 | 前缀 | 示例文件名 |
|----|------|------------|
| 文学 | `lit-` | `lit-magical-realism.md` |
| 电影/影像 | `film-` | `film-editing-rhythm.md` |
| 音乐 | `music-` | `music-modal-jazz.md` |
| 计算机 | `cs-` | `cs-dp-intro.md` |
| 哲学 | `phil-` | `phil-stoicism.md` |
| 物理 | `phys-` | `phys-entropy-intuition.md` |
| 天文 | `astro-` | `astro-exoplanets.md` |
| 跨学科 | `x-` | `x-info-theory-physics.md` |
| 实体 | `entity-` | `entity-author-orwell.md` |

### 文件路径约定

```
wiki/topics/<slug>.md
wiki/maps/<slug>.md
wiki/entities/entity-<slug>.md
wiki/papers/<slug>.md
wiki/projects/<project>/<slug>.md
```

**导航靠 `index.md` 分区**，不靠再建一层学科文件夹。静态资源统一放各目录下的 `assets/`。

---

## Raw 与 URL 归档

### 何时需要 Raw

| 情况 | 是否 Raw |
|------|----------|
| 长、杂、来源重要、含图、以后可能回看 | **是** → `references/raw/` |
| 已足够干净的小结论 | 可直接写 `wiki/`，`sources` 挂 URL |
| 仅截图 / 幻灯片 | **几乎总是** Raw |

Raw 约定：Agent **默认只读**原文；结构化结论写在 `wiki/` 并链回 Raw。

### 只有 URL 时

**方式一（推荐）**：对 Agent 说「投喂 wiki」+ URL，由 Agent 抓取并归档。

**方式二（终端）**：

```bash
python3 scripts/ingest_url_to_raw.py 'https://example.com/article'
# 需要正文配图时：
python3 scripts/ingest_url_to_raw.py 'https://…' --fetch-images
```

> 注：`ingest_url_to_raw.py` 为文档约定脚本；若本地尚未提供，由 Agent 用 Firecrawl / curl 等方式 fallback。

### 合并 vs 新建 topic

归档前先查是否已有同主题页：

1. 读 `wiki/index.md` 或 `grep` 相关关键词
2. **extend** 已有 topic：新段落 + 更新 `updated` + 补 `sources`
3. **新建** topic：主题独立、会反复检索。用户已要求 L2 时也可以新建；默认 L1 不因此级联其它页

---

## 图片处理

### 存放位置

| 归属 | 路径 |
|------|------|
| Raw 配图 | `references/raw/assets/<stem>/` |
| Wiki 独有图 | `wiki/<dir>/assets/<stem>/` |
| **默认策略** | Wiki **引用** Raw assets，避免重复存图 |

### 嵌入语法

```markdown
# Raw 文件内
![描述](./assets/<stem>/file.png)
*图：…*

# Wiki 引用 Raw
![描述](../../references/raw/assets/<stem>/file.png)
```

### 获取优先级

1. 用户 attach → 复制到 Raw assets
2. Firecrawl MCP（网页正文与图片）
3. `scripts/ingest_url_to_raw.py --fetch-images`（若可用）
4. curl（fallback）

信息图 / 清单图：**Raw 内表格或列表转写** + 保留原图。

完整说明：[`wiki/references/image-handling-guide.md`](../references/image-handling-guide.md)

---

## 归档深度 L0 / L1 / L2

Agent 默认 **L1 标准**。来源看起来重要也不会自动升级。你可口头覆盖：

| 你说 | 档位 |
|------|------|
| 「只要 Raw」 | L0 |
| 「标准 wiki」 / 什么都不说 | L1（不写 `wiki/log.md`，不级联 entity） |
| 「L2」「深挖」「compile」「级联」 | L2 compile |

| 档位 | 典型输入 | Raw | Wiki | 导航 |
|------|----------|-----|------|------|
| **L0 片段** | 单图/单段、无 URL | 必做 | 短段并入已有 topic 或 seed | 仅当新主题 |
| **L1 标准** | URL、文章摘要 | 长/杂/重要时必做 | topic-ingest 模板 | index **或** map 一条入口 |
| **L2 深读（compile）** | 你明示要深挖或级联 | 全文或精读摘录 | 完整 Assessment + Boundary + Actionable | 相关 entity + 相关 map + index + `wiki/log.md` 一条 `ingest`。changelog 仅结构变更 |

L2 不改无关阅读笔记正文，也不按每源 10–15 页凑数。检查清单在 `/wiki` skill 的「L2 dry-run」。

### confidence 粗算（growing / stale 页）

| 来源组合 | 建议 confidence |
|----------|-----------------|
| 仅截图/聊天、无一手 URL | ≤ 0.70 |
| 截图 + ≥2 独立二次文献一致 | 0.65–0.75 |
| 一手 URL / 官方文档 + Raw | ≥ 0.80 |
| 二手解读、无源码核对 | 0.55–0.65 |

详见 [`references/archive-depth.md`](../../references/archive-depth.md)。

---

## 导航与互链

### 入口层级

1. **全局**：[`wiki/index.md`](../index.md)
2. **域 / 主题**：[`wiki/maps/learning-spine.md`](./learning-spine.md) 等 map
3. **项目**：`wiki/projects/<name>/index.md`
4. **叶子**：topic / entity / paper

### 何时更新 index / changelog / log

| 变更 | index | changelog | `wiki/log.md` |
|------|-------|-----------|---------------|
| 新 topic，值得反复找到（默认 L1） | 一条入口，或只写 map | 不写 | 不写 |
| 用户明示 L2 compile | 对应分区一行 | 不写（除非同时改了 schema） | 一条 `ingest` |
| 新 map / 大结构调整 | ✅ | ✅ | 不写 |
| 仅给已有 topic 补一段 | 可选 | 不写 | 不写 |
| `/query` 或 `/lint` 结束 | 不写 | 不写 | 一条 `query` 或 `lint` |
| 合并 / 删除页 | ✅ | ✅ | 不写 |

### Related 链接

每页至少 **2 个 Related**，类型尽量多样（map + entity + topic），让结构从链接中涌现。

---

## Topic 与 Entity 怎么选

| 问题 | 建什么 |
|------|--------|
| 「这是谁 / 哪部 / 哪个概念？」 | `wiki/entities/entity-*.md` |
| 「我怎么理解 / 比较 / 应用？」 | `wiki/topics/<prefix>-*.md` |
| 单次读/观/听记录 | 写在 **entity 页** 的「个人笔记」小节 |

**避免重复 hub**：一个概念只建一篇 entity，多学科 topic 链向同一 entity。

详见 [`wiki/entities/README.md`](../entities/README.md)。

---

## 模板选择

| 模板 | 适用 |
|------|------|
| `topic-template.md` | 通用主题（概念、方法、机制） |
| `topic-ingest-template.md` | 从 URL / Raw / 文章提炼 |
| `topic-faq-template.md` | 面试问答、排障 FAQ |
| `map-template.md` | 导航、学习路径 |
| `entity-template.md` | 术语 / 人物 / 作品定义 |
| `paper-template.md` | 论文阅读笔记 |
| `project-note-template.md` | 项目决策、风险、指标 |

设计原则与 MVP 标准：[`wiki/templates/README.md`](../templates/README.md)

---

## 脚本与验收

### 机器 lint

```bash
python3 scripts/lint_wiki.py
python3 scripts/lint_wiki.py --strict
python3 scripts/check_retrieval_cases.py
python3 -m pytest scripts/test_lint_wiki.py scripts/test_check_retrieval_cases.py scripts/test_check_skill_sync.py -q
```

lint 退出码：`0` 无 error（可以有 warning）；`1` 有 error，或 `--strict` 下有 warning；`2` 用法或环境错误。`/lint` 的第一步就是第一条命令。`check_retrieval_cases.py` 同样是 0 通过、1 有格式或路径错误、2 读不到文件；它不打分，也没有 warning 档。

### 技能镜像

```bash
python3 scripts/check_skill_sync.py
```

对照 `.agents/skills/` 与 `.cursor/skills/`、`.claude/skills/`、`.codex/skills/`。退出码：`0` 按文件哈希一致；`1` 漂移（打印路径）；`2` 用法错误或找不到 canonical 目录。这不是 `lint_wiki.py` 的检查。只改 `.agents/skills/`，再同步三份镜像。

### 图片路径验收

```bash
scripts/wiki_verify_images.sh wiki/topics/cs-example.md
# 或批量
scripts/wiki_verify_images.sh wiki/topics/*.md
```

退出码 0 = 全部 OK；1 = 存在断链。

### `/wiki` 轻量验收清单

- [ ] 新页目录正确；`sources` 可追溯
- [ ] 至少一个入口（index / map / project）可到达
- [ ] 图片文件存在、相对路径正确、有 alt
- [ ] 跑 `python3 scripts/lint_wiki.py`（`/lint` 的第一步）

---

## Git 与多宿主协作

- **默认分支**：`master`
- **远程**：`https://github.com/masterroland13/wiki`
- **多 Agent / 多宿主**：同一远程可能有多处提交 → **先 `git pull` 再大改**；冲突以合并结果为准
- Wiki 的单一真相在 **仓库**，不在某次聊天里

Obsidian 可选：直接打开 `wiki/` 文件夹浏览；维护约定仍以 Schema 为准。

---

## 常见场景速查

### 我读了一篇文章，想记下来

```
对 Agent：归档进 wiki
附件/粘贴：https://…
补充：我关心的是 XXX 结论
```

Agent 会：定 L1 → 必要时 Raw → `wiki/topics/` → 更新 index。

### 我有一张截图，没有链接

```
对 Agent：投喂 wiki，这是某分享会的截图
附件：screenshot.png
```

Agent 会：Raw + 结构化转写 → 短 topic 或并入已有页。

### 我只有一个想法，还没想清楚

手动写入 [`wiki/inbox.md`](../inbox.md)，周末说「`/review` 复盘 inbox」。

### 新材料和旧笔记打架

不要直接改掉旧主张。按上文「矛盾与取代」和 [`WIKI_SCHEMA.md`](../WIKI_SCHEMA.md) 写 `## Contradictions`，或用 `supersedes` / `superseded_by` 更换阅读入口。lint 不裁定谁对。

### 某页写了很久，不确定是否过时

把 frontmatter 改为 `status: stale`，设 `review_after`，然后 `/review`。

### 链接红了 / 找不到新写的页

说「**lint 一下**」或「**整理 wiki**」。Agent 会先跑 `python3 scripts/lint_wiki.py`，再看导航。

### 我想规划跨学科学习

打开 [`learning-spine.md`](./learning-spine.md)，按阶段补 seed topic，再在 index 链入。

### 某项目知识不想和通用 topic 混在一起

建 `wiki/projects/<name>/index.md` 作为 hub，项目笔记用 `project-note-template.md`。

---

## 延伸阅读

| 文档 | 内容 |
|------|------|
| [`AGENTS.md`](../../AGENTS.md) | 项目正文、技能路径、文档索引 |
| [`wiki/WIKI_SCHEMA.md`](../WIKI_SCHEMA.md) | 目录分工、维护习惯（Schema 权威） |
| [`wiki/index.md`](../index.md) | 主题导航入口 |
| [`capture-review-archival-workflow.md`](./capture-review-archival-workflow.md) | Capture → Review → Archive |
| [`learning-spine.md`](./learning-spine.md) | 跨学科学习主轴 |
| [`references/archive-depth.md`](../../references/archive-depth.md) | L0/L1/L2 与 confidence |
| [`references/raw/README.md`](../../references/raw/README.md) | Raw 收件箱说明 |

---

## Related

- [Wiki 索引](../index.md)
- [Capture → Review → Archive](./capture-review-archival-workflow.md)
- [Learning Spine](./learning-spine.md)
- [WIKI_SCHEMA](../WIKI_SCHEMA.md)
