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


@app.command("post-init")
def post_init(
    yes: bool = typer.Option(False, "--yes", "-y", help="Skip interactive selection."),
    target: Path = typer.Argument(
        default=Path("."),
        help="Project directory. Defaults to current directory.",
    ),
) -> None:
    """Inspect project, select standards, write CLAUDE.md, install skills."""
    from .commands.post_init_cmd import run
    run(target.resolve(), yes=yes)


@app.command("post-propose")
def post_propose(
    change_id: str = typer.Argument(
        ..., help="Change ID (directory name under openspec/changes/)."
    ),
    target: Path = typer.Argument(
        default=Path("."),
        help="Project directory. Defaults to current directory.",
    ),
) -> None:
    """Inject standard tasks into a change's tasks.md via Claude."""
    from .commands.post_propose_cmd import run
    run(change_id, target.resolve())


@app.command("post-apply")
def post_apply(
    change_id: str = typer.Argument(..., help="Change ID."),
    target: Path = typer.Argument(
        default=Path("."),
        help="Project directory. Defaults to current directory.",
    ),
) -> None:
    """(Not yet implemented) Run after a change is applied."""
    from .commands.post_apply_cmd import run
    run(change_id, target.resolve())


@app.command("post-archive")
def post_archive(
    change_id: str = typer.Argument(..., help="Change ID."),
    target: Path = typer.Argument(
        default=Path("."),
        help="Project directory. Defaults to current directory.",
    ),
) -> None:
    """(Not yet implemented) Run after a change is archived."""
    from .commands.post_archive_cmd import run
    run(change_id, target.resolve())


@app.callback(invoke_without_command=True)
def default_callback(ctx: typer.Context) -> None:
    """OpenSpec lifecycle companion for architecture governance."""
    if ctx.invoked_subcommand is None:
        console.print(ctx.get_help())
