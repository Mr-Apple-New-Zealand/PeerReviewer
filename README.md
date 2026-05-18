# PeerReviewer

A code review training and testing platform for AI-powered peer review agents. Contains a deliberately flawed banking application with 60+ intentional bugs across multiple categories, serving as a realistic test corpus for evaluating automated code review systems.

## Purpose

PeerReviewer is designed to:

- **Train and evaluate AI code review agents** by providing a realistic codebase full of intentional defects
- **Test detection coverage** across a wide range of vulnerability and anti-pattern categories
- **Serve as an educational resource** for learning secure coding practices and common defects
- **Benchmark code review tools** against a known, documented set of issues

The sample application is a plausible ASP.NET Core banking API — realistic enough to challenge reviewers, but seeded with bugs that a thorough review should catch.

## Sample Application: SampleBankingApp

The test subject is a REST API for a fictional bank, built with:

- **ASP.NET Core 8.0** (C#)
- **SQL Server** via ADO.NET (raw SQL)
- **JWT Bearer** authentication
- **System.Net.Mail** for email notifications

### API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/auth/login` | Authenticate and receive JWT token |
| `GET` | `/api/user` | List users (paginated) |
| `GET` | `/api/user/{id}` | Get user by ID |
| `PUT` | `/api/user/{id}` | Update user profile |
| `DELETE` | `/api/user/{id}` | Delete user |
| `GET` | `/api/user/search` | Search users |
| `GET` | `/api/user/audit` | Retrieve audit log |
| `POST` | `/api/transaction/transfer` | Transfer funds between accounts |
| `POST` | `/api/transaction/deposit` | Deposit with bonus interest |
| `POST` | `/api/transaction/refund/{id}` | Refund a transaction |

## Bug Categories

The 60+ documented issues span the following categories:

| Category | Count | Examples |
|----------|-------|---------|
| Critical Security | 11 | SQL injection, hardcoded backdoor, broken access control, disabled JWT expiry |
| Configuration | 9 | Secrets committed to source, permissive CORS, debug pages always enabled |
| Dead Code | 11 | Unused methods, unreachable code, superseded implementations |
| Error Handling | 7 | Swallowed exceptions, missing DB transactions, leaked stack traces |
| Missing Null Checks | 7 | Null config values, unchecked row access, unvalidated parameters |
| Logic Errors | 5 | Zero-value transfers, wrong fee/interest rates, self-transfers, off-by-one pagination |
| Anti-patterns | 6 | Mutable static state, regex compiled per-call, string concatenation in loops |
| Resource Leaks | 5 | Unclosed DB connections, undisposed SMTP clients |
| Magic Values | 5 | Hardcoded constants that should be configurable |
| Refactoring | 3 | Duplicated validation, overly long methods |

See [ISSUES.md](ISSUES.md) for the full inventory with descriptions and locations.

## Project Structure

```
PeerReviewer/
├── SampleBankingApp/
│   ├── Controllers/
│   │   ├── AuthController.cs
│   │   ├── UserController.cs
│   │   └── TransactionController.cs
│   ├── Services/
│   │   ├── AuthService.cs
│   │   ├── UserService.cs
│   │   ├── TransactionService.cs
│   │   └── EmailService.cs
│   ├── Models/
│   │   ├── User.cs
│   │   └── Transaction.cs
│   ├── Data/
│   │   └── DatabaseHelper.cs
│   ├── Helpers/
│   │   └── StringHelper.cs
│   ├── Program.cs
│   ├── appsettings.json
│   └── SampleBankingApp.csproj
└── ISSUES.md
```

## Running the Application

The application is intentionally broken in various ways and **should not be deployed to a real environment**. It exists solely as a review target.

If you need to build it for local testing:

**Prerequisites:**
- .NET 8.0 SDK
- SQL Server with a `BankingDB` database
- Update credentials in `appsettings.json`

```bash
cd SampleBankingApp
dotnet restore
dotnet build
dotnet run
```

## Using This as a Review Benchmark

1. Point your code review agent or tool at the `SampleBankingApp/` directory
2. Collect the issues it reports
3. Cross-reference against [ISSUES.md](ISSUES.md) to measure:
   - **True positive rate** — how many documented issues were caught?
   - **False positive rate** — how many reported issues aren't in the inventory?
   - **Category coverage** — which defect types does the tool handle well or miss?

## Warning

This codebase contains intentional security vulnerabilities including SQL injection, hardcoded credentials, and broken authentication. Do not use any part of this code in a real application.
