#!/usr/bin/env python3
"""Machine lint for wiki Markdown: frontmatter, relative links, orphan candidates.

This is the executable subset of wiki/WIKI_SCHEMA.md. It does not decide which
contradictory claim is true, and it does not read source mtimes or prose quality.
It does warn when a page with superseded_by is still linked from wiki/index.md.

Exit codes:
  0  no errors (warnings are allowed)
  1  one or more errors, or any warning when --strict is set
  2  usage error, missing wiki directory, or missing PyYAML

Warnings-only runs stay exit 0 so this script is not a CI gate.
"""

from __future__ import annotations

import argparse
import datetime as dt
import re
import sys
import urllib.parse
from dataclasses import dataclass
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover - exercised only when PyYAML is absent
    yaml = None


REQUIRED_FIELDS = ("type", "status", "created", "updated", "tags", "sources")
TYPES = {"topic", "map", "paper", "entity", "project-note"}
STATUSES = {"seed", "growing", "stable", "stale"}
REVIEW_STATUSES = {"growing", "stale"}

# Structural docs are not knowledge pages. They are still link-checked.
FRONTMATTER_EXEMPT_EXACT = {
    "wiki/changelog.md",
    "wiki/log.md",
    "wiki/WIKI_SCHEMA.md",
    "wiki/templates/template-design-rationale.md",
}
FRONTMATTER_EXEMPT_PREFIXES = (
    "wiki/references/",
    "wiki/evals/",
)

DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
LINK_RE = re.compile(r"!?\[[^\]\n]*\]\(([^)\n]+)\)")
FENCE_RE = re.compile(
    r"^[ \t]{0,3}(```+|~~~+)[^\n]*\n.*?\n[ \t]{0,3}\1[ \t]*$",
    re.MULTILINE | re.DOTALL,
)
FENCE_OPEN_RE = re.compile(
    r"^[ \t]{0,3}(```+|~~~+)[^\n]*\n.*\Z",
    re.MULTILINE | re.DOTALL,
)
INLINE_CODE_RE = re.compile(r"`[^`\n]+`")
SCHEME_RE = re.compile(r"^[a-zA-Z][a-zA-Z0-9+.-]*:")
DEST_TITLE_RE = re.compile(r"""^(\S+?)(?:\s+(?:"[^"]*"|'[^']*'))?$""")
TIMESTAMP_TAG = "tag:yaml.org,2002:timestamp"


if yaml is not None:

    class FrontmatterLoader(yaml.SafeLoader):
        """Safe YAML loader that keeps dates as strings.

        PyYAML otherwise builds datetime.date and raises ValueError for values
        such as 2026-13-40, which would abort the whole run.
        """

    FrontmatterLoader.yaml_implicit_resolvers = {
        key: [(tag, pattern) for tag, pattern in items if tag != TIMESTAMP_TAG]
        for key, items in yaml.SafeLoader.yaml_implicit_resolvers.items()
        if any(tag != TIMESTAMP_TAG for tag, _pattern in items)
    }
else:  # pragma: no cover - PyYAML is required to run
    FrontmatterLoader = None


def load_frontmatter(raw: str):
    if yaml is None:
        raise RuntimeError("PyYAML is required (pip install pyyaml)")
    return yaml.load(raw, Loader=FrontmatterLoader)


@dataclass(frozen=True)
class Finding:
    severity: str  # "error" or "warning"
    path: str
    message: str


@dataclass
class LintResult:
    pages_scanned: int
    frontmatter_pages: int
    findings: list[Finding]

    @property
    def errors(self) -> list[Finding]:
        return [item for item in self.findings if item.severity == "error"]

    @property
    def warnings(self) -> list[Finding]:
        return [item for item in self.findings if item.severity == "warning"]


def requires_frontmatter(rel: str) -> bool:
    """Knowledge pages must carry the frontmatter contract. READMEs and guides do not."""
    if rel in FRONTMATTER_EXEMPT_EXACT or rel.startswith(FRONTMATTER_EXEMPT_PREFIXES):
        return False
    if Path(rel).name == "README.md":
        return False
    return True


def is_orphan_candidate(rel: str) -> bool:
    """Templates are scaffolds. index.md is the navigation root."""
    if rel == "wiki/index.md" or rel.startswith(("wiki/templates/", "wiki/evals/")):
        return False
    return True


