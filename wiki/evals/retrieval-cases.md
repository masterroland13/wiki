# Retrieval cases

`/query` 的迷你金标。流程见 [`.agents/skills/query/SKILL.md`](../../.agents/skills/query/SKILL.md)。

下面第一个 `yaml` 代码块是机器可读的题集。`python3 scripts/check_retrieval_cases.py` 检查：

- 至少 10 题，其中至少 3 题 `kind: paraphrase`（问法不包含期望页的一级标题）
- `direct` / `paraphrase` 的 `expect` 路径在仓库里存在
- `intentional-miss` 的 `expect` 必须为空，并在 `note` 里写明为什么故意没有页

脚本不打分、不读向量、不检索 `references/raw/`。建议人工或 agent 抽检时，命中率目标 ≥70%：打开期望页，或按技能说 **I can't find**。编造路径算失败。

## 抽检记录（2026-11-02）

按技能从 `wiki/index.md` 出发，打开下表里的页，不使用检索服务。

| 题 | 从索引走到 | 结果 |
|----|------------|------|
| q02 | 人文区「笔记 1–4」链到痛苦恐惧症笔记 | 页内主旨是把痛苦排出生活。命中 `wiki/topics/phil-han-palliative-society-ch01-algophobia-notes.md` |
| q03 | 人文区「笔记 5–10」 | 页内「幸福强制」写绩效化的幸福预期。命中 `wiki/topics/phil-han-palliative-society-notes-05-10.md` |
| q09 | Start Here 的 Learning spine | 阶段表是先广度再深度。命中 `wiki/maps/learning-spine.md` |
| q14 | 理工区还没有笔记，索引指向 inbox | 没有 `cs-` topic。应按失败协议回答找不到，不编造 `wiki/topics/cs-dp-intro.md` |

```yaml
cases:
  - id: q01
    kind: direct
    question: "《妥协社会》这本书的书目页在哪？"
    expect:
      - wiki/entities/entity-book-palliative-society.md
  - id: q02
    kind: paraphrase
    question: "韩炳哲写当代人拼命把疼痛和否定性赶出生活，我的读书笔记在哪一页？"
    expect:
      - wiki/topics/phil-han-palliative-society-ch01-algophobia-notes.md
  - id: q03
    kind: paraphrase
    question: "幸福被变成要优化的绩效、人被要求反省内心而不是看社会结构，笔记在哪？"
    expect:
      - wiki/topics/phil-han-palliative-society-notes-05-10.md
  - id: q04
    kind: paraphrase
    question: "从痛变得没有意义，一直写到他者消失、同情心变薄，这部分笔记在哪一页？"
    expect:
      - wiki/topics/phil-han-palliative-society-notes-11-27.md
  - id: q05
    kind: paraphrase
    question: "只留下书里的原句和旁边的解读、没有展开我自己的想法，那份材料是哪一页？"
    expect:
      - wiki/topics/phil-han-palliative-society-highlights.md
  - id: q06
    kind: paraphrase
    question: "27 条读书想法分别落在哪几个文件，有没有一张对照表？"
    expect:
      - wiki/maps/phil-han-palliative-society-reading-index.md
  - id: q07
    kind: paraphrase
    question: "一个念头还没想好归到文学还是哲学，先记到哪一页？"
    expect:
      - wiki/inbox.md
  - id: q08
    kind: direct
    question: "Capture、Review、Archive 三步写在哪？"
    expect:
      - wiki/maps/capture-review-archival-workflow.md
  - id: q09
    kind: paraphrase
    question: "学习上先给每个学科一张地图，再挑一两门挖深，这张阶段表在哪？"
    expect:
      - wiki/maps/learning-spine.md
  - id: q10
    kind: direct
    question: "/teacher 的会话记忆放在哪个项目页？"
    expect:
      - wiki/projects/learning-progress/index.md
  - id: q11
    kind: paraphrase
    question: "我希望上课的节奏、以及短期和长期想学什么，记在哪？"
    expect:
      - wiki/projects/learning-progress/learner-profile.md
  - id: q12
    kind: direct
    question: "目录怎么分、frontmatter 机器规则写在哪？"
    expect:
      - wiki/WIKI_SCHEMA.md
  - id: q13
    kind: direct
    question: "这个知识库怎么上手、技能怎么触发？"
    expect:
      - wiki/maps/wiki-teaching-usage-handbook.md
    note: "旧路径 wiki/maps/wiki-user-guide.md 只保留跳转，正文在新手册。"
  - id: q14
    kind: intentional-miss
    question: "动态规划的入门笔记在哪？"
    expect: []
    note: "索引的理工区没有计算机笔记，只指向 inbox。Schema 里的 cs-dp-intro 只是命名例子，仓库中没有这张 topic。"
  - id: q15
    kind: intentional-miss
    question: "熵的直觉解释有没有专页？"
    expect: []
    note: "没有 phys- topic。Schema 里的 phys-entropy-intuition 只是命名例子。"
```
