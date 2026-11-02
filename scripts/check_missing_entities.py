#!/usr/bin/env python3
"""Report missing-entity candidates. Does not create or edit wiki pages.

A candidate needs the same missing entity on at least two distinct wiki pages.
Two signals count:

- a Markdown link, wikilink, or frontmatter path (sources / people / works)
  whose target is a missing ``wiki/entities/entity-*.md``
- an explicit mention: a bare wikilink ``[[name]]``, or a link destination
  ``entity:name``

Prose that merely repeats a name does not count. One page that repeats a link
does not count. Matching an existing entity title, filename slug, or ``aliases``
entry drops the mention. A wikilink whose text matches another wiki page's
title or filename is not an entity candidate.

The user-named exception lives in ``/review``. This script has no flag that
lowers the threshold below 2, and it never writes files.

Exit codes:
  0  scan finished (candidates are allowed)
  1  candidates exist and --strict was set
  2  usage error, missing wiki directory, threshold below 2, or missing PyYAML
"""

from __future__ import annotations

import argparse
import re
import sys
import urllib.parse
from dataclasses import dataclass
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover - exercised only when PyYAML is absent
    yaml = None


MIN_PAGES = 2
MAX_MENTION_CHARS = 80
REF_KEYS = ("sources", "people", "works")

LINK_RE = re.compile(r"!?\[[^\]\n]*\]\(([^)\n]+)\)")
WIKILINK_RE = re.compile(r"(?<!!)\[\[([^\]\n]+)\]\]")
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
HEADING_RE = re.compile(r"^#\s+(.+?)\s*$", re.MULTILINE)
ENTITY_FILE_RE = re.compile(r"^entity-.+\.md$")
WRAPPERS_RE = re.compile(r"[《》「」『』“”\"'‘’]+")


@dataclass
class MentionBucket:
    display: str
    pages: set[str]


@dataclass(frozen=True)
class Candidate:
    kind: str  # "link" or "mention"
    key: str
    pages: tuple[str, ...]


@dataclass(frozen=True)
class ScanResult:
    pages_scanned: int
    min_pages: int
    candidates: tuple[Candidate, ...]


def scan(root: Path, *, min_pages: int = MIN_PAGES) -> ScanResult:
    """Scan ``wiki/`` under ``root``. Raises FileNotFoundError if wiki/ is missing.

    ``min_pages`` below 2 raises ValueError. The CLI turns that into exit 2.
    """
    if min_pages < MIN_PAGES:
        raise ValueError(f"min_pages must be >= {MIN_PAGES}")
    if yaml is None:
        raise RuntimeError("PyYAML is required (pip install pyyaml)")

    root = root.resolve()
    wiki = root / "wiki"
    if not wiki.is_dir():
        raise FileNotFoundError(f"wiki directory not found: {wiki}")

    pages = sorted(path for path in wiki.rglob("*.md") if path.is_file())
    texts: dict[Path, str] = {}
    rels: dict[Path, str] = {}
    for path in pages:
        rels[path] = path.relative_to(root).as_posix()
        try:
            texts[path] = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            texts[path] = ""

    identities = collect_identities(pages, rels, texts)
    link_pages: dict[str, set[str]] = {}
    mention_pages: dict[str, MentionBucket] = {}

    for path in pages:
        rel = rels[path]
        if rel.startswith("wiki/templates/"):
            continue
        body, frontmatter_dests = split_body_and_refs(texts[path])
        masked = mask_code(body)
        for dest in (match.group(1) for match in LINK_RE.finditer(masked)):
            observe_destination(root, path, rel, dest, identities, link_pages, mention_pages)
        for raw in (match.group(1) for match in WIKILINK_RE.finditer(masked)):
            observe_wikilink(root, path, rel, raw, identities, link_pages, mention_pages)
        for dest in frontmatter_dests:
            observe_destination(root, path, rel, dest, identities, link_pages, mention_pages)

    candidates: list[Candidate] = []
    for key in sorted(link_pages):
        found = tuple(sorted(link_pages[key]))
        if len(found) >= min_pages:
            candidates.append(Candidate("link", key, found))
    mention_items = sorted(mention_pages.values(), key=lambda item: item.display)
    for item in mention_items:
        found = tuple(sorted(item.pages))
        if len(found) >= min_pages:
            candidates.append(Candidate("mention", item.display, found))
    candidates.sort(key=lambda item: (item.kind, item.key))
    return ScanResult(len(pages), min_pages, tuple(candidates))


