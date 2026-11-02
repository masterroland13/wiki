# Review 模式

## Weekly（默认）

**时间盒：** 15–30 分钟  
**适合：** 用户说「review 一下」「weekly review」「整理 wiki」且未指定范围

**顺序：**

1. 读 `wiki/inbox.md` — 处理或 defer 每一项（目标：inbox 只留真正未决的）
2. 扫 **due 页**（见 triage-checklist）— 最多处理 5 页，其余改 `review_after`
3. **缺失 entity** — 跑 `python3 scripts/check_missing_entities.py`，按下方规则写入复盘。不达门槛不建页
4. **Inspiration pass** — 3 条 Capture 线索
5. 一句话总结 + 建议下次 review 日期

**输出模板：**

```markdown
## Review · [日期] · Weekly

### 处理
| 来源 | 动作 | 结果路径 |
|------|------|----------|

### 延期
- …

### 灵感（可 Capture）
1. …
2. …
3. …

### 缺失 entity
- …（或：无）

### 下次
- 建议 review_after: YYYY-MM-DD
- 可选: /lint 若坏链多
```

---

## Topic sweep

**适合：** 「review 一下 agent 工程」「过一遍 leetcode map」

1. 读指定 `wiki/maps/` 或 `wiki/projects/.../index.md`
2. 列出下游 topic / entity 链接
3. 每页过 **主张 / 证据 / 边界**。与另一页冲突时写 `## Contradictions` 或 supersession 字段，禁止静默覆盖（见 `wiki/WIKI_SCHEMA.md`「矛盾与取代」）
4. 补 map 上的缺口表（「还缺哪条 topic」）
5. Inspiration：该主题下 2–3 个未写透的问题

**不要** brute-force 读整棵 `wiki/`；只跟 map 走。

---

## Recall

**适合：** 「复习 wiki 里的 Go」「考我系统设计笔记」

与 `/teacher` 的区别：**材料已在 wiki**，不再教新课；目标是 **提取 + 漏洞 + 回写**。

1. 从 map/topic 抽 3–5 个 **主张**（先问用户，再给反馈）
2. 用户答不上来 → 指向具体 topic 段落，不整篇重讲
3. 暴露的漏洞 → **defer** 或当场补一段进 topic + 调 `confidence`
4. 可选：生成 2 条 spaced-review 的 `review_after`

---

## Quick

**适合：** 「只有 5 分钟」「快速过 inbox」

- 只处理 inbox 前 3 条
- 不做 inspiration pass（除非用户要）
- 输出 ≤ 10 行

---

## 缺失 entity（Weekly 必跑）

```bash
python3 scripts/check_missing_entities.py
```

脚本只报告，不建页，不改笔记。默认退出码 0（有候选也是 0）。`--strict` 时有候选才退出 1。`--min-pages` 小于 2 时退出 2，不能把门槛调低。契约在 `wiki/WIKI_SCHEMA.md`「实体页」。

**什么算一个候选**

- 至少 **2 个不同的 wiki 页**链向同一个还不存在的 `wiki/entities/entity-*.md`。
- 或同一个名字用显式 wiki 链接（双括号）或 `entity:名字` 出现在至少 2 个不同的页上，并且还没有对得上的 entity（标题、文件名 slug 或 `aliases`）。
- 同一页写两次只算 1 页。
- 散文里的人名、书名不计数。阅读笔记里反复出现某个人，不会因此建议建页。
- 名字已经对上别的 wiki 页标题或文件名：不是 entity 候选（那是 topic 或 map）。

**何时可以新建 `wiki/entities/entity-*.md`**

- 脚本列出了候选，并且它确实是稳定节点（人、作品、组织、概念 hub），不是「我怎么理解」。
- **或者**用户在当次 review 里点名要建这个 entity。点名是例外，不是把门槛改成 1。
- 两条都不满足：不要新建。

不要为空的学科建空 topic。索引里没有笔记的分区指向 `wiki/inbox.md`。

输出里照抄脚本的候选行和页路径。0 条就写「缺失 entity：无」。

---

## 与 Capture → Archive 的衔接

Review **不负责**首次归档长文；那是 `/wiki`。

Review **负责**：

- inbox 里「已 Capture 未 Archive」的项 → 决定是否调用 wiki 流程或手动 promote
- 已 Archive 但 `growing` 的页 → 收敛成 stable
- 到期页 → 重读 Raw，更新结论或标 stale
