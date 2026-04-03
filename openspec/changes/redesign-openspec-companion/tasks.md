## 1. Extend standard YAML schema and loader
- [x] 1.1 Update `Standard` dataclass in `models.py` to hold `post_init`, `post_propose`, `condition` structured fields
- [x] 1.2 Update `standards/loader.py` to parse the new schema; preserve backward compatibility for any YAML still using flat fields during migration
- [x] 1.3 Migrate all 21 builtin standard YAML files: move `prompt`, `output_file`, `claude_md_section` under `post_init`; add a `condition` block where appropriate
- [x] 1.4 Add `post_propose` block to each builtin standard: at minimum one run-tests task and one do-not-remove task per standard that generates a test file
- [x] 1.5 Verify loader reads all 21 updated files without error

## 2. Implement condition evaluation
- [x] 2.1 Add `evaluate_condition(standard, ctx: ProjectContext) -> bool` function
- [x] 2.2 Implement `languages` check (intersection with `ctx.languages`)
- [x] 2.3 Implement `project_type` check (match against `ctx.project_type`)
- [x] 2.4 Implement `dependencies` check (presence in `ctx.pyproject` dependency lists)
- [x] 2.5 Implement `features` check (`bdd` → `ctx.uses_bdd`; extensible)
- [x] 2.6 Absent `condition` block → always returns `True`

## 3. Implement `post-init` command
- [x] 3.1 Create `src/agency_standards/commands/post_init_cmd.py`
- [x] 3.2 Inspect project, evaluate conditions, collect applicable standards with a `post_init` block
- [x] 3.3 Write `CLAUDE.md` from each applicable standard's `post_init.claude_md_section`
- [x] 3.4 Install Claude Code skills (reuse or adapt existing `install_cmd.py` logic)
- [x] 3.5 Print instructions to run `/agency-standards:generate` in Claude Code

## 4. Implement `post-propose` command
- [x] 4.1 Create `src/agency_standards/commands/post_propose_cmd.py`
- [x] 4.2 Resolve change directory from `<target>/openspec/changes/<change-id>/`; error if not found
- [x] 4.3 Read `proposal.md` and `tasks.md` from the change directory
- [x] 4.4 Inspect project, evaluate conditions, collect applicable standards with a `post_propose` block
- [x] 4.5 Build Claude API prompt: proposal content + current tasks.md + each standard's insert position and task lines
- [x] 4.6 Call Claude API (use `anthropic` SDK); stream or await full response
- [x] 4.7 Write Claude's returned content to `tasks.md`, replacing previous content
- [x] 4.8 Print summary: which standards contributed tasks

## 5. Stub `post-apply` and `post-archive` commands
- [x] 5.1 Create `post_apply_cmd.py` and `post_archive_cmd.py` printing "not yet implemented"

## 6. Rewrite `cli.py`
- [x] 6.1 Remove `init`, `add`, `update`, `status`, `standards list` commands
- [x] 6.2 Register `post-init`, `post-propose`, `post-apply`, `post-archive` subcommands
- [x] 6.3 Make `post-propose` the default (invoked when first positional arg is a change ID with no subcommand)

## 7. Remove dead code
- [x] 7.1 Delete `commands/init_cmd.py`, `commands/update_cmd.py`, `commands/status_cmd.py`, `commands/standards_cmd.py`, `commands/install_cmd.py` (or refactor install logic into post_init_cmd.py)
- [x] 7.2 Delete `generator.py` if no longer needed; otherwise remove `get_standard_version`
- [x] 7.3 Delete or repurpose `config.py` (`.agency-standards.yaml` config file no longer needed)

## 8. Verify
- [x] 8.1 Run `agency-standards post-init` in a test Python project — CLAUDE.md written, skills installed, no crash
- [x] 8.2 Create a test proposal; run `agency-standards post-propose <change-id>` — tasks.md updated with injected tasks, no crash
- [x] 8.3 Confirm old commands (`init`, `add`) are gone
- [x] 8.4 Run `ruff check src/` — no lint errors
