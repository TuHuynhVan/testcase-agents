# Format contract (single source of truth)

All agents and `scripts/validate_testcases.py` follow this. Keys stay in English
(parseable); the *content* is written in the language of the input spec.

## 01-requirements.md

```
### REQ-001 — Short title
- Source: where in the spec (section / page / quote ≤ 15 words)
- Statement: ONE atomic, testable sentence (one "shall" only)
- Scope: in            <!-- or: out (excluded from coverage) -->
- Notes: optional
```

Open questions go in a section `## Open Questions`:

```
- Q-001 [BLOCKING] <question>  → Answer: <filled by human>
- Q-002 [NON-BLOCKING] <question>  → Assumption: <what we assume>
```

## 02-test-design.md  (WHAT to test — no steps yet)

```
### COND-001 | REQ-001 | BVA | Password length boundary 8/64
- Check: one line, the condition under test
- Rationale: why this technique, why this matters (risk)
- Planned-TCs: 3
```

`COND-nnn | REQ-id[, REQ-id] | Technique | Title`.
Technique ∈ EP, BVA, DecisionTable, StateTransition, ErrorGuessing, UseCase, Security, Usability, Perf.

## 03-testcases.md  (HOW to test)

```
### TC-001 | Login fails with wrong password
- REQ: REQ-001
- Cond: COND-001
- Type: Negative            <!-- Positive | Negative | Boundary | Security | Usability | Perf -->
- Priority: P1              <!-- P1 critical | P2 major | P3 minor -->
- Technique: EP
- Preconditions: User "alice" exists and is active
- Test data: username=alice; password=WrongPass1
- Steps:
  1. Open the login page
  2. Enter the test data and click "Login"
- Expected:
  1. Login form is displayed with empty fields
  2. Error "Invalid username or password" is shown; user stays on login page; no session cookie set
```

Rules
- Every TC traces to ≥1 REQ and exactly 1 COND.
- `Expected` items are numbered by the step they follow; the LAST step MUST have one.
- Expected = observable fact (UI text, status code, DB value, state). Never "works correctly".
- One TC = one verification goal. No bundling of unrelated checks.
- No TC without a COND. No COND without a TC. No in-scope REQ without a COND.
