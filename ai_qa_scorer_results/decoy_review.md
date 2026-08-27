# Code Review — SampleBankingApp

The following issues were identified during review of the full source tree.


## Security Vulnerabilities

- **`Services/AuthService.cs`** (line ~35): SQL Injection (login) — `Username` and `Password` are string-interpolated directly into a `SELECT` query. Payload `admin'--` bypasses authentication entirely.
- **`Services/AuthService.cs`** (line ~49): Backdoor / hardcoded admin bypass — `AdminBypassPassword = "SuperAdmin2024"` allows login as superadmin without a DB record.
- **`Services/AuthService.cs`** (line ~56): Broken password hashing — MD5 with no salt. Identical passwords produce identical hashes, enabling rainbow-table and credential-stuffing attacks.
- **`Services/UserService.cs`** (line ~45, 60): SQL Injection (UpdateUser / DeleteUser) — `email`, `username`, and `id` are string-interpolated into UPDATE/DELETE statements.
- **`Services/UserService.cs`** (line ~88): SQL Injection (SearchUsers) — `query` is interpolated into a LIKE clause via `ExecuteQuery`.
- **`Services/TransactionService.cs`** (line ~50, 53): SQL Injection (Transfer/Deposit) — `fromUserId`, `toUserId`, `amount` all concatenated into UPDATE statements.
- **`Services/TransactionService.cs`** (line ~82): SQL Injection (RecordTransaction) — `description` is interpolated; a malicious description can inject arbitrary SQL.
- **`appsettings.json`** (line all): Hardcoded production credentials — DB password, JWT secret, and SMTP credentials committed to source control.
- **`Program.cs`** (line ~30): JWT lifetime validation disabled (`ValidateLifetime = false`) — tokens never expire, stolen tokens are valid forever.
- **`Controllers/UserController.cs`** (line ~53): Broken Access Control — `PUT /api/user/{id}` has no check that the caller owns the account; any user can overwrite any other user's profile.
- **`Controllers/UserController.cs`** (line ~67): Missing Authorization — `DELETE /api/user/{id}` has no role check; any authenticated user can delete any account.

## Logic Errors

- **`Services/TransactionService.cs`** (line ~25): `amount < 0` check allows zero-value transfers (`amount == 0`). Should be `amount <= 0`.
- **`Services/TransactionService.cs`** (line ~43): Balance check excludes the fee — `if (fromBalance >= amount)` should be `>= amount + fee`. A user with exactly `amount` in their account passes the check but their balance goes negative after the fee is deducted.
- **`Services/UserService.cs`** (line ~73): Off-by-one in pagination — `skip = page * pageSize` skips `pageSize` extra rows for page 1. Should be `(page - 1) * pageSize`. Page 1 returns rows `pageSize+1` onwards instead of row 1.
- **`Services/TransactionService.cs`** (line ~60): Incorrect interest rate — deposit bonus uses `0.05m` (5%) instead of intended `0.01m` (1%); also the formula applies it on every deposit as if it's a recurring interest accrual.
- **`Controllers/TransactionController.cs`** (line ~26): Self-transfer allowed — no check that `fromUserId != request.ToUserId`. Self-transfer deducts the fee with no credit, effectively charging the user for nothing.