def lint_root(root: Path) -> LintResult:
    """Lint wiki/ under a repository root. Raises FileNotFoundError if wiki/ is missing."""
    if yaml is None:
        raise RuntimeError("PyYAML is required (pip install pyyaml)")

    root = root.resolve()
    wiki = root / "wiki"
    if not wiki.is_dir():
        raise FileNotFoundError(f"wiki directory not found: {wiki}")

    pages = sorted(path for path in wiki.rglob("*.md") if path.is_file())
    page_rel: dict[Path, str] = {}
    texts: dict[Path, str] = {}
    findings: list[Finding] = []
    seen: set[tuple[str, str, str]] = set()

    def add(severity: str, rel: str, message: str) -> None:
        key = (severity, rel, message)
        if key in seen:
            return
        seen.add(key)
        findings.append(Finding(severity, rel, message))

    frontmatter_pages = 0
    superseded_rels: list[str] = []
    for path in pages:
        rel = path.relative_to(root).as_posix()
        page_rel[path.resolve()] = rel
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            add("error", rel, "file is not valid UTF-8")
            text = ""
        texts[path] = text
        if requires_frontmatter(rel):
            frontmatter_pages += 1
            check_frontmatter(text, rel, path, add, superseded_rels)

    inbound: set[Path] = set()
    for path in pages:
        rel = page_rel[path.resolve()]
        # Templates are copied into topics/maps/projects before their example
        # links (example-*.md, paths relative to the destination) exist.
        if rel.startswith("wiki/templates/"):
            continue
        _state, body = split_frontmatter(texts[path])
        for dest in extract_destinations(body):
            target = classify_destination(path, dest)
            if target is None:
                continue
            if not target.is_file():
                add("error", rel, f"broken relative link: {dest.strip()}")
                continue
            resolved = target.resolve()
            if resolved in page_rel and resolved != path.resolve():
                inbound.add(resolved)

    for resolved, rel in sorted(page_rel.items(), key=lambda item: item[1]):
        if is_orphan_candidate(rel) and resolved not in inbound:
            add("warning", rel, "orphan candidate (no inbound markdown link from another wiki page)")

    warn_index_promoted_superseded(pages, page_rel, texts, superseded_rels, add)

    findings.sort(key=lambda item: (0 if item.severity == "error" else 1, item.path, item.message))
    return LintResult(len(pages), frontmatter_pages, findings)


def check_frontmatter(text: str, rel: str, path: Path, add, superseded_rels: list[str]) -> None:
    state, _body, raw = split_frontmatter_raw(text)
    if state == "absent":
        fields = ", ".join(REQUIRED_FIELDS)
        add("error", rel, f"missing frontmatter (required fields: {fields})")
        return
    if state == "unclosed":
        add("error", rel, "unclosed frontmatter")
        return

    try:
        loaded = load_frontmatter(raw) if raw.strip() else {}
    except (yaml.YAMLError, ValueError) as exc:
        detail = str(exc).splitlines()[0].strip() if str(exc).strip() else "invalid YAML"
        add("error", rel, f"frontmatter YAML parse error: {detail}")
        return

    if loaded is None:
        loaded = {}
    if not isinstance(loaded, dict):
        add("error", rel, "frontmatter must be a mapping")
        return

    require_enum(loaded, "type", TYPES, rel, add)
    status = require_enum(loaded, "status", STATUSES, rel, add)
    require_date_field(loaded, "created", rel, add)
    require_date_field(loaded, "updated", rel, add)
    tags = require_list(loaded, "tags", rel, add)
    sources = require_list(loaded, "sources", rel, add)

    if tags is not None:
        for item in tags:
            if isinstance(item, str) and item.strip():
                continue
            add("error", rel, "tags entries must be non-empty strings")
            break

    if sources is not None:
        for item in sources:
            check_source_item(path, rel, item, add)

    check_optional_refs(loaded, "supersedes", rel, path, add)
    if check_optional_refs(loaded, "superseded_by", rel, path, add):
        superseded_rels.append(rel)

    review = loaded.get("review_after")
    review_missing = review is None or review == ""
    if review_missing:
        if status in REVIEW_STATUSES:
            add("warning", rel, f"status {status} is missing review_after (YYYY-MM-DD)")
    elif normalize_date(review) is None:
        add("error", rel, "invalid date for 'review_after' (expected YYYY-MM-DD)")


