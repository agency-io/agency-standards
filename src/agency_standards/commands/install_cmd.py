import shutil
from pathlib import Path

from rich.console import Console

SKILLS_SOURCE = Path(__file__).parent.parent / "skills"
SKILLS_DEST_SUBDIR = ".claude/commands/agency-standards"

console = Console()


def install_skills(project_dir: Path) -> None:
    dest_dir = project_dir / SKILLS_DEST_SUBDIR
    dest_dir.mkdir(parents=True, exist_ok=True)

    for skill_file in sorted(SKILLS_SOURCE.glob("*.md")):
        dest = dest_dir / skill_file.name
        shutil.copy2(skill_file, dest)
        console.print(
            f"  Installed [cyan]{SKILLS_DEST_SUBDIR}/{skill_file.name}[/cyan]"
        )
