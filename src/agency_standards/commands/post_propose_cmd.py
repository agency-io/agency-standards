import sys
from pathlib import Path

import anthropic
from rich.console import Console

from ..inspector import inspect
from ..standards.loader import evaluate_condition, load_all

console = Console()

MODEL = "claude-sonnet-4-6"


def run(change_id: str, target: Path) -> None:
    change_dir = target / "openspec" / "changes" / change_id
    if not change_dir.exists():
        console.print(
            f"[red]Change directory not found: {change_dir}[/red]"
        )
        sys.exit(1)

    proposal_path = change_dir / "proposal.md"
    tasks_path = change_dir / "tasks.md"

    if not proposal_path.exists():
        console.print(f"[red]proposal.md not found in {change_dir}[/red]")
        sys.exit(1)
    if not tasks_path.exists():
        console.print(f"[red]tasks.md not found in {change_dir}[/red]")
        sys.exit(1)

    proposal_content = proposal_path.read_text()
    tasks_content = tasks_path.read_text()

    ctx = inspect(target)
    applicable = [
        s for s in load_all()
        if evaluate_condition(s, ctx) and s.post_propose is not None
    ]

    if not applicable:
        console.print("[yellow]No applicable standards with post_propose blocks found.[/yellow]")
        return

    console.print(
        f"[dim]{len(applicable)} standards will contribute tasks: "
        + ", ".join(s.id for s in applicable)
        + "[/dim]"
    )

    prompt = _build_prompt(proposal_content, tasks_content, applicable)
    updated_tasks = _call_claude(prompt)

    tasks_path.write_text(updated_tasks)
    console.print(f"Updated [cyan]{tasks_path.relative_to(target)}[/cyan]")
    console.print(
        "Standards that contributed tasks: "
        + ", ".join(f"[cyan]{s.id}[/cyan]" for s in applicable)
    )


def _build_prompt(proposal_content: str, tasks_content: str, applicable: list) -> str:
    standards_section = ""
    for standard in applicable:
        pp = standard.post_propose
        task_lines = "\n".join(f"  - {t}" for t in pp.tasks)
        standards_section += (
            f"\nStandard: {standard.id}\n"
            f"Insert position: {pp.insert}\n"
            f"Tasks to add:\n{task_lines}\n"
        )

    return (
        "You are rewriting a tasks.md file for a software change proposal.\n\n"
        "## Proposal context\n"
        f"{proposal_content}\n\n"
        "## Current tasks.md\n"
        f"{tasks_content}\n\n"
        "## Standards to inject\n"
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
