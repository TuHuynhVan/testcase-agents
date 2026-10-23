# Test-case generation agents (Claude Code)

Bộ subagent giúp Claude **sinh test case có Steps + Expected rõ ràng, ít "linh tinh", có kiểm chứng và có người duyệt**.
A Claude Code project: 4 subagents + 1 orchestrating skill + a deterministic validator.

## Vì sao prompt đơn lẻ hay ra nhiều rác? / Why a single prompt gives noise
Claude được yêu cầu "viết test case" ngay từ spec → nó viết thừa, lặp, bịa expected result. Bộ này tách việc:

| Bước | Agent | Làm gì | Người duyệt (HIL) |
|---|---|---|---|
| 1 | `requirement-analyst` | Tách spec thành REQ nhỏ, liệt kê **câu hỏi còn thiếu** (không tự bịa) | ✅ Gate 1: trả lời câu hỏi, duyệt REQ |
| 2 | `test-designer` | Chọn *cần test gì* (EP/BVA/bảng quyết định…) và **số lượng TC tối thiểu** | ✅ Gate 2: duyệt phạm vi/số lượng |
| 3 | `testcase-writer` | Viết TC theo format cố định (song song nếu spec lớn) | |
| 4 | `testcase-reviewer` | Người kiểm tra **độc lập**: chạy validator + soi trùng lặp, expected mơ hồ/bịa, thiếu coverage → PASS/FAIL, loop ≤ 3 vòng | |
| 5 | (orchestrator) | Xuất `testcases.csv` | ✅ Gate 3: chốt cuối |

Kiểm chứng 2 lớp: **script** `scripts/validate_testcases.py` (đủ trường, trace REQ→COND→TC, trùng lặp, expected mơ hồ, coverage) + **reviewer agent** (ngữ nghĩa).

## Cài đặt / Setup
1. Cài [Claude Code](https://docs.claude.com/en/docs/claude-code), cần Python 3 (không cần thư viện).
2. Copy cả thư mục này (hoặc chỉ `.claude/`, `templates/`, `scripts/`, `CLAUDE.md`) vào repo của bạn, rồi `cd` vào đó và chạy `claude`.

## Dùng / Usage
```
/gen-testcases docs/login-spec.md
/gen-testcases docs/big-spec.md --parallel     # nhiều writer chạy song song
```
Hoặc dán thẳng spec / user story sau lệnh. Claude sẽ dừng ở 3 gate để hỏi bạn. Kết quả: `runs/<slug>/` gồm
`01-requirements.md`, `02-test-design.md`, `03-testcases.md`, `04-review-round*.md`, `testcases.csv` (mở bằng Excel / import Jira, TestRail).

Bạn có thể **tự sửa file** `01`/`02` giữa các gate rồi bảo "tiếp tục".

## Mẹo để kết quả tốt / Tips
- Đưa spec càng cụ thể càng tốt (message lỗi, giới hạn, role). Cái gì thiếu, agent sẽ hỏi — hãy trả lời thay vì để nó đoán.
- Muốn đổi cột/format: sửa `templates/testcase-format.md` **và** `scripts/validate_testcases.py` (hai nơi phải khớp).
- Muốn ít/nhiều TC hơn: nói ở Gate 2 ("giảm còn ~20 TC", "thêm negative cho thanh toán").
- Ngôn ngữ test case theo ngôn ngữ của spec (tiếng Việt OK); tên trường giữ tiếng Anh.

## Thử nhanh validator
```
cd examples/sample-run
python3 ../../scripts/validate_testcases.py --reqs 01-requirements.md --design 02-test-design.md --tc 03-testcases.md
```