def normalize_ref_field(value) -> tuple[str, list[str]]:
    """Classify an optional supersedes / superseded_by value.

    Returns ("empty", []), ("ok", entries), or ("invalid", []).
    Empty means the field is absent in effect: null, blank, or no non-empty strings.
    """
    if value is None or value == "":
        return "empty", []
    if isinstance(value, str):
        text = value.strip()
        if not text:
            return "empty", []
        return "ok", [text]
    if isinstance(value, list):
        entries: list[str] = []
        for item in value:
            if item is None or item == "":
                continue
            if not isinstance(item, str):
                return "invalid", []
            text = item.strip()
            if text:
                entries.append(text)
        if not entries:
            return "empty", []
        return "ok", entries
    return "invalid", []


def check_optional_refs(loaded: dict, key: str, rel: str, path: Path, add) -> list[str]:
    """Warn on a bad optional ref field. Return entries when it counts as set.

    Missing files are warnings, not errors, so an optional field cannot fail the run.
    An invalid shape does not count as set.
    """
    if key not in loaded:
        return []
    shape, entries = normalize_ref_field(loaded.get(key))
    if shape == "invalid":
        add("warning", rel, f"{key} must be a path or a list of paths")
        return []
    for item in entries:
        if ref_target_exists(path, item):
            continue
        add("warning", rel, f"{key} path not found: {item}")
    return entries


def ref_target_exists(md_file: Path, item: str) -> bool:
    """True when the entry is not a missing local file. Labels and URLs pass."""
    if is_external(item) or item.startswith("#"):
        return True
    if any(char in item for char in "<>*"):
        return True
    if not is_path_like(item):
        return True
    dest = item.split("#", 1)[0].split("?", 1)[0].strip()
    if not dest:
        return True
    return resolve_relative(md_file, dest).is_file()


def warn_index_promoted_superseded(pages, page_rel, texts, superseded_rels: list[str], add) -> None:
    """Warn when wiki/index.md links a page whose superseded_by is set.

    Only direct links on wiki/index.md count. Maps, project hubs, and links
    inside fenced or inline code do not. The check does not walk a graph.
    """
    if not superseded_rels:
        return
    index_path = next((path for path in pages if page_rel.get(path.resolve()) == "wiki/index.md"), None)
    if index_path is None:
        return
    promoted: set[Path] = set()
    _state, body = split_frontmatter(texts.get(index_path, ""))
    for dest in extract_destinations(body):
        target = classify_destination(index_path, dest)
        if target is None or not target.is_file():
            continue
        promoted.add(target.resolve())
    for rel in superseded_rels:
        page = next((path for path in pages if page_rel.get(path.resolve()) == rel), None)
        if page is not None and page.resolve() in promoted:
            add("warning", rel, "superseded_by is set but wiki/index.md still links to this page")


def check_source_item(path: Path, rel: str, item, add) -> None:
    if isinstance(item, dict):
        return
    if not isinstance(item, str):
        add("error", rel, "sources entries must be strings or mappings")
        return
    text = item.strip()
    if not text or is_external(text) or text.startswith("#"):
        return
    if any(char in text for char in "<>*"):
        return
    if not is_path_like(text):
        return
    target = resolve_relative(path, text)
    if not target.is_file():
        add("error", rel, f"sources path not found: {text}")


def require_enum(data: dict, key: str, allowed: set[str], rel: str, add) -> str | None:
    if key not in data or data[key] is None or data[key] == "":
        add("error", rel, f"missing frontmatter field '{key}'")
        return None
    value = data[key]
    if not isinstance(value, str):
        add("error", rel, f"invalid {key} (expected {'|'.join(sorted(allowed))})")
        return None
    text = value.strip()
    if text not in allowed:
        add("error", rel, f"invalid {key} '{text}' (expected {'|'.join(sorted(allowed))})")
        return None
    return text


def require_date_field(data: dict, key: str, rel: str, add) -> None:
    if key not in data or data[key] is None or data[key] == "":
        add("error", rel, f"missing frontmatter field '{key}'")
        return
    if normalize_date(data[key]) is None:
        add("error", rel, f"invalid date for '{key}' (expected YYYY-MM-DD)")


def require_list(data: dict, key: str, rel: str, add) -> list | None:
    if key not in data or data[key] is None:
        add("error", rel, f"missing frontmatter field '{key}'")
        return None
    if not isinstance(data[key], list):
        add("error", rel, f"frontmatter field '{key}' must be a list")
        return None
    return data[key]


