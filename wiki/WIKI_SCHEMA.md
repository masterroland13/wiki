# Wiki Schema

本文件约定 **长期维护方式**：可复用知识放在 `wiki/`；`references/raw/` 与 `references/papers/` 为 **原始材料库**（尽量不改写原文）。

设计目标：**Git + 编辑器 + Agent 可长期维护**；Obsidian 仅作可选浏览器。

## 分层

| 层 | 路径 | 用途 |
|----|------|------|
| Raw | `references/raw/` | 剪藏、备份、长文、草稿；**默认不删改原文** |
| Papers | `references/papers/` | PDF 原件（可选） |
| Wiki | `wiki/` | 长期笔记与导航 |
| Schema | `AGENTS.md` + 本文件 | 仓库说明与目录约定 |

## `wiki/` 目录分工

| 路径 | 作用 |
|------|------|
| `wiki/index.md` | 总入口与索引表 |
| `wiki/changelog.md` | 结构性变更时追加（非每笔必写） |
| `wiki/log.md` | 操作日志：ingest / query / lint。与 changelog 分开。默认 L1 不写 ingest 条目 |
| `wiki/inbox.md` | **可选**：尚未归档的待办清单 |
| `wiki/maps/` | 主题地图、学习路线、总览 |
| `wiki/roadmaps/` | 细分路线（如某学科子路线） |
| `wiki/topics/` | 主题笔记（概念、读书记录、方法等） |
| `wiki/entities/` | 术语 / 作品 / 人物等短定义页 |
| `wiki/papers/` | 单篇论文阅读笔记 |
| `wiki/projects/` | 按项目归档的知识。其中 `learning-progress/` 是行为记忆层，不是主题事实 |
| `wiki/templates/` | 新页骨架 |
| `wiki/evals/` | `/query` 金标（不是知识页） |

## 默认导航协议

1. 读 `wiki/index.md`
2. 读相关 `wiki/maps/` 或 `wiki/projects/`
3. 再进入 `wiki/topics/`、`wiki/entities/` 等叶子页

回答已有笔记（`/query`）也按这个顺序，并在答案里引用仓库路径。找不到就停，不编造路径。见 `.agents/skills/query/SKILL.md`。事实题不从行为记忆层起读。

`/teacher`、`/teacher-cs` 与 `/review` 在讲课或复盘之前，额外读下一节的行为记忆层。那一步不改变上面的主题导航，也不把该层当成 `index.md` 的主题主入口。

## 行为记忆与写入路由

`wiki/projects/learning-progress/` 是**行为记忆层**：学习者偏好、纠错、教学进度。可复用事实（概念、读书结论、可引用主张）留在 `wiki/topics/`、`wiki/entities/`、`wiki/papers/`，导航留在 `wiki/maps/` 与 `wiki/index.md`。

本层**不是**知识的单一真相源，也**不是**主题索引。`wiki/index.md` 可以在「项目」里轻链 hub（[`projects/learning-progress/index.md`](./projects/learning-progress/index.md)）。不要把偏好页放进文艺、人文、理工、跨学科这些主题分区。不要求 Mem0、Letta 或任何云端记忆；本层就是仓库里的 Markdown，可 git 审计。

本地说明与同一张路由表：[`projects/learning-progress/README.md`](./projects/learning-progress/README.md)。若两处表述不一致，以本节为准。

**禁止**把行为偏好写进 topic、entity、paper 的正文。一句里既有测量结果又有「下次怎么教我」，拆开：结果进 topic，教法进本层。

### 写入路由

| 写什么 | 写到哪里 | 不要写到哪里 |
|--------|----------|----------------|
| 可复用事实、概念、读书结论、可引用主张 | `wiki/topics/`、`wiki/entities/`、`wiki/papers/`；导航在 `wiki/maps/` 与 `wiki/index.md` | `wiki/projects/learning-progress/` |
| 学习者偏好（节奏、语言、要提示还是要结论、纠错口吻） | `wiki/projects/learning-progress/`（`learner-profile.md` 或 `preferences/`） | topic / entity / paper 正文 |
| 纠错与「下次怎么教」 | 同上 | topic / entity / paper 正文 |
| 教学进度、场景水平、未完成任务 | `wiki/projects/learning-progress/`（hub，以及已有的 `scenes/` 等） | topic / entity / paper 正文 |
| 原始材料 | `references/raw/` 或 `references/papers/` | 不把偏好改写成 raw，也不把 raw 改成偏好 |
| 一次 ingest / query / lint | `wiki/log.md`（动词与默认 L1 规则见「操作日志与 changelog」，本层不新增动词） | 不把偏好当成一条 log |
| 目录约定或 schema 变更 | `wiki/changelog.md` | 不把一次教学偏好写成结构性变更 |

