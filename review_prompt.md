You are an expert software engineer performing a thorough peer code review.
Review the source files from branch '{branch_name}' (commit {commit_sha}).

{truncation_note}

Work through EVERY category below methodically. For each category, read every file carefully and report ALL issues you find, no matter how minor. Do not skip a category because you found nothing — if a category is clean, say so.

---

## Review Categories

### 1. Security Vulnerabilities
Check for: SQL injection (including string-interpolated queries, LIKE clauses, UPDATE/DELETE/INSERT statements, and helper methods that accept raw SQL fragments); hardcoded credentials, passwords, API keys, or backdoors in source files or config; broken or weak cryptography (MD5, SHA1, no salt); JWT misconfiguration (ValidateLifetime, weak secrets); broken access control (missing ownership checks on PUT/DELETE endpoints); missing authorization attributes; open CORS policy; developer exception pages in production; HTTPS disabled; debug symbols in release builds; production secrets committed to source control.

### 2. Logic Errors
Check for: off-by-one errors (especially in pagination — e.g. `page * pageSize` vs `(page-1) * pageSize`); incorrect boundary conditions (e.g. `< 0` when `<= 0` is needed); balance or fee calculations that exclude a component (e.g. checking balance >= amount but then deducting amount + fee); incorrect rates or constants (e.g. interest rate applied as 5% instead of 1%); missing self-referential checks (e.g. transferring to yourself); any operation that can produce a negative balance or nonsensical result.

### 3. Error Handling
Check for: methods that catch broad `Exception` and swallow it silently; catch blocks that return empty collections — callers cannot distinguish 'no results' from 'error'; operations that lack a database transaction where two or more writes must be atomic; side effects (e.g. email sending) that can throw after a DB write has already committed; raw `ex.Message` or stack traces returned to HTTP clients; missing rate limiting or account lockout on authentication endpoints.

### 4. Resource Leaks
Check for: `SqlConnection`, `SqlDataReader`, `SqlCommand` that are opened but never closed or disposed; connections returned from helper methods where the caller never disposes them; `SmtpClient` held as an instance field (not thread-safe, socket never released); `MailMessage` or other `IDisposable` objects created but never disposed; any exception path that skips a `Close()` or `Dispose()` call.

### 5. Null Reference Risks
Check for: configuration values read with `_config["key"]` passed directly to methods that cannot accept null (e.g. `Encoding.UTF8.GetBytes`); `DataTable.Rows[0]` accessed without first checking `Rows.Count > 0`; `.Value` on a nullable or `?.Value` result passed to `int.Parse` without null guard; method parameters used (`.ToUpper()`, `.Length`, etc.) before a null check; model-bound request objects used in controller actions without a null check.

### 6. Dead Code
Work this category as a search, not an impression -- an unused method is proved by the ABSENCE of a caller, which you cannot see by reading top to bottom.
Step 1: list EVERY method defined in the source files above. Include private methods, public methods, and helpers in every class -- services, controllers, data access and utility classes alike.
Step 2: for each name on that list, scan all the source files for a call to it.
Step 3: report every method whose name appears only at its own definition. Name each one explicitly in its own row. Work the whole list -- do not stop once you have found a few, and do not assume a method is used because it looks useful or well written.
Also check for: methods marked `[Obsolete]` that are still present; code after an unconditional `return` statement (unreachable); duplicate implementations where a fixed version exists alongside a broken one but only the broken one is called; `throw new NotImplementedException()` in non-stub code.

### 7. Magic Strings and Numbers
Check for: numeric literals used inline without a named constant (e.g. fee rates, page size limits, deposit caps, string length limits); string literals for email addresses, role names, or config keys repeated in multiple places; values that belong in configuration (e.g. `appsettings.json`) but are hardcoded in source.

### 8. Anti-patterns and Code Quality
Check for: string concatenation inside a loop (O(n²) — use `StringBuilder` or `string.Join`); `new Regex(...)` inside a method called repeatedly (should be `static readonly`); shared mutable static state accessed from multiple threads without synchronization; reimplementing standard library methods that already exist (e.g. `string.IsNullOrWhiteSpace`); helper methods designed to leak resource ownership to callers with no documented contract; duplicated validation logic that should be extracted to a shared method (report it once per method that repeats the block, naming each).
Also report refactoring opportunities: any method whose body carries three or more distinct responsibilities that would be clearer and more testable split into named private helpers -- name the method and say which responsibilities you would separate.

### 9. Configuration Issues
Check for: `UseDeveloperExceptionPage()` called unconditionally; `ValidateLifetime = false` on JWT; HTTPS redirection commented out; overly permissive CORS (`AllowAnyOrigin` + `AllowAnyMethod`); debug log levels set for production namespaces; outdated or vulnerable NuGet packages (check `.csproj`); missing environment-specific config overrides (`appsettings.Production.json`).

### 10. Missing Unit Tests
Check whether a test project exists. If not, list the specific methods and scenarios that are most critical to test, focusing on boundary conditions, auth flows, financial calculations, and pagination.

---

## Output Format

Produce a Markdown report with one `##` section per category above.
**You MUST include all 10 sections.** If a category has no issues, write 'No issues found.'

Within each section use a Markdown table with columns:
| File | Line | Issue | Fix |
Keep each CELL to one sentence — no code blocks, no nested bullets. That limit applies to the width of a cell, NOT to the number of rows.
Give every occurrence its own row, and name the specific method, field or symbol it concerns. Do not merge several occurrences into one summary row such as 'several methods build SQL by interpolation' -- list each method separately. Do not end a section early because the pattern has been illustrated: a reader must be able to act on each row without going back to the source to find the other instances.
Thoroughness matters more than length here. You have ample output budget; a section with fifteen genuine rows is better than the same section trimmed to five.

Complete all 10 sections before adding any additional commentary.

---

## Source Files

{diff}