# ROADMAP（可选）

仓库工程向 Backlog；**知识导航**见 [`wiki/index.md`](wiki/index.md)。

## Icebox

- 体量变大时：评估 MCP 检索（如 sage-wiki）或 `qmd` 本地搜索
- 同步 skill：`.agents/` → `.cursor/` / `.claude/` / `.codex/` 的脚本或 checklist

## 已完成

- 2026-11-02：Slice C 矛盾与取代（可选 `supersedes` / `superseded_by`，模板两节，合成示例，index 主推 warning）。不自动裁定对错。
- 2026-11-02：Slice B `/query` + 检索金标（[`wiki/evals/retrieval-cases.md`](wiki/evals/retrieval-cases.md)，[`scripts/check_retrieval_cases.py`](scripts/check_retrieval_cases.py)）。未上向量检索。
- 2026-11-02：Slice A 机器 lint（[`scripts/lint_wiki.py`](scripts/lint_wiki.py) + pytest）；`/lint` 先跑脚本。计划见 [`docs/plans/wiki-frontier-upgrade.md`](docs/plans/wiki-frontier-upgrade.md)
- 2026-06-30：方案 A 骨架初始化（见 [`wiki/changelog.md`](wiki/changelog.md)）
