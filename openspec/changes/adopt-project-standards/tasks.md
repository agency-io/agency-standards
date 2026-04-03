# Tasks: adopt-project-standards

## Implementation

- [x] Update `src/agency_standards/standards/loader.py` — add `load_project(root)` that reads from `<root>/standards/`; add `load_catalog()` for browsing; update `load_all(root)` to return project standards when `standards/` exists, builtins otherwise
- [x] Update `src/agency_standards/commands/post_init_cmd.py` — after selection, copy each selected builtin YAML into `standards/<id>.yaml`; skip (with notice) if file already exists; write `.agency-standards.yaml` as before
- [x] Update `src/agency_standards/commands/list_cmd.py` — show `✓` for adopted (in `standards/`), `[custom]` for custom (in `standards/` but no builtin counterpart), unmarked for available builtins
- [x] Thread `target` / project root into all commands that call `load_all()` so project standards are resolved relative to the correct directory
- [x] Update `src/agency_standards/commands/pre_init_cmd.py` — same copy behaviour as post-init

## Validation

- [x] `post-init --yes` creates `standards/` and populates it with one YAML per applicable standard
- [x] Re-running `post-init` does not overwrite an existing (possibly edited) standard YAML
- [x] A YAML added manually to `standards/` is picked up by `load_all()` and shown in `list`
- [x] `agency-standards list` shows `✓` for adopted standards and `[custom]` for project-only ones
- [x] When `standards/` exists, builtins not in that directory are NOT active (not written to CLAUDE.md)
- [x] `.agency-standards.yaml` still written correctly after selection
