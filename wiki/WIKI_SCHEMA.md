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

## 默认导航协议

1. 读 `wiki/index.md`
2. 读相关 `wiki/maps/` 或 `wiki/projects/`
3. 再进入 `wiki/topics/`、`wiki/entities/` 等叶子页

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
4. 体检：按需 `/lint`；语义整理用 `/review`

## 与 `/wiki` · `/lint` · `/review` 的配合

| 技能 | 何时 |
|------|------|
| **/wiki** | 新 URL、截图、聊天、JD → Raw + topic + 导航 |
| **/review** | inbox、到期页、`growing`/`stale` → 提炼、互链 |
| **/lint** | 坏链、孤岛页、frontmatter、图片路径 |

## YAML frontmatter（按需）

必填建议：`type`、`status`、`created`、`updated`、`tags`、`sources`

`type`：`topic` | `map` | `paper` | `entity` | `project-note`  
`status`：`seed` | `growing` | `stable` | `stale`

`growing` / `stale` 建议补 `confidence`（0.0–1.0）、`review_after`（YYYY-MM-DD）。

高价值页：一句结论 + 来源 + ≥2 个 Related；ingest 页补 claim / evidence / boundary（见 `templates/topic-ingest-template.md`）。

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
