"""Minimal safe discovery and loading pattern for the course skill profile."""

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class SkillRecord:
    name: str
    description: str
    path: Path


def discover_skills(trusted_root: Path) -> dict[str, SkillRecord]:
    """Build a metadata catalog without exposing complete bodies to routing."""

    root = trusted_root.resolve(strict=True)
    catalog: dict[str, SkillRecord] = {}

    for path in sorted(root.glob("*/SKILL.md")):
        if path.is_symlink() or path.parent.is_symlink():
            continue
        resolved = path.resolve(strict=True)
        if root not in resolved.parents:
            raise ValueError(f"Skill escaped trusted root: {path}")

        name, description = _read_frontmatter(resolved)
        if name != path.parent.name:
            raise ValueError(f"Skill name must match directory: {path}")
        if name in catalog:
            raise ValueError(f"Duplicate skill name: {name}")
        catalog[name] = SkillRecord(name, description, resolved)

    if not catalog:
        raise ValueError(f"No valid skills under {trusted_root}")
    return catalog


def _read_frontmatter(path: Path) -> tuple[str, str]:
    """Parse the two fields supported by this teaching implementation."""

    with path.open(encoding="utf-8") as skill_file:
        if skill_file.readline().strip() != "---":
            raise ValueError(f"Missing frontmatter: {path}")
        metadata: dict[str, str] = {}
        for line in skill_file:
            if line.strip() == "---":
                break
            key, separator, value = line.partition(":")
            if separator:
                metadata[key.strip()] = value.strip().strip('"\'')
        else:
            raise ValueError(f"Unclosed frontmatter: {path}")

    name = metadata.get("name", "")
    description = metadata.get("description", "")
    if not name or not description:
        raise ValueError(f"name and description are required: {path}")
    return name, description


def catalog_prompt(catalog: dict[str, SkillRecord]) -> str:
    """Expose only compact routing metadata."""

    return "\n".join(
        f"- {record.name}: {record.description}"
        for record in catalog.values()
    )


def load_skill(name: str, catalog: dict[str, SkillRecord]) -> tuple[str, Path]:
    """Load one exact allowlisted skill; never interpret name as a path."""

    record = catalog.get(name)
    if record is None:
        raise ValueError(f"Unknown skill {name!r}")
    text = record.path.read_text(encoding="utf-8")
    if len(text) > 40_000:
        raise ValueError(f"Skill exceeds configured size limit: {name}")
    return text, record.path


if __name__ == "__main__":
    raise SystemExit("Import this example; do not run it as an application.")
