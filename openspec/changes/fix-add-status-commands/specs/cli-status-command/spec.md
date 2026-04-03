## ADDED Requirements

### Requirement: Status command shows standard ID, config membership, and last-modified time
The `status` command SHALL display a table of generated architecture test files with columns for
filename, standard ID (read from the file header), whether the standard is still present in
`.agency-standards.yaml`, and the file's last-modified timestamp. It SHALL NOT perform any
version comparison.

#### Scenario: Standard is active in config
- **WHEN** the user runs `agency-standards status` and a generated test's standard ID appears in `.agency-standards.yaml`
- **THEN** the Status column shows `in config` (highlighted green)
- **AND** the Last modified column shows the file's mtime as a date string
- **AND** no version or "behind" text appears anywhere in the output

#### Scenario: Standard has been removed from config
- **WHEN** the user runs `agency-standards status` and a generated test's standard ID does NOT appear in `.agency-standards.yaml`
- **THEN** the Status column shows `not in config` (highlighted yellow)

#### Scenario: No architecture directory found
- **WHEN** the user runs `agency-standards status` and no `tests/architecture/` directory exists
- **THEN** the CLI prints a message instructing the user to run `init` first
- **AND** exits with code 0

#### Scenario: No generated files found
- **WHEN** `tests/architecture/` exists but contains no generated test files
- **THEN** the CLI prints a message indicating no generated tests were found

## REMOVED Requirements

### Requirement: Version-based staleness check
**Reason**: The file header format no longer includes a version number; the regex never matches,
causing every file to show "behind". Version tracking is not useful now that generation is
delegated to a Claude Code skill rather than the CLI itself.
**Migration**: No migration needed; the new config-membership check provides equivalent
actionable signal.
