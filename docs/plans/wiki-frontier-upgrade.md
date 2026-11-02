# Wiki 前沿升级施工计划

> 仓库：https://github.com/masterroland13/wiki（`master`）  
> 调研真源：[`llm-wiki-frontier-2026-11.md`](../research/llm-wiki-frontier-2026-11.md)  
> 审查手册：[`wiki-slice-audit.md`](../handbooks/wiki-slice-audit.md)  
> 冲突序：`AGENTS.md` / `wiki/WIKI_SCHEMA.md` > `ROADMAP.md` > 本计划 > 其它 docs  
> 北极星：git + markdown + agent；Obsidian 最多只读  
> 状态：2026-11-02 已确认。本轮只施工 **Slice A**。  
> 日期：2026-11-02（Asia/Shanghai）

---

## 0. 背景与目标

### 0.1 现状一句话
已是 Karpathy LLM Wiki 正确底座（raw → wiki → schema），并领先 gist：`/wiki` `/lint` `/review`、claim 模板、多宿主 skills。内容仍早期；相对 late-2026 的缺口主要是**可测契约**（机器 lint、contradiction/supersession、`/query`、ops log、检索评测），不是换产品。

### 0.2 本阶段目标（可观察）
1. Schema 里写的规则，脚本能失败（机器 lint）。
2. Karpathy 三操作齐全：Ingest / **Query** / Lint（Review、Teacher 保留）。
3. 矛盾与 supersession 有协议与示例，禁止静默覆盖。
4. 有 ops `log.md`；默认仍 L1 小步，可选 L2 级联。
5. 检索有迷你金标集；体量门槛前不上向量全栈。

### 0.3 抄 / 不抄（计划约束）

| 抄 | 不抄 |
|----|------|
| 机器 lint、log.md、contradiction/supersession、`/query`+eval、可选 L2 级联、source-clock stale、记忆分层、skill 同步校验 | Obsidian 写入 SSOT、GraphRAG/LightRAG 全栈、Mem0 存正文、Notion/NotebookLM、默认 raw 向量 RAG、强制每源碰 15 页 |

---

## 1. 全局约定

### 1.1 范围外 / 缓做
- GraphRAG / LightRAG / HippoRAG 服务化
- Obsidian 插件栈作写入真相源；静态站点非本阶段必做（Slice J 可选）
- Mem0 / Letta 云服务必选
- 强制全库重 compile
- 改默认「必须先 Raw 再 Wiki」（保持现有弹性；高价值页可鼓励）
- 本阶段不上付费托管知识库

### 1.2 默认值是否变化
| 项 | 现状 | 本计划 |
|----|------|--------|
| Ingest 默认深度 | L1 小步 | **不变**；L2 为可选开关 |
| 检索 | index + agent 读页 | B 增加 `/query` 流程；G 达阈值才启用混合检索 |
| Lint | 散文 checklist | A 后改为「脚本先跑 + 语义后判」 |
| Obsidian | 非必需 | **不变** |

改默认行为必须单独成刀并在验收写明；本计划无「静默改默认」。

### 1.3 落点层（本仓库无 loop 分层，用目录职责代替）
| 层 | 路径 | 允许写入的刀 |
|----|------|--------------|
| Schema | `AGENTS.md`、`wiki/WIKI_SCHEMA.md`、`CLAUDE.md`（镜像） | 每刀可同步；契约以 Schema 为准 |
| Skills canonical | `.agents/skills/<name>/` | 改技能只改这里 |
| Skills mirrors | `.cursor/` `.claude/` `.codex/` | 由 I 校验；改完同步或脚本报漂移 |
| Scripts | `scripts/` | lint/search/verify；禁止根目录临时脚本 |
| Wiki 内容 | `wiki/**` | 协议示例页、log、evals、模板；不借升级刀重写既有阅读笔记正文 |
| Research/Plans | `docs/research/`、`docs/plans/`（新建） | 落盘调研与本计划（用户确认后） |
| ROADMAP | `ROADMAP.md` | 每阶段末更新 Icebox/完成项 |
| Changelog | `wiki/changelog.md` | 结构性变更追加；非每笔 ops |

禁止：把检索/校验逻辑焊进聊天散文 skill 而无脚本真源；禁止把行为偏好写进 `topics/` 正文（F 后路由明确）。

