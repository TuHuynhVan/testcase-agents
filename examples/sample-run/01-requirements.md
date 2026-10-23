# Requirements (APPROVED)

### REQ-001 — Login with valid credentials
- Source: spec §1
- Statement: The system shall authenticate a user who submits a valid username and password.
- Scope: in

### REQ-002 — Generic error on bad credentials
- Source: spec §2
- Statement: The system shall show "Invalid username or password" for any failed login, without revealing which field was wrong.
- Scope: in

### REQ-003 — Lockout after 5 failures
- Source: spec §3
- Statement: The system shall lock an account for 15 minutes after 5 consecutive failed logins.
- Scope: in

## Open Questions
- Q-001 [NON-BLOCKING] Does a successful login reset the failure counter?  → Assumption: yes
