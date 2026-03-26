from pathlib import Path

from rich.console import Console
from rich.table import Table

from .. import __version__
from ..generator import get_standard_id, get_standard_version
from ..inspector import inspect

console = Console()


def run(target: Path) -> None:
    ctx = inspect(target)
    arch_dirs = [d / "architecture" for d in ctx.test_dirs if (d / "architecture").exists()]

    if not arch_dirs:
        console.print("[yellow]No tests/architecture/ directory found. Run init first.[/yellow]")
        return

    arch_dir = arch_dirs[0]
    generated_files = [f for f in arch_dir.glob("test_*.py") if _is_generated(f)]

    if not generated_files:
        console.print("[yellow]No generated architecture tests found.[/yellow]")
        return

    table = Table(title=f"Architecture Tests — {arch_dir.relative_to(target)}")
    table.add_column("File", style="cyan")
    table.add_column("Standard")
    table.add_column("Generated at")
    table.add_column("Status")

    for path in sorted(generated_files):
        content = path.read_text()
        sid = get_standard_id(content) or "unknown"
        ver = get_standard_version(content) or "unknown"
        status = "[green]current[/green]" if ver == __version__ else f"[yellow]behind (v{ver} → v{__version__})[/yellow]"
        table.add_row(path.name, sid, f"v{ver}", status)

    console.print(table)
