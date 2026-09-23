"""Discover skill metadata and load only allowlisted skill instructions."""

from __future__ import annotations

import re
from pathlib import Path
from typing import TypedDict


MAX_SKILL_BYTES = 64 * 1024
MAX_FRONTMATTER_LINES = 32
MAX_FRONTMATTER_LINE_CHARS = 1_000
SKILL_NAME_PATTERN = re.compile(r"^[a-z][a-z0-9_-]{0,63}$")


class SkillEntry(TypedDict):
    """Metadata retained after discovery; the instruction body stays unloaded."""

    description: str
    path: Path


SkillCatalog = dict[str, SkillEntry]


def _plain_scalar(value: str, *, path: Path, key: str) -> str:
    """Parse the small one-line YAML scalar subset used by these skills."""
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
        value = value[1:-1]
    if not value:
        raise ValueError(f"Empty {key!r} in {path}")
    return value


def _read_frontmatter(path: Path) -> dict[str, str]:
    """Read frontmatter only, without placing the instruction body in memory."""
    try:
        size = path.stat().st_size
    except OSError as error:
        raise ValueError(f"Cannot inspect skill file {path}: {error}") from error
    if size > MAX_SKILL_BYTES:
        raise ValueError(f"Skill file exceeds {MAX_SKILL_BYTES} bytes: {path}")

    metadata: dict[str, str] = {}
    try:
        with path.open(encoding="utf-8") as skill_file:
            if skill_file.readline().strip() != "---":
                raise ValueError(f"Missing YAML frontmatter in {path}")
            for _ in range(MAX_FRONTMATTER_LINES):
                line = skill_file.readline()
                if not line:
                    break
                if len(line) > MAX_FRONTMATTER_LINE_CHARS:
                    raise ValueError(f"Frontmatter line is too long in {path}")
                if line.strip() == "---":
                    return metadata
                if not line.strip() or line.lstrip().startswith("#"):
                    continue
                key, separator, value = line.partition(":")
                key = key.strip()
                if not separator or not key or key in metadata:
                    raise ValueError(f"Invalid frontmatter line in {path}: {line.rstrip()!r}")
                metadata[key] = _plain_scalar(value, path=path, key=key)
    except UnicodeDecodeError as error:
        raise ValueError(f"Skill file is not valid UTF-8: {path}") from error

    raise ValueError(
        f"Unclosed frontmatter within {MAX_FRONTMATTER_LINES} lines in {path}"
    )


def discover_skills(root: Path) -> SkillCatalog:
    """Return trusted routing metadata for direct child skill directories.

    Discovery reads only frontmatter. Symlinks and nested or escaping paths are
    rejected so a model-selected skill name can never become an arbitrary path.
    """
    try:
        resolved_root = Path(root).resolve(strict=True)
    except OSError as error:
        raise ValueError(f"Skill root does not exist: {root}") from error
    if not resolved_root.is_dir():
        raise ValueError(f"Skill root is not a directory: {resolved_root}")

    catalog: SkillCatalog = {}
    for candidate in sorted(resolved_root.glob("*/SKILL.md")):
        if candidate.is_symlink() or candidate.parent.is_symlink():
            raise ValueError(f"Skill paths may not be symlinks: {candidate}")
        try:
            path = candidate.resolve(strict=True)
        except OSError as error:
            raise ValueError(f"Cannot resolve skill path {candidate}: {error}") from error
        if path.parent.parent != resolved_root:
            raise ValueError(f"Skill path escapes its root: {candidate}")

        metadata = _read_frontmatter(path)
        name = metadata.get("name", "")
        description = metadata.get("description", "")
        if not SKILL_NAME_PATTERN.fullmatch(name):
            raise ValueError(f"Invalid skill name {name!r} in {path}")
        if name != path.parent.name:
            raise ValueError(f"Skill name must match its folder: {path}")
        if not description or len(description) > 500:
            raise ValueError(f"Skill description must contain 1-500 characters: {path}")
        if name in catalog:
            raise ValueError(f"Duplicate skill name: {name}")
        catalog[name] = {"description": description, "path": path}

    if not catalog:
        raise ValueError(f"No skills found under {resolved_root}")
    return catalog


def catalog_prompt(catalog: SkillCatalog) -> str:
    """Format routing metadata without exposing any skill instruction body."""
    if not catalog:
        raise ValueError("Skill catalog is empty")
    return "\n".join(
        f"- {name}: {catalog[name]['description']}" for name in sorted(catalog)
    )


def load_skill(name: str, catalog: SkillCatalog) -> tuple[str, Path]:
    """Load one discovered skill by exact allowlisted name."""
    if name not in catalog:
        choices = ", ".join(sorted(catalog))
        raise ValueError(f"Unknown skill {name!r}; choose from: {choices}")

    entry = catalog[name]
    path = entry["path"]
    if not isinstance(path, Path):
        raise ValueError(f"Catalog path for {name!r} is invalid")
    if path.is_symlink() or path.parent.is_symlink():
        raise ValueError(f"Skill paths may not be symlinks: {path}")
    try:
        resolved_path = path.resolve(strict=True)
    except OSError as error:
        raise ValueError(f"Cannot resolve skill path {path}: {error}") from error
    if resolved_path != path or path.name != "SKILL.md" or path.parent.name != name:
        raise ValueError(f"Catalog path for {name!r} is not a discovered skill file")

    metadata = _read_frontmatter(path)
    if metadata.get("name") != name or metadata.get("description") != entry["description"]:
        raise ValueError(f"Skill metadata changed after discovery: {path}")
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError as error:
        raise ValueError(f"Skill file is not valid UTF-8: {path}") from error
    return text, path
