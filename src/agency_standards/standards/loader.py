from pathlib import Path

import yaml

from ..models import Condition, InitPhase, ProjectContext, Standard, TaskPhase

BUILTIN_DIR = Path(__file__).parent.parent / "builtin_standards"
PROJECT_STANDARDS_SUBDIR = "standards"


def load_builtin() -> list[Standard]:
    return _load_from_dir(BUILTIN_DIR, source="builtin")


def load_project(root: Path) -> list[Standard]:
    """Load standards from the project's standards/ directory."""
    project_dir = root / PROJECT_STANDARDS_SUBDIR
    if not project_dir.exists():
        return []
    return _load_from_dir(project_dir, source="project")


def load_all(root: Path | None = None) -> list[Standard]:
    """Return active standards. Project standards take precedence over builtins when present."""
    if root is not None:
        project = load_project(root)
        if project:
            # Merge: project standards override builtins with the same ID; remaining builtins
            # are included only when no standards/ dir existed (checked above).
            return project
    return load_builtin()


def load_catalog() -> list[Standard]:
    """Return all builtin standards — used for list/post-init browsing regardless of project."""
    return load_builtin()


def load_by_id(standard_id: str, root: Path | None = None) -> Standard | None:
    for standard in load_all(root):
        if standard.id == standard_id:
            return standard
    return None


def evaluate_condition(standard: Standard, ctx: ProjectContext) -> bool:
    """Return True if the standard applies to the given project context."""
    if standard.condition is None:
        return True
    cond = standard.condition
    return (
        _check_languages(cond, ctx)
        and _check_project_type(cond, ctx)
        and _check_dependencies(cond, ctx)
        and _check_features(cond, ctx)
    )


def _check_languages(cond: Condition, ctx: ProjectContext) -> bool:
    if cond.languages is None:
        return True
    return bool(set(cond.languages) & set(ctx.languages))


def _check_project_type(cond: Condition, ctx: ProjectContext) -> bool:
    if cond.project_type is None:
        return True
    return ctx.project_type in cond.project_type


def _check_dependencies(cond: Condition, ctx: ProjectContext) -> bool:
    if cond.dependencies is None:
        return True
    project = ctx.pyproject.get("project", {})
    all_deps: list[str] = list(project.get("dependencies", []))
    for group in ctx.pyproject.get("dependency-groups", {}).values():
        all_deps += [d for d in group if isinstance(d, str)]
    deps_str = " ".join(all_deps).lower()
    return all(dep.lower() in deps_str for dep in cond.dependencies)


def _check_features(cond: Condition, ctx: ProjectContext) -> bool:
    if cond.features is None:
        return True
    for feature in cond.features:
        if feature == "bdd" and not ctx.uses_bdd:
            return False
        if feature == "openspec" and not ctx.uses_openspec:
            return False
    return True


def _parse_init_phase(raw: dict) -> InitPhase:
    return InitPhase(
        output_file=raw.get("output_file", ""),
        prompt=raw.get("prompt", ""),
        claude_md_section=raw.get("claude_md_section", ""),
    )


def _parse_task_phase(raw: dict) -> TaskPhase:
    return TaskPhase(
        insert=raw.get("insert", "append"),
        tasks=raw.get("tasks", []),
    )


def _parse_standard(data: dict, source: str) -> Standard:
    """Parse a standard from YAML data supporting both old flat and new nested formats."""
    condition: Condition | None = None

    if "condition" in data:
        c = data["condition"]
        condition = Condition(
            languages=c.get("languages"),
            project_type=c.get("project_type"),
            dependencies=c.get("dependencies"),
            features=c.get("features"),
        )

    # Init phases
    pre_init = _parse_init_phase(data["pre_init"]) if "pre_init" in data else None
    if "post_init" in data:
        post_init = _parse_init_phase(data["post_init"])
    elif "output_file" in data or "prompt" in data:
        # Backward-compat: flat format
        post_init: InitPhase | None = _parse_init_phase(data)
    else:
        post_init = None

    # Task-injection phases
    pre_propose = _parse_task_phase(data["pre_propose"]) if "pre_propose" in data else None
    post_propose = _parse_task_phase(data["post_propose"]) if "post_propose" in data else None
    pre_apply = _parse_task_phase(data["pre_apply"]) if "pre_apply" in data else None
    post_apply = _parse_task_phase(data["post_apply"]) if "post_apply" in data else None
    pre_archive = _parse_task_phase(data["pre_archive"]) if "pre_archive" in data else None
    post_archive = _parse_task_phase(data["post_archive"]) if "post_archive" in data else None

    return Standard(
        id=data["id"],
        name=data["name"],
        description=data["description"],
        source=source,
        tags=data.get("tags", ["general"]),
        pre_init=pre_init,
        post_init=post_init,
        pre_propose=pre_propose,
        post_propose=post_propose,
        pre_apply=pre_apply,
        post_apply=post_apply,
        pre_archive=pre_archive,
        post_archive=post_archive,
        condition=condition,
    )


def _load_from_dir(directory: Path, source: str) -> list[Standard]:
    standards = []
    if not directory.exists():
        return standards
    for path in sorted(directory.glob("*.yaml")):
        try:
            data = yaml.safe_load(path.read_text())
            standards.append(_parse_standard(data, source))
        except Exception as e:
            print(f"Warning: could not load standard from {path}: {e}")
    return standards
