---
name: wiki
description: Archive URLs, screenshots, chat excerpts, and job posts into wiki Raw+Wiki. Use when the user says 投喂 wiki, /wiki, 归档进 wiki, 合并到知识库, or attaches slides/screenshots for the knowledge base. Handles TrendRadar daily digest, image assets, navigation updates, and topic-ingest templates—not a heavy compile loop.
---

# wiki

把外部材料或对话内容合并进 wiki 知识库（**Raw + Wiki + Schema**）。优先 **小步归档、互链、必要导航**；不要发明重型 compile loop。

## 先读

1. `AGENTS.md`
2. `wiki/WIKI_SCHEMA.md`
3. `wiki/index.md`

任务已落在某 map / project 时，再读对应导航页。

## 路由（按顺序判断，命中即走该支）

```
输入
 ├─ TrendRadar 特征？ → references/trendradar-pointer.md + references/raw/trendradar/README.md
 ├─ 仅截图/幻灯片/视频帧、无稳定 URL？ → references/screenshot-only.md
 └─ 其它（URL、长文、JD、论文摘要、聊天）→ 下方「通用流程」
```

**TrendRadar**：不要回到通用 Raw 顶层或乱开 deep-dive topic（除非用户明确要求 Level 2）。

## 通用流程

### 1. 定归档深度

读 `references/archive-depth.md` — **L0 片段 / L1 标准 / L2 深读**。**默认 L1**。单图无 URL 倾向 L0 或 L1（含 Raw 转写）。来源看起来重要、或是 TrendRadar S 档，都不要自动升到 L2。

#### 如何留在 L1

没有下面的 opt-in 用语时，停在 L1（输入明显只是片段时用 L0）：

- 写或补**一篇** topic
- 需要反复找到时，在 `wiki/index.md` **或**一个相关 map 上加一条入口
- 更新该页 `updated`
- 不级联 entity，不改多张 map，不重排 index
- **不**写 `wiki/log.md`
- **不**为这次小补丁写 `wiki/changelog.md`
- 不改无关阅读笔记正文，不凑 10–15 页

#### 如何打开 L2 compile

用户明确说出任一用语才进入 L2：**「L2」**、**「深挖」**、**「compile」**、**「级联」**。TrendRadar 路由不变：用户没要求 Level 2 就不要开 deep-dive topic。

L2 在 L1 那一页之上只多做四件事：

1. **entity**：相关专名已有短定义就加一条链到本次 topic；没有、且会反复检索，才新建短定义。不把阅读笔记正文搬进 entity。
2. **map**：已有相关 map 就加一行链接。没有合适的 map、且主题会反复打开，才新建一页。不重写 map 里其它主题的段落。
3. **index**：在对应分区加或改一行。不重排无关分区。
4. **log**：在 `wiki/log.md` **顶部**追加一条。标题严格是 `## [YYYY-MM-DD] ingest | 标题`（动词只有 `ingest` 这一个词）。

L2 仍然不做：不写 changelog（除非同一次还改了 schema 或目录约定）；不改无关 topic 的正文或文风；不自动裁定矛盾；不按「每源 10–15 页」扩写。

### 2. 是否要 Raw

| 情况 | Raw |
|------|-----|
| 长、杂、来源重要、含图、以后可能回看 | 先落 `references/raw/` |
| 已足够干净的小结论 | 可直接 `wiki/`，`sources` 挂 URL |
| 仅截图 | **几乎总是** Raw（见 screenshot-only） |

### 3. 图片

读 `references/image-ingest.md`；细节见 `wiki/references/image-handling-guide.md`。

- 优先 **Raw assets + Wiki 相对引用**，不重复存图
- 信息图/清单图：**Raw 内表格/列表转写** + 保留原图
- 网页：**Firecrawl 优先**；curl / `ingest_url_to_raw.py` 为 fallback

### 4. 写哪一层

| 路径 | 用途 |
|------|------|
| `wiki/topics/` | 主题结论、方法、市场观察 |
| `wiki/maps/` | 多 topic 导航 |
| `wiki/entities/` | 术语/工具短定义 |
| `wiki/projects/` | 项目上下文知识 |

创建页优先 `wiki/templates/`（ingest / topic / faq / entity / paper / project-note / map）。

### 5. 导航与两份日志

