from pathlib import Path

import typer
from rich.console import Console

app = typer.Typer(
    name="agency-standards",
    help="OpenSpec lifecycle companion for architecture governance.",
    no_args_is_help=False,
)

console = Console()


@app.command("post-init")
def post_init(
    target: Path = typer.Argument(
        default=Path("."),
        help="Project directory. Defaults to current directory.",
    ),
) -> None:
    """Inspect project, write CLAUDE.md, install skills."""
    from .commands.post_init_cmd import run
    run(target.resolve())


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
def default_callback(
    ctx: typer.Context,
    change_id: str | None = typer.Argument(
        default=None,
        help="Change ID — shorthand for `agency-standards post-propose <change-id>`.",
    ),
    target: Path = typer.Option(
        Path("."),
        "--target", "-t",
        help="Project directory. Defaults to current directory.",
    ),
) -> None:
    """If a change-id is given with no subcommand, run post-propose."""
    if ctx.invoked_subcommand is not None:
        return
    if change_id is not None:
        from .commands.post_propose_cmd import run
        run(change_id, target.resolve())
    else:
        console.print(ctx.get_help())
