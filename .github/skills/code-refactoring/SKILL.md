---
name: code-refactoring
description: 'Use for behavior-preserving code refactoring: improve readability, maintainability, duplication, or control flow while preserving public behavior and validating the smallest change. Trigger on refactor, clean up, simplify, extract helper, or reduce duplication.'
argument-hint: 'Provide target file/symbol, refactoring goal, behavior/API constraints, and relevant tests or validation.'
user-invocable: true
---

# Code Refactoring

## Purpose

Make the smallest useful structural change to existing code while preserving its externally observable behavior. This skill is for refactoring, not feature development, bug fixing, or broad cleanup. If the user requests a behavior change as well, separate it from the refactor and follow the request explicitly.

Use [the request template](./assets/refactoring-request-template.md) to structure new refactoring requests. Use [the evaluation cases](./references/evaluation-cases.md) as a final consistency check for ambiguous requests and validation outcomes.

## Required Procedure

1. **Identify scope.** Locate the target symbols, direct callers, nearby tests, and project guidance. Inspect only the files needed to understand the requested behavior. Preserve unrelated work and existing user changes.
2. **Resolve intent.** Identify the requested structural improvement and the behavior that must remain unchanged. If the target, goal, or behavior contract is unclear and different interpretations could change outputs, side effects, exceptions, ordering, or public interfaces, ask one concise clarifying question before editing. Otherwise choose the smallest interpretation consistent with the request.
3. **Establish a baseline.** Find the narrowest existing test or validation command for the target. Run it before editing when practical. Note existing failures; do not attribute them to the refactor. If no relevant tests exist, inspect callers and project conventions. Do not invent a new test framework or test unrelated behavior.
4. **State the refactor hypothesis.** Before editing, briefly name the concrete structural change and the behavior it is expected to preserve. Make one small, reversible edit focused on that hypothesis.
5. **Validate immediately.** After the first substantive edit, run the narrowest relevant executable check before additional reading or edits. Prefer a targeted test, then a focused type or lint check. If it fails, determine whether the failure is caused by this change; repair only this slice and rerun the same check. Do not expand the change while the first check is unresolved.
6. **Review scope and behavior.** Inspect the resulting diff for unrelated edits, accidental API changes, altered exception behavior, changed ordering or side effects, and unnecessary formatting churn. Add or update focused tests only when needed to protect the refactor's behavior contract and consistent with project patterns.
7. **Report accurately.** Summarize the structural change, files touched, exact validation command and outcome, and any remaining risk. Never say behavior is proven unchanged when tests or an equivalent check were unavailable. Distinguish pre-existing failures from regressions.

## Non-Negotiable Constraints

- Do not add features, silently fix unrelated bugs, or combine a behavior change with a refactor.
- Do not change public APIs, return values, exception types/messages, ordering, persistence, or side effects unless explicitly requested.
- Do not rename or reorganize unrelated code for style alone.
- Do not replace project conventions or add dependencies without an explicit need.
- Do not discard, overwrite, or revert unrelated user changes.
- Do not claim a test, lint, or type check passed unless it was actually run.
- If behavior preservation cannot be established, stop before risky edits and explain the uncertainty.

## Completion Checklist

- [ ] Target and refactoring goal are bounded.
- [ ] Behavior contract and nearest callers/tests were inspected.
- [ ] Baseline result is known or its absence is stated.
- [ ] Change is limited to the stated structural improvement.
- [ ] Focused validation ran after editing, or the blocker is explicit.
- [ ] Diff and final summary identify behavior risks and remaining gaps.