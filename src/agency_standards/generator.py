import re

from .models import CUSTOM_MARKER, GENERATED_MARKER, ProjectContext, Standard


def wrap_with_header(content: str, standard_id: str) -> str:
    header = (
        f"{GENERATED_MARKER} | standard: {standard_id}\n"
        f"{CUSTOM_MARKER}\n\n"
    )
    return header + content


def preserve_custom_section(old_content: str, new_content: str) -> str:
    """Keep anything after CUSTOM_MARKER from the old file, append to new generated content."""
    if CUSTOM_MARKER in old_content:
        _, custom = old_content.split(CUSTOM_MARKER, 1)
        custom = custom.strip()
    else:
        custom = ""

    if CUSTOM_MARKER in new_content:
        header_and_body, _ = new_content.split(CUSTOM_MARKER, 1)
        base = header_and_body + CUSTOM_MARKER + "\n"
    else:
        base = new_content + "\n" + CUSTOM_MARKER + "\n"

    if custom:
        return base + "\n" + custom + "\n"
    return base


def get_standard_id(content: str) -> str | None:
    match = re.search(r"standard: ([\w-]+)", content)
    return match.group(1) if match else None


def resolve_output_filename(standard: Standard, ctx: ProjectContext) -> str:
    """Derive a language-appropriate filename from the standard's output_file base name."""
    if standard.post_init is None:
        return ""
    base = standard.post_init.output_file
    if "." in base:
        return base

    lang = ctx.languages[0] if ctx.languages else "python"

    if lang == "go":
        name = base.removeprefix("test_")
        return f"{name}_test.go"
    elif lang == "typescript":
        name = base.removeprefix("test_").replace("_", "-")
        return f"{name}.test.ts"
    elif lang == "java":
        parts = base.removeprefix("test_").split("_")
        pascal = "".join(p.capitalize() for p in parts)
        return f"{pascal}Test.java"
    else:
        if not base.startswith("test_"):
            base = f"test_{base}"
        return f"{base}.py"
