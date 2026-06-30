# Wiki Templates

这套模板不是“排版偏好”，而是为了解决三个真实问题：

1. **低摩擦记录**：先写下来，而不是先设计目录和分类。
2. **批判性思考**：每页都要区分“主张”和“证据”，避免只做摘要搬运。
3. **长期可复用**：几周后还能快速读懂、复盘、链接到其它页面。

## 设计原则（重构后）

- **最小必填优先**：首轮只要求必要字段和最短结论，降低启动成本。
- **两阶段写作**：先 Capture（2-5 分钟），再 Deepen（10-20 分钟）。
- **主张-证据分离**：关键结论要有对应来源或数据，不用“感觉正确”。
- **显式不确定性**：记录边界条件、反例、待验证点。
- **链接优先于文件夹**：至少补 2 个 Related 链接，推动结构涌现。

## 统一 Frontmatter 约定

### 必填（所有模板）

- `type`
- `status`
- `created`
- `updated`
- `tags`
- `sources`

### 选填（按需）

- `project`
- `confidence`（0.0-1.0）
- `review_after`（建议复盘日期）
- `date`
- `people`
- `rating`

## 模板选择

- `topic-template.md`: 通用主题页（概念、方法、机制）
- `topic-faq-template.md`: 面试问答、复盘问答、排障问答
- `topic-ingest-template.md`: 从 Raw/文章/帖子提炼为可执行知识
- `map-template.md`: 导航、分层结构、学习路径或知识编排
- `entity-template.md`: 实体/术语定义与边界澄清
- `paper-template.md`: 论文阅读笔记（方法与证据导向）
- `project-note-template.md`: 项目知识中枢（决策、风险、指标）

设计依据与方法映射见：`template-design-rationale.md`。

## 首轮完成标准（MVP）

1. 一句可复用结论（不超过 30 秒可读）
2. 至少一条可信来源（`sources`）
3. 至少两条 Related 链接
4. 至少一个“不确定性/待验证点”
