#!/usr/bin/env python3
"""Deterministic verifier for the test-case pipeline (stdlib only).

Usage:
  validate_testcases.py --reqs 01-requirements.md --design 02-test-design.md \
      --tc 03-testcases.md [--strict] [--export testcases.csv]

Exit code: 0 = no errors, 1 = errors (or warnings with --strict), 2 = bad input.
Checks the contract in templates/testcase-format.md.
"""
import argparse
import csv
import difflib
import re
import sys
from pathlib import Path

TYPES = {"Positive", "Negative", "Boundary", "Security", "Usability", "Perf"}
PRIORITIES = {"P1", "P2", "P3"}
TECHNIQUES = {"EP", "BVA", "DecisionTable", "StateTransition", "ErrorGuessing",
              "UseCase", "Security", "Usability", "Perf"}
FIELDS = ["REQ", "Cond", "Type", "Priority", "Technique", "Preconditions",
          "Test data", "Steps", "Expected"]
VAGUE = [
    "works correctly", "work correctly", "as expected", "works properly",
    "works fine", "is correct", "displayed correctly", "behaves normally",
    "successfully" , "hoạt động bình thường", "hoạt động đúng", "đúng như mong đợi",
    "như mong đợi", "hiển thị đúng", "xử lý đúng", "không có lỗi",
]
MAX_TC_PER_COND = 3
MAX_STEPS = 10


def blocks(text, header_re):
    """Split text into (match, body) for each '### ' header matching header_re."""
    ms = list(re.finditer(header_re, text, re.M))
    out = []
    for i, m in enumerate(ms):
        end = ms[i + 1].start() if i + 1 < len(ms) else len(text)
        # stop at next level-2 heading so trailing sections don't leak in
        body = text[m.end():end]
        body = re.split(r"^## ", body, maxsplit=1, flags=re.M)[0]
        out.append((m, body))
    return out


def parse_reqs(text):
    reqs = {}
    for m, body in blocks(text, r"^###\s+(REQ-\d+)\b.*$"):
        scope = re.search(r"^-\s*Scope:\s*(\w+)", body, re.M)
        stmt = re.search(r"^-\s*Statement:\s*(.+)$", body, re.M)
        reqs[m.group(1)] = {
            "in_scope": not (scope and scope.group(1).lower() == "out"),
            "statement": stmt.group(1).strip() if stmt else "",
        }
    return reqs


def parse_design(text):
    conds = {}
    for m, body in blocks(text, r"^###\s+(COND-\d+)\s*\|\s*([^|]+)\|\s*([^|]+)\|\s*(.*)$"):
        conds[m.group(1)] = {
            "reqs": [r.strip() for r in m.group(2).split(",") if r.strip()],
            "technique": m.group(3).strip(),
            "title": m.group(4).strip(),
        }
    return conds


def parse_tcs(text):
    tcs = []
    for m, body in blocks(text, r"^###\s+(TC-\d+)\s*\|\s*(.*)$"):
        tc = {"id": m.group(1), "title": m.group(2).strip(), "f": {}}
        cur = None
        for line in body.splitlines():
            h = re.match(r"^-\s*(" + "|".join(re.escape(f) for f in FIELDS) + r"):\s*(.*)$", line)
            if h:
                cur = h.group(1)
                tc["f"][cur] = h.group(2).strip()
            elif cur and line.strip():
                tc["f"][cur] += "\n" + line.strip()
        tcs.append(tc)
    return tcs


def numbered(s):
    """'1. a\n2. b' -> {1:'a', 2:'b'}"""
    out = {}
    for line in s.splitlines():
        m = re.match(r"^\s*(\d+)[.)]\s*(.+)$", line)
        if m:
            out[int(m.group(1))] = m.group(2).strip()
    return out


