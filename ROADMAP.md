# ROADMAP（可选）

仓库工程向 Backlog；**知识导航**见 [`wiki/index.md`](wiki/index.md)。

## Icebox

- 体量变大时：评估 MCP 检索（如 sage-wiki）或 `qmd` 本地搜索

## 已完成

- 2026-11-02：Slice I 技能同步校验（[`scripts/check_skill_sync.py`](scripts/check_skill_sync.py)）。Canonical 是 `.agents/skills/`；`.cursor/skills/`、`.claude/skills/`、`.codex/skills/` 只做镜像。漂移退出码 1 并打印路径。
- 2026-11-02：Slice F 行为记忆层（`wiki/projects/learning-progress/`：偏好 / 纠错 / 教学进度；写入路由在 schema 与该目录 README；`/teacher` 与 `/review` 启动先读）。事实与偏好的合成示例分开。不要求 Mem0。未做 Slice G–J。
- 2026-11-02：Slice E source-clock stale（`wiki/` 外 source 的 mtime 日期晚于 `updated` 时 warning，建议 `status: stale`，不写回）。未做 Slice F–J。
- 2026-11-02：Slice D 操作日志 [`wiki/log.md`](wiki/log.md) + 可选 L2 compile（默认仍 L1；级联限于相关 entity / map / index / log）。
- 2026-11-02：Slice C 矛盾与取代（可选 `supersedes` / `superseded_by`，模板两节，合成示例，index 主推 warning）。不自动裁定对错。
- 2026-11-02：Slice B `/query` + 检索金标（[`wiki/evals/retrieval-cases.md`](wiki/evals/retrieval-cases.md)，[`scripts/check_retrieval_cases.py`](scripts/check_retrieval_cases.py)）。未上向量检索。
- 2026-11-02：Slice A 机器 lint（[`scripts/lint_wiki.py`](scripts/lint_wiki.py) + pytest）；`/lint` 先跑脚本。计划见 [`docs/plans/wiki-frontier-upgrade.md`](docs/plans/wiki-frontier-upgrade.md)
- 2026-06-30：方案 A 骨架初始化（见 [`wiki/changelog.md`](wiki/changelog.md)）
