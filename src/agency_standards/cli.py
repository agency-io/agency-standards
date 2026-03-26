from pathlib import Path
from typing import Optional

import typer
from rich.console import Console

from . import __version__

app = typer.Typer(
    name="agency-standards",
    help="AI-powered architecture governance for Python projects.",
    no_args_is_help=True,
)
standards_app = typer.Typer(help="Manage the standards library.")
app.add_typer(standards_app, name="standards")

console = Console()


@app.command()
def init(
    target: Path = typer.Argument(
        default=Path("."),
        help="Project directory to initialise. Defaults to current directory.",
    ),
) -> None:
    """Wizard: inspect a project and generate architecture tests + CLAUDE.md."""
    from .commands.init_cmd import run
    run(target.resolve())


@app.command()
def update(
    target: Path = typer.Argument(
        default=Path("."),
        help="Project directory to update.",
    ),
    standard: Optional[str] = typer.Option(
        None, "--standard", "-s", help="Update a single standard by ID."
    ),
) -> None:
    """Re-generate managed architecture test files, preserving custom sections."""
    from .commands.update_cmd import run
    run(target.resolve(), standard_id=standard)


@app.command()
def status(
    target: Path = typer.Argument(
        default=Path("."),
        help="Project directory to inspect.",
    ),
) -> None:
    """Show which generated files are current and which are behind."""
    from .commands.status_cmd import run
    run(target.resolve())


@app.command()
def add(
    standard_id: Optional[str] = typer.Argument(
        default=None,
        help="ID of a standard to add (from `agency-standards standards list`).",
    ),
    target: Path = typer.Option(
        Path("."),
        "--target", "-t",
        help="Project directory.",
    ),
    describe: Optional[str] = typer.Option(
        None, "--describe", "-d",
        help="Describe a custom standard in plain English to generate and add it.",
    ),
) -> None:
    """Add a single standard to the project."""
    from .commands.init_cmd import (
        _generate_and_write_test,
        _generate_custom_standard,
        _resolve_arch_dir,
        _update_claude_md,
    )
    from .inspector import inspect
    from .standards.loader import load_by_id

    resolved = target.resolve()
    ctx = inspect(resolved)

    if describe:
        standard = _generate_custom_standard(describe, ctx)
    elif standard_id:
        standard = load_by_id(standard_id)
        if not standard:
            console.print(f"[red]Standard '{standard_id}' not found.[/red]")
            raise typer.Exit(1)
    else:
        console.print("[red]Provide a standard ID or --describe.[/red]")
        raise typer.Exit(1)

    if standard:
        arch_dir = _resolve_arch_dir(resolved, ctx)
        arch_dir.mkdir(parents=True, exist_ok=True)
        _generate_and_write_test(standard, ctx, arch_dir)
        _update_claude_md(resolved, [standard], ctx)


@standards_app.command("list")
def standards_list() -> None:
    """List all available standards (built-in and local)."""
    from .commands.standards_cmd import list_standards
    list_standards()


@app.callback(invoke_without_command=True)
def version_callback(
    version: bool = typer.Option(False, "--version", "-v", help="Show version and exit."),
) -> None:
    if version:
        console.print(f"agency-standards v{__version__}")
        raise typer.Exit()
