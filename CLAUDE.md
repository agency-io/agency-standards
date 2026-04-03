## AAA Pattern (Arrange / Act / Assert)

Every unit and integration test must have three explicit sections:

```python
# Python example
def test_something(self):
    # Arrange
    expected_value = "hello"

    # Act
    actual_value = do_something()

    # Assert
    assert actual_value == expected_value, f"Expected {expected_value!r} but got {actual_value!r}"
```

Rules:
- Arrange, Act, Assert markers are mandatory in every test method
- Empty sections still need the marker
- Act contains exactly one operation
- Assert contains only assertions, no additional logic
- Does not apply to BDD step files (Given/When/Then)

## ADR Format and Lifecycle

ADRs (Architectural Decision Records) capture significant project-level decisions
that future contributors need to understand.

### ADR directory

Use whichever location is already established in the project:
- `openspec/adrs/` — OpenSpec projects
- `docs/adr/` — Nygard-style convention
- `adr/` — flat convention
- `docs/decisions/` — alternative convention

### When to create an ADR

The default criteria are listed below. Projects can override them by adding an
`## ADR Criteria` section to a project spec or README — if that section exists,
use it instead of the defaults.

Default: create an ADR when a decision:
- Defines how two or more systems or services integrate
- Introduces or removes an external library or framework dependency
- Establishes a design pattern reused across multiple components
- Sets a constraint based on an external service limit or protocol behaviour
- Defines a schema or data model that multiple components depend on

### Directory naming

```
<adr-dir>/adr-NNN-<slug>/
```

- NNN is a zero-padded sequential number: 001, 002, 003 ...
- <slug> is a short kebab-case description: `sqlite-storage`, `provider-pattern`
- Numbers must be sequential with no gaps

### Required file: adr.md

Every ADR directory must contain `adr.md` with all six sections:

```markdown
# ADR-NNN: Title

## Status
Proposed | Accepted | Deprecated | Superseded by ADR-NNN

## Context
Background: what situation or constraint led to this decision.

## Options Considered
- **Option A** — description and trade-offs
- **Option B** — description and trade-offs

## Decision
What was decided, stated clearly and specifically.

## Rationale
Why this option was chosen over the alternatives.

## Consequences
- What becomes easier as a result
- What becomes harder or is now constrained
```

### Reference tracking files (OpenSpec projects)

When using `openspec/adrs/`, write a small reference file inside the ADR directory
to create a forward-trace when the ADR is consulted or created during a change:

- `proposal-<change-id>.md` — written during the proposal stage
- `apply-<change-id>.md` — written during the implementation stage

No other file types are permitted in an OpenSpec ADR directory.

### Supersession

When a newer decision overrides an older one:
1. Update the old ADR's `## Status` to `Superseded by ADR-NNN`
2. In the new ADR's `## Context`, reference the old ADR and explain why it no longer holds

## Assertion Failure Messages

Every comparison assertion must include a human-readable failure message.

### Why

Without a message, a failing assertion prints only the raw values — or nothing at all.
A developer reading CI output has to open the test file, find the assertion, and work out
what was expected and why. A good message makes the failure self-explanatory.

### By language

**Python**
```python
# Bad
assert actual_count == expected_count

# Good
assert actual_count == expected_count, (
    f"Expected {expected_count} items but got {actual_count}"
)
```

**Python unittest**
```python
# Bad
self.assertEqual(actual, expected)

# Good
self.assertEqual(actual, expected, msg=f"Expected {expected!r} but got {actual!r}")
```

**Go (testify)**
```go
// Bad
assert.Equal(t, want, got)

// Good
assert.Equal(t, want, got, "account status after creation")
```

**Java JUnit 5**
```java
// Bad
assertEquals(expected, actual);

// Good
assertEquals(expected, actual, "account count after deletion");
```

### Exceptions — messages not required

- `assert value is not None` / null checks
- Simple boolean truthiness checks (`assert response.ok`)
- BDD step files (the Gherkin scenario text serves as the description)

## File Length

Source files must not exceed 500 lines (including blank lines and comments).

### Why

