from pathlib import Path

try:
    import tomllib
except ImportError:
    import tomli as tomllib  # type: ignore[no-redef]

from .models import ProjectContext


def inspect(root: Path) -> ProjectContext:
    ctx = ProjectContext(root=root)
    _detect_languages(ctx)
    _find_src_dirs(ctx)
    _find_test_dirs(ctx)
    _collect_test_files(ctx)
    _collect_src_files(ctx)
    _collect_existing_arch_tests(ctx)
    _load_pyproject(ctx)
    _detect_project_type(ctx)
    return ctx


def _detect_languages(ctx: ProjectContext) -> None:
    root = ctx.root
    if list(root.rglob("*.py")):
        ctx.languages.append("python")
    if list(root.rglob("*.go")):
        ctx.languages.append("go")
    if list(root.rglob("*.ts")) or list(root.rglob("*.tsx")):
        ctx.languages.append("typescript")
    if list(root.rglob("*.java")):
        ctx.languages.append("java")


def _find_src_dirs(ctx: ProjectContext) -> None:
    candidates = ["src", "app", "lib"]
    for candidate in candidates:
        p = ctx.root / candidate
        if p.is_dir():
            ctx.src_dirs.append(p)
    # also look for src/package_name pattern
    src = ctx.root / "src"
    if src.is_dir():
        for child in src.iterdir():
            if child.is_dir() and not child.name.startswith(".") and child.name != "__pycache__":
                if child not in ctx.src_dirs:
                    ctx.src_dirs.append(child)


def _find_test_dirs(ctx: ProjectContext) -> None:
    candidates = ["tests", "test"]
    for candidate in candidates:
        p = ctx.root / candidate
        if p.is_dir():
            ctx.test_dirs.append(p)
    # backend/tests pattern
    for subdir in ["backend", "api", "server"]:
        p = ctx.root / subdir / "tests"
        if p.is_dir():
            ctx.test_dirs.append(p)


def _collect_test_files(ctx: ProjectContext) -> None:
    for test_dir in ctx.test_dirs:
        unit_dir = test_dir / "unit"
        if unit_dir.is_dir():
            ctx.unit_test_files.extend(sorted(unit_dir.rglob("test_*.py")))
        integration_dir = test_dir / "integration"
        if integration_dir.is_dir():
            ctx.integration_test_files.extend(sorted(integration_dir.rglob("test_*.py")))
        # flat test layout — no unit/ or integration/ subdirs
        if not unit_dir.is_dir() and not integration_dir.is_dir():
            ctx.unit_test_files.extend(sorted(test_dir.glob("test_*.py")))


def _collect_src_files(ctx: ProjectContext) -> None:
    for src_dir in ctx.src_dirs:
        ctx.src_files.extend(sorted(src_dir.rglob("*.py")))


def _collect_existing_arch_tests(ctx: ProjectContext) -> None:
    for test_dir in ctx.test_dirs:
        arch_dir = test_dir / "architecture"
        if arch_dir.is_dir():
            ctx.existing_arch_tests.extend(sorted(arch_dir.glob("test_*.py")))


def _load_pyproject(ctx: ProjectContext) -> None:
    pyproject_path = ctx.root / "pyproject.toml"
    if pyproject_path.exists():
        try:
            ctx.pyproject = tomllib.loads(pyproject_path.read_text())
        except Exception:
            ctx.pyproject = {}
    # also check backend/pyproject.toml
    backend_pyproject = ctx.root / "backend" / "pyproject.toml"
    if not ctx.pyproject and backend_pyproject.exists():
        try:
            ctx.pyproject = tomllib.loads(backend_pyproject.read_text())
        except Exception:
            ctx.pyproject = {}


def _detect_project_type(ctx: ProjectContext) -> None:
    deps = []
    project = ctx.pyproject.get("project", {})
    deps += project.get("dependencies", [])
    for group in ctx.pyproject.get("dependency-groups", {}).values():
        deps += [d for d in group if isinstance(d, str)]

    dep_str = " ".join(deps).lower()

    if "fastapi" in dep_str or "flask" in dep_str or "django" in dep_str or "starlette" in dep_str:
        ctx.project_type = "api"
    elif "typer" in dep_str or "click" in dep_str or "argparse" in dep_str:
        ctx.project_type = "cli"
    elif ctx.src_files and not ctx.test_dirs:
        ctx.project_type = "library"
    else:
        ctx.project_type = "unknown"