def collect_identities(
    pages: list[Path],
    rels: dict[Path, str],
    texts: dict[Path, str],
) -> set[str]:
    """Names that already have a wiki page, plus entity aliases and slugs."""
    names: set[str] = set()
    for path in pages:
        rel = rels[path]
        names.add(normalize_name(path.stem))
        heading = first_heading(texts[path])
        if heading:
            names.add(normalize_name(heading))
        loaded = parse_frontmatter(texts[path])
        title = loaded.get("title") if isinstance(loaded, dict) else None
        if isinstance(title, str):
            names.add(normalize_name(title))
        if not is_entity_rel(rel):
            continue
        slug = path.stem[len("entity-") :]
        names.add(normalize_name(slug))
        names.add(normalize_name(slug.replace("-", " ")))
        for alias in string_items(loaded.get("aliases") if isinstance(loaded, dict) else None):
            names.add(normalize_name(alias))
    names.discard("")
    return names


def observe_destination(
    root: Path,
    md_file: Path,
    source_rel: str,
    dest: str,
    identities: set[str],
    link_pages: dict[str, set[str]],
    mention_pages: dict[str, MentionBucket],
) -> None:
    name = entity_scheme_name(dest)
    if name is not None:
        add_mention(name, source_rel, identities, mention_pages)
        return
    key = missing_entity_link(root, md_file, dest)
    if key:
        link_pages.setdefault(key, set()).add(source_rel)


def observe_wikilink(
    root: Path,
    md_file: Path,
    source_rel: str,
    raw: str,
    identities: set[str],
    link_pages: dict[str, set[str]],
    mention_pages: dict[str, MentionBucket],
) -> None:
    target = raw.split("|", 1)[0].split("#", 1)[0].strip()
    if not target:
        return
    if is_path_like_target(target):
        if is_entity_pointer(target):
            dest = entity_pointer_dest(target)
            key = missing_entity_link(root, md_file, dest)
            if key:
                link_pages.setdefault(key, set()).add(source_rel)
        return
    add_mention(target, source_rel, identities, mention_pages)


def add_mention(
    surface: str,
    source_rel: str,
    identities: set[str],
    mention_pages: dict[str, MentionBucket],
) -> None:
    text = surface.strip()
    if not text or len(text) > MAX_MENTION_CHARS:
        return
    norm = normalize_name(text)
    if len(norm) < 2 or norm in identities:
        return
    bucket = mention_pages.get(norm)
    if bucket is None:
        mention_pages[norm] = MentionBucket(text, {source_rel})
        return
    bucket.pages.add(source_rel)


def entity_pointer_dest(target: str) -> str:
    """Turn ``entity-foo`` / ``entity-foo.md`` into a repo-relative entity path."""
    name = Path(target).name
    if not name.endswith(".md"):
        name = f"{name}.md"
    if "/" in target or "\\" in target:
        return target.replace("\\", "/")
    return f"wiki/entities/{name}"


def is_path_like_target(target: str) -> bool:
    return "/" in target or "\\" in target or target.endswith(".md") or target.startswith("entity-")


def is_entity_pointer(target: str) -> bool:
    name = Path(target.replace("\\", "/")).name
    if name.endswith(".md"):
        return name.startswith("entity-")
    return target.startswith("entity-")


def missing_entity_link(root: Path, md_file: Path, raw: str) -> str | None:
    """Repo-relative path of a missing entity file, or None."""
    dest = raw_destination(raw)
    if not dest or is_external(dest) or dest.startswith("#"):
        return None
    if any(char in dest for char in "<>*"):
        return None
    dest = urllib.parse.unquote(dest)
    dest = dest.split("#", 1)[0].split("?", 1)[0].strip()
    if not dest:
        return None

    ordered: list[Path] = [(md_file.parent / dest).resolve()]
    if not dest.startswith(("/", ".", "\\")) and ".." not in Path(dest).parts:
        ordered.append((root / dest).resolve())

    saw_entity = False
    entity_rel = ""
    for resolved in ordered:
        rel = repo_rel(root, resolved)
        if rel is None or not is_entity_rel(rel):
            continue
        saw_entity = True
        entity_rel = rel
        if resolved.is_file():
            return None
    if saw_entity:
        return entity_rel
    return None


def entity_scheme_name(raw: str) -> str | None:
    dest = raw_destination(raw)
    if not dest.lower().startswith("entity:"):
        return None
    name = urllib.parse.unquote(dest.split(":", 1)[1])
    name = name.split("#", 1)[0].split("?", 1)[0].strip()
    return name or None


