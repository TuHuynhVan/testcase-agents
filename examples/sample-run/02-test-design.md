# Test design (APPROVED)

### COND-001 | REQ-001 | UseCase | Valid login succeeds
- Check: valid user reaches the home page with a session
- Rationale: core happy path
- Planned-TCs: 1

### COND-002 | REQ-002 | EP | Invalid username vs invalid password give same message
- Check: both failure classes show the identical generic error
- Rationale: prevents account enumeration
- Planned-TCs: 2

### COND-003 | REQ-003 | BVA | Lockout threshold 4 / 5 failures
- Check: 4th failure does not lock, 5th does
- Rationale: boundary of the lock rule
- Planned-TCs: 2
