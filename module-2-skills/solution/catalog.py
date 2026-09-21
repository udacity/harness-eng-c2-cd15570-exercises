"""Discover skill metadata without loading the skill instructions."""

from pathlib import Path


def discover_skills(root: Path) -> dict[str, dict[str, str | Path]]:
    """Read only SKILL.md frontmatter; return a name-to-description/path catalog."""
    catalog: dict[str, dict[str, str | Path]] = {}
    for path in sorted(root.glob("*/SKILL.md")):
        with path.open(encoding="utf-8") as skill_file:
            if skill_file.readline().strip() != "---":
                raise ValueError(f"Missing YAML frontmatter in {path}")
            metadata: dict[str, str] = {}
            for line in skill_file:
                if line.strip() == "---":
                    break
                key, separator, value = line.partition(":")
                if separator:
                    metadata[key.strip()] = value.strip().strip('"\'')
            else:
                raise ValueError(f"Unclosed YAML frontmatter in {path}")

        name = metadata.get("name", "")
        description = metadata.get("description", "")
        if not name or not description or name != path.parent.name:
            raise ValueError(f"Skill name/description must match its folder: {path}")
        if name in catalog:
            raise ValueError(f"Duplicate skill name: {name}")
        catalog[name] = {"description": description, "path": path}

    if not catalog:
        raise ValueError(f"No skills found under {root}")
    return catalog


def catalog_prompt(catalog: dict[str, dict[str, str | Path]]) -> str:
    """Expose routing metadata, never the detailed skill bodies."""
    return "\n".join(
        f"- {name}: {entry['description']}" for name, entry in catalog.items()
    )


def load_skill(name: str, catalog: dict[str, dict[str, str | Path]]) -> tuple[str, Path]:
    """Load one allowlisted skill and return its full text plus provenance."""
    if name not in catalog:
        raise ValueError(f"Unknown skill {name!r}; choose from {', '.join(catalog)}")
    path = catalog[name]["path"]
    assert isinstance(path, Path)
    return path.read_text(encoding="utf-8"), path
