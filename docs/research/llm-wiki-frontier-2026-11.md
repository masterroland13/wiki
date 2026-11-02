# AI/LLM 个人知识库调研与升级建议

> 调研日期：2026-11-02（Asia/Shanghai）  
> 对象仓库：https://github.com/masterroland13/wiki（`master`，只读，未改仓库）  
> 基线：Karpathy LLM Wiki gist + 本仓库 2026-06/07 骨架与首批内容  
> 约束：保持 **git + markdown + agent**；不默认锁入 Obsidian

> **落盘**：本文是 2026-11-02 调研稿的仓库副本，结论未改写。上文「只读，未改仓库」和文末边界说的是调研当时。施工以 [`wiki-frontier-upgrade.md`](../plans/wiki-frontier-upgrade.md) 为准；本文不记录实现进度。

---

## 0. 执行摘要（给决策用）

1. **Karpathy 模式仍是正确底座**：`raw/` 不可变 + `wiki/` LLM 编译层 + `AGENTS.md`/`WIKI_SCHEMA.md` schema；本仓库已完整落地三层，且比 gist 原型多了 skills、frontmatter、templates、Capture→Review→Archive。
2. **2025–late 2026 的共识升级不在「换产品」，而在「可检验的编辑工程」**：lintable schema、provenance/stale 检测、矛盾显式化、supersession、检索可度量（Erik Evenson Part 2；llm-wiki-kit）。
3. **记忆层 vs 文档 wiki 必须拆开**：wiki = 世界事实；agent memory（偏好、纠错、行为）应另文件/另层（Mem0/Letta 家族思想），本仓库 `learning-progress` 已有雏形但未制度化。
4. **检索升级路径清晰**：当前靠 `index.md` + agent 读文件；体量变大时走 **index grep → BM25 → embeddings → RRF/rerank**，优先索引 **wiki 蒸馏页** 而非 raw chunk（Karpathy 推荐 QMD；llm-wiki-kit 三层检索）。
5. **内容成熟度仍早期**：约 4 topics / 1 entity / 4 maps / 空 papers / 几乎空 raw；设计债比内容债更大——补「操作契约」比补 GraphRAG 更划算。
6. **本仓库已领先 gist 的部分**：`/wiki` `/lint` `/review` 分工、claim/evidence/boundary 模板、`review_after`/`confidence`、跨 Cursor/Claude/Codex skill 副本、明确无 Obsidian 锁入。
7. **相对前沿的主要缺口**：机器可跑的 lint（非纯 prose skill）、操作日志 `log.md`、矛盾/supersession 协议、ingest 级联更新、query 技能、检索评测 harness、source-mtime → stale 标记。
8. **不抄**：完整 Obsidian 插件栈、GraphRAG/LightRAG 全量图库、Mem0 作为知识正文存储、Notion AI 闭源库、重型 hosted wiki 后端。
9. **优先切片**：① 机器 lint + frontmatter 契约 ② query skill + 检索验收集 ③ contradiction/supersession ④ ingest 级联 + log ⑤ 可选 QMD/BM25（体量门槛后再上）。
10. **开放问题**：目标体量（百页 vs 千页）、是否接受可选 Obsidian 只读浏览、偏好本地 QMD 还是脚本级 BM25、是否把「行为记忆」与 wiki 正式分文件。

---

## 1. Karpathy LLM Wiki 要点与 2025–2026 后续

### 1.1 原 gist 核心（primary）

来源：https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f