def is_entity_rel(rel: str) -> bool:
    return rel.startswith("wiki/entities/") and ENTITY_FILE_RE.match(Path(rel).name) is not None


def repo_rel(root: Path, path: Path) -> str | None:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return None


def normalize_name(text: str) -> str:
    text = text.strip().casefold().replace("\u3000", " ")
    text = WRAPPERS_RE.sub("", text)
    text = text.replace("-", " ").replace("_", " ").replace("—", " ").replace("–", " ")
    text = re.sub(r"\s+", " ", text).strip()
    return text


def first_heading(text: str) -> str:
    _state, body = split_frontmatter(text)
    match = HEADING_RE.search(body)
    if match is None:
        return ""
    return match.group(1).strip()


def parse_frontmatter(text: str) -> dict:
    state, _body, raw = split_frontmatter_raw(text)
    if state != "ok" or not raw.strip() or yaml is None:
        return {}
    try:
        loaded = yaml.safe_load(raw)
    except yaml.YAMLError:
        return {}
    if isinstance(loaded, dict):
        return loaded
    return {}


def split_body_and_refs(text: str) -> tuple[str, list[str]]:
    state, body, raw = split_frontmatter_raw(text)
    if state != "ok":
        return text, []
    loaded = {}
    if raw.strip() and yaml is not None:
        try:
            parsed = yaml.safe_load(raw)
        except yaml.YAMLError:
            parsed = None
        if isinstance(parsed, dict):
            loaded = parsed
    dests: list[str] = []
    for key in REF_KEYS:
        dests.extend(string_items(loaded.get(key)))
    return body, dests


def string_items(value) -> list[str]:
    if isinstance(value, str):
        text = value.strip()
        return [text] if text else []
    if isinstance(value, list):
        items: list[str] = []
        for item in value:
            if isinstance(item, str) and item.strip():
                items.append(item.strip())
        return items
    return []


def split_frontmatter(text: str) -> tuple[str, str]:
    state, body, _raw = split_frontmatter_raw(text)
    if state == "ok":
        return state, body
    return state, text


def split_frontmatter_raw(text: str) -> tuple[str, str, str]:
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


def mask_code(text: str) -> str:
    """Hide fenced and inline code so examples are not mentions."""

    def blank(match: re.Match) -> str:
        return re.sub(r"[^\n]", " ", match.group(0))

    text = FENCE_RE.sub(blank, text)
    text = FENCE_OPEN_RE.sub(blank, text)
    text = INLINE_CODE_RE.sub(blank, text)
    return text


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


def format_report(result: ScanResult) -> str:
    lines = [
        f"missing-entity candidates: {len(result.candidates)} "
        f"(threshold: {result.min_pages} distinct pages)"
    ]
    for item in result.candidates:
        lines.append(f"- {item.kind} {item.key} pages={len(item.pages)}")
        for page in item.pages:
            lines.append(f"  - {page}")
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Report wiki names that look like missing entities. "
            "A candidate must appear on at least 2 distinct wiki pages "
            "(missing entity-*.md link, [[name]] wikilink, or entity:name). "
            "Prose mentions do not count. This command does not create files. "
            "Exit 0 when the scan finishes. Exit 1 with --strict if any candidate exists. "
            "Exit 2 on usage errors or a threshold below 2."
        )
    )
    parser.add_argument("--root", type=Path, default=None, help="Repository root (default: parent of this script)")
    parser.add_argument(
        "--min-pages",
        type=int,
        default=MIN_PAGES,
        help=f"Distinct wiki pages required (minimum {MIN_PAGES})",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit 1 when any candidate is reported",
    )
    try:
        args = parser.parse_args(sys.argv[1:] if argv is None else argv)
    except SystemExit as exc:
        code = exc.code
        return code if isinstance(code, int) else 2

    if args.min_pages < MIN_PAGES:
        print(f"error: --min-pages must be >= {MIN_PAGES}", file=sys.stderr)
        return 2
    if yaml is None:
        print("error: PyYAML is required (pip install pyyaml)", file=sys.stderr)
        return 2

    root = args.root if args.root is not None else Path(__file__).resolve().parent.parent
    try:
        result = scan(root, min_pages=args.min_pages)
    except FileNotFoundError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    except (RuntimeError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    sys.stdout.write(format_report(result))
    if args.strict and result.candidates:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
