# docs

仓库工程文档（调研、计划、审查）。知识导航仍以 [`wiki/index.md`](../wiki/index.md) 为准；目录契约以 [`wiki/WIKI_SCHEMA.md`](../wiki/WIKI_SCHEMA.md) 为准。

| 文档 | 用途 |
|------|------|
| [llm-wiki-frontier-2026-11.md](research/llm-wiki-frontier-2026-11.md) | 2026-11-02 前沿调研：抄什么、不抄什么、缺口 |
| [wiki-frontier-upgrade.md](plans/wiki-frontier-upgrade.md) | 升级施工计划（Slice A–J） |
| [wiki-slice-audit.md](handbooks/wiki-slice-audit.md) | 每一刀结束后的切片审查手册 |

## 当前范围

已落地文档。**Slice A**（机器 lint）、**Slice B**（`/query` + 检索金标）、**Slice C**（矛盾与取代协议）、**Slice D**（`wiki/log.md` + 可选 L2 compile，默认仍 L1）、**Slice E**（source-clock stale warning，不写回 status）、**Slice F**（`wiki/projects/learning-progress/` 行为记忆层与写入路由；不要求 Mem0）与 **Slice I**（`.agents/skills/` 为 canonical；`scripts/check_skill_sync.py` 对照 Cursor / Claude / Codex 镜像）已实现。Slice G、H、J 未做。

```bash
python3 scripts/lint_wiki.py
python3 scripts/check_retrieval_cases.py
python3 scripts/check_skill_sync.py
python3 -m pytest scripts/ -q
```

退出码、必填字段和 warning 规则见 [`wiki/WIKI_SCHEMA.md`](../wiki/WIKI_SCHEMA.md) 的「机器规则子集」。`/lint` 必须先跑上面的脚本。
