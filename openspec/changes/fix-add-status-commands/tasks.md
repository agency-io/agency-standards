## 1. Add shared `write_claude_md` helper
- [ ] 1.1 Create `write_claude_md(target: Path, standard_ids: list[str]) -> None` (suggest placing in `init_cmd.py` or a new `claude_md.py`)
- [ ] 1.2 For each ID, load the standard via `load_by_id`; collect its `claude_md_section`
- [ ] 1.3 Write all sections into `<target>/CLAUDE.md`, creating or overwriting the file

## 2. Restore CLAUDE.md writing in `init` (`src/agency_standards/commands/init_cmd.py`)
- [ ] 2.1 After `write_config(target, selected_ids)`, call `write_claude_md(target, selected_ids)`
- [ ] 2.2 Print a confirmation line: e.g. "Updated CLAUDE.md"

## 3. Fix `add` command (`src/agency_standards/cli.py`)
- [ ] 3.1 Remove the three deleted-function imports (`_generate_and_write_test`, `_generate_custom_standard`, `_resolve_arch_dir`, `_update_claude_md`)
- [ ] 3.2 If `--describe` given: call `_build_custom_standard(describe)` from `init_cmd.py` and `save_custom(standard)` from `standards/loader.py`
- [ ] 3.3 If standard ID given: call `load_by_id(standard_id)` and exit with error if not found
- [ ] 3.4 Call `add_standard_id(resolved, standard.id)` from `config.py`
- [ ] 3.5 Call `write_claude_md(resolved, get_active_ids(resolved))` to update CLAUDE.md
- [ ] 3.6 Call `install_skills(resolved)` from `install_cmd.py`
- [ ] 3.7 Print: "Standard '<id>' added. Run `/agency-standards:generate` in Claude Code to create the test."

## 4. Remove dead code (`src/agency_standards/generator.py`)
- [ ] 4.1 Delete `get_standard_version()` function
- [ ] 4.2 Remove the `from . import __version__` import (only used by `get_standard_version`)

## 5. Fix `status` command (`src/agency_standards/commands/status_cmd.py`)
- [ ] 5.1 Remove `from .. import __version__` import
- [ ] 5.2 Remove `get_standard_version` from `generator` import
- [ ] 5.3 Load active standard IDs from config using `get_active_ids(target)`
- [ ] 5.4 Replace "Generated at" column with "Last modified" showing file mtime as a date
- [ ] 5.5 Replace "Status" column logic: show `[green]in config[/green]` if standard ID is in active IDs, `[yellow]not in config[/yellow]` otherwise
- [ ] 5.6 Remove version-comparison code

## 6. Verify
- [ ] 6.1 Run `agency-standards init -y` in a test project — must write config, write CLAUDE.md, install skills, no crash
- [ ] 6.2 Run `agency-standards add aaa-comments` — must update config, update CLAUDE.md, no crash
- [ ] 6.3 Run `agency-standards status` — must show standard IDs, config membership, and mtime; no "behind"
- [ ] 6.4 Run `ruff check src/` — no lint errors
