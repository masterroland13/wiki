"""Behavior tests for scripts/lint_wiki.py. Bad pages live in tmp dirs, not the repo."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

_SCRIPT = Path(__file__).resolve().parent / "lint_wiki.py"
_SPEC = importlib.util.spec_from_file_location("lint_wiki", _SCRIPT)
assert _SPEC is not None and _SPEC.loader is not None
lint_wiki = importlib.util.module_from_spec(_SPEC)
sys.modules[_SPEC.name] = lint_wiki
_SPEC.loader.exec_module(lint_wiki)

REPO_ROOT = Path(__file__).resolve().parents[1]


def write(root: Path, rel: str, text: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def page(body: str = "Body.\n", **fields: str) -> str:
    data = {
        "type": "topic",
        "status": "seed",
        "created": "2026-11-02",
        "updated": "2026-11-02",
        "tags": "[]",
        "sources": "[]",
    }
    data.update(fields)
    lines = ["---"]
    for key in ("type", "status", "created", "updated", "tags", "sources"):
        lines.append(f"{key}: {data[key]}")
    for key, value in data.items():
        if key not in ("type", "status", "created", "updated", "tags", "sources"):
            lines.append(f"{key}: {value}")
    lines.append("---")
    lines.append("")
    lines.append(body)
    return "\n".join(lines)


def messages(result, severity: str | None = None) -> list[str]:
    return [
        f"{item.path}: {item.message}"
        for item in result.findings
        if severity is None or item.severity == severity
    ]


def test_missing_frontmatter_reports_path(tmp_path: Path) -> None:
    write(tmp_path, "wiki/topics/bare.md", "# Bare\n\nNo frontmatter.\n")
    write(tmp_path, "wiki/index.md", page("See [bare](./topics/bare.md).\n", type="map"))
    result = lint_wiki.lint_root(tmp_path)
    errors = messages(result, "error")
    assert any(line.startswith("wiki/topics/bare.md:") and "missing frontmatter" in line for line in errors)


def test_missing_required_field_reports_path(tmp_path: Path) -> None:
    text = page().replace("tags: []\n", "")
    write(tmp_path, "wiki/topics/no-tags.md", text)
    write(tmp_path, "wiki/index.md", page("See [page](./topics/no-tags.md).\n", type="map"))
    result = lint_wiki.lint_root(tmp_path)
    assert any(
        item.path == "wiki/topics/no-tags.md" and "missing frontmatter field 'tags'" in item.message
        for item in result.errors
    )


def test_invalid_type_and_status_report_path(tmp_path: Path) -> None:
    write(tmp_path, "wiki/topics/bad.md", page(type="essay", status="draft"))
    write(tmp_path, "wiki/index.md", page("See [bad](./topics/bad.md).\n", type="map"))
    result = lint_wiki.lint_root(tmp_path)
    blob = "\n".join(messages(result, "error"))
    assert "wiki/topics/bad.md" in blob
    assert "invalid type 'essay'" in blob
    assert "invalid status 'draft'" in blob


def test_broken_relative_link_reports_path(tmp_path: Path) -> None:
    write(tmp_path, "wiki/topics/hole.md", page("See [missing](./missing.md).\n"))
    write(tmp_path, "wiki/index.md", page("See [hole](./topics/hole.md).\n", type="map"))
    result = lint_wiki.lint_root(tmp_path)
    assert any(
        item.path == "wiki/topics/hole.md" and "broken relative link: ./missing.md" in item.message
        for item in result.errors
    )


def test_broken_image_reports_path(tmp_path: Path) -> None:
    write(tmp_path, "wiki/topics/pic.md", page("![chart](./assets/missing.png)\n"))
    write(tmp_path, "wiki/index.md", page("See [pic](./topics/pic.md).\n", type="map"))
    result = lint_wiki.lint_root(tmp_path)
    assert any(
        item.path == "wiki/topics/pic.md" and "broken relative link: ./assets/missing.png" in item.message
        for item in result.errors
    )


def test_http_anchor_and_existing_link_are_ignored(tmp_path: Path) -> None:
    body = "\n".join(
        [
            "See [web](https://example.com/a).",
            "See [mail](mailto:a@example.com).",
            "See [here](#section).",
            "See [readme](../../README.md).",
            "",
        ]
    )
    write(tmp_path, "README.md", "# Repo\n")
    write(tmp_path, "wiki/topics/ok.md", page(body))
    write(tmp_path, "wiki/index.md", page("See [ok](./topics/ok.md#section).\n", type="map"))
    result = lint_wiki.lint_root(tmp_path)
    assert result.errors == []
    assert result.warnings == []


def test_code_fence_and_inline_code_are_not_checked(tmp_path: Path) -> None:
    body = "\n".join(
        [
            "Placeholder stays inside the fence:",
            "",
            "```markdown",
            "![描述](./assets/<stem>/file.png)",
            "[gone](./does-not-exist.md)",
            "```",
            "",
            "Inline `[gone](./also-missing.md)` is an example.",
            "",
        ]
    )
    write(tmp_path, "wiki/topics/examples.md", page(body))
    write(tmp_path, "wiki/index.md", page("See [examples](./topics/examples.md).\n", type="map"))
    result = lint_wiki.lint_root(tmp_path)
    assert result.errors == []


def test_later_frontmatter_block_is_not_parsed(tmp_path: Path) -> None:
    body = "\n".join(
        [
            "Example only:",
            "",
            "---",
            "type: not-a-type",
            "status: nope",
            "---",
            "",
        ]
    )
    write(tmp_path, "wiki/topics/sample.md", page(body))
    write(tmp_path, "wiki/index.md", page("See [sample](./topics/sample.md).\n", type="map"))
    result = lint_wiki.lint_root(tmp_path)
    assert result.errors == []


def test_growing_and_stale_without_review_after_warn(tmp_path: Path) -> None:
    write(tmp_path, "wiki/topics/grow.md", page(status="growing"))
    write(tmp_path, "wiki/topics/old.md", page(status="stale"))
    write(
        tmp_path,
        "wiki/index.md",
        page("See [grow](./topics/grow.md) and [old](./topics/old.md).\n", type="map", status="seed"),
    )
    result = lint_wiki.lint_root(tmp_path)
    assert result.errors == []
    warned = {item.path: item.message for item in result.warnings}
    assert "missing review_after" in warned["wiki/topics/grow.md"]
    assert "missing review_after" in warned["wiki/topics/old.md"]


def test_seed_with_empty_review_after_is_clean(tmp_path: Path) -> None:
    write(tmp_path, "wiki/topics/seed.md", page(status="seed", review_after=""))
    write(tmp_path, "wiki/index.md", page("See [seed](./topics/seed.md).\n", type="map"))
    result = lint_wiki.lint_root(tmp_path)
    assert result.findings == []


def test_review_after_present_suppresses_warning(tmp_path: Path) -> None:
    write(tmp_path, "wiki/topics/grow.md", page(status="growing", review_after="2026-12-01"))
    write(tmp_path, "wiki/index.md", page("See [grow](./topics/grow.md).\n", type="map"))
    result = lint_wiki.lint_root(tmp_path)
    assert result.findings == []


def test_orphan_candidate_reports_path_and_spares_linked_pages(tmp_path: Path) -> None:
    write(tmp_path, "wiki/topics/linked.md", page("Linked.\n"))
    write(tmp_path, "wiki/topics/lonely.md", page("Alone.\n"))
    write(tmp_path, "wiki/index.md", page("See [linked](./topics/linked.md).\n", type="map"))
    result = lint_wiki.lint_root(tmp_path)
    orphans = [item.path for item in result.warnings if "orphan candidate" in item.message]
    assert orphans == ["wiki/topics/lonely.md"]
    assert result.errors == []


def test_evals_are_structural_not_knowledge_pages(tmp_path: Path) -> None:
    write(tmp_path, "wiki/evals/retrieval-cases.md", "# Retrieval cases\n\nNo frontmatter.\n")
    write(tmp_path, "wiki/index.md", page("Root only.\n", type="map"))
    result = lint_wiki.lint_root(tmp_path)
    assert result.findings == []

    write(tmp_path, "wiki/evals/retrieval-cases.md", "See [missing](./missing.md).\n")
    result = lint_wiki.lint_root(tmp_path)
    assert any(
        item.path == "wiki/evals/retrieval-cases.md" and "broken relative link: ./missing.md" in item.message
        for item in result.errors
    )
    assert not any("frontmatter" in item.message for item in result.findings)


def test_index_and_templates_are_not_orphan_candidates(tmp_path: Path) -> None:
    write(tmp_path, "wiki/index.md", page("Root only.\n", type="map"))
    write(tmp_path, "wiki/templates/unused.md", page("Scaffold.\n"))
    result = lint_wiki.lint_root(tmp_path)
    assert result.findings == []


def test_sources_missing_path_reports_path(tmp_path: Path) -> None:
    write(
        tmp_path,
        "wiki/topics/src.md",
        page(sources="\n  - ../missing-source.md\n  - https://example.com/ok"),
    )
    write(tmp_path, "wiki/index.md", page("See [src](./topics/src.md).\n", type="map"))
    result = lint_wiki.lint_root(tmp_path)
    assert any(
        item.path == "wiki/topics/src.md" and "sources path not found: ../missing-source.md" in item.message
        for item in result.errors
    )
    assert not any("example.com" in item.message for item in result.findings)


def test_invalid_yaml_and_date_report_path(tmp_path: Path) -> None:
    write(
        tmp_path,
        "wiki/topics/yaml.md",
        '---\ntype: "unterminated\nstatus: seed\n---\n\n# x\n',
    )
    write(tmp_path, "wiki/topics/date.md", page(created="2026-13-40"))
    write(
        tmp_path,
        "wiki/index.md",
        page("See [yaml](./topics/yaml.md) and [date](./topics/date.md).\n", type="map"),
    )
    result = lint_wiki.lint_root(tmp_path)
    blob = "\n".join(messages(result, "error"))
    assert "wiki/topics/yaml.md" in blob and "frontmatter YAML parse error" in blob
    assert "wiki/topics/date.md" in blob and "invalid date for 'created'" in blob


def test_warnings_exit_zero_and_strict_exits_one(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    write(tmp_path, "wiki/topics/grow.md", page(status="growing"))
    write(tmp_path, "wiki/index.md", page("See [grow](./topics/grow.md).\n", type="map"))

    code = lint_wiki.main(["--root", str(tmp_path)])
    out = capsys.readouterr().out
    assert code == 0
    assert "WARN wiki/topics/grow.md:" in out
    assert "errors=0 warnings=1" in out

    strict = lint_wiki.main(["--root", str(tmp_path), "--strict"])
    strict_out = capsys.readouterr().out
    assert strict == 1
    assert "wiki/topics/grow.md" in strict_out


def test_errors_exit_nonzero_and_print_path(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    write(tmp_path, "wiki/topics/hole.md", page("See [missing](./nope.md).\n"))
    write(tmp_path, "wiki/index.md", page("See [hole](./topics/hole.md).\n", type="map"))
    code = lint_wiki.main(["--root", str(tmp_path)])
    out = capsys.readouterr().out
    assert code == 1
    assert "ERROR wiki/topics/hole.md:" in out
    assert "./nope.md" in out


def test_missing_wiki_directory_exits_2(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    code = lint_wiki.main(["--root", str(tmp_path)])
    err = capsys.readouterr().err
    assert code == 2
    assert "wiki directory not found" in err


def test_template_placeholder_links_are_not_errors(tmp_path: Path) -> None:
    write(tmp_path, "wiki/templates/topic-template.md", page("See [ex](../topics/example-topic.md).\n"))
    write(tmp_path, "wiki/index.md", page("Root.\n", type="map"))
    result = lint_wiki.lint_root(tmp_path)
    assert result.errors == []
    assert result.warnings == []


def test_repository_has_no_errors() -> None:
    result = lint_wiki.lint_root(REPO_ROOT)
    assert result.errors == []
    assert result.pages_scanned > 0
    assert not any("still links to this page" in item.message for item in result.warnings)
    assert not any("must be a path or a list of paths" in item.message for item in result.warnings)
    assert not any(item.message.startswith("superseded_by path not found") for item in result.warnings)
    assert not any(item.message.startswith("supersedes path not found") for item in result.warnings)


def test_contradiction_demo_keeps_both_claims_and_hides_superseded_page_from_index() -> None:
    demo = (REPO_ROOT / "wiki/topics/x-demo-contradiction-coexistence.md").read_text(encoding="utf-8")
    filing = (REPO_ROOT / "wiki/topics/x-demo-superseded-filing.md").read_text(encoding="utf-8")
    index = (REPO_ROOT / "wiki/index.md").read_text(encoding="utf-8")
    assert "## Contradictions" in demo and "## Superseded" in demo
    assert "不裁定" in demo
    assert "78" in demo and "81" in demo
    assert "supersedes:" in demo
    assert "superseded_by:" not in demo
    assert "## Contradictions" in filing and "## Superseded" in filing
    assert "phil-" in filing
    assert "superseded_by:" in filing
    assert "x-demo-contradiction-coexistence.md" in index
    assert "x-demo-superseded-filing.md" not in index


@pytest.mark.parametrize("value", ["./newer.md", "\n  - ./newer.md"])
def test_index_link_to_superseded_page_warns(tmp_path: Path, value: str) -> None:
    write(tmp_path, "wiki/topics/newer.md", page("Successor.\n"))
    write(
        tmp_path,
        "wiki/topics/old.md",
        page("See [newer](./newer.md).\n", superseded_by=value),
    )
    write(tmp_path, "wiki/index.md", page("See [old](./topics/old.md).\n", type="map"))
    result = lint_wiki.lint_root(tmp_path)
    assert result.errors == []
    assert any(
        item.path == "wiki/topics/old.md"
        and item.message == "superseded_by is set but wiki/index.md still links to this page"
        for item in result.warnings
    )


def test_index_promoted_superseded_page_is_warning_not_error(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    write(tmp_path, "wiki/topics/newer.md", page("Successor.\n"))
    write(
        tmp_path,
        "wiki/topics/old.md",
        page("See [newer](./newer.md).\n", superseded_by="./newer.md"),
    )
    write(tmp_path, "wiki/index.md", page("See [old](./topics/old.md).\n", type="map"))
    code = lint_wiki.main(["--root", str(tmp_path)])
    out = capsys.readouterr().out
    assert code == 0
    assert "WARN wiki/topics/old.md: superseded_by is set but wiki/index.md still links to this page" in out
    assert "ERROR" not in out
    strict = lint_wiki.main(["--root", str(tmp_path), "--strict"])
    assert strict == 1


def test_superseded_page_linked_only_from_map_or_project_is_not_promoted(tmp_path: Path) -> None:
    write(tmp_path, "wiki/topics/newer.md", page("Successor.\n"))
    write(
        tmp_path,
        "wiki/topics/old.md",
        page("See [newer](./newer.md).\n", superseded_by="./newer.md"),
    )
    write(tmp_path, "wiki/maps/hub.md", page("See [old](../topics/old.md).\n", type="map"))
    write(
        tmp_path,
        "wiki/projects/demo/index.md",
        page("See [old](../../topics/old.md).\n", type="project-note"),
    )
    write(
        tmp_path,
        "wiki/index.md",
        page("See [map](./maps/hub.md) and [project](./projects/demo/index.md).\n", type="map"),
    )
    result = lint_wiki.lint_root(tmp_path)
    assert result.findings == []


def test_successor_on_index_with_only_supersedes_does_not_warn(tmp_path: Path) -> None:
    write(tmp_path, "wiki/topics/old.md", page("Old wording stays.\n"))
    write(
        tmp_path,
        "wiki/topics/newer.md",
        page("See [old](./old.md).\n", supersedes="./old.md"),
    )
    write(tmp_path, "wiki/index.md", page("See [newer](./topics/newer.md).\n", type="map"))
    result = lint_wiki.lint_root(tmp_path)
    assert result.findings == []


def test_empty_or_absent_superseded_by_does_not_warn(tmp_path: Path) -> None:
    write(tmp_path, "wiki/topics/empty.md", page("Empty field.\n", superseded_by="[]"))
    write(tmp_path, "wiki/topics/absent.md", page("No field.\n"))
    write(
        tmp_path,
        "wiki/index.md",
        page("See [empty](./topics/empty.md) and [absent](./topics/absent.md).\n", type="map"),
    )
    result = lint_wiki.lint_root(tmp_path)
    assert result.findings == []


def test_index_code_mention_does_not_promote_superseded_page(tmp_path: Path) -> None:
    write(tmp_path, "wiki/topics/newer.md", page("Successor.\n"))
    write(
        tmp_path,
        "wiki/topics/old.md",
        page("See [newer](./newer.md).\n", superseded_by="./newer.md"),
    )
    write(tmp_path, "wiki/topics/hub.md", page("See [old](./old.md).\n"))
    index_body = "\n".join(
        [
            "Mention `./topics/old.md` in inline code.",
            "",
            "```markdown",
            "[old](./topics/old.md)",
            "```",
            "",
            "See [hub](./topics/hub.md).",
            "",
        ]
    )
    write(tmp_path, "wiki/index.md", page(index_body, type="map"))
    result = lint_wiki.lint_root(tmp_path)
    assert result.findings == []


def test_invalid_superseded_by_shape_warns_without_promotion(tmp_path: Path) -> None:
    text = page("See [hub](./hub.md).\n")
    text = text.replace("---\n\n", "superseded_by: 3\n---\n\n", 1)
    write(tmp_path, "wiki/topics/old.md", text)
    write(tmp_path, "wiki/topics/hub.md", page("Hub.\n"))
    write(tmp_path, "wiki/index.md", page("See [old](./topics/old.md).\n", type="map"))
    result = lint_wiki.lint_root(tmp_path)
    assert result.errors == []
    assert [item.message for item in result.warnings] == ["superseded_by must be a path or a list of paths"]


def test_missing_supersession_path_warns_and_does_not_fail(tmp_path: Path) -> None:
    write(
        tmp_path,
        "wiki/topics/old.md",
        page("Kept.\n", superseded_by="./missing.md", supersedes="./also-missing.md"),
    )
    write(tmp_path, "wiki/index.md", page("Root only.\n", type="map"))
    result = lint_wiki.lint_root(tmp_path)
    assert result.errors == []
    blob = "\n".join(messages(result, "warning"))
    assert "wiki/topics/old.md: superseded_by path not found: ./missing.md" in blob
    assert "wiki/topics/old.md: supersedes path not found: ./also-missing.md" in blob
    assert "still links to this page" not in blob
