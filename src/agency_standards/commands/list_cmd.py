from pathlib import Path

from rich.console import Console
from rich.rule import Rule

from ..config import load_config
from ..standards.loader import load_all

console = Console()


def run(filter_tag: str | None, verbose: bool, project_path: Path) -> None:
    standards = load_all()
    enabled_ids = set(load_config(project_path))

    if filter_tag:
        standards = [s for s in standards if filter_tag.lower() in [t.lower() for t in s.tags]]
        if not standards:
            console.print(f"[yellow]No standards match filter: {filter_tag}[/yellow]")
            return

    for standard in sorted(standards, key=lambda s: s.id):
        enabled_marker = "[green]✓[/green] " if standard.id in enabled_ids else "  "
        tags_str = f"[dim][{', '.join(standard.tags)}][/dim]" if standard.tags else ""
        console.print(f"{enabled_marker}[bold]{standard.id}[/bold]  {standard.name}  {tags_str}")

        if verbose and standard.post_init and standard.post_init.claude_md_section:
            console.print(Rule(style="dim"))
            console.print(standard.post_init.claude_md_section.strip())
            console.print(Rule(style="dim"))
            console.print()

    count_label = f"{len(standards)} standard{'s' if len(standards) != 1 else ''}"
    if filter_tag:
        count_label += f" matching filter '{filter_tag}'"
    console.print(f"\n[dim]{count_label}[/dim]")