### 1.4 需要同步的文档（全局）
确认开工后：
1. 落盘 `docs/research/llm-wiki-frontier-2026-11.md`（自调研稿）
2. 落盘 `docs/plans/wiki-frontier-upgrade.md`（本计划）
3. 落盘 `docs/handbooks/wiki-slice-audit.md`（审查手册）
4. 更新 `docs/README.md` 索引（若无则新建）
5. 各刀结束：按刀更新 `wiki/changelog.md`、必要时 `ROADMAP.md`、`AGENTS.md` 索引表

### 1.5 施工纪律（对齐用户档案）
- 一刀一刀；确认「从 X 开始」才动代码
- 不主动 commit/push；用户说提交才提交
- 每刀结束跑 slice-audit；小修就地、大问题只报告
- 测试断言行为；报告真实收集数与结果

### 1.6 建议施工顺序
**A → B → C → D → E**，并行可插 **F、I**；**G** 达体量/评测门槛；**H** 可在 C 后；**J** 最低优先。

---

## 2. 切片明细

### Slice A — 机器 Lint + Frontmatter 契约

> 状态：2026-11-02 已实现（`scripts/lint_wiki.py`、pytest、Schema 机器规则、`/lint` 先跑脚本）。不要在本切片上重做。

- **工期**：0.5–1.5 天  
- **依赖闸门**：无（首刀）  
- **做什么**：
  1. 新增 `scripts/lint_wiki.py`：校验必填 frontmatter（type/status/created/updated/tags/sources）、枚举值、相对链接可达、orphan 候选、`growing|stale` 缺 `review_after` → warn/error
  2. `WIKI_SCHEMA.md` 标明「机器规则子集」与退出码约定
  3. `/lint` skill（`.agents` + 同步宿主副本）改为：先跑脚本 → 再语义检查
  4. README 或 schema 写清运行命令
  5. 必要时 `scripts/fixtures/` 或文档内「故意坏样例」说明（可不入库坏页，用单测临时文件）
- **不做什么**：语义矛盾检测；CI 强制阻断（可先本地 warn）；上向量检索；重写既有笔记正文
- **正向验收**：
  - `python scripts/lint_wiki.py` 在当前仓库可跑通并打印摘要
  - 故意缺字段 / 坏相对链接时报告**具体路径**
  - exit code：有 error ≠ 0；仅 warn 可用约定码或 flag 区分（文档写明）
  - `/lint` skill 明文要求先跑脚本
- **反向验收**：
  - 根目录无临时 lint 脚本残留
  - 未改 ingest 默认深度
  - 未引入 Obsidian/CI 必过门（除非另刀）
- **落点层**：`scripts/` + Schema + `.agents/skills/lint/`（+ mirrors）
- **测试命令**：
  - `python scripts/lint_wiki.py`（全库）
  - `python -m pytest scripts/test_lint_wiki.py -q`（若有；对临时坏 fixture 断言报错路径）
  - 无 pytest 时：文档化的手工正/反例 + 脚本自检函数
- **易返工点**：历史页大量 warn → baseline allowlist 或分批修；YAML 边缘语法；Windows/WSL 路径

### Slice B — `/query` Skill + 迷你检索评测集
- **工期**：1–2 天  
- **依赖闸门**：A 完成（index/链接健康更可信）；可与 F 并行概念工作，但技能落盘在 A 后
- **做什么**：
  1. `.agents/skills/query/SKILL.md`：流程 = 读 `wiki/index.md` → 选相关 map/topic → 作答并**引用仓库路径**；找不到则明确失败协议；高价值答案可提议回写（不自动大改）
  2. `wiki/evals/retrieval-cases.md`（或 json）10–20 条：`问题 → 期望打开的页路径`（含释义问法）
  3. 可选 `scripts/eval_retrieval_checklist.md` 记录人工/agent 命中
  4. `AGENTS.md` 技能表与 Schema「与技能配合」表增加 `/query`
  5. 同步宿主 skill 副本
- **不做什么**：引入向量库/QMD（留给 G）；默认对 `references/raw` 做 RAG SSOT；自动全库回写
- **正向验收**：
  - 评测集存在且 ≥10 条；含至少 3 条非标题同词问法
  - 按 skill 流程，约定命中率目标（建议 ≥70% 打开正确页或明确「找不到」而非瞎编）
  - 答案模板要求列出所读路径
- **反向验收**：
  - 无 embedding 服务依赖
  - 失败时不伪造来源路径
