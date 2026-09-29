# Refactoring Request

Fill the required fields. Use `none` or `not sure` rather than leaving an important constraint ambiguous.

- **Target file(s) or symbol(s) (required):**
- **Refactoring goal (required):** Improve readability / reduce duplication / simplify control flow / extract helper / other:
- **Current problem or motivation:**
- **Behavior that must remain unchanged (required):** Inputs and outputs, public API, errors/exceptions, ordering, side effects, persistence:
- **Constraints:** Files or interfaces to preserve; scope limits; dependency limits:
- **Validation:** Relevant test, type-check, lint command, or `detect appropriate existing checks`:

## Suggested Request Keywords

Use only those relevant to the task:

- `behavior-preserving`
- `no functional changes`
- `preserve public API`
- `preserve exception behavior`
- `reduce duplication`
- `improve readability`
- `simplify control flow`
- `extract helper`
- `keep scope limited`
- `preserve unrelated changes`
- `run focused validation`

## Example

Refactor `src/parser.py::parse_record` to reduce duplicated validation branches. Preserve accepted inputs, returned values, exception types, and validation order. Keep the public API unchanged, do not add dependencies, and run the existing parser tests.