def normalize_date(value) -> str | None:
    """Accept YAML dates and YYYY-MM-DD strings. Reject other shapes."""
    if isinstance(value, dt.datetime):
        value = value.date()
    if isinstance(value, dt.date):
        return value.isoformat()
    if isinstance(value, str):
        text = value.strip()
        if not DATE_RE.fullmatch(text):
            return None
        try:
            dt.date.fromisoformat(text)
        except ValueError:
            return None
        return text
    return None


def split_frontmatter(text: str) -> tuple[str, str]:
    state, body, _raw = split_frontmatter_raw(text)
    if state == "ok":
        return state, body
    return state, text


def split_frontmatter_raw(text: str) -> tuple[str, str, str]:
    """Return (state, body, raw_yaml). Only a leading --- block is frontmatter."""
    if text.startswith("\ufeff"):
        text = text[1:]
    lines = text.splitlines(keepends=True)
    if not lines or lines[0].strip() != "---":
        return "absent", text, ""
    for index in range(1, len(lines)):
        if lines[index].strip() == "---":
            raw = "".join(lines[1:index])
            body = "".join(lines[index + 1 :])
            return "ok", body, raw
    return "unclosed", text, ""


def extract_destinations(body: str) -> list[str]:
    masked = mask_code(body)
    return [match.group(1) for match in LINK_RE.finditer(masked)]


def mask_code(text: str) -> str:
    """Hide fenced and inline code so example links are not checked."""

    def blank(match: re.Match) -> str:
        return re.sub(r"[^\n]", " ", match.group(0))

    text = FENCE_RE.sub(blank, text)
    text = FENCE_OPEN_RE.sub(blank, text)
    text = INLINE_CODE_RE.sub(blank, text)
    return text


def classify_destination(md_file: Path, raw: str) -> Path | None:
    """Return a filesystem path to check, or None when the destination is out of scope."""
    dest = raw_destination(raw)
    if not dest or is_external(dest) or dest.startswith("#"):
        return None
    if any(char in dest for char in "<>*"):
        return None
    dest = urllib.parse.unquote(dest)
    dest = dest.split("#", 1)[0].split("?", 1)[0].strip()
    if not dest:
        return None
    return resolve_relative(md_file, dest)


def raw_destination(raw: str) -> str:
    text = raw.strip()
    if not text:
        return ""
    if text[0] == "<":
        end = text.find(">")
        if end != -1:
            return text[1:end].strip()
    match = DEST_TITLE_RE.match(text)
    if match:
        return match.group(1)
    return text.split()[0]


def is_external(dest: str) -> bool:
    return dest.startswith("//") or SCHEME_RE.match(dest) is not None


def is_path_like(text: str) -> bool:
    return "/" in text or text.startswith(".") or text.endswith(".md")


def resolve_relative(md_file: Path, dest: str) -> Path:
    path = Path(dest)
    if path.is_absolute():
        return path
    return (md_file.parent / path).resolve()


def format_report(result: LintResult) -> str:
    lines = [f"{'ERROR' if item.severity == 'error' else 'WARN'} {item.path}: {item.message}" for item in result.findings]
    lines.append(
        "summary: "
        f"scanned={result.pages_scanned} "
        f"frontmatter_pages={result.frontmatter_pages} "
        f"errors={len(result.errors)} "
        f"warnings={len(result.warnings)}"
    )
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Lint wiki Markdown frontmatter, relative links, orphan candidates, "
            "and index links to pages with superseded_by. "
            "Exit 0 when there is no error (warnings allowed). "
            "Exit 1 on errors, or on warnings if --strict. Exit 2 on usage or setup failure."
        )
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=None,
        help="Repository root (default: parent of this script)",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit 1 when any warning is present",
    )
    try:
        args = parser.parse_args(sys.argv[1:] if argv is None else argv)
    except SystemExit as exc:
        code = exc.code
        return code if isinstance(code, int) else 2

    root = args.root if args.root is not None else Path(__file__).resolve().parent.parent
    if yaml is None:
        print("error: PyYAML is required (pip install pyyaml)", file=sys.stderr)
        return 2
    try:
        result = lint_root(root)
    except FileNotFoundError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    except RuntimeError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    sys.stdout.write(format_report(result))
    if result.errors or (args.strict and result.warnings):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