- **落点层**：`.agents/skills/query/` + `wiki/evals/` + Schema/AGENTS
- **测试命令**：按 `retrieval-cases` 走 1 轮抽检记录；可选轻量脚本检查 cases 文件格式与期望路径存在
- **易返工点**：评测过拟合 index 措辞；金标谁维护（默认：agent 起草、你审）

### Slice C — Contradiction / Supersession 协议
- **工期**：1–1.5 天  
- **依赖闸门**：A（frontmatter 字段可被 lint 认知）
- **做什么**：
  1. 模板增加 `## Contradictions`、`## Superseded`（或等价）；frontmatter 可选 `supersedes` / `superseded_by`
  2. `/wiki` `/review` 增加：「发现冲突禁止静默覆盖；必须显式块或字段」
  3. lint 可列出：带 `superseded_by` 仍被 index 主推的页（warn）
  4. 至少 1 个示例页（可用合成 demo 页，避免篡改既有阅读结论）
  5. Schema 写清字段可选性与高价值页才填
- **不做什么**：自动裁判对错；上图数据库；强制所有旧页回填
- **正向验收**：示例页可演示冲突并存；schema/skills 交叉引用一致；lint 识别 superseded 主推 warn
- **反向验收**：未静默删改既有主张；未新增必填字段导致全库变红（保持可选）
- **落点层**：`wiki/templates/` + Schema + skills wiki/review/lint + 示例页
- **测试命令**：`python scripts/lint_wiki.py`；打开示例页人工对照协议
- **易返工点**：字段过多导致 ingest 摩擦 → 严格可选

### Slice D — Ops Log + 可选 L2 Ingest 级联
- **工期**：1–2 天  
- **依赖闸门**：A；C 协议已写入 wiki skill 更佳（可弱依赖）
- **做什么**：
  1. 新增 `wiki/log.md`（操作日志；与 `changelog.md` 职责分离）
  2. 条目前缀约定：`## [YYYY-MM-DD] ingest|query|lint | title`
  3. `/wiki` 增加 **L2 compile 可选路径**：更新相关 entity/map/index + 写 log；**默认仍 L1**
  4. Schema/AGENTS 说明 log vs changelog；index 链到 log（可选）
- **不做什么**：每次小补丁写 changelog；强制每源 10–15 页；把 changelog 改成 ops log
- **正向验收**：一次文档化的 L2 演练有 log 条目且 index/map/entity 有预期触达；用户可只开 L1
- **反向验收**：默认路径仍是小步归档；未级联重写无关阅读笔记风格正文
- **落点层**：`wiki/log.md` + `/wiki` skill + Schema
- **测试命令**：按 skill 检查清单走一遍 L1/L2 dry-run（可在 PR 描述复述）；lint 不因 log 格式失败
- **易返工点**：级联范围膨胀 → 限定 entity/map/index/log

### Slice E — Source-clock Stale 检测
- **工期**：0.5–1 天  
- **依赖闸门**：A
- **做什么**：
  1. 当 `sources` 含仓库内 raw 路径时，比较页 `updated` 与源 mtime（或源 frontmatter date）
  2. 过期 → lint warn + 建议 `status: stale`
  3. 文档写明：纯 URL sources 无 mtime则跳过
- **不做什么**：自动重写全文；对 URL 伪造成 stale
- **正向验收**：人为调源文件时间可触发 warn；无 repo 内 sources 的页跳过
- **反向验收**：无自动改 status 写回（除非用户另刀授权）
- **落点层**：`scripts/lint_wiki.py` + Schema
- **测试命令**：pytest/fixture 或脚本内单元测试；全库 lint
- **易返工点**：时区/git checkout 时间；WSL 与 Windows mtime

### Slice F — 行为记忆层制度化（可插）
- **工期**：0.5–1 天  
- **依赖闸门**：无（建议 A 后，与 B 可交错）
- **做什么**：Schema/AGENTS 明确：`wiki/projects/learning-progress/`（或约定路径）= 偏好/纠错/教学进度；禁止写入 topic 正文；`/teacher` `/review` 启动读该层；给一例「事实在 topic、偏好在 memory」
- **不做什么**：Mem0 云必选
- **正向验收**：阅读顺序含 memory；写入路由表存在
- **反向验收**：未把 memory 当 topic 索引主入口
- **落点层**：Schema + AGENTS + teacher/review skills + 示例
- **测试命令**：文档审查 + 路由表存在性检查（可挂 lint warn）
- **易返工点**：两层重复 → 路由表写清

