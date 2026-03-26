from rich.console import Console
from rich.table import Table

from ..standards.loader import load_all

console = Console()


def list_standards() -> None:
    standards = load_all()

    table = Table(title="Available Standards")
    table.add_column("ID", style="cyan")
    table.add_column("Name")
    table.add_column("Description")
    table.add_column("Languages")
    table.add_column("Source", style="dim")

    for s in standards:
        table.add_row(
            s.id,
            s.name,
            s.description,
            ", ".join(s.languages),
            s.source,
        )

    console.print(table)