File length is a proxy for complexity. A 600-line file almost always contains more than
one cohesive responsibility. Keeping files short forces decisions about where things belong,
makes code reviews easier to scope, and reduces the chance that two unrelated changes
conflict in the same file.

### How to split a long file

| Situation | Solution |
|---|---|
| Multiple public classes | One class per file (see one-class-per-file standard) |
| Large class with many methods | Extract cohesive groups of methods into collaborator classes |
| Many helper functions | Move to a focused `<concern>_helpers.py` or `utils/<concern>.py` |
| Long test file | Split by scenario — one operation or condition per file |

### Exemptions

The following are not counted toward the limit:
- **Generated files** — migrations, protobuf output, auto-generated clients
- **Vendored code** — third-party code copied into the repo
- **Re-export files** — `__init__.py` or `index.ts` files whose sole purpose is to
  re-export symbols from other modules
- **Type declaration files** — `.d.ts` files in TypeScript projects

If you are unsure whether a file qualifies, apply the limit.

## Test File Naming

Test file names must describe both **what** is being tested and **under what condition**.
A name that mirrors the source module (`test_models.py`) tells you nothing about what
scenario or operation is covered.

### Why

A well-named test file is findable without opening it. When a test fails in CI, the file
name in the output should immediately tell you which operation broke and in what context.
Generic names force developers to search.

### Pattern

```
test_<subject>_<operation>.py
test_<subject>_when_<condition>.py
test_<subject>_<operation>_when_<condition>.py
```

### Examples

| Bad (too generic) | Good (specific) |
|---|---|
| `test_models.py` | `test_account_repository_create.py` |
| `test_utils.py` | `test_date_formatter_when_timezone_missing.py` |
| `test_handlers.py` | `test_order_handler_when_payment_fails.py` |
| `ModelsTest.java` | `AccountRepositoryCreateTest.java` |
| `utils.test.ts` | `date-formatter-empty-timezone.test.ts` |

### Exemptions

These support files are excluded from the naming check:
- `conftest.py`, `__init__.py` — test infrastructure
- `constants.py`, `client.py` — BDD step helpers
- `fixtures.py`, `factories.py` — test data builders
- Step definition files in `given/`, `when/`, `then/` directories

## No Bare / Catch-All Error Handling

Always name the specific exception or error type you are handling. Never use a bare
`except:` or an empty catch block.

### Why

A bare `except` catches everything, including `KeyboardInterrupt`, `SystemExit`, and
programming errors like `AttributeError`. This hides bugs, makes debugging harder, and
can leave the program in an inconsistent state. Naming the exception type makes the
intent explicit and limits the handler to the errors it was designed for.

### Python

```python
# Bad — catches everything including programming errors
try:
    do_something()
except:
    pass

# Bad — too broad
try:
    do_something()
except Exception:
    pass

# Good — specific type
try:
    do_something()
except ValueError as e:
    handle(e)

# Good — multiple specific types
try:
    do_something()
except (KeyError, TypeError) as e:
    log.warning("unexpected input: %s", e)
    raise
```

### TypeScript

```typescript
// Bad — error is swallowed
try {
    doSomething()
} catch {}

// Bad — error is ignored
try {
    doSomething()
} catch (e) {
    // nothing
}

// Good — error is handled or re-raised
try {
    doSomething()
} catch (e) {
    if (e instanceof ValidationError) handle(e)
    else throw e
}
```

### Acceptable patterns

- Re-raising after logging: `except Exception as e: log.error(...); raise`
- Top-level application error boundaries where catching broadly is intentional — document with a comment
- Go: not applicable (Go uses explicit error return values, not exceptions)

## No Magic Strings in Assertions

Extract comparison values to named variables before asserting. Never inline a raw
string or number literal directly in an assertion.

### Why

A magic string in an assertion tells you nothing about intent. `== "active"` is opaque;
`== expected_status` tells you what the value represents. When the test fails, a named
variable also produces a clearer error message because you can include both names.

### Pattern

```python
# Bad — intent unclear, failure message useless
assert account["status"] == "active"

# Good — intent clear, failure message informative
expected_status = "active"
actual_status = account["status"]
assert actual_status == expected_status, (
    f"Expected status {expected_status!r} but got {actual_status!r}"
)
```

