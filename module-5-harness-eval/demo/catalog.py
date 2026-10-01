"""Safe name/description discovery and exact skill loading."""

from pathlib import Path


def discover_skills(root: Path) -> dict[str, dict[str, str | Path]]:
    catalog: dict[str, dict[str, str | Path]] = {}
    for path in sorted(root.glob("*/SKILL.md")):
        if path.is_symlink() or path.parent.is_symlink():
            continue
        with path.open(encoding="utf-8") as source:
            if source.readline().strip() != "---":
                raise ValueError(f"Missing frontmatter in {path}")
            metadata: dict[str, str] = {}
            for line in source:
                if line.strip() == "---":
                    break
                key, separator, value = line.partition(":")
                if separator:
                    metadata[key.strip()] = value.strip().strip("\"'")
            else:
                raise ValueError(f"Unclosed frontmatter in {path}")
        name = metadata.get("name", "")
        description = metadata.get("description", "")
        if not name or not description or name != path.parent.name:
            raise ValueError(f"Invalid skill metadata in {path}")
        catalog[name] = {"description": description, "path": path}
    if not catalog:
        raise ValueError("No skills discovered.")
    return catalog


def catalog_prompt(catalog: dict) -> str:
    return "\n".join(
        f"- {name}: {entry['description']}" for name, entry in catalog.items()
    )


def load_skill(name: str, catalog: dict) -> tuple[str, Path]:
    if name not in catalog:
        raise ValueError(f"Unknown skill {name!r}.")
    path = catalog[name]["path"]
    assert isinstance(path, Path)
    return path.read_text(encoding="utf-8"), path
