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

读 `references/archive-depth.md` — **L0 片段 / L1 标准 / L2 深读**。默认 L1；单图无 URL 倾向 L0 或 L1（含 Raw 转写）。

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

### 5. 导航

- 值得反复找到 → `wiki/index.md` 和/或相关 map
- **新 topic** 或流程变更 → `wiki/changelog.md`
- 仅给已有 topic 补一段/一图 → 更新 topic `updated` 即可，changelog 可选

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

## 轻量验收

- [ ] 新页目录正确；`sources` 可追溯
- [ ] 至少一个入口（index / map / project）可到达
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
