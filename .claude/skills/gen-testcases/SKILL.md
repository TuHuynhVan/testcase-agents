---
name: gen-testcases
description: Generate a reviewed, traceable, low-noise set of test cases from a spec/user stories using a multi-agent loop (analyst -> designer -> writer -> reviewer) with human approval gates. Use when the user asks to generate/write test cases from requirements.
argument-hint: <path-to-spec-or-pasted-text> [--parallel]
---

You are the ORCHESTRATOR. Subagents cannot spawn subagents, so you drive the loop. Work from the project root. Format contract: `templates/testcase-format.md`.

## 0. Setup
- Pick a slug from the spec name; create `runs/<slug>/`. Copy/paste the input into `runs/<slug>/00-input.md` (if the user gave a path, keep a copy; if text, save it).
- If input is empty or a single vague sentence, ask the human for the spec first.

## 1. Requirements  (agent: requirement-analyst)
Run it. Then **HIL GATE 1**:
- For every [BLOCKING] question, ask the human with AskUserQuestion (offer likely answers + Other). Write answers into `01-requirements.md` (`→ Answer:`). Do NOT answer for them.
- Show the REQ list + NON-BLOCKING assumptions. Ask: Approve / Edit file myself / Re-run with feedback.
- Loop (re-run analyst with feedback) until approved. Set `Status: APPROVED`.

## 2. Test design  (agent: test-designer)
Run it. **HIL GATE 2** - show a compact table: REQ -> conditions -> technique -> planned TCs, total count, and "deliberately not tested". Ask: Approve / Too many / Too few / Edit myself. Re-run with feedback until approved. This gate is where scope and volume are decided - it is cheap to change here, expensive later. Set `Status: APPROVED`.

## 3. Write  (agent: testcase-writer)
- Small design (<= ~15 conditions): one writer -> `03-testcases.md`.
- Large design or `--parallel`: split conditions by module/REQ range into slices, launch one writer per slice IN PARALLEL (single message, multiple Agent calls), each writing `03-testcases-<module>.md`; then concatenate into `03-testcases.md` and renumber nothing (IDs were pre-assigned per slice - tell each writer its TC-ID range, e.g. 001-099, 100-199).

## 4. Verify loop  (agent: testcase-reviewer)  - max 3 rounds
Repeat:
1. Launch testcase-reviewer (round N) -> `04-review-round<N>.md`.
2. Read the verdict yourself; also run the validator once to confirm it matches the reviewer's claim.
3. PASS -> go to 5. FAIL -> launch testcase-writer with the review file to fix (writer changes only what findings require). N += 1.
4. If still FAIL after round 3, or a finding needs a business decision, STOP and escalate to the human with the remaining findings; do not loop forever or silently ship.

## 5. HIL GATE 3 - final sign-off
Show: counts, coverage matrix (validator output), review rounds, remaining `[TBD]` items, 3 sample TCs. Ask: Accept / Request changes (loop to 4 with their notes) . On Accept:
`python3 scripts/validate_testcases.py --reqs ... --design ... --tc ... --strict --export runs/<slug>/testcases.csv`
(if --strict fails only on warnings, show them and let the human decide). Report the path of `testcases.csv` (Excel/Jira/TestRail importable).

## Rules
- Never skip a gate; never answer blocking questions yourself; never claim PASS without validator output you have seen.
- Keep the human's time cheap: batch questions, show tables not essays.
- Each file's `Status:` must be APPROVED before the next stage reads it.
