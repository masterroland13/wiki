"""Behavior tests for scripts/check_missing_entities.py."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

_SCRIPT = Path(__file__).resolve().parent / "check_missing_entities.py"
_SPEC = importlib.util.spec_from_file_location("check_missing_entities", _SCRIPT)
assert _SPEC is not None and _SPEC.loader is not None
check_missing_entities = importlib.util.module_from_spec(_SPEC)
sys.modules[_SPEC.name] = check_missing_entities
_SPEC.loader.exec_module(check_missing_entities)

REPO_ROOT = Path(__file__).resolve().parents[1]


def write_page(root: Path, rel: str, text: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def test_two_pages_linking_one_missing_entity_are_reported(tmp_path: Path) -> None:
    write_page(tmp_path, "wiki/topics/a.md", "See [Han](../entities/entity-person-han.md).\n")
    write_page(tmp_path, "wiki/topics/b.md", "See [Han](../entities/entity-person-han.md).\n")
    entities = tmp_path / "wiki" / "entities"
    before = sorted(entities.glob("*.md")) if entities.exists() else []
    result = check_missing_entities.scan(tmp_path)
    report = check_missing_entities.format_report(result)
    assert len(result.candidates) == 1
    candidate = result.candidates[0]
    assert candidate.kind == "link"
    assert candidate.key == "wiki/entities/entity-person-han.md"
    assert candidate.pages == ("wiki/topics/a.md", "wiki/topics/b.md")
    assert "pages=2" in report
    assert "threshold: 2 distinct pages" in report
    after = sorted(entities.glob("*.md")) if entities.exists() else []
    assert before == after
    assert not (tmp_path / "wiki/entities/entity-person-han.md").exists()
    assert check_missing_entities.main(["--root", str(tmp_path)]) == 0


def test_one_page_is_below_threshold(tmp_path: Path) -> None:
    write_page(
        tmp_path,
        "wiki/topics/only.md",
        "See [Han](../entities/entity-person-han.md) and again [Han](../entities/entity-person-han.md).\n",
    )
    result = check_missing_entities.scan(tmp_path)
    assert result.candidates == ()


def test_two_different_missing_entities_do_not_merge(tmp_path: Path) -> None:
    write_page(tmp_path, "wiki/topics/a.md", "See [A](../entities/entity-a.md).\n")
    write_page(tmp_path, "wiki/topics/b.md", "See [B](../entities/entity-b.md).\n")
    result = check_missing_entities.scan(tmp_path)
    assert result.candidates == ()


def test_existing_entity_file_is_not_a_candidate(tmp_path: Path) -> None:
    write_page(tmp_path, "wiki/entities/entity-person-han.md", "# 韩炳哲\n")
    write_page(tmp_path, "wiki/topics/a.md", "See [Han](../entities/entity-person-han.md).\n")
    write_page(tmp_path, "wiki/topics/b.md", "See [Han](../entities/entity-person-han.md).\n")
    result = check_missing_entities.scan(tmp_path)
    assert result.candidates == ()


def test_wikilink_mentions_on_two_pages(tmp_path: Path) -> None:
    write_page(tmp_path, "wiki/topics/a.md", "Notes on [[韩炳哲]].\n")
    write_page(tmp_path, "wiki/topics/b.md", "Again [[韩炳哲]].\n")
    result = check_missing_entities.scan(tmp_path)
    assert len(result.candidates) == 1
    candidate = result.candidates[0]
    assert candidate.kind == "mention"
    assert candidate.key == "韩炳哲"
    assert candidate.pages == ("wiki/topics/a.md", "wiki/topics/b.md")


def test_alias_suppresses_the_mention(tmp_path: Path) -> None:
    write_page(
        tmp_path,
        "wiki/entities/entity-person-han.md",
        "---\naliases:\n  - 韩炳哲\n---\n\n# Byung-Chul Han\n",
    )
    write_page(tmp_path, "wiki/topics/a.md", "[[韩炳哲]]\n")
    write_page(tmp_path, "wiki/topics/b.md", "[[韩炳哲]]\n")
    result = check_missing_entities.scan(tmp_path)
    assert result.candidates == ()


def test_topic_title_is_not_an_entity_candidate(tmp_path: Path) -> None:
    write_page(tmp_path, "wiki/topics/cs-dp-intro.md", "# 动态规划\n")
    write_page(tmp_path, "wiki/maps/one.md", "See [[动态规划]].\n")
    write_page(tmp_path, "wiki/maps/two.md", "See [[动态规划]].\n")
    result = check_missing_entities.scan(tmp_path)
    assert result.candidates == ()


def test_prose_repetition_is_not_a_candidate(tmp_path: Path) -> None:
    for name in ("a", "b", "c"):
        write_page(tmp_path, f"wiki/topics/{name}.md", "韩炳哲写了这本书。韩炳哲又出现一次。\n")
    result = check_missing_entities.scan(tmp_path)
    assert result.candidates == ()


def test_fenced_wikilink_does_not_count(tmp_path: Path) -> None:
    write_page(tmp_path, "wiki/topics/a.md", "[[韩炳哲]]\n")
    write_page(tmp_path, "wiki/topics/b.md", "```\n[[韩炳哲]]\n```\n")
    result = check_missing_entities.scan(tmp_path)
    assert result.candidates == ()


def test_entity_scheme_on_two_pages(tmp_path: Path) -> None:
    write_page(tmp_path, "wiki/topics/a.md", "See [韩炳哲](entity:韩炳哲).\n")
    write_page(tmp_path, "wiki/topics/b.md", "See [韩炳哲](entity:韩炳哲).\n")
    result = check_missing_entities.scan(tmp_path)
    assert len(result.candidates) == 1
    assert result.candidates[0].kind == "mention"
    assert result.candidates[0].key == "韩炳哲"


def test_frontmatter_sources_count_as_inbound_links(tmp_path: Path) -> None:
    body = "---\nsources:\n  - ../entities/entity-person-han.md\n---\n\n# Note\n"
    write_page(tmp_path, "wiki/topics/a.md", body)
    write_page(tmp_path, "wiki/topics/b.md", body)
    result = check_missing_entities.scan(tmp_path)
    assert len(result.candidates) == 1
    assert result.candidates[0].key == "wiki/entities/entity-person-han.md"


def test_template_example_links_are_ignored(tmp_path: Path) -> None:
    link = "See [Han](../entities/entity-person-han.md).\n"
    write_page(tmp_path, "wiki/templates/entity-template.md", link)
    write_page(tmp_path, "wiki/topics/only.md", link)
    result = check_missing_entities.scan(tmp_path)
    assert result.candidates == ()


def test_strict_exits_1_when_candidates_exist(tmp_path: Path) -> None:
    write_page(tmp_path, "wiki/topics/a.md", "[[吴琼]]\n")
    write_page(tmp_path, "wiki/topics/b.md", "[[吴琼]]\n")
    assert check_missing_entities.main(["--root", str(tmp_path), "--strict"]) == 1


def test_min_pages_below_two_is_rejected(tmp_path: Path) -> None:
    write_page(tmp_path, "wiki/topics/a.md", "[[吴琼]]\n")
    assert check_missing_entities.main(["--root", str(tmp_path), "--min-pages", "1"]) == 2
    try:
        check_missing_entities.scan(tmp_path, min_pages=1)
    except ValueError as exc:
        assert "2" in str(exc)
    else:
        raise AssertionError("min_pages=1 must raise ValueError")


def test_missing_wiki_directory_exits_2(tmp_path: Path) -> None:
    assert check_missing_entities.main(["--root", str(tmp_path)]) == 2


def test_index_has_no_pending_ingest_placeholder() -> None:
    text = (REPO_ROOT / "wiki" / "index.md").read_text(encoding="utf-8")
    assert "待 ingest" not in text
    assert "inbox.md" in text


def test_live_wiki_does_not_recommend_the_existing_book_or_prose_names() -> None:
    result = check_missing_entities.scan(REPO_ROOT)
    report = check_missing_entities.format_report(result)
    assert result.min_pages >= 2
    assert "entity-book-palliative-society" not in report
    assert "韩炳哲" not in report
    for candidate in result.candidates:
        assert len(candidate.pages) >= 2
        assert len(set(candidate.pages)) == len(candidate.pages)
    assert check_missing_entities.main(["--root", str(REPO_ROOT)]) == 0