`/teacher` 与 `/review` 启动时先读本层（README 的路由表、hub、learner profile；场景页按需），再讲课或复盘。`/wiki` 归档事实时走 topic，不把偏好塞进 topic。`/query` 回答事实时不把本层当证据；只有问题明确在问偏好、纠错或进度时才打开它，并标明这是行为记忆。

合成示例（虚构，不是阅读笔记）：事实在 [`topics/x-demo-fact-vs-preference.md`](./topics/x-demo-fact-vs-preference.md)（北窗焦点块的小时完成数）；偏好在 [`projects/learning-progress/preferences/demo-hint-first.md`](./projects/learning-progress/preferences/demo-hint-first.md)（先给提示、单次不超过 25 分钟、先用中文纠正）。两边互链，偏好不写进 topic 正文。

## 学科 slug 前缀（建议）

| 域 | 前缀 | 示例 |
|----|------|------|
| 文学 | `lit-` | `lit-magical-realism.md` |
| 电影/影像 | `film-` | `film-editing-rhythm.md` |
| 音乐 | `music-` | `music-modal-jazz.md` |
| 计算机 | `cs-` | `cs-dp-intro.md` |
| 哲学 | `phil-` | `phil-stoicism.md` |
| 物理 | `phys-` | `phys-entropy-intuition.md` |
| 天文 | `astro-` | `astro-exoplanets.md` |
| 跨学科 | `x-` | `x-info-theory-physics.md` |
| 实体 | `entity-` | `entity-author-orwell.md` |

实体页统一放 `wiki/entities/`；主题页放 `wiki/topics/`。**导航**靠 `index.md` 分区，不靠再建一层学科文件夹。

## 两段式工作流

1. **Capture**：新想法先落 `wiki/inbox.md` 或临时页
2. **Review**：按周 `/review`，沉淀到 `topics/` / `maps/` / `entities/`
3. **Archive**：值得反复找到的页，从 `index.md` 或 map 链入

详见 [`maps/capture-review-archival-workflow.md`](./maps/capture-review-archival-workflow.md)。

## 维护习惯（轻量）

1. 新材料：可进 `references/raw/`；复用结论写在 `wiki/`，并链回 Raw
2. 导航：从 `index.md` 或 map 链到值得反复打开的页
3. 结构性变更：在 `changelog.md` 顶部记一条。小补丁和默认 L1 归档不必写
4. 操作流水：写在 `log.md`（见下节）。不要把 changelog 当成 ops log
5. 体检：按需 `/lint`（先跑 `python3 scripts/lint_wiki.py`，再看脚本不管的导航与模板结构）；语义整理用 `/review`
6. 技能：只改 `.agents/skills/`，再同步宿主镜像，并用 `python3 scripts/check_skill_sync.py` 核对。不要把某一宿主副本当成另一份原文

## 与 `/wiki` · `/query` · `/lint` · `/review` · `/teacher` 的配合

| 技能 | 何时 |
|------|------|
| **/wiki** | 新 URL、截图、聊天、JD → Raw + topic + 导航。**默认 L1**。用户说出「L2 / 深挖 / compile / 级联」才走 L2 compile（相关 entity、相关 map、index + 一条 ingest log）。与已有页冲突时禁止静默覆盖，须写矛盾块或 supersession 字段 |
| **/query** | 用已有 wiki 页回答：index → map/topic，引用仓库路径；找不到就明说。页与页冲突时并列引用，不选边。结束时在 `log.md` 追加一条 `query`（不是知识回写） |
| **/review** | inbox、到期页、`growing`/`stale` → 提炼、互链。启动时先读行为记忆层。冲突时禁止静默覆盖，须写矛盾块或 supersession 字段。偏好与纠错写回 `learning-progress/`，不写进 topic 正文 |
| **/lint** | 先跑 `scripts/lint_wiki.py`，再查导航与模板结构。脚本会警告 `superseded_by` 页仍被 `wiki/index.md` 主推。哪一边为真不在此技能。结束时在 `log.md` 追加一条 `lint`（记下 error / warning 数），不要为此再跑一轮 lint。改过技能后可选再跑 `scripts/check_skill_sync.py`（不改变 lint 的退出码约定） |
| **/teacher** | 还不会、要推导、系统学习（通用 + CS，见 `domain-cs.md`）。启动时先读行为记忆层。偏好不写进 topic 正文 |
| **/teacher-cs** | 同上，CS 触发别名（算法、LeetCode、面试） |