### Slice G — 可选 Hybrid 检索（门槛后）
- **工期**：1.5–2.5 天  
- **依赖闸门**：**B 评测集存在**；且（wiki 实质页 ≥50 **或** 纯 index 命中率低于约定阈值）
- **做什么**：QMD CLI/MCP 或 `scripts/search_wiki.py`；索引限 `wiki/**/*.md`；`/query` 在 index 不足时 fallback；更新 ROADMAP
- **不做什么**：索引隐私 raw 到远程；替换 index-first；未达门槛强行上
- **正向验收**：同评测集有可测提升；离线可跑
- **反向验收**：无远程向量库默认依赖
- **落点层**：scripts 或外部 CLI 文档 + query skill + ROADMAP
- **测试命令**：评测集前后对比表；搜索 smoke
- **易返工点**：WSL 模型体积；维护成本

### Slice H — Entity/Maps 强化与索引健康（可插）
- **工期**：1 天  
- **依赖闸门**：A；建议 C 后
- **做什么**：entity 模板 typed fields；`/review` weekly 扫「提及未建 entity」（门槛 ≥2 入链或用户点名）；index 去掉长期空壳「待 ingest」或改链 inbox
- **不做什么**：为空学科建空 topic
- **正向验收**：报告 missing-entity 候选；index 无误导空表
- **反向验收**：entity 未爆炸（有门槛）
- **落点层**：templates + review skill + index 清理
- **测试命令**：lint + 人工看 index
- **易返工点**：门槛过低

### Slice I — Skill 同步与 Canonical 校验（可插）
- **工期**：0.5 天  
- **依赖闸门**：无；建议每改 skill 后跑
- **做什么**：`scripts/check_skill_sync.py`：`.agents/skills` vs `.cursor/.claude/.codex` 哈希；文档规定只改 `.agents` 再同步
- **不做什么**：submodule 过度抽象
- **正向验收**：故意改副本能被抓出
- **反向验收**：无
- **落点层**：`scripts/` + AGENTS/ROADMAP（勾掉 Icebox 对应项）
- **测试命令**：`python scripts/check_skill_sync.py`
- **易返工点**：无

### Slice J — 轻量只读浏览（可选，最低优先）
- **工期**：1–2 天  
- **依赖闸门**：用户明确要
- **做什么**：静态 HTML 或 Obsidian **只读**打开 `wiki/`
- **不做什么**：发布流水线核心化；托管知识库
- **正向验收**：只读可点链接；构建可重复
- **反向验收**：未成为写入 SSOT
- **落点层**：可选 `docs/` 或 GitHub Pages 说明
- **测试命令**：本地打开抽检
- **易返工点**：分心；默认不做

---

## 3. 里程碑与合并策略

| 里程碑 | 含刀 | 完成定义 |
|--------|------|----------|
| M1 契约底座 | A（+I 更好） | 机器 lint 日可用 |
| M2 可查询 | B | 三操作齐；有金标 |
| M3 可信生命周期 | C、E | 冲突/过期可表达 |
| M4 编译闭环 | D（+F） | log + 可选 L2；记忆分层 |
| M5 规模检索 | G（门槛） | 评测可证提升 |

每刀建议独立 PR/提交意图（用户授权后再 commit）；禁止一个大 PR 糊弄多里程碑。

---

## 4. 开放问题（默认假设，可改）

| # | 问题 | 本计划默认假设 |
|---|------|----------------|
| 1 | 目标体量 | 近月仍「几十页学习 wiki」→ G 缓做 |
| 2 | Ingest | 默认 L1；L2 可选 |
| 3 | Obsidian | 不引入；J 仅你点名 |
| 4 | Raw 纪律 | 不强制；高价值鼓励 |
| 5 | 评测金标 | agent 起草，你审 |
| 6 | 公共仓隐私 | 检索索引只本地；raw 慎放秘密 |
| 7 | learning-progress | F 升为正式 memory 层 |

---

## 5. 确认清单

- [x] 同意抄/不抄与范围外
- [x] 同意顺序 A→B→C→D→E；本轮只做 Slice A
- [x] 同意默认假设（未另行修订）
- [x] 2026-11-02 确认：落盘 docs，并实现 Slice A

后续切片仍遵守：不改 ingest 默认深度；不上 GraphRAG / Obsidian 写入真相源；不重写既有阅读笔记正文。未确认的切片不开工。
