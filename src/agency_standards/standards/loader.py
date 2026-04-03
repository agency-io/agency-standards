from pathlib import Path

import yaml

from ..models import Condition, PostApply, PostInit, PostPropose, ProjectContext, Standard

BUILTIN_DIR = Path(__file__).parent.parent / "builtin_standards"
USER_DIR = Path.home() / ".agency-standards" / "standards"


def load_builtin() -> list[Standard]:
    return _load_from_dir(BUILTIN_DIR, source="builtin")


def load_user() -> list[Standard]:
    if not USER_DIR.exists():
        return []
    return _load_from_dir(USER_DIR, source="local")


def load_all() -> list[Standard]:
    return load_builtin() + load_user()


def load_by_id(standard_id: str) -> Standard | None:
    for standard in load_all():
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


def _parse_standard(data: dict, source: str) -> Standard:
    """Parse a standard from YAML data supporting both old flat and new nested formats."""
    post_init: PostInit | None = None
    post_propose: PostPropose | None = None
    post_apply: PostApply | None = None
    condition: Condition | None = None

    # New nested format
    if "post_init" in data:
        pi = data["post_init"]
        post_init = PostInit(
            output_file=pi.get("output_file", ""),
            prompt=pi.get("prompt", ""),
            claude_md_section=pi.get("claude_md_section", ""),
        )
    elif "output_file" in data or "prompt" in data:
        # Backward-compat: flat format
        post_init = PostInit(
            output_file=data.get("output_file", ""),
            prompt=data.get("prompt", ""),
            claude_md_section=data.get("claude_md_section", ""),
        )

    if "post_propose" in data:
        pp = data["post_propose"]
        post_propose = PostPropose(
            insert=pp.get("insert", "append"),
            tasks=pp.get("tasks", []),
        )

    if "post_apply" in data:
        pa = data["post_apply"]
        post_apply = PostApply(
            insert=pa.get("insert", "append"),
            tasks=pa.get("tasks", []),
        )

    if "condition" in data:
        c = data["condition"]
        condition = Condition(
            languages=c.get("languages"),
            project_type=c.get("project_type"),
            dependencies=c.get("dependencies"),
            features=c.get("features"),
        )

    return Standard(
        id=data["id"],
        name=data["name"],
        description=data["description"],
        source=source,
        tags=data.get("tags", ["general"]),
        post_init=post_init,
        post_propose=post_propose,
        post_apply=post_apply,
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
