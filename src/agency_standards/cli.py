from pathlib import Path

import typer
from rich.console import Console

app = typer.Typer(
    name="agency-standards",
    help="OpenSpec lifecycle companion for architecture governance.",
    no_args_is_help=False,
)

console = Console()


@app.command("list")
def list_standards(
    filter_tag: str | None = typer.Option(
        None, "--filter", "-f", help="Filter by tag (e.g. bdd, general, e2e)."
    ),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show full documentation."),
    target: Path = typer.Argument(
        default=Path("."),
        help="Project directory (used to show enabled status). Defaults to current directory.",
    ),
) -> None:
    """List available standards with their documentation."""
    from .commands.list_cmd import run
    run(filter_tag, verbose, target.resolve())


@app.command("pre-init")
def pre_init(
    yes: bool = typer.Option(False, "--yes", "-y", help="Skip interactive selection."),
    target: Path = typer.Argument(default=Path("."), help="Project directory."),
) -> None:
    """Run standard pre_init hooks before openspec init."""
    from .commands.pre_init_cmd import run
    run(target.resolve(), yes=yes)


@app.command("post-init")
def post_init(
    yes: bool = typer.Option(False, "--yes", "-y", help="Skip interactive selection."),
    target: Path = typer.Argument(default=Path("."), help="Project directory."),
) -> None:
    """Inspect project, select standards, write CLAUDE.md, install skills."""
    from .commands.post_init_cmd import run
    run(target.resolve(), yes=yes)


@app.command("pre-propose")
def pre_propose(
    change_id: str = typer.Argument(..., help="Change ID."),
    target: Path = typer.Argument(default=Path("."), help="Project directory."),
) -> None:
    """Inject pre-propose standard tasks into a change's tasks.md via Claude."""
    from .commands.pre_propose_cmd import run
    run(change_id, target.resolve())


@app.command("post-propose")
def post_propose(
    change_id: str = typer.Argument(..., help="Change ID."),
    target: Path = typer.Argument(default=Path("."), help="Project directory."),
) -> None:
    """Inject post-propose standard tasks into a change's tasks.md via Claude."""
    from .commands.post_propose_cmd import run
    run(change_id, target.resolve())


@app.command("pre-apply")
def pre_apply(
    change_id: str = typer.Argument(..., help="Change ID."),
    target: Path = typer.Argument(default=Path("."), help="Project directory."),
) -> None:
    """Inject pre-apply standard tasks into a change's tasks.md via Claude."""
    from .commands.pre_apply_cmd import run
    run(change_id, target.resolve())


@app.command("post-apply")
def post_apply(
    change_id: str = typer.Argument(..., help="Change ID."),
    target: Path = typer.Argument(default=Path("."), help="Project directory."),
) -> None:
    """Inject post-apply standard tasks into a change's tasks.md via Claude."""
    from .commands.post_apply_cmd import run
    run(change_id, target.resolve())


@app.command("pre-archive")
def pre_archive(
    change_id: str = typer.Argument(..., help="Change ID."),
    target: Path = typer.Argument(default=Path("."), help="Project directory."),
) -> None:
    """Inject pre-archive standard tasks into a change's tasks.md via Claude."""
    from .commands.pre_archive_cmd import run
    run(change_id, target.resolve())


@app.command("post-archive")
def post_archive(
    change_id: str = typer.Argument(..., help="Change ID."),
    target: Path = typer.Argument(default=Path("."), help="Project directory."),
) -> None:
    """Inject post-archive standard tasks into a change's tasks.md via Claude."""
    from .commands.post_archive_cmd import run
    run(change_id, target.resolve())


@app.callback(invoke_without_command=True)
def default_callback(ctx: typer.Context) -> None:
    """OpenSpec lifecycle companion for architecture governance."""
    if ctx.invoked_subcommand is None:
        console.print(ctx.get_help())
