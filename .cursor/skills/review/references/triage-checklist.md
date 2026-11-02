# Triage 清单

## Inbox

**文件：** `wiki/inbox.md`（若不存在则跳过）

对每条：

- [ ] 是否仍值得保留？否 → 删除并说明
- [ ] 能否用一句话写 **主张**？否 → defer，设 `review_after`
- [ ] 有 **来源**（URL / Raw）？无 → 让用户补或标 seed
- [ ] 归宿：`topics/` | `entities/` | 并入已有页 | 触发 `/wiki` 深归档

处理完后 inbox 只留 **未决** 项；已 promote 的从 inbox 移除或标「已处理 → 链接」。

---

## Due pages

**扫描方式（Agent 执行）：**

1. `grep -r "review_after:" wiki/` 或搜索 frontmatter
2. 取 `review_after` ≤ 今天（或用户给的日期）
3. 额外包含 `status: stale`
4. 可选：`status: growing` 且 `updated` 超过 60 天

**优先级：**

1. stale
2. review_after 过期
3. growing 长期未改

单次 weekly 默认 **最多深审 5 页**；其余只改 `review_after` 排队。

---

## 单页 Review 检查

| 检查 | 通过标准 |
|------|----------|
| 主张 | 文首或 ## 结论 有一句可引用判断 |
| 证据 | `sources` 或正文内 Raw 链接 |
| 边界 | 有 limitations / 何时不适用 / Open Questions |
| 导航 | 至少一条入链（index / map / project） |
| Related | ≥2 个相关内链（高价值页） |
| frontmatter | `type` `status` `updated` `tags` `sources` 齐全。`supersedes` / `superseded_by` 可选，仅高价值页 |
| 冲突 | 与其它页主张打架时写 `## Contradictions` 或 supersession 字段。禁止静默覆盖。不裁定谁对 |

---

## confidence 与 review_after 建议

| status | confidence | review_after |
|--------|------------|--------------|
| seed | 0.3–0.5 | +14 天 |
| growing | 0.5–0.7 | +30 天 |
| stable | 0.7–0.9 | +90 天或省略 |
| stale | 下调 0.1–0.2 | +7 天（催着重读 Raw） |

合并、大改主张后 → 必调 `updated`，视情况写 changelog。主张冲突时不要用合并删掉一边。
