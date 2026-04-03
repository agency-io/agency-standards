import shutil
from pathlib import Path

import questionary
from rich.console import Console

from ..config import load_config, save_config
from ..inspector import inspect
from ..standards.loader import evaluate_condition, load_all

SKILLS_SOURCE = Path(__file__).parent.parent / "skills"
SKILLS_DEST_SUBDIR = ".claude/commands/agency-standards"

console = Console()


def run(target: Path, yes: bool = False) -> None:
    ctx = inspect(target)
    console.print(f"[dim]Inspected project: {target}[/dim]")
    console.print(f"[dim]Languages: {', '.join(ctx.languages) or 'unknown'}[/dim]")

    applicable = [
        s for s in load_all()
        if evaluate_condition(s, ctx) and s.post_init is not None
    ]

    if not applicable:
        console.print("[yellow]No applicable standards found for this project.[/yellow]")
        return

    selected = _select_standards(applicable, target, yes)

    if not selected:
        console.print("[yellow]No standards selected; CLAUDE.md not updated.[/yellow]")
        save_config(target, [])
        return

    _write_claude_md(target, selected)
    _install_skills(target)
    save_config(target, [s.id for s in selected])
    console.print(f"Saved [cyan].agency-standards.yaml[/cyan] ({len(selected)} standards enabled)")

    console.print(
        "\nRun [cyan]/agency-standards:generate[/cyan] in Claude Code to generate"
        " architecture tests"
    )


def _select_standards(applicable: list, target: Path, yes: bool) -> list:
    if yes:
        console.print(f"[dim]--yes flag: applying all {len(applicable)} applicable standards[/dim]")
        return applicable

    enabled_ids = set(load_config(target))

    choices = [
        questionary.Choice(
            title=f"{s.id}  [{', '.join(s.tags)}]  — {s.description}",
            value=s,
            checked=(s.id in enabled_ids) if enabled_ids else True,
        )
        for s in applicable
    ]

    selected = questionary.checkbox(
        f"Select standards to enable ({len(applicable)} applicable):",
        choices=choices,
    ).ask()

    return selected if selected is not None else []


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
