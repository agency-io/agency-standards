# Change: Fix broken `add` and `status` commands left by incomplete refactor

## Why

The codebase was refactored from CLI-driven test generation (calling the Anthropic API directly)
to a skill-based approach where Claude Code does the generation. The refactor was left incomplete:
the `add` command imports three deleted functions and crashes with `ImportError`; the `status`
command always displays "behind" because its version-comparison regex no longer matches the header
format written by the rest of the code; and `CLAUDE.md` is never written by the CLI even though
`_update_claude_md` was removed during the refactor without replacement.

## What Changes

- **`cli.py` `add` command** — rewrite to use existing `add_standard_id` and `install_skills`;
  remove deleted-function imports; write CLAUDE.md after updating config; print instructions to
  run the Claude Code skill for test generation.
- **`init_cmd.py`** — restore CLAUDE.md writing after config is written (was deleted with
  `_update_claude_md` during the refactor); delegate to new shared `write_claude_md` helper.
- **`generator.py`** — remove `get_standard_version()` (dead code; the header format it matched
  was removed during the refactor).
- **`status_cmd.py`** — remove version comparison and the `__version__` import; display standard
  ID, whether the standard is still in config, and last-modified time instead.
- **`config.py`** — no change needed; `add_standard_id` already handles load-append-write.
- **New `write_claude_md` helper** — shared function that reads active standards and writes their
  `claude_md_section` blocks into `CLAUDE.md` at the target project root. Called by both `init`
  and `add`. The generate skill also updates CLAUDE.md when it runs.

## Impact

- Affected specs: `cli-add-command`, `cli-status-command`, `claude-md-management`
- Affected code:
  - `src/agency_standards/cli.py` (lines 77–104)
  - `src/agency_standards/commands/init_cmd.py`
  - `src/agency_standards/generator.py` (`get_standard_version` function)
  - `src/agency_standards/commands/status_cmd.py`
  - new helper (likely in `src/agency_standards/commands/init_cmd.py` or a new `claude_md.py`)
