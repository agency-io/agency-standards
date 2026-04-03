"""Shared task-injection logic for all propose/apply/archive phase commands."""
import sys
from pathlib import Path

from rich.console import Console

from ..inspector import inspect
from ..models import Standard, TaskPhase
from ..standards.loader import evaluate_condition, load_all

console = Console()


def run_task_injection(phase_name: str, phase_attr: str, change_id: str, target: Path) -> None:
    """Inject tasks for `phase_name` into a change's tasks.md."""
    change_dir = target / "openspec" / "changes" / change_id
    if not change_dir.exists():
        console.print(f"[red]Change directory not found: {change_dir}[/red]")
        sys.exit(1)

    tasks_path = change_dir / "tasks.md"
    if not tasks_path.exists():
        console.print(f"[red]tasks.md not found in {change_dir}[/red]")
        sys.exit(1)

    ctx = inspect(target)

    def has_phase(s: Standard) -> bool:
        return getattr(s, phase_attr, None) is not None

    applicable = [s for s in load_all(target) if evaluate_condition(s, ctx) and has_phase(s)]

    if not applicable:
        console.print(
            f"[yellow]No applicable standards with {phase_attr} blocks found.[/yellow]"
        )
        return

    console.print(
        f"[dim]{len(applicable)} standards will contribute {phase_name} tasks: "
        + ", ".join(s.id for s in applicable)
        + "[/dim]"
    )

    content = tasks_path.read_text()
    for standard in applicable:
        phase: TaskPhase = getattr(standard, phase_attr)
        content = _inject(content, phase, standard.id)

    tasks_path.write_text(content)
    console.print(f"Updated [cyan]{tasks_path.relative_to(target)}[/cyan]")
    console.print(
        f"Standards that contributed {phase_name} tasks: "
        + ", ".join(f"[cyan]{s.id}[/cyan]" for s in applicable)
    )


def _inject(content: str, phase: TaskPhase, standard_id: str) -> str:
    """Insert phase tasks into content at the declared position, skipping duplicates."""
    new_lines = [f"- [ ] [{standard_id}] {t}" for t in phase.tasks]
    new_lines = [line for line in new_lines if line not in content]
    if not new_lines:
        return content

    block = "\n".join(new_lines)
    insert = phase.insert.strip()

    if insert == "prepend":
        return block + "\n" + content
    if insert == "append":
        return content.rstrip("\n") + "\n" + block + "\n"
    if insert.startswith("before:"):
        return _insert_before_section(content, block, insert[len("before:"):])
    if insert.startswith("after:"):
        return _insert_after_section(content, block, insert[len("after:"):])
    return content.rstrip("\n") + "\n" + block + "\n"


def _insert_before_section(content: str, block: str, section: str) -> str:
    lines = content.splitlines(keepends=True)
    for i, line in enumerate(lines):
        if line.strip() == f"## {section}":
            lines.insert(i, block + "\n")
            return "".join(lines)
    console.print(f"  [yellow]Section '{section}' not found; appending tasks[/yellow]")
    return content.rstrip("\n") + "\n" + block + "\n"


def _insert_after_section(content: str, block: str, section: str) -> str:
    lines = content.splitlines(keepends=True)
    for i, line in enumerate(lines):
        if line.strip() == f"## {section}":
            j = i + 1
            while j < len(lines) and not lines[j].startswith("## "):
                j += 1
            lines.insert(j, block + "\n")
            return "".join(lines)
    console.print(f"  [yellow]Section '{section}' not found; appending tasks[/yellow]")
    return content.rstrip("\n") + "\n" + block + "\n"