### By language

| Language | Expected variable | Actual variable |
|---|---|---|
| Python | `expected_*` | `actual_*` |
| Go | `want` / `expected` | `got` |
| TypeScript | `expected` | `actual` / `result` |
| Java | `expected` | `actual` |

### Exceptions — literals are permitted

- **Null/nil/None checks**: `assert result is None`
- **Boolean checks**: `assert response.ok`
- **Count checks where the value is self-evident**: `assert len(items) == 0`
- **Key/field presence checks**: `assert "id" in response`

## No Skipped Tests

Tests must never be skipped using skip markers or decorators.

### Why

Skipped tests are invisible failures. They were written because someone believed the
behaviour mattered enough to specify, and then quietly switched off. Skipped tests
accumulate over time, are rarely re-enabled, and give false confidence in coverage.
The discipline: a test either runs and passes, or it does not exist.

### Forbidden markers

| Language | Forbidden |
|---|---|
| Python | `@pytest.mark.skip`, `@pytest.mark.skipif`, `@pytest.mark.xfail`, `pytest.skip()` |
| TypeScript | `xit`, `xdescribe`, `test.skip`, `it.skip`, `describe.skip` |
| Java | `@Disabled`, `@Ignore` |
| Go | `t.Skip()` |

### What to do instead

| Situation | Resolution |
|---|---|
| Infrastructure is hard to set up | Fix the infrastructure |
| Test is flaky | Find and fix the root cause |
| Feature not yet built | Delete the test; re-add it when the feature is implemented |
| Behaviour is environment-specific | Make the test environment-agnostic or use fixtures |

### BDD / Gherkin

For Gherkin feature files, `@skip` and `@wip` tags are covered by the
`e2e-no-skipped-scenarios` standard. The `@internal` tag is the only permitted
Gherkin exclusion.

## One Class Per File

Each source file should define at most one public class.

### Why

A file with multiple public classes is doing more than one thing. It makes the codebase
harder to navigate (you cannot predict which file a class lives in), harder to test in
isolation, and harder to change (a change to one class may unintentionally affect others
in the same file). The rule is a forcing function for single-responsibility modules.

### What counts as a violation

```python
# Bad — two independent public classes in one file
class OrderRepository:
    ...

class PaymentRepository:
    ...
```

```python
# Good — each class gets its own file
# order_repository.py
class OrderRepository:
    ...

# payment_repository.py
class PaymentRepository:
    ...
```

### Acceptable exceptions

- **Private/inner helper classes** tightly coupled to the main class and not used elsewhere:
  ```python
  class OrderRepository:
      class _CacheKey:   # private, only used inside OrderRepository
          ...
  ```
- **Exception classes** defined alongside the class that raises them:
  ```python
  class OrderNotFoundError(Exception): ...

  class OrderRepository:
      def get(self, id): raise OrderNotFoundError(id)
  ```
- **Dataclasses or value objects** that exist solely as the return type of the main class
- **Enums** — a file of enum values is not the same as a file with multiple classes

### Applies to

Source files only. Test files are not checked by this standard.

## One Test Class Per File

Each unit test file should contain at most one test class.

### Why

A test file with multiple test classes is covering multiple concerns. This makes the file
name too generic (it cannot describe all the classes it contains), makes it harder to find
the test for a specific operation, and makes individual test classes harder to run in
isolation. One class per file enforces a natural scope boundary.

This standard pairs directly with `file-naming` — if a file needs two test classes, it
is almost always a sign the file name is also too generic.

### Bad — multiple test classes in one file

```python
# test_account_repository.py — BAD
class TestCreate:
    def test_creates_account(self): ...

class TestUpdate:
    def test_updates_status(self): ...

class TestDelete:
    def test_deletes_account(self): ...
```

### Good — one class per file

```python
# test_account_repository_create.py
class TestCreate:
    def test_creates_account(self): ...

# test_account_repository_update.py
class TestUpdate:
    def test_updates_status(self): ...

# test_account_repository_delete.py
class TestDelete:
    def test_deletes_account(self): ...
```

### Applies to

Unit test files only. BDD step files and integration test support files are excluded.
