# wiki — 个人复利知识库

基于 [Karpathy LLM Wiki](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f) 思路的 **轻量实现**：`references/raw/` 收原件，`wiki/` 存结构化笔记，Agent 通过 `/wiki`、`/query`、`/review`、`/lint` 维护。

- **远程**：https://github.com/masterroland13/wiki
- **入口**：[`wiki/index.md`](wiki/index.md)
- **规则**：[`wiki/WIKI_SCHEMA.md`](wiki/WIKI_SCHEMA.md)
- **维护说明**：[`AGENTS.md`](AGENTS.md)
- **工程文档**：[`docs/README.md`](docs/README.md)（调研 / 计划 / 审查）

## 快速开始

1. 新材料 → 对话中说「投喂 wiki」或 `/wiki`
2. 待整理 → 先记 [`wiki/inbox.md`](wiki/inbox.md)，每周 `/review`
3. 按笔记提问 → 「/query」或「根据笔记回答」。找不到应明说，而不是编造页
4. 体检 → 「lint 一下 wiki」，或先跑 `python3 scripts/lint_wiki.py`

## 目录概览

```
wiki/
├── index.md          # 总导航
├── inbox.md          # 待归档
├── changelog.md      # 结构性变更
├── log.md            # ingest / query / lint；默认 L1 不写 ingest
├── maps/ topics/ entities/ projects/ papers/ templates/
├── evals/            # /query 金标
references/
├── raw/              # 原件收件箱
└── papers/           # PDF（可选）
.agents/skills/       # 技能正文 canonical（.cursor/.claude/.codex 只做镜像）
```
