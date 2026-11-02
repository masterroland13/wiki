"""Behavior tests for scripts/check_retrieval_cases.py. No embedding service."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

_SCRIPT = Path(__file__).resolve().parent / "check_retrieval_cases.py"
_SPEC = importlib.util.spec_from_file_location("check_retrieval_cases", _SCRIPT)
assert _SPEC is not None and _SPEC.loader is not None
check_retrieval_cases = importlib.util.module_from_spec(_SPEC)
sys.modules[_SPEC.name] = check_retrieval_cases
_SPEC.loader.exec_module(check_retrieval_cases)

REPO_ROOT = Path(__file__).resolve().parents[1]
GOLD = REPO_ROOT / "wiki" / "evals" / "retrieval-cases.md"


def write_cases(root: Path, body: str, name: str = "cases.md") -> Path:
    path = root / name
    path.write_text(body, encoding="utf-8")
    return path


def yaml_doc(cases: str) -> str:
    return f"# cases\n\n```yaml\n{cases}```\n"


def messages(result) -> list[str]:
    return [f"{item.path}: {item.message}" for item in result.findings]


def test_repo_gold_set_passes() -> None:
    result = check_retrieval_cases.check_file(GOLD, REPO_ROOT)
    assert result.ok, messages(result)
    assert result.case_count >= 10
    assert result.paraphrase_count >= 3
    assert result.intentional_miss_count >= 1
    assert result.paths_checked >= 10


def test_repo_gold_set_cli_exits_0() -> None:
    code = check_retrieval_cases.main(["--root", str(REPO_ROOT), "--cases", str(GOLD)])
    assert code == 0


def test_missing_expect_path_reports_that_path(tmp_path: Path) -> None:
    text = yaml_doc(
        "cases:\n"
        "  - id: q01\n"
        "    kind: direct\n"
        "    question: where is the missing page?\n"
        "    expect:\n"
        "      - wiki/topics/does-not-exist.md\n"
    )
    path = write_cases(tmp_path, text)
    result = check_retrieval_cases.check_file(path, tmp_path, min_cases=1, min_paraphrase=0)
    blob = "\n".join(messages(result))
    assert "wiki/topics/does-not-exist.md" in blob
    assert "expected path not found" in blob


def test_paraphrase_that_copies_the_title_fails(tmp_path: Path) -> None:
    page = tmp_path / "wiki" / "topics" / "pain.md"
    page.parent.mkdir(parents=True)
    page.write_text("# 痛苦恐惧症专页\n\nBody.\n", encoding="utf-8")
    text = yaml_doc(
        "cases:\n"
        "  - id: q01\n"
        "    kind: paraphrase\n"
        "    question: 痛苦恐惧症专页在哪？\n"
        "    expect:\n"
        "      - wiki/topics/pain.md\n"
    )
    path = write_cases(tmp_path, text)
    result = check_retrieval_cases.check_file(path, tmp_path, min_cases=1, min_paraphrase=1)
    blob = "\n".join(messages(result))
    assert "q01" in blob
    assert "痛苦恐惧症专页" in blob
    assert "wiki/topics/pain.md" in blob


def test_intentional_miss_with_empty_expect_passes(tmp_path: Path) -> None:
    text = yaml_doc(
        "cases:\n"
        "  - id: q01\n"
        "    kind: intentional-miss\n"
        "    question: 有没有量子计算笔记？\n"
        "    expect: []\n"
        "    note: 仓库里还没有这张页。\n"
    )
    path = write_cases(tmp_path, text)
    result = check_retrieval_cases.check_file(path, tmp_path, min_cases=1, min_paraphrase=0)
    assert result.ok, messages(result)
    assert result.intentional_miss_count == 1
    assert result.paths_checked == 0


def test_intentional_miss_must_not_list_a_path(tmp_path: Path) -> None:
    page = tmp_path / "wiki" / "index.md"
    page.parent.mkdir(parents=True)
    page.write_text("# Index\n", encoding="utf-8")
    text = yaml_doc(
        "cases:\n"
        "  - id: q01\n"
        "    kind: intentional-miss\n"
        "    question: 故意缺失却填了路径\n"
        "    expect:\n"
        "      - wiki/index.md\n"
        "    note: 不应列出路径。\n"
    )
    path = write_cases(tmp_path, text)
    result = check_retrieval_cases.check_file(path, tmp_path, min_cases=1, min_paraphrase=0)
    assert any("empty expect" in item.message for item in result.findings)


def test_too_few_paraphrases_reports_the_count(tmp_path: Path) -> None:
    page = tmp_path / "wiki" / "index.md"
    page.parent.mkdir(parents=True)
    page.write_text("# Index\n", encoding="utf-8")
    text = yaml_doc(
        "cases:\n"
        "  - id: q01\n"
        "    kind: direct\n"
        "    question: 索引在哪？\n"
        "    expect:\n"
        "      - wiki/index.md\n"
    )
    path = write_cases(tmp_path, text)
    result = check_retrieval_cases.check_file(path, tmp_path, min_cases=1, min_paraphrase=3)
    assert any("paraphrase" in item.message and "found 0" in item.message for item in result.findings)


def test_missing_yaml_fence_is_a_read_failure(tmp_path: Path) -> None:
    path = write_cases(tmp_path, "# no fence\n\nJust prose.\n")
    result = check_retrieval_cases.check_file(path, tmp_path)
    assert result.case_count == 0
    assert any("could not read cases" in item.message for item in result.findings)
    assert check_retrieval_cases.main(["--root", str(tmp_path), "--cases", path.name]) == 2


def test_missing_cases_file_exits_2(tmp_path: Path) -> None:
    code = check_retrieval_cases.main(
        ["--root", str(tmp_path), "--cases", "wiki/evals/missing.md"]
    )
    assert code == 2


def test_checker_does_not_depend_on_an_embedding_service() -> None:
    text = _SCRIPT.read_text(encoding="utf-8")
    for banned in (
        "openai",
        "chromadb",
        "qdrant",
        "faiss",
        "sentence_transformers",
        "lancedb",
        "qmd",
    ):
        assert banned not in text.lower()


def test_skill_requires_path_citations_and_failure_protocol() -> None:
    skill = (REPO_ROOT / ".agents" / "skills" / "query" / "SKILL.md").read_text(encoding="utf-8")
    assert "I can't find" in skill
    assert "wiki/index.md" in skill
    assert "仓库路径" in skill
    for mirror in (".cursor", ".claude", ".codex"):
        copy = REPO_ROOT / mirror / "skills" / "query" / "SKILL.md"
        assert copy.read_text(encoding="utf-8") == skill
