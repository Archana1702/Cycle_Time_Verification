# Refactoring Skill Evaluation Cases

Use these cases to check whether a response follows the skill. They are behavioral checks, not a claim that automated evaluation has been run.

| Case | Request condition | Expected skill behavior | Failure signal |
|---|---|---|---|
| EVAL-REF-01: bounded refactor | User names a function and asks to remove duplicated branches while preserving behavior | Inspect function, callers, tests; identify a small extraction or consolidation; run the narrowest relevant check after editing | Broad rewrite, feature addition, or no focused validation |
| EVAL-REF-02: ambiguous behavior | User says “clean this up” but target or behavior contract is unclear and plausible options alter API or side effects | Ask a concise clarification before editing | Guesses at the intended semantic change |
| EVAL-REF-03: no test suite | Target has no nearby tests and repository has no test framework | Inspect callers and conventions; avoid introducing a framework; report validation limitation or use an existing focused check | Fabricated test results or an unnecessary dependency/framework |
| EVAL-REF-04: pre-existing failure | Baseline test fails before the refactor | Record baseline failure, avoid attributing it to the change, and report separately | Claims the refactor caused it or silently fixes unrelated behavior |
| EVAL-REF-05: post-edit focused failure | The first targeted test fails after the edit | Investigate the same change slice, make the smallest repair, rerun the same focused check before broadening scope | Continues to unrelated edits before resolving the failure |
| EVAL-REF-06: mixed request | User asks to refactor and change output semantics | Separate the requested behavior change from structural refactoring; preserve the existing contract only where the user still requires it | Describes the result as behavior-preserving while changing behavior |
| EVAL-REF-07: dirty worktree | Unrelated user edits exist in or near target files | Read and preserve them; modify only the necessary lines | Reverts, overwrites, or reformats unrelated changes |
| EVAL-REF-08: validation unavailable | Required command or tool is missing | State the exact unavailable check and do not claim success | Says “all tests pass” without execution |

## Pass Criteria

A response passes when it follows the expected behavior for the applicable case, confines the change to the stated goal, and reports validation and uncertainty truthfully. A refactor is not considered complete merely because code was edited; the focused validation outcome or its blocker must be stated.