from pathlib import Path

import questionary
import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from .. import __version__
from ..generator import generate_claude_md_update, generate_test, wrap_with_header
from ..inspector import inspect
from ..models import ProjectContext, Standard
from ..standards.loader import load_all

console = Console()


def run(target: Path) -> None:
    console.print(Panel(f"[bold]agency-standards init[/bold] v{__version__}", expand=False))

    ctx = inspect(target)
    _print_project_summary(ctx)

    if not questionary.confirm("Proceed with this project?", default=True).ask():
        raise typer.Abort()

    available = [s for s in load_all() if "python" in s.languages]
    if not available:
        console.print("[red]No standards available.[/red]")
        raise typer.Exit(1)

    selected_ids = questionary.checkbox(
        "Select standards to apply:",
        choices=[
            questionary.Choice(title=f"{s.name} — {s.description}", value=s.id)
            for s in available
        ],
        default=[s.id for s in available],
    ).ask()

    if not selected_ids:
        console.print("[yellow]No standards selected. Nothing to do.[/yellow]")
        raise typer.Exit()

    custom_description = questionary.text(
        "Add a custom standard? (describe in plain English, or leave blank to skip):",
        default="",
    ).ask()

    selected = [s for s in available if s.id in selected_ids]

    if custom_description and custom_description.strip():
        custom = _generate_custom_standard(custom_description.strip(), ctx)
        if custom:
            selected.append(custom)

    arch_dir = _resolve_arch_dir(target, ctx)
    arch_dir.mkdir(parents=True, exist_ok=True)

    console.print(f"\nGenerating architecture tests in [cyan]{arch_dir.relative_to(target)}[/cyan]")

    for standard in selected:
        _generate_and_write_test(standard, ctx, arch_dir)

    _update_claude_md(target, selected, ctx)

    console.print(
        Panel(
            f"[green]Done.[/green] Applied {len(selected)} standards.\n"
            f"Run: [cyan]pytest {arch_dir.relative_to(target)}[/cyan]",
            expand=False,
        )
    )


def _print_project_summary(ctx: ProjectContext) -> None:
    table = Table(show_header=False, box=None, padding=(0, 1))
    table.add_row("[dim]Root[/dim]", str(ctx.root))
    table.add_row("[dim]Languages[/dim]", ", ".join(ctx.languages) or "unknown")
    table.add_row("[dim]Project type[/dim]", ctx.project_type)
    table.add_row(
        "[dim]Source dirs[/dim]",
        ", ".join(str(p.relative_to(ctx.root)) for p in ctx.src_dirs) or "none found",
    )
    table.add_row(
        "[dim]Test dirs[/dim]",
        ", ".join(str(p.relative_to(ctx.root)) for p in ctx.test_dirs) or "none found",
    )
    table.add_row("[dim]Unit tests[/dim]", str(len(ctx.unit_test_files)))
    table.add_row("[dim]Integration tests[/dim]", str(len(ctx.integration_test_files)))
    if ctx.existing_arch_tests:
        table.add_row(
            "[dim]Existing arch tests[/dim]",
            ", ".join(p.name for p in ctx.existing_arch_tests),
        )
    console.print(Panel(table, title="Project", expand=False))


def _generate_custom_standard(description: str, ctx: ProjectContext) -> Standard | None:
    from ..generator import generate_test as gen
    from ..standards.loader import save_custom

    console.print(f"\n[dim]Generating custom standard: {description[:60]}...[/dim]")

    # derive a slug id from the description
    import re
    standard_id = re.sub(r"[^a-z0-9]+", "-", description.lower())[:40].strip("-")
    output_file = f"test_{standard_id.replace('-', '_')}.py"

    custom = Standard(
        id=standard_id,
        name=description[:60],
        description=description,
        languages=["python"],
        output_file=output_file,
        prompt=(
            f"Generate a pytest architecture test that enforces the following rule:\n\n"
            f"{description}\n\n"
            "Use Python's ast module or file scanning as appropriate. "
            "Collect all violations before failing and report them clearly."
        ),
        claude_md_section=f"## Custom: {description[:60]}\n\n{description}",
        source="custom",
    )

    saved_path = save_custom(custom)
    console.print(f"[dim]Saved custom standard to {saved_path}[/dim]")
    return custom


def _generate_and_write_test(standard: Standard, ctx: ProjectContext, arch_dir: Path) -> None:
    dest = arch_dir / standard.output_file

    if dest.exists():
        overwrite = questionary.confirm(
            f"{standard.output_file} already exists. Regenerate?", default=False
        ).ask()
        if not overwrite:
            console.print(f"  [dim]Skipped {standard.output_file}[/dim]")
            return

    console.print(f"  Generating [cyan]{standard.output_file}[/cyan]...", end=" ")

    try:
        code = generate_test(standard, ctx)
        content = wrap_with_header(code, standard.id)
        dest.write_text(content)
        console.print("[green]done[/green]")
    except Exception as e:
        console.print(f"[red]failed: {e}[/red]")


def _update_claude_md(target: Path, standards: list[Standard], ctx: ProjectContext) -> None:
    claude_md_path = target / "CLAUDE.md"
    existing = claude_md_path.read_text() if claude_md_path.exists() else ""

    console.print("\nUpdating [cyan]CLAUDE.md[/cyan]...", end=" ")
    try:
        updated = generate_claude_md_update(standards, ctx, existing)
        claude_md_path.write_text(updated)
        console.print("[green]done[/green]")
    except Exception as e:
        console.print(f"[red]failed: {e}[/red]")


def _resolve_arch_dir(target: Path, ctx: ProjectContext) -> Path:
    if ctx.test_dirs:
        return ctx.test_dirs[0] / "architecture"
    return target / "tests" / "architecture"
