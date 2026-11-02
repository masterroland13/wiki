#!/usr/bin/env python3
"""Check the /query gold set format and that expected wiki paths exist.

This does not answer questions, score an agent, or call an embedding service.
It does not search references/raw/.

Exit codes:
  0  gold set is well formed and expected paths exist
  1  format, count, title-overlap, or missing-path failure
  2  usage error, unreadable file, or missing PyYAML
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover - exercised only when PyYAML is absent
    yaml = None


KINDS = {"direct", "paraphrase", "intentional-miss"}
DEFAULT_CASES = Path("wiki/evals/retrieval-cases.md")
FENCE_RE = re.compile(r"```ya?ml[^\n]*\n(.*?)```", re.DOTALL | re.IGNORECASE)
HEADING_RE = re.compile(r"^#\s+(.+?)\s*$", re.MULTILINE)
FRONTMATTER_RE = re.compile(r"\A---\n.*?\n---\n", re.DOTALL)


@dataclass
class Finding:
    path: str
    message: str


@dataclass
class CheckResult:
    case_count: int = 0
    paraphrase_count: int = 0
    intentional_miss_count: int = 0
    paths_checked: int = 0
    findings: list[Finding] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.findings


def repo_root_from_script() -> Path:
    return Path(__file__).resolve().parent.parent


def load_cases_document(text: str, suffix: str) -> object:
    if suffix == ".json":
        return json.loads(text)
    match = FENCE_RE.search(text)
    if match is None:
        raise ValueError("no ```yaml case block found")
    if yaml is None:
        raise RuntimeError("PyYAML is required (pip install pyyaml)")
    return yaml.safe_load(match.group(1))


def first_heading(text: str) -> str:
    body = FRONTMATTER_RE.sub("", text, count=1)
    match = HEADING_RE.search(body)
    if match is None:
        return ""
    return re.sub(r"\s+", " ", match.group(1)).strip()


def contained(title: str, question: str) -> bool:
    if len(title) < 4:
        return False
    return title.casefold() in re.sub(r"\s+", " ", question).casefold()


def resolve_repo_path(root: Path, rel: str) -> tuple[Path | None, str | None]:
    if not isinstance(rel, str) or not rel.strip():
        return None, "empty path"
    rel = rel.strip()
    if rel.startswith(("/", "\\")) or "\\" in rel or ".." in Path(rel).parts:
        return None, f"not a relative repo path: {rel}"
    path = (root / rel).resolve()
    try:
        path.relative_to(root.resolve())
    except ValueError:
        return None, f"not a relative repo path: {rel}"
    return path, None


def check_document(
    document: object,
    root: Path,
    *,
    source: str,
    min_cases: int = 10,
    min_paraphrase: int = 3,
) -> CheckResult:
    result = CheckResult()

    def add(path: str, message: str) -> None:
        result.findings.append(Finding(path, message))

    if not isinstance(document, dict) or not isinstance(document.get("cases"), list):
        add(source, "document must be a mapping with a cases list")
        return result

    seen_ids: set[str] = set()
    seen_questions: set[str] = set()
    for index, raw in enumerate(document["cases"], start=1):
        label = f"{source}#case-{index}"
        if not isinstance(raw, dict):
            add(label, "case must be a mapping")
            continue
        case_id = raw.get("id")
        if not isinstance(case_id, str) or not case_id.strip():
            add(label, "missing id")
            case_id = label
        else:
            case_id = case_id.strip()
            label = case_id
            if case_id in seen_ids:
                add(case_id, "duplicate id")
            seen_ids.add(case_id)

        kind = raw.get("kind")
        if kind not in KINDS:
            add(label, f"kind must be one of {', '.join(sorted(KINDS))}")

        question = raw.get("question")
        if not isinstance(question, str) or not question.strip():
            add(label, "missing question")
            question = ""
        else:
            question = re.sub(r"\s+", " ", question).strip()
            if question in seen_questions:
                add(label, "duplicate question")
            seen_questions.add(question)

        expect = raw.get("expect")
        if not isinstance(expect, list) or not all(isinstance(item, str) for item in expect):
            add(label, "expect must be a list of paths")
            expect = []

        note = raw.get("note", "")
        if note is None:
            note = ""
        if not isinstance(note, str):
            add(label, "note must be a string")
            note = ""

        result.case_count += 1
        if kind == "paraphrase":
            result.paraphrase_count += 1
        if kind == "intentional-miss":
            result.intentional_miss_count += 1
            if expect:
                add(label, "intentional-miss must have an empty expect list")
            if not note.strip():
                add(label, "intentional-miss requires a note explaining the miss")
            continue

        if kind in KINDS and not expect:
            add(label, "expect must list at least one repo path")

        for rel in expect:
            path, error = resolve_repo_path(root, rel)
            if error is not None or path is None:
                add(label, error or f"expected path not found: {rel}")
                continue
            if not path.is_file():
                add(rel, f"expected path not found: {rel}")
                continue
            result.paths_checked += 1
            if kind == "paraphrase":
                try:
                    title = first_heading(path.read_text(encoding="utf-8"))
                except UnicodeDecodeError:
                    add(rel, "expected page is not valid UTF-8")
                    continue
                if title and contained(title, question):
                    add(label, f"paraphrase question contains page title {title!r} from {rel}")

    if result.case_count < min_cases:
        add(source, f"need at least {min_cases} cases, found {result.case_count}")
    if result.paraphrase_count < min_paraphrase:
        add(
            source,
            f"need at least {min_paraphrase} paraphrase cases, found {result.paraphrase_count}",
        )
    return result


def check_file(
    cases_path: Path,
    root: Path,
    *,
    min_cases: int = 10,
    min_paraphrase: int = 3,
) -> CheckResult:
    source = cases_path.as_posix()
    result = CheckResult()
    if not cases_path.is_file():
        result.findings.append(Finding(source, "cases file not found"))
        return result
    read_errors: tuple[type[BaseException], ...] = (
        OSError,
        UnicodeDecodeError,
        ValueError,
        json.JSONDecodeError,
    )
    if yaml is not None:
        read_errors = read_errors + (yaml.YAMLError,)
    try:
        text = cases_path.read_text(encoding="utf-8")
        document = load_cases_document(text, cases_path.suffix.lower())
    except read_errors as exc:
        result.findings.append(Finding(source, f"could not read cases: {exc}"))
        return result
    return check_document(
        document,
        root,
        source=source,
        min_cases=min_cases,
        min_paraphrase=min_paraphrase,
    )


def format_report(result: CheckResult) -> str:
    lines = [f"ERROR {item.path}: {item.message}" for item in result.findings]
    direct = result.case_count - result.paraphrase_count - result.intentional_miss_count
    lines.append(
        "summary: "
        f"cases={result.case_count} "
        f"direct={direct} "
        f"paraphrase={result.paraphrase_count} "
        f"intentional_miss={result.intentional_miss_count} "
        f"paths_checked={result.paths_checked} "
        f"errors={len(result.findings)}"
    )
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Check wiki/evals retrieval cases: format, paraphrase count, "
            "and that expected paths exist. No embeddings."
        )
    )
    parser.add_argument("--root", type=Path, default=None, help="Repository root")
    parser.add_argument(
        "--cases",
        type=Path,
        default=DEFAULT_CASES,
        help="Gold-set markdown (yaml fence) or json, relative to --root unless absolute",
    )
    parser.add_argument("--min-cases", type=int, default=10)
    parser.add_argument("--min-paraphrase", type=int, default=3)
    try:
        args = parser.parse_args(sys.argv[1:] if argv is None else argv)
    except SystemExit as exc:
        code = exc.code
        return code if isinstance(code, int) else 2

    root = (args.root if args.root is not None else repo_root_from_script()).resolve()
    cases_path = args.cases if args.cases.is_absolute() else root / args.cases
    if yaml is None and cases_path.suffix.lower() != ".json":
        print("error: PyYAML is required (pip install pyyaml)", file=sys.stderr)
        return 2
    try:
        result = check_file(
            cases_path,
            root,
            min_cases=args.min_cases,
            min_paraphrase=args.min_paraphrase,
        )
    except RuntimeError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    # Distinguish "file missing / unreadable" as exit 2 when no cases were parsed.
    if result.case_count == 0 and any(
        "not found" in item.message or "could not read" in item.message for item in result.findings
    ):
        for item in result.findings:
            print(f"error: {item.path}: {item.message}", file=sys.stderr)
        return 2

    sys.stdout.write(format_report(result))
    return 0 if result.ok else 1


if __name__ == "__main__":
    sys.exit(main())
