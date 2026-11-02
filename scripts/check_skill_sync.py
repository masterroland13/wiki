#!/usr/bin/env python3
"""Compare host skill mirrors to the canonical `.agents/skills/` tree.

Canonical skill text lives only in `.agents/skills/`. The host copies
`.cursor/skills/`, `.claude/skills/`, and `.codex/skills/` must match it
file-by-file. Edit the canonical tree, then copy that same content into
the mirrors. Do not treat a host copy as a second source of truth.

Comparison is SHA-256 of file bytes (not a text diff). Empty directories
are ignored. `__pycache__/`, `.DS_Store`, and `*.pyc` are ignored.
Directory symlinks are not followed.

Exit codes:
  0  every mirrored file matches the canonical tree
  1  drift: hash differs, a canonical file is missing, or a mirror has an extra file
  2  usage error, or the canonical skill directory is missing

Drift is an error. There is no warn-only mode that still exits 0.
"""

from __future__ import annotations

import argparse
import hashlib
import os
import sys
from dataclasses import dataclass, field
from pathlib import Path

DEFAULT_CANONICAL = Path(".agents/skills")
DEFAULT_MIRRORS = (
    Path(".cursor/skills"),
    Path(".claude/skills"),
    Path(".codex/skills"),
)
IGNORE_DIR_NAMES = {"__pycache__"}
IGNORE_FILE_NAMES = {".DS_Store"}


@dataclass(frozen=True)
class Finding:
    path: str
    kind: str
    message: str


@dataclass
class CheckResult:
    canonical_display: str
    hosts: list[str]
    canonical_files: int = 0
    findings: list[Finding] = field(default_factory=list)
    fatal: str | None = None

    @property
    def mirror_count(self) -> int:
        return len(self.hosts)

    @property
    def ok(self) -> bool:
        return self.fatal is None and not self.findings


def repo_root_from_script() -> Path:
    return Path(__file__).resolve().parent.parent


def display_path(root: Path, path: Path) -> str:
    absolute = path if path.is_absolute() else root / path
    try:
        return absolute.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return absolute.as_posix()


def list_files(root: Path) -> dict[str, Path]:
    """Map a skill-tree-relative POSIX path to the file on disk."""
    found: dict[str, Path] = {}
    if not root.is_dir():
        return found
    for dirpath, dirnames, filenames in os.walk(root, followlinks=False):
        dirnames[:] = [name for name in dirnames if name not in IGNORE_DIR_NAMES]
        base = Path(dirpath)
        for name in filenames:
            if name in IGNORE_FILE_NAMES or name.endswith(".pyc"):
                continue
            path = base / name
            if path.is_symlink() and not path.exists():
                found[path.relative_to(root).as_posix()] = path
                continue
            if not path.is_file():
                continue
            found[path.relative_to(root).as_posix()] = path
    return found


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def check_sync(canonical: Path, mirrors: list[Path], *, root: Path) -> CheckResult:
    canon_label = display_path(root, canonical)
    hosts = [display_path(root, mirror) for mirror in mirrors]
    if not canonical.is_dir():
        return CheckResult(
            canonical_display=canon_label,
            hosts=hosts,
            fatal=f"canonical skill directory not found: {canon_label}",
        )

    canon_files = list_files(canonical)
    result = CheckResult(
        canonical_display=canon_label,
        hosts=hosts,
        canonical_files=len(canon_files),
    )
    canon_hashes: dict[str, str] = {}

    def canonical_hash(rel: str) -> str:
        if rel not in canon_hashes:
            canon_hashes[rel] = sha256_file(canon_files[rel])
        return canon_hashes[rel]

    for mirror, mirror_label in zip(mirrors, hosts, strict=True):
        if not mirror.is_dir():
            if not canon_files:
                result.findings.append(
                    Finding(mirror_label, "missing", "mirror directory missing")
                )
            else:
                for rel in sorted(canon_files):
                    result.findings.append(
                        Finding(
                            f"{mirror_label}/{rel}",
                            "missing",
                            "mirror directory missing",
                        )
                    )
            continue

        mirror_files = list_files(mirror)
        for rel in sorted(set(canon_files) | set(mirror_files)):
            mirrored = f"{mirror_label}/{rel}"
            in_canon = rel in canon_files
            in_mirror = rel in mirror_files
            if in_canon and not in_mirror:
                result.findings.append(Finding(mirrored, "missing", "not in mirror"))
                continue
            if in_mirror and not in_canon:
                result.findings.append(
                    Finding(mirrored, "extra", f"not in canonical {canon_label}")
                )
                continue
            try:
                left = canonical_hash(rel)
                right = sha256_file(mirror_files[rel])
            except OSError as exc:
                result.findings.append(Finding(mirrored, "unreadable", str(exc)))
                continue
            if left != right:
                result.findings.append(
                    Finding(
                        mirrored,
                        "differs",
                        f"sha256 differs from {canon_label}/{rel}",
                    )
                )
    return result


def format_report(result: CheckResult) -> str:
    labels = {
        "differs": "DIFFERS",
        "missing": "MISSING",
        "extra": "EXTRA",
        "unreadable": "ERROR",
    }
    lines = [
        f"{labels.get(item.kind, item.kind.upper())} {item.path}: {item.message}"
        for item in result.findings
    ]
    hosts = ",".join(result.hosts)
    lines.append(
        "summary: "
        f"canonical={result.canonical_display} "
        f"mirrors={result.mirror_count} "
        f"hosts={hosts} "
        f"files={result.canonical_files} "
        f"drifts={len(result.findings)}"
    )
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Hash-compare .agents/skills against host mirrors "
            "(.cursor/skills, .claude/skills, .codex/skills)."
        )
    )
    parser.add_argument("--root", type=Path, default=None, help="Repository root")
    parser.add_argument(
        "--canonical",
        type=Path,
        default=DEFAULT_CANONICAL,
        help="Canonical skill root, relative to --root unless absolute",
    )
    parser.add_argument(
        "--mirror",
        action="append",
        default=None,
        dest="mirrors",
        type=Path,
        help=(
            "Mirror skill root, relative to --root unless absolute. "
            "Repeat to check more than one. Defaults to the three host copies."
        ),
    )
    try:
        args = parser.parse_args(sys.argv[1:] if argv is None else argv)
    except SystemExit as exc:
        code = exc.code
        return code if isinstance(code, int) else 2

    root = (args.root if args.root is not None else repo_root_from_script()).resolve()
    canonical = args.canonical if args.canonical.is_absolute() else root / args.canonical
    mirror_args = list(DEFAULT_MIRRORS if args.mirrors is None else args.mirrors)
    mirrors = [path if path.is_absolute() else root / path for path in mirror_args]
    result = check_sync(canonical, mirrors, root=root)
    if result.fatal:
        print(f"error: {result.fatal}", file=sys.stderr)
        return 2
    sys.stdout.write(format_report(result))
    return 0 if result.ok else 1


if __name__ == "__main__":
    sys.exit(main())
