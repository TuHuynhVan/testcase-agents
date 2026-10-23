# Test cases

### TC-001 | Valid credentials log the user in
- REQ: REQ-001
- Cond: COND-001
- Type: Positive
- Priority: P1
- Technique: UseCase
- Preconditions: Active user "alice" with password "Passw0rd!"
- Test data: username=alice; password=Passw0rd!
- Steps:
  1. Open the login page
  2. Enter the test data and click "Login"
- Expected:
  1. Login form is shown with empty username and password fields
  2. User is redirected to /home and the header shows "alice"

### TC-002 | Unknown username shows generic error
- REQ: REQ-002
- Cond: COND-002
- Type: Negative
- Priority: P1
- Technique: EP
- Preconditions: No user "ghost" exists
- Test data: username=ghost; password=Passw0rd!
- Steps:
  1. Open the login page
  2. Enter the test data and click "Login"
- Expected:
  1. Login form is shown with empty fields
  2. Error "Invalid username or password" is shown; user stays on /login

### TC-003 | Wrong password shows the same generic error
- REQ: REQ-002
- Cond: COND-002
- Type: Negative
- Priority: P1
- Technique: EP
- Preconditions: Active user "alice"
- Test data: username=alice; password=Wrong123!
- Steps:
  1. Open the login page
  2. Enter the test data and click "Login"
- Expected:
  1. Login form is shown with empty fields
  2. Error text is exactly "Invalid username or password", identical to TC-002; user stays on /login

### TC-004 | 4th consecutive failure does not lock the account
- REQ: REQ-003
- Cond: COND-003
- Type: Boundary
- Priority: P2
- Technique: BVA
- Preconditions: Active user "bob", 0 failed attempts
- Test data: username=bob; password=Wrong123!
- Steps:
  1. Submit the test data 4 times
  2. Submit username=bob; password=<correct> once
- Expected:
  1. Each attempt shows "Invalid username or password"
  2. Login succeeds and user is redirected to /home

### TC-005 | 5th consecutive failure locks the account for 15 minutes
- REQ: REQ-003
- Cond: COND-003
- Type: Boundary
- Priority: P1
- Technique: BVA
- Preconditions: Active user "carol", 0 failed attempts
- Test data: username=carol; password=Wrong123!
- Steps:
  1. Submit the test data 5 times
  2. Submit username=carol; password=<correct>
- Expected:
  1. The 5th attempt shows the account-locked message
  2. Login is rejected with the locked message; no session is created; lock expires at +15 min
