# 仅截图 / 幻灯片 / 视频帧（无稳定 URL）

**范例**：[`references/raw/claude-code-bashtool-20-security-checks-2026-05-31.md`](../../../../references/raw/claude-code-bashtool-20-security-checks-2026-05-31.md) → [`wiki/topics/cs-claude-code-bashtool-20-security-checks.md`](../../../../wiki/topics/cs-claude-code-bashtool-20-security-checks.md)

## 何时走本路由

- 用户 attach 图片，或对话里只有截图/幻灯片/视频帧
- **没有**可靠文章 URL（或仅有平台内嵌，无法稳定抓取）
- 非 TrendRadar 条目

## 执行顺序

1. **落 Raw**（几乎总是需要）
   - 路径：`references/raw/<主题-stem>-YYYY-MM-DD.md`
   - assets：`references/raw/assets/<stem>/`（stem 可与文件名 stem 对齐，日期后缀可省略目录名）

2. **复制图片到 assets**
   - Cursor 附件常见路径：`~/.cursor/projects/<project>/assets/image-*.png`
   - 工作区若已有复制件，同样 `cp` 到 Raw assets
   - 使用语义化文件名，例如 `bashtool-20-security-checks-radar.png`

3. **结构化转写（必做）**
   - 信息图、清单、架构图：在 Raw 中用 **表格或列表** 写出图中可核对内容
   - 图片仍是原件；转写是可检索的 canonical 文本层
   - alt 文本包含关键实体名（便于 grep）

4. **Wiki**
   - 默认 L1：`wiki/templates/topic-ingest-template.md`
   - 图片 **引用 Raw assets**（不重复拷贝）：`../../references/raw/assets/<stem>/file.png`
   - Wiki 可摘要；完整表留在 Raw

5. **可选互证**
   - 若主题可公开检索（技术产品、论文、新闻），用 Firecrawl 等补 1–2 源
   - 无 URL 时不编造；在 Open Questions 写「待补视频/文章链接」
   - 有互证仍缺一手链 → `confidence` ≤ 0.75

6. **导航**
   - 值得反复找到 → `wiki/index.md` + 相关 `wiki/maps/`
   - 新 topic 或改流程 → `wiki/changelog.md`

## 视频截图额外字段（Raw 顶部）

```markdown
- **材料类型**：视频截图（约 MM:SS / 总时长）
- **待补来源**：[视频 URL 未知]
```

有 URL 后回写 Raw 与 Wiki `sources`。

## 禁止

- 只把图丢进 `wiki/projects/.../assets` 而无 Raw（除非纯项目 UI  mockup，见 image-handling-guide 场景 3 例外）
- 只嵌图不转写（后续无法检索）
- 无互证却写 `confidence: 0.9`