| 概念 | 内容 |
|------|------|
| 与 RAG 的差异 | RAG 每次查询从 raw 重发现；Wiki 在 ingest 时**编译**知识，查询读已互链的 markdown |
| 三层 | **Raw**（不可变）→ **Wiki**（LLM 拥有、人类主要阅读）→ **Schema**（`CLAUDE.md`/`AGENTS.md`） |
| 三操作 | **Ingest**（一源可触 10–15 页）· **Query**（好答案可回写 wiki）· **Lint**（矛盾/过期/孤岛/缺页） |
| 导航 | `index.md`（内容目录）+ `log.md`（时序操作日志，可用统一前缀方便 grep） |
| 规模观 | ~100 sources / 数百页时 index 足够；更大再上本地搜索（明确点名 [qmd](https://github.com/tobi/qmd)） |
| Obsidian | 推荐作**浏览器/IDE**，非知识真相源；知识在 git+md |

### 1.2 社区后续中真正「改进了模式」的点

| 来源 | 改进 |
|------|------|
| [Erik Evenson · Building an LLM Wiki Part 2](https://erikevenson.net/building-an-llm-wiki-part-2.html)（2026） | ① schema 必须 **lintable** ② source 时间戳 → **stale** ③ 共享假设规范化 ④ **矛盾显式化**（不静默调和）⑤ 结构化 page types ⑥ **事实 wiki vs 行为 memory 分离** ⑦ **检索评测 harness** + BM25 |
| [llm-wiki-kit SPECIFICATION](https://github.com/MauricioPerera/llm-wiki-kit/blob/main/SPECIFICATION.md) | Facts/Entities/Concepts/Synthesis/Sources 分桶；**supersession 链**；ingest=单 commit；三层检索（index → BM25 → embeddings+RRF）；检索对象是 wiki 而非 raw chunks |
| [Starmorph 指南](https://blog.starmorph.com/blog/karpathy-llm-wiki-knowledge-base-guide)（2026-04） | 编译器类比；社区实现谱系；LLM Wiki vs RAG 选型表；QMD/Dataview/Web Clipper 推荐栈；指出 v2 扩展（confidence/supersession/typed edges） |
| [pratiyush llm-wiki research](https://pratiyush.github.io/llm-wiki/docs/research.html) | 15 实现聚类：纯 skill / md+轻脚本 / Obsidian 耦合 / 重型托管；建议 stdlib-first、Obsidian 仅 adapter、保留 Karpathy 三层 |
| [lemma llm-wiki-v2 研究笔记](https://github.com/xenitV1/lemma/blob/main/docs/research/llm-wiki-v2.md) | confidence 衰减、supersession、forgetting/deprioritize、typed relations、图遍历查询（规模上来后再需要） |
| [Memory Landscape](https://www.memoryplugin.com/wiki/landscape.html) | **Corpus memory**（GraphRAG/LightRAG/…）vs **Agent memory**（Mem0/Letta/Zep）；markdown 是合理地板；按失败模式选型 |

### 1.3 对本仓库的含义（一句话）

你们已经站在正确范式上；2026 前沿是把「散文约定」变成「可测契约 + 可度量检索 + 显式知识生命周期」，而不是换一套 PKM 产品。

---

## 2. 竞品/路径全景（可偷设计，非营销）

### 2.1 Competitive landscape

| Approach | Core idea | Strength | Weakness | Fit for this repo |
|----------|-----------|----------|----------|-------------------|
| **Karpathy-style md+git wiki** | Ingest 时编译互链 md；schema 约束 agent | 可审计、可 git、低基建、知识复利 | 规模上千页后导航/一致性变难 | **主路径（已采用）** |
| **Karpathy successors（Evenson / wiki-kit / v2）** | Lintable 元数据、stale、supersession、检索层 | 直接补 gist 缺口 | 实现成本上升；易过度设计 | **高优先抄设计** |
| **Hybrid search（BM25+vector+rerank）** e.g. **QMD** | 本地对 md 混合检索 | 解决「页在但找不到」 | 模型/索引运维；小库杀鸡用牛刀 | **体量门槛后强推**（ROADMAP 已提 qmd） |
| **Classical RAG**（PrivateGPT/LocalGPT/LlamaIndex chunk） | 查询时从 raw chunk 检索 | 大库、高频变文档 | 无编译、矛盾并存、难复利 | **低 fit**；仅作 raw 深挖补充，不作 SSOT |
| **GraphRAG** | 实体图 + community 摘要 | 全局主题/sensemaking | 重、全量重建贵、小库过重 | **不抄基建**；可偷「社区摘要≈maps」 |
| **LightRAG / HippoRAG** | 增量双层图 / 轻量多跳 | 文档变更友好、多跳便宜 | 仍是检索栈，非可编辑 wiki | **理念可参考**；不替换 wiki |
| **RAPTOR** | 递归摘要树 | 细节+主题分层 | 树维护成本 | 可偷「分层摘要」进 maps |
| **Entity-first / Zettelkasten+LLM**（A-MEM 等） | 原子笔记 + 邻域改写 | 涌现连接 | 易碎片、难导航 | 你们已有 entities；**强化 entity hub，勿全面原子化** |
| **Mem0 / supermemory** | Agent 个性化记忆 CRUD | 跨会话偏好/事实轻量 | 不适合作文档正文库 | **行为/偏好层**，不进 `wiki/topics` |
| **Letta/MemGPT** | Agent 自编辑分层记忆 | 自主 curation | 不可预测、难审计 | 理念：working/episodic/semantic 分层 → 可映射 inbox/log/wiki |
| **Zep/Graphiti** | 双时态 KG、矛盾使边失效 | 「当时为真」查询 | 过重 | 偷 **bi-temporal / superseded** 元数据，不引入图库 |
| **Claude Projects / Cursor rules / AGENTS.md** | 项目级指令 + skills | 跨会话纪律 | 指令漂移、副本同步债 | **已采用**；需加强「契约可测」 |
| **Obsidian + Smart Connections** | 本地 vault + 向量/图 UI | 浏览体验好 | 易锁 UI；插件生态分心 | **可选只读前端**；真相仍在 git |
| **Logseq / Foam / Dendron / SiYuan / Anytype / Capacities / Reflect** | 大纲/层级/对象库 PKM | 各有导航哲学 | 多为编辑器中心，非 agent-compiler | 偷导航隐喻即可（block ref、hierarchy、object） |
| **Notion AI / NotebookLM** | 托管问答 | 上手快 | 闭源、难 git、难 agent 写回 | **不抄** |
| **宿主技能包**（wiki-skills 等） | `/ingest` `/lint` slash | 可移植 | 质量参差 | 对齐操作名；保留你们更细的 `/review` |

### 2.2 产品里值得偷的「设计点子」（不迁产品）

| 来源产品/系统 | 可偷点子 | 落到本仓库 |
|---------------|----------|------------|
| Obsidian Dataview | frontmatter 可查询表 | `scripts/lint_wiki.py` 输出 due/stale 表；不必装 Obsidian |
| Obsidian graph / backlinks | 入链密度、hub/orphan | lint 报告 orphans + 建议 Related |
| Logseq / Zettelkasten | 原子主张 + 双向链接 | 保持 claim 段；entity 短页 |
| Dendron | 层级命名/schema | 已有 slug 前缀；可加可选 `domain:` frontmatter |
| Capacities / Anytype | 对象类型字段 | entity 模板加 typed fields（book/person/tool） |
| NotebookLM | 「来源接地」回答 | query skill：答案必须链回 wiki 路径 + sources |
| GraphRAG communities | 主题社区摘要 | `/review` 生成/刷新 maps，而非 Leiden 图算法 |
| Mem0 | 读时冲突排序 vs 写时 diff | 行为记忆可 append；wiki 事实用 supersession |
| QMD | BM25+vector+RRF+rerank | ROADMAP 兑现为可选 MCP/CLI |

---

## 3. 本仓库现状快照（只读）

### 3.1 架构符合度

| Karpathy / 前沿要素 | 本仓库 | 状态 |
|---------------------|--------|------|
| Raw 不可变 | `references/raw/`、`references/papers/` | ✅ 有约定；内容几乎空 |
| Wiki 编译层 | `wiki/{topics,entities,maps,projects,papers,templates}` | ✅ 结构成熟 |
| Schema SSOT | `AGENTS.md` + `wiki/WIKI_SCHEMA.md` | ✅ 清晰；跨宿主说明好 |
| Ingest | `/wiki` skill + 深度 L0/L1/L2 + 图片/TrendRadar | ✅ 比 gist 更实操 |
| Query | 无独立 `/query`；依赖 agent 读 index | ⚠️ 缺口 |
| Lint | `/lint` **散文 checklist**；仅 `scripts/wiki_verify_images.sh` | ⚠️ 非机器契约 |
| Review | `/review` 很强（inbox/due/inspiration） | ✅ 领先多数 fork |
| index.md | 有，分区导航 | ✅；内容稀疏 |
| log.md | **无**（仅 changelog 结构性变更） | ❌ |
| Frontmatter | type/status/tags/sources/confidence/review_after | ✅ 设计好；执行未机器校验 |
| Skills 多宿主 | `.agents` + `.cursor`/`.claude`/`.codex` 副本 | ✅；ROADMAP 仍记同步债 |
| Teacher | `/teacher` + evals | ✅ 独特增值（学习向） |

### 3.2 内容成熟度（tree 统计，约）

| 区域 | 数量（实质 md） | 备注 |
|------|-----------------|------|
| `wiki/topics/` | 4 | 全为《妥协社会》阅读笔记簇 |
| `wiki/entities/` | 1 (+README) | `entity-book-palliative-society` |
| `wiki/maps/` | 4 | user-guide / workflow / learning-spine / 阅读索引 |
| `wiki/projects/` | learning-progress 骨架 | 行为记忆雏形 |
| `wiki/papers/` | 0 | 目录约定有、内容无 |
| `references/raw/` | 基本空 | 尚未形成「源→编译」数据流 |
| `scripts/` | 1 | 仅图片校验 |
| 最近有意义推送 | changelog **2026-07-08** | 距调研日约 **4 个月** |

结论：这是 **设计完整、内容种子期** 的仓库；升级应优先「操作契约与检索」，而非 GraphRAG。

### 3.3 已有高质量设计（应保留）

- Capture → Review → Archive 工作流 map  
- topic-ingest：TL;DR / Claims / Assessment / Boundaries / Actions / Open Questions  
- `/wiki` 与 `/review` 严格分工（机械 vs 语义）  
- 明确 **无 Obsidian 锁入**  
- 学科 slug 前缀 + flat topics（不靠深层文件夹）  
- `AGENTS.md` 启动阅读顺序与文档优先级表  

---

## 4. 抄 / 不抄（相对当前 wiki）

| 抄（Adopt） | 为什么 | 不抄（Skip） | 为什么 |
|-------------|--------|--------------|--------|
| 机器可跑 lint（缺字段、坏链、orphan、非法 type/status） | Evenson「最大偏离」；你们 `/lint` 目前靠模型自觉 | Obsidian 作为写入真相源 / 必备插件栈 | 与仓库目标冲突；浏览可选 |
| `wiki/log.md` 或 `ops-log.md`（ingest/query/lint 时序） | Karpathy 双文件导航；changelog 只管结构 | 把 changelog 改成操作日志 | 职责混淆 |
| Contradiction / superseded 块 + frontmatter 字段 | 2026 共识；避免静默调和 | 自动「选边」消矛盾 | 丢掉最有价值信息 |
| Source mtime / ingest 后标记依赖页 stale | provenance → trust | 全库定时重写所有页 | 噪声大、耗 token |
| `/query` skill：先 index → 定点读页 → 可回写 | Karpathy 三操作缺一 | 默认对 raw 做向量 RAG 当 SSOT | 违背编译模式 |
| 小型 retrieval eval 集（10–30 问） | 「找不到已有页」是头号静默失败 | 一上来上 GraphRAG/LightRAG 服务 | 体量与运维不匹配 |
| 行为记忆与事实 wiki 分离（扩展 `learning-progress` 或 `MEMORY.md`） | Evenson / Mem0 分野 | Mem0/Letta 存主题笔记正文 | 不可 git 审计、难互链 |
| Ingest 级联清单（更新相关 entity/map/index/log） | gist「一源 10–15 页」 | 每次 ingest 强制全库重编译 | 成本高、早期不必要 |
| 可选 QMD/BM25（wiki/ 上）达阈值后启用 | ROADMAP 已写；Karpathy 推荐 | 现在就上向量库+重排全栈 | 当前 <20 实质页，ROI 负 |
| Entity typed fields（书/人/工具） | Capacities 对象思想 | 全面改成对象数据库 UI | 离开 md+git |
| Maps 作「社区摘要」定期刷新 | 偷 GraphRAG 产出形态 | Leiden/社区检测管线 | 过度工程 |
| Skill 同步脚本/checksum | ROADMAP Icebox | 四套技能长期手拷无校验 | 已有漂移风险 |
| Fact 原子页（可选、高信心声明） | wiki-kit facts 桶 | 强制一切改成 fact 页 | 与阅读笔记/学习场景不搭 |

---

## 5. Gap analysis（相对 late-2026 最佳实践）

| 维度 | 最佳实践 | 本仓库 | Gap 严重度 |
|------|----------|--------|------------|
| Schema 可执行性 | zod/脚本校验 frontmatter | 仅文档建议 | **高** |
| 知识生命周期 | supersession、stale-by-source、confidence 衰减 | 有 status/confidence/review_after，无 supersedes、无 source-clock | **高** |
| 矛盾处理 | 显式 contradiction 段 | 模板无标准矛盾协议 | **中高** |
| 操作完备性 | ingest / query / lint | ingest+lint+review+teacher；**无 query**；lint 非机械 | **高** |
| 可观测性 | log.md + 可 grep 前缀 | 仅结构性 changelog | **中** |
| 检索 | index → BM25 → embed | 仅 index + 模型自搜 | **中**（现体量可忍，不设防会炸） |
| 评测 | retrieval harness | teacher 有 evals；wiki 检索无 | **中高** |
| Ingest 深度 | 级联更新多页 | `/wiki` 偏「小步归档」，明确避免重 compile | **中**（有意轻量；需「可选 L2 compile」） |
| Raw→Wiki 闭环 | 源入库再编译 | raw 空、内容多直接写 wiki | **中**（小库可接受；缺 provenance 硬度） |
| Memory 分层 | 事实 vs 行为 | learning-progress 雏形未写进 schema | **中** |
| 多宿主技能 | 单 canonical + 同步 | 四份拷贝，无自动化 | **低中** |
| 规模工具 | QMD/MCP | ROADMAP Icebox 未开工 | **低**（现在）→ 未来 **高** |

**总判**：底层范式不落后；落后在 **2026 上半年社区沉淀的「可信任工程细节」**（约 3–4 个月设计债判断成立）。

---

## 6. 推荐升级原则（不变的北极星）

1. **真相在 git 里的 markdown**；聊天记录不是 SSOT。  
2. **继续 LLM-maintained wiki，不引入 Obsidian 锁入**；Obsidian/静态 HTML 最多只读浏览。  
3. **编译优先于检索**：能 ingest 时写好的互链与主张，不靠每次 query 从 raw 拼。  
4. **契约可测**：schema 里写的，lint 必须能失败。  
5. **显示冲突，不消灭冲突**；supersede 留痕。  
6. **事实 wiki ≠ 行为 memory**；偏好/纠错/教学进度另层。  
7. **检索随体量渐进**：<50 页靠 index；50–200 加 BM25；再上向量+rerank。  
8. **检索对象优先 wiki 蒸馏页**；raw 仅在需要原文证据时打开。  
9. **切片可回滚**：ingest/大改尽量原子、可 revert；先契约后重型工具。  
10. **评测驱动**：没有「问句→应开页」金标，不算检索升级完成。

---

## 7. 日级切片提案（0.5–2.5 天）

> 每项：Do / Don't / Acceptance / Risks。按「可独立合并」设计。

### Slice A — 机器 Lint + Frontmatter 契约（0.5–1.5d）⭐ 影响/成本最优

- **Do**：新增 `scripts/lint_wiki.py`（或等价）：校验必填 frontmatter、枚举 `type`/`status`、相对链接、orphan 候选、`growing|stale` 缺 `review_after`；`/lint` skill 改为「先跑脚本再人工判语义」；在 `WIKI_SCHEMA.md` 标明机器规则子集。  
- **Don't**：一次做语义矛盾检测、不上 CI 强制阻断（可先 warn）。  
- **Acceptance**：对当前仓库跑通；故意缺字段/坏链能报路径；exit code 区分 error/warn；文档写清如何跑。  
- **Risks**：历史页大量 warn → 先 baseline allowlist；YAML 边缘语法。

### Slice B — `/query` Skill + 迷你检索评测集（1–2d）⭐

- **Do**：`.agents/skills/query/SKILL.md`：读 index → 选页 → 作答并引用路径；高价值答案提议回写；`wiki/evals/retrieval-cases.md`（或 json）10–20 条「问题 → 期望页」；手动/脚本记命中率。  
- **Don't**：本切片引入向量库；不要对 raw 做默认 RAG。  
- **Acceptance**：评测集上 agent 按流程打开正确页 ≥ 约定阈值（如 70%+）；query skill 有明确失败时「我找不到」协议。  
- **Risks**：评测集过拟合 index 措辞；需含释义问法。

### Slice C — Contradiction / Supersession 协议（1–1.5d）⭐

- **Do**：模板增加 `## Contradictions` / `## Superseded`；frontmatter 可选 `supersedes` / `superseded_by`；`/wiki` 与 `/review` 增加「发现冲突时禁止静默覆盖」；lint 可列出带 superseded 仍被 index 主推的页。  
- **Don't**：自动裁判对错；不上图数据库。  
- **Acceptance**：至少 1 个示例页展示冲突并存；schema/技能交叉引用一致。  
- **Risks**：字段过多导致 ingest 摩擦 → 保持可选、高价值页才填。

### Slice D — Ops Log + Ingest 级联模式（1–2d）

- **Do**：新增 `wiki/log.md`（或 `wiki/ops-log.md`），条目前缀如 `## [YYYY-MM-DD] ingest | title`；`/wiki` 增加 **L2 compile** 可选路径：更新相关 entity/map/index + log；默认仍小步 L1。  
- **Don't**：把每次小补丁都写 changelog；不要强制每源碰 15 页。  
- **Acceptance**：一次完整 L2 ingest 有 log 条目且 index 有更新；用户可只开 L1。  
- **Risks**：级联过度改写阅读笔记风格页 → 限定「entity/map/index」级联范围。

### Slice E — Source-clock Stale 检测（0.5–1d）

- **Do**：页 `sources` 含 raw 路径时，lint 比较页 `updated` 与源文件 mtime（或源 frontmatter date）；过期标 warn + 建议 `status: stale`。  
- **Don't**：自动重写全文。  
- **Acceptance**：人为调源文件时间可触发 warn；无 sources 的页跳过。  
- **Risks**：直接 URL sources 无 mtime → 仅对 repo 内路径生效并写明。

### Slice F — 行为记忆层制度化（0.5–1d）

- **Do**：在 schema 明确：`wiki/projects/learning-progress/`（或根 `MEMORY.md`）= 偏好/纠错/教学进度；禁止把行为指令写入 topic 正文；`/teacher`/`/review` 启动时读该层。  
- **Don't**：引入 Mem0 云服务作为必选。  
- **Acceptance**：AGENTS 阅读顺序含 memory 层；一例「事实在 topic、偏好在 memory」。  
- **Risks**：两层重复 → 技能写清写入路由表。

### Slice G — 可选 Hybrid 检索（QMD 或轻量 BM25）（1.5–2.5d）

- **Do**：达到阈值（如 ≥50 wiki 页或 retrieval eval < 阈值）后：接入 **QMD** CLI/MCP，或 `scripts/search_wiki.py`（谁先谁简单）；检索集合限 `wiki/**/*.md`；更新 ROADMAP 与 `/query`。  
- **Don't**：索引隐私 raw 到远程；不要替换 index-first 流程（混合检索是 fallback）。  
- **Acceptance**：同一评测集比纯 index 有可测提升；离线可跑。  
- **Risks**：本地模型体积/CPU；Windows/WSL 路径；维护成本 → 设启用门槛。

### Slice H — Entity/Maps 强化与索引健康（1d）

- **Do**：entity 模板 typed fields；`/review` weekly 强制扫「被提及未建 entity」；index 分区去掉长期「待 ingest」空壳或改成 backlog 链到 inbox。  
- **Don't**：为空学科建空 topic 占位。  
- **Acceptance**：lint/report 列出 missing-entity 候选；index 无误导性空表。  
- **Risks**：entity 爆炸 → 门槛「≥2 入链或用户点名才建」。

### Slice I — Skill 同步与 Canonical 校验（0.5d）

- **Do**：脚本检查 `.agents/skills` 与 `.cursor/.claude/.codex` 哈希一致；文档规定只改 `.agents`。  
- **Don't**：用 submodule 过度抽象。  
- **Acceptance**：故意改副本能被脚本抓出。  
- **Risks**：无。

### Slice J — 轻量静态 HTML/浏览（可选，1–2d）

- **Do**：若需要非编辑器浏览，生成静态站点（社区方向）或允许 Obsidian **只读**打开 `wiki/`。  
- **Don't**：把发布流水线当核心；不绑托管知识库。  
- **Acceptance**：只读链接可点；构建可重复。  
- **Risks**：分心；优先级低于 A–E。

---

## 8. Top 5 升级切片（影响/成本排序）

| Rank | Slice | 为何排前 |
|------|-------|----------|
| 1 | **A 机器 Lint + Frontmatter 契约** | 杠杆最大；锁住后续所有质量 |
| 2 | **B `/query` + 检索评测集** | 补齐三操作；让「知识可找」可测 |
| 3 | **C Contradiction / Supersession** | 信任感；对齐 2026 共识 |
| 4 | **D Ops log + L2 ingest 级联** | 接近 Karpathy 编译闭环，且保持 L1 轻量默认 |
| 5 | **E Source-clock stale** 或 **G QMD**（若已规划猛增内容则 G 提前） | E 成本更低先做；内容冲量上来再 G |

并行可插：`F` 记忆分层、`I` skill 同步（低风险）。

---

## 9. 风险与开放问题（需用户拍板）

1. **目标体量**：继续「个人阅读+学习」几十页，还是冲向数百页研究 wiki？决定是否立刻上 QMD。  
2. **Ingest 哲学**：保持「小步归档」为主，或接受可选 **L2 重 compile**？  
3. **Obsidian**：是否允许「可选只读前端」，还是严格编辑器+agent？  
4. **Raw 纪律**：是否强制高价值页必须有 `references/raw/` 落盘？  
5. **评测维护者**：retrieval cases 由你写金标，还是接受 agent 起草你审？  
6. **隐私**：公共 GitHub 仓库 vs 未来私密 raw；检索索引是否只留本地。  
7. **Teacher 边界**：learning-progress 是否升级为正式 memory 层 SSOT？  

---

## 10. Sources（URL）

### Primary / 模式

- Karpathy LLM Wiki gist: https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f  
- Raw gist: https://gist.githubusercontent.com/karpathy/442a6bf555914893e9891c11519de94f/raw  
- Erik Evenson, Building an LLM Wiki Part 2: https://erikevenson.net/building-an-llm-wiki-part-2.html  
- Starmorph guide (2026-04-09): https://blog.starmorph.com/blog/karpathy-llm-wiki-knowledge-base-guide  
- llm-wiki-kit SPECIFICATION: https://github.com/MauricioPerera/llm-wiki-kit/blob/main/SPECIFICATION.md  
- pratiyush llm-wiki research clusters: https://pratiyush.github.io/llm-wiki/docs/research.html  
- lemma llm-wiki-v2 notes: https://github.com/xenitV1/lemma/blob/main/docs/research/llm-wiki-v2.md  

### Memory / RAG landscape

- Memory Tool Landscape: https://www.memoryplugin.com/wiki/landscape.html  
- QMD (Tobi Lütke): https://github.com/tobi/qmd  
- Microsoft GraphRAG: https://github.com/microsoft/graphrag  
- LightRAG: https://github.com/HKUDS/LightRAG  
- HippoRAG: https://github.com/OSU-NLP-Group/HippoRAG  
- Mem0: https://github.com/mem0ai/mem0  
- Letta: https://github.com/letta-ai/letta  
- Zep Graphiti: https://github.com/getzep/graphiti  

### 本仓库（只读抽样）

- Repo: https://github.com/masterroland13/wiki  
- `wiki/WIKI_SCHEMA.md`, `AGENTS.md`, `wiki/index.md`, `inbox.md`, `changelog.md`, `ROADMAP.md`  
- Skills: `.agents/skills/{wiki,lint,review}/SKILL.md`  
- Template: `wiki/templates/topic-ingest-template.md`  
- Tree via GitHub Git Trees API: `master` recursive（2026-11-02 拉取）

---

## 11. 调研边界说明

- 未 clone、未 commit、未改远程仓库。  
- Web 检索与页面抓取聚焦 2025–late 2026 模式文与官方/一等博客；未做穷尽竞品评测。  
- 内容计数基于 GitHub tree，可能遗漏 LFS/未跟踪本地文件；以远程 `master` 为准。  

---

*文档结束。下一步建议：用户确认 Top 5 切片优先级与开放问题后，再用 `slice-plan` 落成可施工日计划（仍先确认再写代码）。*
