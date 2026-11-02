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
| `wiki/inbox.md` | **可选**：尚未归档的待办清单 |
| `wiki/maps/` | 主题地图、学习路线、总览 |
| `wiki/roadmaps/` | 细分路线（如某学科子路线） |
| `wiki/topics/` | 主题笔记（概念、读书记录、方法等） |
| `wiki/entities/` | 术语 / 作品 / 人物等短定义页 |
| `wiki/papers/` | 单篇论文阅读笔记 |
| `wiki/projects/` | 按项目归档的知识 |
| `wiki/templates/` | 新页骨架 |
| `wiki/evals/` | `/query` 金标（不是知识页） |

## 默认导航协议

1. 读 `wiki/index.md`
2. 读相关 `wiki/maps/` 或 `wiki/projects/`
3. 再进入 `wiki/topics/`、`wiki/entities/` 等叶子页

回答已有笔记（`/query`）也按这个顺序，并在答案里引用仓库路径。找不到就停，不编造路径。见 `.agents/skills/query/SKILL.md`。

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
3. 大改动：在 `changelog.md` 顶部记一条
4. 体检：按需 `/lint`（先跑 `python3 scripts/lint_wiki.py`，再看脚本不管的导航与模板结构）；语义整理用 `/review`

## 与 `/wiki` · `/query` · `/lint` · `/review` · `/teacher` 的配合

| 技能 | 何时 |
|------|------|
| **/wiki** | 新 URL、截图、聊天、JD → Raw + topic + 导航 |
| **/query** | 用已有 wiki 页回答：index → map/topic，引用仓库路径；找不到就明说 |
| **/review** | inbox、到期页、`growing`/`stale` → 提炼、互链 |
| **/lint** | 先跑 `scripts/lint_wiki.py`，再查导航与模板结构；语义矛盾不在此技能 |
| **/teacher** | 还不会、要推导、系统学习（通用 + CS，见 `domain-cs.md`） |
| **/teacher-cs** | 同上，CS 触发别名（算法、LeetCode、面试） |

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

## YAML frontmatter（按需）

必填建议：`type`、`status`、`created`、`updated`、`tags`、`sources`

`type`：`topic` | `map` | `paper` | `entity` | `project-note`  
`status`：`seed` | `growing` | `stable` | `stale`

`growing` / `stale` 建议补 `confidence`（0.0–1.0）、`review_after`（YYYY-MM-DD）。

高价值页：一句结论 + 来源 + ≥2 个 Related；ingest 页补 claim / evidence / boundary（见 `templates/topic-ingest-template.md`）。

可执行契约见下一节。没写进机器规则的「建议」（含 `confidence`）不会让脚本失败。

## 机器规则子集（`scripts/lint_wiki.py`）

本表是可失败的契约。矛盾、supersession、source mtime、向量检索不在本子集。故意写坏的页面不入库；`scripts/test_lint_wiki.py` 用临时文件断言路径和退出码。

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
| 知识页 | 检查 frontmatter。不含 `wiki/changelog.md`、`wiki/WIKI_SCHEMA.md`、任意 `README.md`、`wiki/templates/template-design-rationale.md`、`wiki/references/**`、`wiki/evals/**` |
| `wiki/templates/**` | 仍检查 frontmatter；不把骨架链接当断链。模板按复制后的目录写相对路径（项目笔记在 `wiki/projects/<name>/`），`example-*.md` 故意不存在 |
| `wiki/evals/**` | 金标，不是知识页：不查 frontmatter，也不当 orphan。仍检查相对链接 |
| orphan 候选 | 除 `wiki/index.md`、`wiki/templates/**` 与 `wiki/evals/**` 外，没有其它 wiki 页用 Markdown 链入 |

只解析文件开头的 frontmatter。正文里后来的 `---` 块不是元数据。未列出的键（`title`、`confidence`、`project` 等）不导致失败。

### 级别

| 检查 | 级别 |
|------|------|
| 缺少 frontmatter，YAML 无法解析，或不是 mapping | error |
| 缺少 `type` / `status` / `created` / `updated` / `tags` / `sources` | error |
| `type` 不在 `topic` \| `map` \| `paper` \| `entity` \| `project-note` | error |
| `status` 不在 `seed` \| `growing` \| `stable` \| `stale` | error |
| `created` / `updated` / 非空的 `review_after` 不是合法 `YYYY-MM-DD` | error |
| `tags` / `sources` 不是列表，或某个 tag 不是非空字符串 | error |
| `sources` 中的相对路径不存在（URL 跳过；没有 `/` 且不以 `.md` 结尾的标签跳过） | error |
| Markdown 或图片的相对链接目标不是已存在文件 | error |
| `growing` 或 `stale` 缺少 `review_after` | warning |
| orphan 候选 | warning |

`tags` 与 `sources` 可以是空列表。`seed` / `stable` 可以不写 `review_after`。

### 退出码

| 码 | 含义 |
|----|------|
| 0 | 没有 error。允许 warning |
| 1 | 有 error；或加上 `--strict` 时有 warning |
| 2 | 用法错误、找不到 `wiki/`、或未安装 PyYAML |

默认不把 warning 当失败，本脚本因此不是 CI 阻断门。`/lint` 必须先跑脚本，再看导航和模板结构。`confidence` 与语义矛盾仍由人判断。

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
