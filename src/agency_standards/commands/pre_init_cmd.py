import shutil
from pathlib import Path

import questionary
from rich.console import Console

from ..config import load_config
from ..inspector import inspect
from ..standards.loader import BUILTIN_DIR, evaluate_condition, load_catalog, load_project

SKILLS_SOURCE = Path(__file__).parent.parent / "skills"
SKILLS_DEST_SUBDIR = ".claude/commands/agency-standards"
PROJECT_STANDARDS_SUBDIR = "standards"

console = Console()


def run(target: Path, yes: bool = False) -> None:
    ctx = inspect(target)
    console.print(f"[dim]Inspected project: {target}[/dim]")
    console.print(f"[dim]Languages: {', '.join(ctx.languages) or 'unknown'}[/dim]")

    catalog = [s for s in load_catalog() if evaluate_condition(s, ctx) and s.pre_init is not None]

    if not catalog:
        console.print("[yellow]No applicable standards with pre_init blocks found.[/yellow]")
        return

    selected = _select_standards(catalog, target, yes)

    if not selected:
        console.print("[yellow]No standards selected; CLAUDE.md not updated.[/yellow]")
        return

    _copy_standards(target, selected)
    _write_claude_md(target, selected)
    _install_skills(target)

    console.print(
        "\nRun [cyan]/agency-standards:generate[/cyan] in Claude Code to generate"
        " architecture tests"
    )


def _select_standards(catalog: list, target: Path, yes: bool) -> list:
    if yes:
        console.print(f"[dim]--yes flag: applying all {len(catalog)} applicable standards[/dim]")
        return catalog

    enabled_ids = set(load_config(target))
    adopted_ids = {s.id for s in load_project(target)}

    choices = [
        questionary.Choice(
            title=f"{s.id}  [{', '.join(s.tags)}]  — {s.description}",
            value=s,
            checked=(s.id in adopted_ids or s.id in enabled_ids)
            if (adopted_ids or enabled_ids) else True,
        )
        for s in catalog
    ]

    selected = questionary.checkbox(
        f"Select standards to enable ({len(catalog)} applicable):",
        choices=choices,
    ).ask()

    return selected if selected is not None else []


def _copy_standards(target: Path, selected: list) -> None:
    standards_dir = target / PROJECT_STANDARDS_SUBDIR
    standards_dir.mkdir(exist_ok=True)

    for standard in selected:
        dest = standards_dir / f"{standard.id}.yaml"
        src = BUILTIN_DIR / f"{standard.id}.yaml"
        if dest.exists():
            console.print(f"  [dim]{standard.id} already adopted — skipping copy[/dim]")
        elif src.exists():
            shutil.copy2(src, dest)
            console.print(f"  Adopted [cyan]standards/{standard.id}.yaml[/cyan]")


def _write_claude_md(target: Path, applicable: list) -> None:
    sections = []
    for standard in applicable:
        section = standard.pre_init.claude_md_section
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