## 技能正文的单一真相源

技能正文的 canonical 是 `.agents/skills/`。[`scripts/check_skill_sync.py`](../scripts/check_skill_sync.py) 按文件做 SHA-256 对照。`.cursor/skills/`、`.claude/skills/`、`.codex/skills/` 只是宿主镜像，不是第二份真相源。

**只改 `.agents/skills/`，再把同一内容同步到三个宿主目录。** 不要在某一宿主副本里单独改出分歧，也不要把镜像当成该改的原文。

空目录不参与比较。跳过 `__pycache__/`、`.DS_Store`、`*.pyc`。不跟随目录符号链接。

```bash
python3 scripts/check_skill_sync.py
```

| 码 | 含义 |
|----|------|
| 0 | 每个镜像文件都与 `.agents/skills/` 的字节一致 |
| 1 | 漂移：内容哈希不同、镜像缺文件，或镜像多出 canonical 没有的文件。标准输出打印这些路径（`DIFFERS` / `MISSING` / `EXTRA`） |
| 2 | 用法错误，或找不到 canonical 目录 `.agents/skills/` |

漂移是 error，不是 warning。没有「只警告仍退出 0」的模式。这个脚本不修改 `scripts/lint_wiki.py` 的契约；`/lint` 可以在机器 lint 之外再跑它。

## 检索（`/query`）

不另建向量库。默认也不对 `references/raw/` 做 RAG。

1. 读 `wiki/index.md`，再打开相关 map / project，然后打开 topic / entity
2. 答案列出读过的仓库路径
3. 没有能支撑回答的页：写明 **I can't find**（找不到），不编造路径
4. 高价值答案可以提议写回；不自动改完整库，不借答题改写既有阅读笔记正文

金标：[`evals/retrieval-cases.md`](./evals/retrieval-cases.md)。检查格式和期望路径（故意缺失的题目标成 `intentional-miss`，期望路径为空）：

```bash
python3 scripts/check_retrieval_cases.py
```

这个脚本不回答问题，也不调用 embedding。抽检目标是 ≥70% 打开期望页，或明确说找不到。

## 操作日志与 changelog

两份都按时间追加，职责不同。

| 文件 | 记什么 | 不记什么 |
|------|--------|----------|
| [`log.md`](./log.md) | ingest / query / lint 的一次操作 | 目录约定、schema 契约、技能体系 |
| [`changelog.md`](./changelog.md) | 结构性变更 | 每一次查询、每一次 lint、每一次 L1 小补丁 |

`log.md` 最新条目在顶部。标题能被 grep，动词只能是 `ingest`、`query`、`lint` 之一：

```text
## [YYYY-MM-DD] ingest | 标题
## [YYYY-MM-DD] query | 标题
## [YYYY-MM-DD] lint | 标题
```

这就是 `## [YYYY-MM-DD] ingest|query|lint | title`：方括号里的日期、一个动词、空格、竖线、空格、一行标题。不要把字面量 `ingest|query|lint` 写进标题。

| 动词 | 何时写 |
|------|--------|
| `ingest` | **L2 compile 必写**。L0 / L1 默认不写 |
| `query` | 每次 `/query` 结束写一条，包括回答是「找不到」 |
| `lint` | 每次 `/lint` 结束写一条，记下 error 与 warning 的数量 |

归档深度默认仍是 **L1**（小步：一篇 topic，需要时在 index 或一个 map 上加一条入口）。用户没有说出「L2」「深挖」「compile」「级联」时，不要升级，不要级联 entity。来源看起来重要，也不自动升级。

L2 compile 只在 L1 那一页之外多做四件事：更新**相关** entity（短定义或一条链接）、**相关** map（一行链接；没有合适的 map 且会反复打开才新建）、`index.md` 对应分区的一行，以及 `log.md` 顶部的一条 `ingest`。不改无关阅读笔记的正文和文风，不按「每源 10–15 页」凑数，不自动裁定矛盾，也不因为这次归档去写 changelog。changelog 只在同一次改动了目录约定或 schema 时才写。

