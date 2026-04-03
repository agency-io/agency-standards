from pathlib import Path

from rich.console import Console
from rich.rule import Rule

from ..models import Standard
from ..standards.loader import load_catalog, load_project

console = Console()

PHASE_ATTRS = [
    ("pre_init",    "pre-init"),
    ("post_init",   "post-init"),
    ("pre_propose", "pre-propose"),
    ("post_propose","post-propose"),
    ("pre_apply",   "pre-apply"),
    ("post_apply",  "post-apply"),
    ("pre_archive", "pre-archive"),
    ("post_archive","post-archive"),
]


def _phases(standard: Standard) -> str:
    active = [label for attr, label in PHASE_ATTRS if getattr(standard, attr) is not None]
    return ", ".join(active) if active else "—"


def run(filter_tag: str | None, verbose: bool, project_path: Path) -> None:
    catalog = load_catalog()
    project_standards = load_project(project_path)
    adopted_ids = {s.id for s in project_standards}
    catalog_ids = {s.id for s in catalog}

    custom = [s for s in project_standards if s.id not in catalog_ids]
    all_standards = catalog + custom

    if filter_tag:
        all_standards = [
            s for s in all_standards if filter_tag.lower() in [t.lower() for t in s.tags]
        ]
        if not all_standards:
            console.print(f"[yellow]No standards match filter: {filter_tag}[/yellow]")
            return

    for standard in sorted(all_standards, key=lambda s: s.id):
        if standard.id in adopted_ids and standard.id not in catalog_ids:
            marker = r"[cyan]\[custom][/cyan] "
        elif standard.id in adopted_ids:
            marker = "[green]✓[/green] "
        else:
            marker = "  "

        tags_str = f"[dim][{', '.join(standard.tags)}][/dim]" if standard.tags else ""
        phases_str = f"[dim]{_phases(standard)}[/dim]"
        console.print(f"{marker}[bold]{standard.id}[/bold]  {standard.name}  {tags_str}")
        console.print(f"     [dim]phases:[/dim] {phases_str}")

        if verbose and standard.post_init and standard.post_init.claude_md_section:
            console.print(Rule(style="dim"))
            console.print(standard.post_init.claude_md_section.strip())
            console.print(Rule(style="dim"))
            console.print()

    count_label = f"{len(all_standards)} standard{'s' if len(all_standards) != 1 else ''}"
    if filter_tag:
        count_label += f" matching filter '{filter_tag}'"
    console.print(f"\n[dim]{count_label}[/dim]")
