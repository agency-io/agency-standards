from pathlib import Path

import yaml

from ..models import Standard

BUILTIN_DIR = Path(__file__).parent.parent / "builtin_standards"
USER_DIR = Path.home() / ".agency-standards" / "standards"


def load_builtin() -> list[Standard]:
    return _load_from_dir(BUILTIN_DIR, source="builtin")


def load_user() -> list[Standard]:
    if not USER_DIR.exists():
        return []
    return _load_from_dir(USER_DIR, source="local")


def load_all() -> list[Standard]:
    return load_builtin() + load_user()


def load_by_id(standard_id: str) -> Standard | None:
    for standard in load_all():
        if standard.id == standard_id:
            return standard
    return None


def save_custom(standard: Standard) -> Path:
    USER_DIR.mkdir(parents=True, exist_ok=True)
    path = USER_DIR / f"{standard.id}.yaml"
    data = {
        "id": standard.id,
        "name": standard.name,
        "description": standard.description,
        "languages": standard.languages,
        "output_file": standard.output_file,
        "prompt": standard.prompt,
        "claude_md_section": standard.claude_md_section,
    }
    path.write_text(yaml.dump(data, default_flow_style=False, allow_unicode=True))
    return path


def _load_from_dir(directory: Path, source: str) -> list[Standard]:
    standards = []
    if not directory.exists():
        return standards
    for path in sorted(directory.glob("*.yaml")):
        try:
            data = yaml.safe_load(path.read_text())
            standards.append(
                Standard(
                    id=data["id"],
                    name=data["name"],
                    description=data["description"],
                    languages=data.get("languages", ["python"]),
                    output_file=data["output_file"],
                    prompt=data["prompt"],
                    claude_md_section=data.get("claude_md_section", ""),
                    source=source,
                )
            )
        except Exception as e:
            print(f"Warning: could not load standard from {path}: {e}")
    return standards