`log.md` 不是知识页。和 `changelog.md` 一样**不要求 frontmatter**。机器 lint 仍检查里面的相对链接。还没建出来的预期路径用反引号，不要写成 Markdown 链接。细则与 opt-in 用语见 `.agents/skills/wiki/SKILL.md`。演练条目在 [`log.md`](./log.md)（`L2 dry-run — synthetic example-widget`）：只列出预期触达，没有创建那些页。

## YAML frontmatter（按需）

必填建议：`type`、`status`、`created`、`updated`、`tags`、`sources`

`type`：`topic` | `map` | `paper` | `entity` | `project-note`  
`status`：`seed` | `growing` | `stable` | `stale`

`growing` / `stale` 建议补 `confidence`（0.0–1.0）、`review_after`（YYYY-MM-DD）。

高价值页：一句结论 + 来源 + ≥2 个 Related；ingest 页补 claim / evidence / boundary（见 `templates/topic-ingest-template.md`）。冲突或更换阅读入口时，再补下面的可选块，不必给旧页补字段。

可执行契约见「机器规则子集」。没写进机器规则的「建议」（含 `confidence`，以及空着的 `supersedes` / `superseded_by`）不会让脚本失败。

## 矛盾与取代（可选）

只在高价值页使用。普通页和旧页不用回填。这里不判断哪一边为真，也不建图数据库。

两条主张对不上时，**禁止静默覆盖**：不要删改已有句子来显得一致，也不要只留下认为对的一边。把双方写进 `## Contradictions`（对方路径、两边主张、各自来源）。需要换「先读哪一页」时，旧页留在仓库里，用 `## Superseded` 和下面的字段留痕。取代只表示阅读入口变了，不表示旧主张为假。

| 字段 | 何时写 | 形状 |
|------|--------|------|
| `supersedes` | 本页取代了哪些页的阅读位置 | 省略、空、一个相对路径，或路径列表 |
| `superseded_by` | 哪些页取代了本页的阅读位置 | 同上 |

路径相对**当前页**，与 Markdown 链接相同（例如 `./other-topic.md`）。两个字段都可以不写。不要为此新增 `status` 枚举。

模板里的 `## Contradictions` 与 `## Superseded` 可以留空。合成示例（两边主张都在，旧归档建议被标成取代但没有删掉）：[`topics/x-demo-contradiction-coexistence.md`](./topics/x-demo-contradiction-coexistence.md)，被取代的一页是 [`topics/x-demo-superseded-filing.md`](./topics/x-demo-superseded-filing.md)。

`/wiki` 与 `/review` 发现冲突时必须走这一节，不能直接改掉旧主张。`/query` 并列引用冲突页，不选边。`/lint` 只做下一节的机械警告。

## 机器规则子集（`scripts/lint_wiki.py`）

本表是可失败的契约。哪一边主张为真、向量检索不在本子集。source-clock 只比较 `wiki/` 外已存在文件的 mtime 日期与 `updated`，不改页面。`superseded_by` 仍被 index 主推是 warning，规则写在下面。故意写坏的页面不入库；`scripts/test_lint_wiki.py` 用临时文件断言路径和退出码。

依赖：Python 3.11+、PyYAML。测试另需 pytest。

```bash
python3 scripts/lint_wiki.py
python3 scripts/lint_wiki.py --strict
python3 -m pytest scripts/test_lint_wiki.py -q
```

`python` 在指向 Python 3 时与 `python3` 相同。本仓库其它脚本示例使用 `python3`。

### 扫描范围

| 范围 | 行为 |
|------|------|
| `wiki/**/*.md` | 检查行内相对链接与图片。跳过 fenced code、行内代码、带 scheme 的 URL、`//`、纯锚点，以及路径里含 `<` `>` `*` 的占位符 |
| 知识页 | 检查 frontmatter。不含 `wiki/changelog.md`、`wiki/log.md`、`wiki/WIKI_SCHEMA.md`、任意 `README.md`、`wiki/templates/template-design-rationale.md`、`wiki/references/**`、`wiki/evals/**`。`wiki/log.md` 与 changelog 一样豁免：操作日志的标题前缀不是知识页字段，缺 frontmatter 不是 error。相对链接照查 |
| `wiki/templates/**` | 仍检查 frontmatter；不把骨架链接当断链。模板按复制后的目录写相对路径（项目笔记在 `wiki/projects/<name>/`），`example-*.md` 故意不存在 |
| `wiki/evals/**` | 金标，不是知识页：不查 frontmatter，也不当 orphan。仍检查相对链接 |
| orphan 候选 | 除 `wiki/index.md`、`wiki/templates/**` 与 `wiki/evals/**` 外，没有其它 wiki 页用 Markdown 链入 |

