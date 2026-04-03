# Tasks: add-standard-discovery

## Implementation

- [x] Re-introduce `src/agency_standards/config.py` — `load_config(path)` reads `.agency-standards.yaml`, `save_config(path, ids)` writes it; returns `{"standards": {"enabled": [...]}}` structure
- [x] Add `src/agency_standards/commands/list_cmd.py` — `run(filter_tag, verbose, project_path)` loads all standards, optionally loads config for enabled markers, prints table/sections to console
- [x] Register `list` subcommand in `src/agency_standards/cli.py` — `agency-standards list [--filter TAG] [--verbose/-v]`
- [x] Update `src/agency_standards/commands/post_init_cmd.py` — after inspection, load config, build checkbox choices (pre-checked per config or all-checked if no config), prompt with `questionary.checkbox`, apply only selected
- [x] Add `--yes/-y` flag to `post-init` in `src/agency_standards/cli.py` and thread through to `post_init_cmd.run()`
- [x] After selection, call `save_config(target, [s.id for s in selected])` to persist `.agency-standards.yaml`
- [x] Document `.agency-standards.yaml` in README — teams should commit it; subsequent runs use it for pre-checked defaults

## Validation

- [x] `agency-standards list` exits 0 and prints all 21 builtin standards
- [x] `agency-standards list --filter bdd` shows only BDD-tagged standards
- [x] `agency-standards list --verbose` shows `claude_md_section` content for each standard
- [x] `agency-standards post-init` shows a checkbox prompt with all applicable standards pre-checked
- [x] `agency-standards post-init --yes` skips prompt, writes CLAUDE.md and `.agency-standards.yaml`
- [x] On second `post-init` run, previously-selected standards are pre-checked and unselected ones are unchecked
- [x] Empty selection produces warning and does not overwrite CLAUDE.md
- [x] `agency-standards list` marks enabled standards with `✓` when `.agency-standards.yaml` is present