def norm(s):
    return re.sub(r"\W+", " ", s.lower()).strip()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--reqs", required=True)
    ap.add_argument("--design", required=True)
    ap.add_argument("--tc", required=True)
    ap.add_argument("--strict", action="store_true")
    ap.add_argument("--export")
    a = ap.parse_args()

    try:
        reqs = parse_reqs(Path(a.reqs).read_text(encoding="utf-8"))
        conds = parse_design(Path(a.design).read_text(encoding="utf-8"))
        tcs = parse_tcs(Path(a.tc).read_text(encoding="utf-8"))
    except OSError as e:
        print(f"ERROR input: {e}")
        return 2
    errors, warns = [], []
    E = lambda m: errors.append(m)
    W = lambda m: warns.append(m)

    if not reqs: E("no REQ-xxx blocks found in requirements file")
    if not conds: E("no COND-xxx blocks found in design file")
    if not tcs: E("no TC-xxx blocks found in test case file")

    # design -> requirements
    for cid, c in conds.items():
        for r in c["reqs"]:
            if r not in reqs: E(f"{cid}: unknown requirement {r}")
        if c["technique"] not in TECHNIQUES:
            E(f"{cid}: technique '{c['technique']}' not in {sorted(TECHNIQUES)}")
    covered_reqs = {r for c in conds.values() for r in c["reqs"]}
    for rid, r in reqs.items():
        if r["in_scope"] and rid not in covered_reqs:
            E(f"{rid}: in-scope requirement has no COND in design")
        if not r["statement"]:
            W(f"{rid}: missing Statement")

    # test cases
    seen_ids, per_cond, sigs = set(), {}, {}
    for tc in tcs:
        t, f = tc["id"], tc["f"]
        if t in seen_ids: E(f"{t}: duplicate id")
        seen_ids.add(t)
        for k in FIELDS:
            if not f.get(k, "").strip(): E(f"{t}: missing/empty field '{k}'")
        trs = [x.strip() for x in f.get("REQ", "").split(",") if x.strip()]
        for r in trs:
            if r not in reqs: E(f"{t}: unknown requirement {r}")
        cond = f.get("Cond", "").strip()
        if cond and cond not in conds: E(f"{t}: unknown condition {cond}")
        elif cond:
            per_cond.setdefault(cond, []).append(t)
            if trs and not set(trs) & set(conds[cond]["reqs"]):
                E(f"{t}: REQ {trs} not linked to {cond} (design says {conds[cond]['reqs']})")
        if f.get("Type") and f["Type"] not in TYPES: E(f"{t}: Type '{f['Type']}' invalid")
        if f.get("Priority") and f["Priority"] not in PRIORITIES: E(f"{t}: Priority '{f['Priority']}' invalid")
        if f.get("Technique") and f["Technique"] not in TECHNIQUES: E(f"{t}: Technique '{f['Technique']}' invalid")

        steps, exp = numbered(f.get("Steps", "")), numbered(f.get("Expected", ""))
        if not steps: E(f"{t}: Steps must be a numbered list")
        else:
            if sorted(steps) != list(range(1, len(steps) + 1)): E(f"{t}: step numbers not 1..n")
            if len(steps) > MAX_STEPS: W(f"{t}: {len(steps)} steps (> {MAX_STEPS}) - split the TC?")
        if not exp: E(f"{t}: Expected must be a numbered list")
        elif steps:
            bad = set(exp) - set(steps)
            if bad: E(f"{t}: Expected refers to missing step(s) {sorted(bad)}")
            if max(steps) not in exp: E(f"{t}: last step {max(steps)} has no Expected")
        for n, txt in exp.items():
            low = txt.lower()
            hit = next((v for v in VAGUE if v in low), None)
            if hit: W(f"{t}: Expected #{n} is vague ('{hit}') - state the observable result")
            elif len(txt) < 12: W(f"{t}: Expected #{n} too short to be observable: '{txt}'")

        sig = norm(f.get("Steps", "")) + "|" + norm(f.get("Expected", ""))
        if sig in sigs: E(f"{t}: identical steps+expected as {sigs[sig]} (duplicate)")
        else: sigs[sig] = t

    # near-duplicate titles
    for i in range(len(tcs)):
        for j in range(i + 1, len(tcs)):
            ratio = difflib.SequenceMatcher(None, norm(tcs[i]["title"]), norm(tcs[j]["title"])).ratio()
            if ratio >= 0.9:
                W(f"{tcs[i]['id']} ~ {tcs[j]['id']}: near-identical titles ({ratio:.0%})")

    # design coverage / over-testing
    for cid in conds:
        n = len(per_cond.get(cid, []))
        if n == 0: E(f"{cid}: no test case covers this condition")
        elif n > MAX_TC_PER_COND: W(f"{cid}: {n} TCs (> {MAX_TC_PER_COND}) - possible over-testing")

    print(f"REQs={len(reqs)} (in scope {sum(r['in_scope'] for r in reqs.values())})  "
          f"CONDs={len(conds)}  TCs={len(tcs)}")
    print("\nCoverage  REQ -> COND -> TC")
    for rid, r in reqs.items():
        cs = [c for c, v in conds.items() if rid in v["reqs"]]
        ts = [t for c in cs for t in per_cond.get(c, [])]
        flag = "" if r["in_scope"] else "  (out of scope)"
        print(f"  {rid}: {len(cs)} cond, {len(ts)} TC {ts}{flag}")
    for m in errors: print("ERROR  ", m)
    for m in warns: print("WARN   ", m)
    verdict = "FAIL" if errors or (a.strict and warns) else "PASS"
    print(f"\nVERDICT: {verdict}  ({len(errors)} errors, {len(warns)} warnings)")

    if a.export and verdict == "PASS":
        with open(a.export, "w", newline="", encoding="utf-8-sig") as fh:  # BOM: Excel-friendly
            w = csv.writer(fh)
            w.writerow(["TC ID", "Title", "REQ", "Condition", "Type", "Priority", "Technique",
                        "Preconditions", "Test data", "Steps", "Expected"])
            for tc in tcs:
                f = tc["f"]
                w.writerow([tc["id"], tc["title"], f["REQ"], f["Cond"], f["Type"], f["Priority"],
                            f["Technique"], f["Preconditions"], f["Test data"], f["Steps"], f["Expected"]])
        print(f"Exported {len(tcs)} test cases -> {a.export}")
    return 0 if verdict == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
