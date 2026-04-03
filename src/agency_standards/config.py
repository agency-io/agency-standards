from pathlib import Path

import yaml

CONFIG_FILENAME = ".agency-standards.yaml"


def load_config(project_root: Path) -> list[str]:
    """Return list of enabled standard IDs from .agency-standards.yaml, or empty list."""
    config_file = project_root / CONFIG_FILENAME
    if not config_file.exists():
        return []
    data = yaml.safe_load(config_file.read_text()) or {}
    return data.get("standards", {}).get("enabled", [])


def save_config(project_root: Path, enabled_ids: list[str]) -> None:
    """Write enabled standard IDs to .agency-standards.yaml."""
    config_file = project_root / CONFIG_FILENAME
    data = {"standards": {"enabled": sorted(enabled_ids)}}
    config_file.write_text(yaml.dump(data, default_flow_style=False, sort_keys=True))
