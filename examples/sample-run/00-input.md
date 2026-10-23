# Login (sample spec)
1. Users log in with username + password.
2. Wrong credentials show the generic error "Invalid username or password" (do not reveal which field is wrong).
3. After 5 consecutive failed attempts the account is locked for 15 minutes.
4. Password length must be 8-64 characters when set.
