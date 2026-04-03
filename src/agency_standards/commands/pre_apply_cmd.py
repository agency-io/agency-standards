from pathlib import Path

from ._task_injection import run_task_injection


def run(change_id: str, target: Path) -> None:
    run_task_injection("pre-apply", "pre_apply", change_id, target)
