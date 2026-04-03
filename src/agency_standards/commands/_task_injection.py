"""Shared task-injection logic for all propose/apply/archive phase commands."""
import sys
from pathlib import Path

import anthropic
from rich.console import Console

from ..inspector import inspect
from ..models import Standard, TaskPhase
from ..standards.loader import evaluate_condition, load_all

console = Console()
MODEL = "claude-sonnet-4-6"


def run_task_injection(phase_name: str, phase_attr: str, change_id: str, target: Path) -> None:
    """Inject tasks for `phase_name` into a change's tasks.md via Claude."""
    change_dir = target / "openspec" / "changes" / change_id
    if not change_dir.exists():
        console.print(f"[red]Change directory not found: {change_dir}[/red]")
        sys.exit(1)

    proposal_path = change_dir / "proposal.md"
    tasks_path = change_dir / "tasks.md"

    if not proposal_path.exists():
        console.print(f"[red]proposal.md not found in {change_dir}[/red]")
        sys.exit(1)
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

    proposal_content = proposal_path.read_text()
    tasks_content = tasks_path.read_text()

    prompt = _build_prompt(phase_name, proposal_content, tasks_content, applicable, phase_attr)
    updated_tasks = _call_claude(prompt)

    tasks_path.write_text(updated_tasks)
    console.print(f"Updated [cyan]{tasks_path.relative_to(target)}[/cyan]")
    console.print(
        f"Standards that contributed {phase_name} tasks: "
        + ", ".join(f"[cyan]{s.id}[/cyan]" for s in applicable)
    )


def _build_prompt(
    phase_name: str,
    proposal_content: str,
    tasks_content: str,
    applicable: list[Standard],
    phase_attr: str,
) -> str:
    standards_section = ""
    for standard in applicable:
        phase: TaskPhase = getattr(standard, phase_attr)
        task_lines = "\n".join(f"  - {t}" for t in phase.tasks)
        standards_section += (
            f"\nStandard: {standard.id}\n"
            f"Insert position: {phase.insert}\n"
            f"Tasks to add:\n{task_lines}\n"
        )

    return (
        f"You are rewriting a tasks.md file for the {phase_name} phase of a software change.\n\n"
        "## Proposal context\n"
        f"{proposal_content}\n\n"
        "## Current tasks.md\n"
        f"{tasks_content}\n\n"
        f"## {phase_name} tasks to inject from applicable standards\n"
        f"{standards_section}\n"
        "Rewrite tasks.md inserting each standard's tasks at the specified position.\n"
        "Rules:\n"
        "- Do not alter existing task wording or numbering\n"
        "- Do not introduce duplicate tasks\n"
        "- Return ONLY the updated tasks.md content, no explanation\n"
    )


def _call_claude(prompt: str) -> str:
    client = anthropic.Anthropic()
    message = client.messages.create(
        model=MODEL,
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}],
    )
    return message.content[0].text