只解析文件开头的 frontmatter。正文里后来的 `---` 块不是元数据。未列出的键（`title`、`confidence`、`project`，以及省略或为空的 `supersedes` / `superseded_by`）不导致失败。

### 级别

| 检查 | 级别 |
|------|------|
| 缺少 frontmatter，YAML 无法解析，或不是 mapping | error |
| 缺少 `type` / `status` / `created` / `updated` / `tags` / `sources` | error |
| `type` 不在 `topic` \| `map` \| `paper` \| `entity` \| `project-note` | error |
| `status` 不在 `seed` \| `growing` \| `stable` \| `stale` | error |
| `created` / `updated` / 非空的 `review_after` 不是合法 `YYYY-MM-DD` | error |
| `tags` / `sources` 不是列表，或某个 tag 不是非空字符串 | error |
| `sources` 中像路径的条目，按当前页相对路径和仓库根相对路径都找不到文件（URL 跳过；没有 `/` 且不以 `.md` 结尾的标签跳过） | error。消息：`sources path not found: {条目}` |
| Markdown 或图片的相对链接目标不是已存在文件 | error |
| `growing` 或 `stale` 缺少 `review_after` | warning |
| orphan 候选 | warning |
| `superseded_by` 已设置，且 `wiki/index.md` 仍有直接 Markdown 链接指向该页 | warning。消息：`superseded_by is set but wiki/index.md still links to this page` |
| `supersedes` 或 `superseded_by` 不是字符串，也不是字符串列表 | warning。消息：`{字段} must be a path or a list of paths` |
| 上述字段里像路径的条目不存在 | warning。消息：`{字段} path not found: {条目}`。不像路径的标签跳过 |
| `wiki/` 外的 source 文件，其 mtime 本地日历日期晚于 `updated` | warning。消息：`source '{路径}' is newer than updated ({源日期} > {updated}); consider status: stale`。不写回 `status` |
| `wiki/projects/learning-progress/` 这个目录存在，但缺少 `README.md` | warning。消息：`learning-progress README.md is missing (write-routing table)`。目录不存在则不查 |
| 该 `README.md` 存在，但没有标题 `## 写入路由` | warning。消息：`learning-progress README.md is missing the write-routing table`。不因此让全库失败 |

`tags` 与 `sources` 可以是空列表。`seed` / `stable` 可以不写 `review_after`。`supersedes` 与 `superseded_by` 可以省略、为空字符串或空列表。

**Index 主推（本脚本的精确定义）**：只看 `wiki/index.md` 正文里的 Markdown 链接。忽略 fenced code、行内 code、带 scheme 的 URL、`//` 和纯锚点，规则与其它相对链接相同。链接解析到带非空 `superseded_by` 的文件，就记一条 warning，路径打在该页上。

- 「已设置」指字段是非空字符串，或列表里至少有一条非空字符串。空值不算。
- 形状不合法时只报形状 warning，不算已设置，因此不会同时报主推 warning。
- 只从 map、使用手册（[`wiki教学与使用手册`](./maps/wiki-teaching-usage-handbook.md)）、`wiki/projects/**/index.md` 或其它 topic 链入，不算主推。不沿链接再走一层。
- 只写了 `supersedes`、没有 `superseded_by` 的页，可以继续留在 index 里。
- 处理这条 warning 时：从 `wiki/index.md` 拿掉该链接，保留页面，让后继页链过来。不要删页，也不要为了消 warning 改写主张。

### Source-clock（mtime 日期）

时钟只用文件系统 mtime（`st_mtime`），不用源 frontmatter 里的日期，也不读 git 历史。Raw、PDF 和图片通常没有 YAML 日期；mtime 对每个已存在文件都有定义。

**比较规则**

