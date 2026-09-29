---
name: Code Refactoring
description: Refactor existing code for readability, maintainability, or reduced duplication while preserving behavior and validating the change.
argument-hint: Provide the target file or symbol, refactoring goal, constraints, and any required tests.
agent: agent
---

Refactor the requested code using the structured request below. If a field is unspecified, inspect the repository and choose the smallest reasonable change; ask only if the ambiguity could change externally observable behavior.

## Refactoring Request

- **Target file(s) or symbol(s):** ${input:target}
- **Goal:** ${input:goal}
- **Current problem or motivation:** ${input:problem}
- **Constraints / behavior to preserve:** ${input:constraints}
- **Tests or validation expected:** ${input:validation}

## Suggested Keywords

Include the terms that fit the task to make the request precise:

- `behavior-preserving`
- `no functional changes`
- `reduce duplication`
- `improve readability`
- `simplify control flow`
- `extract helper/function`
- `preserve public API`
- `keep scope limited`
- `add or update tests`
- `run focused validation`

## Instructions

1. Read the target code and the nearest relevant tests or callers before editing.
2. State the intended behavior-preserving change briefly, then make the smallest useful refactor.
3. Preserve existing behavior, public interfaces, and unrelated user changes. Do not add features or perform broad cleanup unless requested.
4. Update or add focused tests only when needed to protect behavior or satisfy the request.
5. Run the narrowest relevant test, lint, or type-check command after editing. If validation cannot run, report why without claiming success.
6. Summarize the files changed, the refactoring performed, and validation results. Call out any behavior change or unresolved risk explicitly.