- 值得反复找到 → L1 在 `wiki/index.md` **或**一个相关 map 上加一条入口。L2 才同时动相关 entity、相关 map 和 index（见第 1 节）
- 只给已有 topic 补一段或一图 → 更新该页 `updated`。不写 changelog，不写 log
- **`wiki/changelog.md`**：只记结构性变更（目录约定、schema、技能体系）。新 topic 本身不是结构变更
- **`wiki/log.md`**：L2 的 `ingest` 必写；L0 / L1 不写。`query` / `lint` 由对应技能在结束时写，格式见 schema「操作日志与 changelog」

### 6. frontmatter

必填：`type`、`status`、`created`、`updated`、`tags`、`sources`

- `growing` / `stale`：补 `confidence`、`review_after`
- `seed` / `stable`：可省略 confidence

页面至少：**一句结论 + 来源 + 2 个 Related**；高价值页补 claim / evidence / boundary（ingest 模板）。

### 冲突与取代

发现新材料与已有页冲突时，**禁止静默覆盖**。不要删改已有主张来显得一致，也不要只留下认为对的一边。规则在 `wiki/WIKI_SCHEMA.md`「矛盾与取代」。字段可选，只给高价值页用，不要求回填旧页。

- **并存**：在相关页写 `## Contradictions`（对方路径、两边主张、各自来源）。不裁定谁对。
- **更换阅读入口**：旧页保留原文，写 `superseded_by`；新页写 `supersedes`。路径相对该页。这不表示旧主张为假。
- 带 `superseded_by` 的页不要放进 `wiki/index.md` 主表。从后继页链入即可。
- 合成示例：`wiki/topics/x-demo-contradiction-coexistence.md`（被取代的一页不在 index 主表）。

## L2 dry-run（检查清单，默认不执行）

用户没说 L2 / 深挖 / compile / 级联时，跳过本节，按 L1 做完即止。

下面用一条**虚构**来源核对级联范围。真做 L2 之前逐项对照。本清单的样例页**不要**为了演练而创建；仓库里的 [`wiki/log.md`](../../../wiki/log.md) 已有同标题的演练条目，写明未执行写入。

样例 log 标题：

```text
## [2026-11-02] ingest | L2 dry-run — synthetic example-widget
```

若用户当时说了「L2」，预期只碰：

| 触达 | 路径 | 预期改动 |
|------|------|----------|
| topic（L1 也会写） | `wiki/topics/cs-example-widget.md` | 新建或补一篇 ingest 页 |
| entity | `wiki/entities/entity-example-widget.md` | 短定义 + 链到 topic |
| map | `wiki/maps/learning-spine.md` | 加一行链接，不改其它阶段正文 |
| index | `wiki/index.md` | 对应分区加一行 |
| log | `wiki/log.md` | 顶部追加上面的 `ingest` 条目 |

明确不碰：`wiki/changelog.md`；`wiki/topics/phil-han-palliative-society-*.md` 以及任何无关阅读笔记正文；其它 map 里已有段落。

- [ ] 用户用了「L2」「深挖」「compile」「级联」之一；否则停在 L1，不写 log
- [ ] log 标题匹配 `## [YYYY-MM-DD] ingest | title`，动词不是字面量 `ingest|query|lint`
- [ ] entity、map、index 各有一条具名触达，或写明「已有且无需改」并给出路径
- [ ] 没有改写无关阅读笔记正文，没有为凑页数新开 topic
- [ ] changelog 未写，除非同一次还有结构变更

## 轻量验收

- [ ] 新页目录正确；`sources` 可追溯
- [ ] 至少一个入口（index / map / project）可到达
- [ ] 未要求 L2 时，没有级联 entity，也没有写 `wiki/log.md`
- [ ] 图片文件存在、相对路径正确、有 alt（+ 必要时说明）
- [ ] 可选：`scripts/wiki_verify_images.sh` 或 `/lint` 查坏链与 frontmatter
- [ ] 若与已有页冲突：已写 `## Contradictions` 或 supersession 字段，没有静默覆盖

##  bundled references（按需读）

| 文件 | 内容 |
|------|------|
| `references/trendradar-pointer.md` | TrendRadar 入口 |
| `references/screenshot-only.md` | 无 URL 截图/幻灯片 |
| `references/archive-depth.md` | L0/L1/L2、confidence |
| `references/image-ingest.md` | 抓图策略与路径 |

## 输出风格

- 写成「别人以后能看懂」的稳定笔记，非单次聊天备忘录
- 信息不全 → 线索页/初稿，降低 confidence，Open Questions 写缺口
- 至少一条可执行结论或边界说明，避免只摘录不判断
