"""Behavior tests for scripts/check_skill_sync.py."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

_SCRIPT = Path(__file__).resolve().parent / "check_skill_sync.py"
_SPEC = importlib.util.spec_from_file_location("check_skill_sync", _SCRIPT)
assert _SPEC is not None and _SPEC.loader is not None
check_skill_sync = importlib.util.module_from_spec(_SPEC)
sys.modules[_SPEC.name] = check_skill_sync
_SPEC.loader.exec_module(check_skill_sync)

REPO_ROOT = Path(__file__).resolve().parents[1]
HOSTS = (".cursor/skills", ".claude/skills", ".codex/skills")


def write_tree(root: Path, files: dict[str, str]) -> None:
    for rel, text in files.items():
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")


def skill_files() -> dict[str, str]:
    return {
        "lint/SKILL.md": "---\nname: lint\n---\n\n# lint\n\nRun the script.\n",
        "teacher/references/modes.md": "# modes\n\nAsk, then wait.\n",
    }


def layout(tmp_path: Path, files: dict[str, str] | None = None) -> None:
    payload = skill_files() if files is None else files
    write_tree(tmp_path / ".agents" / "skills", payload)
    for host in HOSTS:
        write_tree(tmp_path / host, payload)


def test_identical_trees_pass(tmp_path: Path) -> None:
    layout(tmp_path)
    result = check_skill_sync.check_sync(
        tmp_path / ".agents" / "skills",
        [tmp_path / host for host in HOSTS],
        root=tmp_path,
    )
    assert result.ok, check_skill_sync.format_report(result)
    assert result.canonical_files == 2
    assert result.mirror_count == 3
    report = check_skill_sync.format_report(result)
    assert "drifts=0" in report
    assert check_skill_sync.main(["--root", str(tmp_path)]) == 0


def test_content_drift_names_the_mirror_path(tmp_path: Path) -> None:
    layout(tmp_path)
    drifted = tmp_path / ".codex/skills/teacher/references/modes.md"
    drifted.write_text(drifted.read_text(encoding="utf-8") + "\n# host-only edit\n", encoding="utf-8")
    result = check_skill_sync.check_sync(
        tmp_path / ".agents" / "skills",
        [tmp_path / host for host in HOSTS],
        root=tmp_path,
    )
    report = check_skill_sync.format_report(result)
    assert not result.ok
    assert "DIFFERS .codex/skills/teacher/references/modes.md" in report
    assert check_skill_sync.main(["--root", str(tmp_path)]) == 1


def test_missing_mirror_file_names_that_path(tmp_path: Path) -> None:
    layout(tmp_path)
    (tmp_path / ".cursor/skills/lint/SKILL.md").unlink()
    result = check_skill_sync.check_sync(
        tmp_path / ".agents" / "skills",
        [tmp_path / host for host in HOSTS],
        root=tmp_path,
    )
    report = check_skill_sync.format_report(result)
    assert "MISSING .cursor/skills/lint/SKILL.md" in report
    assert check_skill_sync.main(["--root", str(tmp_path)]) == 1


def test_extra_mirror_file_names_that_path(tmp_path: Path) -> None:
    layout(tmp_path)
    extra = tmp_path / ".claude/skills/lint/HOST-NOTES.md"
    extra.write_text("do not invent a second source of truth\n", encoding="utf-8")
    result = check_skill_sync.check_sync(
        tmp_path / ".agents" / "skills",
        [tmp_path / host for host in HOSTS],
        root=tmp_path,
    )
    report = check_skill_sync.format_report(result)
    assert "EXTRA .claude/skills/lint/HOST-NOTES.md" in report
    assert check_skill_sync.main(["--root", str(tmp_path)]) == 1


def test_ds_store_only_on_a_mirror_is_ignored(tmp_path: Path) -> None:
    layout(tmp_path)
    (tmp_path / ".cursor/skills/.DS_Store").write_bytes(b"junk")
    cache = tmp_path / ".claude/skills/lint/__pycache__"
    cache.mkdir()
    (cache / "SKILL.cpython-311.pyc").write_bytes(b"\x00pyc")
    result = check_skill_sync.check_sync(
        tmp_path / ".agents" / "skills",
        [tmp_path / host for host in HOSTS],
        root=tmp_path,
    )
    assert result.ok, check_skill_sync.format_report(result)


def test_missing_canonical_directory_exits_2(tmp_path: Path) -> None:
    result = check_skill_sync.check_sync(
        tmp_path / ".agents" / "skills",
        [tmp_path / host for host in HOSTS],
        root=tmp_path,
    )
    assert result.fatal is not None
    assert ".agents/skills" in result.fatal
    assert check_skill_sync.main(["--root", str(tmp_path)]) == 2


def test_repository_mirrors_match_canonical() -> None:
    result = check_skill_sync.check_sync(
        REPO_ROOT / ".agents" / "skills",
        [REPO_ROOT / host for host in HOSTS],
        root=REPO_ROOT,
    )
    assert result.fatal is None
    assert result.ok, check_skill_sync.format_report(result)
    assert result.canonical_files > 0
    assert result.hosts == list(HOSTS)
    assert check_skill_sync.main(["--root", str(REPO_ROOT)]) == 0
