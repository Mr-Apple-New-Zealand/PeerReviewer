# Text attachment fixtures

Logs and telemetry exports for the ticket-analyst benchmark. A case references one
of these files from a ticket's `attachments` entry with a text `kind` (`log`,
`text`, `csv` or `json`), and the harness inlines the contents into the rendered
ticket:

```json
{"name": "payments-api-prod.log", "size": "26 KB", "kind": "log",
 "file": "payments_api_prod.log"}
```

Unlike an image attachment these need no vision capability, so every model under
test can be scored on them. Changing a file here changes the SHA of every case
that attaches it, so runs before and after an edit are not reported as comparable.

| File | Used by | What it carries |
|---|---|---|
| `payments_api_prod.log` | C14 | 48-hour dump with four distinct faults (Dapr 403, SQL 245, SQL timeout, validation exception), a credential leak, one container restart, and a bed of routine startup warnings and heartbeats |
| `notifications_api_prod.log` | C15 | SMTP 535 authentication rejections under the benign startup warnings the reporter blames; a fixed-interval retry loop and a growing outbox backlog |
| `statements_api_before.log`, `statements_api_after.log` | C16 | The same clock window either side of a release: one query 100x slower, two others unchanged |
| `sentry_event_batch_actions.json` | C17 | A full Sentry event: a four-hour idle gap, then every request 401, then a cascade of undefined-property errors; a UAT host tagged Production, a stale transaction name, null release and missing source maps |
| `sentry_issue_digest.json` | C18 | Eight Sentry issues over a week: five sharing one cause, a browser-extension issue with the second-highest event count and one user, a low-count issue with the most users, and a resolved issue that has regressed |

## Provenance and anonymisation

These files are derived from a real production Kubernetes pod log and a real
production Sentry event. They keep the shape of the originals — Serilog output
format, ASP.NET Core startup sequence, Dapr service invocation, EF Core and Dapper
stack traces, SQL Server error numbers, MediatR request and transaction lines,
timing distributions, and on the Sentry side the full field set, breadcrumb
structure, SDK metadata, grouping fields and relative timings to the millisecond —
because that shape is what the cases test. Everything that identified the source
has been replaced:

- **Business domain.** The originals came from a warehouse system. Every service,
  handler, controller, command, query, DTO, route, API endpoint, table and
  namespace was renamed into the SampleBankingApp domain used by the rest of the
  benchmark.
- **Infrastructure.** Company domain names, pod names, namespaces, NATS subjects,
  Dapr app-ids, SQL host names and web host names replaced with `example.com` /
  `.internal` equivalents.
- **People and location.** Real user accounts replaced with the benchmark's
  fictional cast at `example.com`. The Sentry event's user geography was reduced
  from city and region level to country.
- **Identifiers and keys.** Barcode-style references, record ids, GUIDs, client
  connection ids, master-data codes, record timestamps, Sentry event and trace
  ids, grouping hashes, bundle content hashes and DSN public keys all
  regenerated. The base64 grouping-enhancements blob was dropped.
- **Credentials.** The connection string in `payments_api_prod.log` is invented.
  No real secret has ever been in these files.
- **Dates.** The Sentry event was rebased from its original date to 2026-09-12,
  so it sits before the benchmark's fixed "today" of 2026-09-15. Relative offsets
  within the session, including the four-hour idle gap, are unchanged.

Some content is deliberately added rather than derived, to give the cases more to
test: the credential-bearing DBG line, the container restart, the client-aborted
request, the 404, the SMTP failures, the outbox backlog, the before/after timing
pairs, and the whole of `sentry_issue_digest.json`. The originals are not in this
repository and should not be added to it.

`sentry_event_batch_actions.json` was trimmed before being committed: the
`raw_stacktrace` array, which duplicated `stacktrace.frames`, was removed, the
repetitive rxjs frames were collapsed behind a marker frame, and low-value
pre-gap UI breadcrumbs were dropped. Every XHR breadcrumb, the token refresh and
the whole post-gap cascade are intact, and the ticket in C17 says support trimmed
the file, so the model is told the export is not complete.
