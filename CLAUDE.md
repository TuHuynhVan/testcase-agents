# Test-case generation team

Run `/gen-testcases <spec file or pasted text>`. Pipeline: requirement-analyst -> test-designer -> testcase-writer -> testcase-reviewer (loop <= 3) with human gates after requirements, design and final.

- Format contract: `templates/testcase-format.md`. Verifier: `scripts/validate_testcases.py`.
- Outputs go in `runs/<slug>/`. Never invent requirements, values or messages - ask the human.
- Fewer, sharper test cases beat many overlapping ones.
