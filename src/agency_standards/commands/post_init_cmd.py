import shutil
from pathlib import Path

from rich.console import Console

from ..inspector import inspect
from ..standards.loader import evaluate_condition, load_all

SKILLS_SOURCE = Path(__file__).parent.parent / "skills"
SKILLS_DEST_SUBDIR = ".claude/commands/agency-standards"

console = Console()


def run(target: Path) -> None:
    ctx = inspect(target)
    console.print(f"[dim]Inspected project: {target}[/dim]")
    console.print(f"[dim]Languages: {', '.join(ctx.languages) or 'unknown'}[/dim]")

    applicable = [
        s for s in load_all()
        if evaluate_condition(s, ctx) and s.post_init is not None
    ]

    if not applicable:
        console.print("[yellow]No applicable standards found for this project.[/yellow]")
    else:
        console.print(f"[dim]{len(applicable)} standards applicable[/dim]")

    _write_claude_md(target, applicable)
    _install_skills(target)

    console.print(
        "\nRun [cyan]/agency-standards:generate[/cyan] in Claude Code to generate"
        " architecture tests"
    )


def _write_claude_md(target: Path, applicable: list) -> None:
    sections = []
    for standard in applicable:
        section = standard.post_init.claude_md_section
        if section and section.strip():
            sections.append(section.strip())

    claude_md = target / "CLAUDE.md"
    if sections:
        content = "\n\n".join(sections) + "\n"
        claude_md.write_text(content)
        console.print(f"Wrote [cyan]CLAUDE.md[/cyan] ({len(sections)} sections)")
    else:
        console.print("[yellow]No claude_md_section content found; CLAUDE.md not written.[/yellow]")


def _install_skills(target: Path) -> None:
    dest_dir = target / SKILLS_DEST_SUBDIR
    dest_dir.mkdir(parents=True, exist_ok=True)

    if not SKILLS_SOURCE.exists():
        console.print("[yellow]No skills directory found; skipping skill installation.[/yellow]")
        return

    for skill_file in sorted(SKILLS_SOURCE.glob("*.md")):
        dest = dest_dir / skill_file.name
        shutil.copy2(skill_file, dest)
        console.print(f"  Installed [cyan]{SKILLS_DEST_SUBDIR}/{skill_file.name}[/cyan]")