1. 只看知识页 frontmatter 的 `sources`。
2. 条目要能解析成仓库内、且不在 `wiki/` 下的已存在文件。顺序：先按**当前页**的相对路径；该路径上没有文件时，再按**仓库根**的相对路径（repo-relative：不以 `/` 或 `.` 开头，路径段里没有 `..`，解析后仍在仓库内）。典型写法是 `references/raw/...`，或从笔记页写出的 `../../references/raw/...`。页相对路径上已经有文件时用它，不再改看仓库根。
3. 取该文件的 mtime，用**运行 lint 的机器的本地时区**转成日历日期，丢掉时分秒。
4. 页 `updated` 是 `YYYY-MM-DD`，没有时区，也没有时刻。
5. 仅当源日期**晚于** `updated` 时发 warning。同一天不算更新。源日期更早或相同则不发这条 warning。当前 `status` 是什么都不影响这条比较。

**警告原文**（`{路径}` 是 `sources` 里写下的字符串，两个日期都是 `YYYY-MM-DD`）：

`source '{路径}' is newer than updated ({源日期} > {updated}); consider status: stale`

一条 source 一条 warning。脚本不写回 `status`、`updated` 或正文。把 `status` 改成 `stale` 不会消除这条 warning。人在审完来源之后，若把 `updated` 改到不早于源日期，警告才会消失。脚本不做这件事。

**跳过（不发这条 warning，也不把 URL 或标签说成过期）**

- `http` / `https` 以及其它带 scheme 的 URL，和以 `//` 开头的地址
- 纯锚点（`#...`）
- 含 `<` `>` `*` 的占位符
- 不像路径的标签：没有 `/`、不以 `.` 开头、也不以 `.md` 结尾（例如 `synthetic-demo`）
- `sources` 里的 mapping，以及空字符串
- 页相对路径和仓库根相对路径都找不到文件：仍是 error `sources path not found: ...`，不另报 stale
- 解析到仓库外的文件
- 解析到 `wiki/` 里面的文件（笔记互链、`WIKI_SCHEMA.md` 等）
- `updated` 不是合法日期（已有 error），无法比较

`wiki/` 内的文件不参加比较：git checkout 会把这些文件的 mtime 收成同一天，用笔记互链做时钟会在每次检出后大面积误报。

**时区与截断**

比较的是两个日历日期，不是时刻。本地时区由运行环境决定（`datetime.fromtimestamp`）。跨时区或靠近午夜时，WSL 与 Windows 可能差一天。检出仓库会刷新 mtime。`wiki/` 外、且被 `sources` 点名的文件，可能因此显得比页上的 `updated` 新。这仍只是 warning。默认退出码不因此变成失败；`--strict` 时它和其它 warning 一样会让退出码变成 1。

### 行为记忆路由表（存在性）

只在 `wiki/projects/learning-progress/` **已经是目录**时检查。临时夹具和尚未采用该层的仓库没有这个目录，就不发下面的 warning。

| 情况 | 消息 |
|------|------|
| 没有 `README.md` | `learning-progress README.md is missing (write-routing table)` |
| 有 `README.md`，正文没有标题 `## 写入路由` | `learning-progress README.md is missing the write-routing table` |

两条都是 warning，不是 error。默认退出码不因此变成失败。脚本不创建文件，也不把路由表写进 topic。标题按子串匹配；写在 fenced code 里也算有这份标题，人仍应让它出现在正文。

### 退出码

| 码 | 含义 |
|----|------|
| 0 | 没有 error。允许 warning |
| 1 | 有 error；或加上 `--strict` 时有 warning |
| 2 | 用法错误、找不到 `wiki/`、或未安装 PyYAML |

默认不把 warning 当失败，本脚本因此不是 CI 阻断门。`/lint` 必须先跑脚本，再看导航和模板结构。`confidence` 与哪一边主张为真仍由人判断。可选 supersession 字段的坏路径是 warning，不是 error，因此不会因为没填这些字段而让全库失败。

## Raw 与 URL

- 可不「先 Raw 再 Wiki」；小结论可直接写 `wiki/`，`sources` 挂 URL
- 长/杂/含图/重要来源：先 `references/raw/`
- 仅 URL：Agent 抓取或 `scripts/ingest_url_to_raw.py`（可加 `--fetch-images`）

归档深度 L0/L1/L2：见 [`references/archive-depth.md`](../references/archive-depth.md)。  
图片：见 [`references/image-ingest.md`](../references/image-ingest.md) 与 [`references/image-handling-guide.md`](./references/image-handling-guide.md)。

## 命名

- `wiki/topics/<slug>.md`
- `wiki/maps/<slug>.md`
- `wiki/entities/<slug>.md`
- `wiki/papers/<slug>.md`
- `wiki/projects/<project>/<slug>.md`

静态资源目录统一用 `assets/`。
