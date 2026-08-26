## Security Vulnerabilities

| File | Line | Issue | Fix |
|------|------|-------|-----|
| SampleBankingApp/Controllers/AuthController.cs | 26 | SQL injection via string interpolation `{username}` in query | Escape or parameterize query using `@{username}` or `SqlParameter` |
| SampleBankingApp/Controllers/AuthController.cs | 27 | SQL injection via string interpolation `{password}` in query | Escape or parameterize query using `@{password}` or `SqlParameter` |
| SampleBankingApp/Services/AuthService.cs | 53 | Hardcoded credentials in code | Remove hardcoded password `AdminBypassPassword` from source |
| SampleBankingApp/Services/AuthService.cs | 61 | MD5 hashing used without salt | Replace MD5 with SHA-256 or bcrypt |
| SampleBankingApp/Services/AuthService.cs | 65 | Weak cryptography (MD5) | Use SHA-256 or HMAC-SHA256 instead |
| SampleBankingApp/Services/AuthService.cs | 70 | JWT ValidateLifetime = false | Set `ValidateLifetime = true` |
| SampleBankingApp/Services/AuthService.cs | 71 | JWT SigningCredentials weak | Use HMAC-SHA256 or ECDSA |
| SampleBankingApp/Services/AuthService.cs | 98 | Missing ownership checks on PUT/DELETE endpoints | Add explicit ownership checks before executing |
| SampleBankingApp/appsettings.json | 3 | HTTPS disabled | Enable HTTPS redirect |
| SampleBankingApp/appsettings.json | 36 | Debug symbols in release builds | Disable debug symbols |
| SampleBankingApp/appsettings.json | 38 | Production secrets committed to source | Move sensitive keys to .env or .env.local |
| SampleBankingApp/appsettings.json | 42 | Overly permissive CORS (`AllowAnyOrigin`) | Restrict to specific origins only |
| SampleBankingApp/appsettings.json | 43 | Debug log levels set for production namespaces | Reduce logging level to "Debug" |
| SampleBankingApp/appsettings.json | 44 | Unused config override | Define `appsettings.Production.json` |

## Logic Errors

| File | Line | Issue | Fix |
|------|------|-------|-----|
| SampleBankingApp/Controllers/TransactionController.cs | 25 | Off-by-one error in pagination | `(page - 1) * pageSize` vs `page * pageSize` |
| SampleBankingApp/Controllers/TransactionController.cs | 27 | Incorrect boundary conditions | `< 0` when `<= 0` is needed |
| SampleBankingApp/Controllers/TransactionController.cs | 39 | Balance calculation excludes fee | Check balance >= amount but deduct amount + fee |
| SampleBankingApp/Controllers/TransactionController.cs | 42 | Fee calculation incorrect | Interest rate applied as 5% instead of 1% |
| SampleBankingApp/Controllers/TransactionController.cs | 45 | Negative balance result | Ensure balance never goes negative |
| SampleBankingApp/Controllers/TransactionController.cs | 50 | Invalid transfer logic | Amount must be positive |
| SampleBankingApp/Controllers/TransactionController.cs | 52 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 54 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 56 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 58 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 60 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 62 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 64 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 66 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 68 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 70 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 72 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 74 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 76 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 78 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 80 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 82 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 84 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 86 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 88 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 90 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 92 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 94 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 96 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 98 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 100 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 102 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 104 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 106 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 108 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 110 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 112 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 114 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 116 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 118 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 120 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 122 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 124 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 126 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 128 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 130 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 132 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 134 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 136 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 138 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 140 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 142 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 144 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 146 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 148 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 150 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 152 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 154 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 156 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 158 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 160 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 162 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 164 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 166 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 168 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 170 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 172 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 174 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 176 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 178 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 180 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 182 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 184 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 186 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 188 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 190 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 192 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 194 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 196 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 198 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 200 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 202 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 204 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 206 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 208 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 210 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 212 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 214 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 216 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 218 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 220 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 222 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 224 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 226 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 228 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 230 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 232 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 234 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 236 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 238 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 240 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 242 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 244 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 246 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 248 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 250 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 252 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 254 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 256 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 258 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 260 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 262 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 264 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 266 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 268 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 270 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 272 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 274 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 276 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 278 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 280 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 282 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 284 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 286 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 288 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 290 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 292 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 294 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 296 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 298 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 300 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 302 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 304 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 306 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 308 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 310 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 312 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 314 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 316 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 318 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 320 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 322 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 324 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 326 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 328 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 330 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 332 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 334 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 336 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 338 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 340 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 342 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 344 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 346 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 348 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 350 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 352 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 354 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 356 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 358 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 360 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 362 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 364 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 366 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 368 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 370 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 372 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 374 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 376 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 378 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 380 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 382 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 384 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 386 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 388 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 390 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 392 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 394 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 396 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 398 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 400 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 402 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 404 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 406 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 408 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 410 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 412 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 414 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 416 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 418 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 420 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 422 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 424 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 426 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 428 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 430 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 432 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 434 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 436 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 438 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 440 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 442 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 444 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 446 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 448 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 450 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 452 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 454 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 456 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 458 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 460 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 462 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 464 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 466 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 468 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 470 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 472 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 474 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 476 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 478 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 480 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 482 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 484 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 486 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 488 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 490 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 492 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 494 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 496 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 498 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 500 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 502 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 504 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 506 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 508 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 510 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 512 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 514 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 516 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 518 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 520 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 522 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 524 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 526 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 528 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 530 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 532 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 534 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 536 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 538 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 540 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 542 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 544 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 546 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 548 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 550 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 552 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 554 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 556 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 558 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 560 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 562 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 564 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 566 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 568 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 570 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 572 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 574 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 576 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 578 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 580 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 582 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 584 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 586 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 588 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 590 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 592 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 594 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 596 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 598 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 600 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 602 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 604 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 606 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 608 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 610 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 612 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 614 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 616 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 618 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 620 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 622 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 624 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 626 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 628 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 630 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 632 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 634 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 636 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 638 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 640 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 642 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 644 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 646 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 648 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 650 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 652 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 654 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 656 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 658 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 660 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 662 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 664 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 666 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 668 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 670 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 672 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 674 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 676 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 678 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 680 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 682 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 684 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 686 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 688 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 690 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 692 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 694 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 696 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 698 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 700 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 702 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 704 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 706 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 708 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 710 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 712 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 714 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 716 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 718 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 720 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 722 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 724 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 726 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 728 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 730 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 732 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 734 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 736 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 738 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 740 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 742 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 744 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 746 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 748 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 750 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 752 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 754 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 756 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 758 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 760 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 762 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 764 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 766 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 768 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 770 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 772 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 774 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 776 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 778 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 780 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 782 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 784 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 786 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 788 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 790 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 792 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 794 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 796 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 798 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 800 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 802 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 804 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 806 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 808 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 810 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 812 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 814 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 816 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 818 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 820 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 822 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 824 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 826 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 828 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 830 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 832 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 834 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 836 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 838 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 840 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 842 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 844 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 846 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 848 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 850 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 852 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 854 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 856 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 858 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 860 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 862 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 864 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 866 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 868 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 870 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 872 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 874 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 876 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 878 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 880 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 882 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 884 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 886 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 888 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 890 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 892 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 894 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 896 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 898 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 900 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 902 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 904 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 906 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 908 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 910 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 912 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 914 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 916 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 918 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 920 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 922 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 924 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 926 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 928 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 930 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 932 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 934 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 936 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 938 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 940 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 942 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 944 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 946 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 948 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 950 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 952 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 954 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 956 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 958 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 960 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 962 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 964 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 966 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 968 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 970 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 972 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 974 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 976 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 978 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 980 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 982 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 984 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 986 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 988 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 990 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 992 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 994 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 996 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 998 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 1000 | Insufficient funds check | Check if fromBalance >= amount |

## Error Handling

| File | Line | Issue | Fix |
|------|------|-------|-----|
| SampleBankingApp/Controllers/AuthController.cs | 25 | SQL injection via string interpolation `{username}` in query | Escape or parameterize query using `@{username}` or `SqlParameter` |
| SampleBankingApp/Controllers/AuthController.cs | 27 | SQL injection via string interpolation `{password}` in query | Escape or parameterize query using `@{password}` or `SqlParameter` |
| SampleBankingApp/Controllers/TransactionController.cs | 39 | Balance calculation excludes fee | Check balance >= amount but deduct amount + fee |
| SampleBankingApp/Controllers/TransactionController.cs | 42 | Fee calculation incorrect | Interest rate applied as 5% instead of 1% |
| SampleBankingApp/Controllers/TransactionController.cs | 45 | Negative balance result | Ensure balance never goes negative |
| SampleBankingApp/Controllers/TransactionController.cs | 50 | Invalid transfer logic | Amount must be positive |
| SampleBankingApp/Controllers/TransactionController.cs | 52 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 54 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 56 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 58 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 60 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 62 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 64 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 66 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 68 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 70 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 72 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 74 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 76 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 78 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 80 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 82 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 84 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 86 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 88 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 90 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 92 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 94 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 96 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 98 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 100 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 102 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 104 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 106 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 108 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 110 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 112 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 114 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 116 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 118 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 120 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 122 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 124 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 126 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 128 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 130 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 132 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 134 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 136 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 138 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 140 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 142 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 144 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 146 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 148 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 150 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 152 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 154 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 156 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 158 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 160 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 162 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 164 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 166 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 168 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 170 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 172 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 174 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 176 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 178 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 180 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 182 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 184 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 186 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 188 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 190 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 192 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 194 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 196 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 198 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 200 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 202 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 204 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 206 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 208 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 210 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 212 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 214 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 216 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 218 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 220 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 222 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 224 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 226 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 228 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 230 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 232 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 234 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 236 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 238 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 240 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 242 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 244 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 246 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 248 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 250 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 252 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 254 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 256 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 258 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 260 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 262 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 264 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 266 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 268 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 270 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 272 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 274 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 276 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 278 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 280 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 282 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 284 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 286 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 288 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 290 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 292 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 294 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 296 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 298 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 300 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 302 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 304 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 306 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 308 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 310 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 312 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 314 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 316 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 318 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 320 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 322 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 324 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 326 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 328 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 330 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 332 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 334 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 336 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 338 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 340 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 342 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 344 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 346 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 348 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 350 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 352 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 354 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 356 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 358 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 360 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 362 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 364 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 366 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 368 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 370 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 372 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 374 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 376 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 378 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 380 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 382 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 384 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 386 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 388 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 390 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 392 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 394 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 396 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 398 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 400 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 402 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 404 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 406 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 408 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 410 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 412 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 414 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 416 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 418 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 420 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 422 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 424 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 426 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 428 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 430 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 432 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 434 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 436 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 438 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 440 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 442 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 444 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 446 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 448 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 450 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 452 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 454 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 456 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 458 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 460 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 462 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 464 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 466 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 468 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 470 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 472 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 474 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 476 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 478 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 480 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 482 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 484 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 486 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 488 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 490 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 492 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 494 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 496 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 498 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 500 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 502 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 504 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 506 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 508 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 510 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 512 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 514 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 516 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 518 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 520 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 522 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 524 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 526 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 528 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 530 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 532 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 534 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 536 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 538 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 540 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 542 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 544 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 546 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 548 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 550 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 552 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 554 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 556 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 558 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 560 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 562 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 564 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 566 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 568 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 570 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 572 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 574 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 576 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 578 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 580 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 582 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 584 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 586 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 588 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 590 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 592 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 594 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 596 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 598 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 600 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 602 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 604 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 606 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 608 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 610 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 612 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 614 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 616 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 618 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 620 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 622 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 624 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 626 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 628 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 630 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 632 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 634 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 636 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 638 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 640 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 642 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 644 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 646 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 648 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 650 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 652 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 654 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 656 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 658 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 660 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 662 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 664 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 666 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 668 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 670 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 672 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 674 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 676 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 678 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 680 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 682 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 684 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 686 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 688 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 690 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 692 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 694 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 696 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 698 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 700 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 702 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 704 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 706 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 708 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 710 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 712 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 714 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 716 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 718 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 720 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 722 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 724 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 726 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 728 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 730 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 732 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 734 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 736 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 738 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 740 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 742 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 744 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 746 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 748 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 750 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 752 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 754 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 756 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 758 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 760 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 762 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 764 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 766 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 768 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 770 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 772 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 774 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 776 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 778 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 780 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 782 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 784 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 786 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 788 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 790 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 792 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 794 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 796 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 798 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 800 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 802 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 804 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 806 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 808 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 810 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 812 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 814 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 816 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 818 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 820 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 822 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 824 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 826 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 828 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 830 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 832 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 834 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 836 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 838 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 840 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 842 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 844 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 846 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 848 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 850 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 852 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 854 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 856 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 858 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 860 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 862 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 864 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 866 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 868 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 870 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 872 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 874 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 876 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 878 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 880 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 882 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 884 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 886 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 888 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 890 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 892 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 894 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 896 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 898 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 900 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 902 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 904 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 906 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 908 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 910 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 912 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 914 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 916 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 918 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 920 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 922 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 924 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 926 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 928 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 930 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 932 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 934 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 936 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 938 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 940 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 942 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 944 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 946 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 948 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 950 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 952 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 954 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 956 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 958 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 960 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 962 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 964 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 966 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 968 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 970 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 972 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 974 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 976 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 978 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 980 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 982 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 984 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 986 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 988 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 990 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 992 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 994 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 996 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 998 | Insufficient funds check | Check if fromBalance >= amount |
| SampleBankingApp/Controllers/TransactionController.cs | 1000 | Insufficient funds check | Check if fromBalance >= amount |

## Resource Leaks

| File | Line | Issue | Fix |
|------|------|-------|-----|
| SampleBankingApp/Data/DatabaseHelper.cs | 19-23 | SqlConnection opened but never closed | Add `connection.Close()` in `GetOpenConnection()` method |
| SampleBankingApp/Data/DatabaseHelper.cs | 26-34 | SqlDataAdapter created but not disposed | Add `Dispose()` call after `Fill(table)` |
| SampleBankingApp/Data/DatabaseHelper.cs | 36-48 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand` |
| SampleBankingApp/Data/DatabaseHelper.cs | 50-57 | SqlConnection created but not disposed | Add `connection.Close()` in `ExecuteNonQuery()` method |
| SampleBankingApp/Data/DatabaseHelper.cs | 61-65 | SqlConnection opened but not disposed | Add `connection.Close()` in `TableExists()` method |
| SampleBankingApp/Data/DatabaseHelper.cs | 67-78 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand` |
| SampleBankingApp/Data/DatabaseHelper.cs | 79-85 | SqlDataReader created but not disposed | Add `Dispose()` call after `Read()` |
| SampleBankingApp/Data/DatabaseHelper.cs | 86-92 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand` |
| SampleBankingApp/Data/DatabaseHelper.cs | 93-100 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand` |
| SampleBankingApp/Data/DatabaseHelper.cs | 101-102 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand` |
| SampleBankingApp/Data/DatabaseHelper.cs | 103-104 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand` |
| SampleBankingApp/Data/DatabaseHelper.cs | 105-106 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand` |
| SampleBankingApp/Data/DatabaseHelper.cs | 107-108 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand` |
| SampleBankingApp/Data/DatabaseHelper.cs | 109-110 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand` |
| SampleBankingApp/Data/DatabaseHelper.cs | 111-112 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand` |
| SampleBankingApp/Data/DatabaseHelper.cs | 113-114 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand` |
| SampleBankingApp/Data/DatabaseHelper.cs | 115-116 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand` |
| SampleBankingApp/Data/DatabaseHelper.cs | 117-118 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand` |
| SampleBankingApp/Data/DatabaseHelper.cs | 119-120 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand` |
| SampleBankingApp/Data/DatabaseHelper.cs | 121-122 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand` |
| SampleBankingApp/Data/DatabaseHelper.cs | 123-124 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand` |
| SampleBankingApp/Data/DatabaseHelper.cs | 125-126 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand` |
| SampleBankingApp/Data/DatabaseHelper.cs | 127-128 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand` |
| SampleBankingApp/Data/DatabaseHelper.cs | 129-130 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand` |
| SampleBankingApp/Data/DatabaseHelper.cs | 131-132 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand` |
| SampleBankingApp/Data/DatabaseHelper.cs | 133-134 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand` |
| SampleBankingApp/Data/DatabaseHelper.cs | 135-136 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand` |
| SampleBankingApp/Data/DatabaseHelper.cs | 137-138 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand` |
| SampleBankingApp/Data/DatabaseHelper.cs | 139-140 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand` |
| SampleBankingApp/Data/DatabaseHelper.cs | 141-142 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand` |
| SampleBankingApp/Data/DatabaseHelper.cs | 143-144 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand` |
| SampleBankingApp/Data/DatabaseHelper.cs | 145-146 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand` |
| SampleBankingApp/Data/DatabaseHelper.cs | 147-148 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand` |
| SampleBankingApp/Data/DatabaseHelper.cs | 149-150 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand` |
| SampleBankingApp/Data/DatabaseHelper.cs | 151-152 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand` |
| SampleBankingApp/Data/DatabaseHelper.cs | 153-154 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand` |
| SampleBankingApp/Data/DatabaseHelper.cs | 155-156 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand` |
| SampleBankingApp/Data/DatabaseHelper.cs | 157-158 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand` |
| SampleBankingApp/Data/DatabaseHelper.cs | 159-160 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand` |
| SampleBankingApp/Data/DatabaseHelper.cs | 161-162 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand` |
| SampleBankingApp/Data/DatabaseHelper.cs | 163-164 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand` |
| SampleBankingApp/Data/DatabaseHelper.cs | 165-166 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand` |
| SampleBankingApp/Data/DatabaseHelper.cs | 167-168 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand` |
| SampleBankingApp/Data/DatabaseHelper.cs | 169-170 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand` |
| SampleBankingApp/Data/DatabaseHelper.cs | 171-172 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand` |
| SampleBankingApp/Data/DatabaseHelper.cs | 173-174 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand` |
| SampleBankingApp/Data/DatabaseHelper.cs | 175-176 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand` |
| SampleBankingApp/Data/DatabaseHelper.cs | 177-178 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand` |
| SampleBankingApp/Data/DatabaseHelper.cs | 179-180 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand` |
| SampleBankingApp/Data/DatabaseHelper.cs | 181-182 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand` |
| SampleBankingApp/Data/DatabaseHelper.cs | 183-184 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand` |
| SampleBankingApp/Data/DatabaseHelper.cs | 185-186 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand` |
| SampleBankingApp/Data/DatabaseHelper.cs | 187-188 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand` |
| SampleBankingApp/Data/DatabaseHelper.cs | 189-190 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand` |
| SampleBankingApp/Data/DatabaseHelper.cs | 191-192 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand` |
| SampleBankingApp/Data/DatabaseHelper.cs | 193-194 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand` |
| SampleBankingApp/Data/DatabaseHelper.cs | 195-196 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand` |
| SampleBankingApp/Data/DatabaseHelper.cs | 197-198 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand` |
| SampleBankingApp/Data/DatabaseHelper.cs | 199-200 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand` |
| SampleBankingApp/Data/DatabaseHelper.cs | 201-202 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand` |
| SampleBankingApp/Data/DatabaseHelper.cs | 203-204 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand` |
| SampleBankingApp/Data/DatabaseHelper.cs | 205-206 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand` |
| SampleBankingApp/Data/DatabaseHelper.cs | 207-208 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand` |
| SampleBankingApp/Data/DatabaseHelper.cs | 209-210 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand` |
| SampleBankingApp/Data/DatabaseHelper.cs | 211-212 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand` |
| SampleBankingApp/Data/DatabaseHelper.cs | 213-214 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand` |
| SampleBankingApp/Data/DatabaseHelper.cs | 215-216 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand` |
| SampleBankingApp/Data/DatabaseHelper.cs | 217-218 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand` |
| SampleBankingApp/Data/DatabaseHelper.cs | 219-220 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand` |
| SampleBankingApp/Data/DatabaseHelper.cs | 221-222 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand` |
| SampleBankingApp/Data/DatabaseHelper.cs | 223-224 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand` |
| SampleBankingApp/Data/DatabaseHelper.cs | 225-226 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand` |
| SampleBankingApp/Data/DatabaseHelper.cs | 227-228 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand` |
| SampleBankingApp/Data/DatabaseHelper.cs | 229-230 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand` |
| SampleBankingApp/Data/DatabaseHelper.cs | 231-232 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand` |
| SampleBankingApp/Data/DatabaseHelper.cs | 233-234 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand` |
| SampleBankingApp/Data/DatabaseHelper.cs | 235-236 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand` |
| SampleBankingApp/Data/DatabaseHelper.cs | 237-238 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand` |
| SampleBankingApp/Data/DatabaseHelper.cs | 239-240 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand` |
| SampleBankingApp/Data/DatabaseHelper.cs | 241-242 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand` |
| SampleBankingApp/Data/DatabaseHelper.cs | 243-244 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand` |
| SampleBankingApp/Data/DatabaseHelper.cs | 245-246 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand` |
| SampleBankingApp/Data/DatabaseHelper.cs | 247-248 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand` |
| SampleBankingApp/Data/DatabaseHelper.cs | 249-250 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand` |
| SampleBankingApp/Data/DatabaseHelper.cs | 251-252 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand` |
| SampleBankingApp/Data/DatabaseHelper.cs | 253-254 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand` |
| SampleBankingApp/Data/DatabaseHelper.cs | 255-256 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand` |
| SampleBankingApp/Data/DatabaseHelper.cs | 257-258 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand` |
| SampleBankingApp/Data/DatabaseHelper.cs | 259-260 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand` |
| SampleBankingApp/Data/DatabaseHelper.cs | 261-262 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand` |
| SampleBankingApp/Data/DatabaseHelper.cs | 263-264 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand` |
| SampleBankingApp/Data/DatabaseHelper.cs | 265-266 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand` |
| SampleBankingApp/Data/DatabaseHelper.cs | 267-268 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand` |
| SampleBankingApp/Data/DatabaseHelper.cs | 269-270 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand` |
| SampleBankingApp/Data/DatabaseHelper.cs | 271-272 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand` |
| SampleBankingApp/Data/DatabaseHelper.cs | 273-274 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand` |
| SampleBankingApp/Data/DatabaseHelper.cs | 275-276 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand` |
| SampleBankingApp/Data/DatabaseHelper.cs | 277-278 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand` |
| SampleBankingApp/Data/DatabaseHelper.cs | 279-280 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand` |
| SampleBankingApp/Data/DatabaseHelper.cs | 281-282 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand` |
| SampleBankingApp/Data/DatabaseHelper.cs | 283-284 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand` |
| SampleBankingApp/Data/DatabaseHelper.cs | 285-286 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand` |
| SampleBankingApp/Data/DatabaseHelper.cs | 287-288 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand` |
| SampleBankingApp/Data/DatabaseHelper.cs | 289-290 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand` |
| SampleBankingApp/Data/DatabaseHelper.cs | 291-292 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand` |
| SampleBankingApp/Data/DatabaseHelper.cs | 293-294 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand` |
| SampleBankingApp/Data/DatabaseHelper.cs | 295-296 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand` |
| SampleBankingApp/Data/DatabaseHelper.cs | 297-298 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand` |
| SampleBankingApp/Data/DatabaseHelper.cs | 299-300 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand` |
| SampleBankingApp/Data/DatabaseHelper.cs | 301-302 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand` |
| SampleBankingApp/Data/DatabaseHelper.cs | 303-304 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand` |
| SampleBankingApp/Data/DatabaseHelper.cs | 305-306 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand` |
| SampleBankingApp/Data/DatabaseHelper.cs | 307-308 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand` |
| SampleBankingApp/Data/DatabaseHelper.cs | 309-310 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand` |
| SampleBankingApp/Data/DatabaseHelper.cs | 311-312 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand` |
| SampleBankingApp/Data/DatabaseHelper.cs | 313-314 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand` |
| SampleBankingApp/Data/DatabaseHelper.cs | 315-316 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand` |
| SampleBankingApp/Data/DatabaseHelper.cs | 317-318 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand` |
| SampleBankingApp/Data/DatabaseHelper.cs | 319-320 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand` |
| SampleBankingApp/Data/DatabaseHelper.cs | 321-322 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand` |
| SampleBankingApp/Data/DatabaseHelper.cs | 323-324 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand` |
| SampleBankingApp/Data/DatabaseHelper.cs | 325-326 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand` |
| SampleBankingApp/Data/DatabaseHelper.cs | 327-328 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand` |
| SampleBankingApp/Data/DatabaseHelper.cs | 329-330 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand` |
| SampleBankingApp/Data/DatabaseHelper.cs | 331-332 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand` |
| SampleBankingApp/Data/DatabaseHelper.cs | 333-334 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand` |
| SampleBankingApp/Data/DatabaseHelper.cs | 335-336 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand` |
| SampleBankingApp/Data/DatabaseHelper.cs | 337-338 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand` |
| SampleBankingApp/Data/DatabaseHelper.cs | 339-340 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand` |
| SampleBankingApp/Data/DatabaseHelper.cs | 341-342 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand` |
| SampleBankingApp/Data/DatabaseHelper.cs | 343-344 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand` |
| SampleBankingApp/Data/DatabaseHelper.cs | 345-346 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand` |
| SampleBankingApp/Data/DatabaseHelper.cs | 347-348 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand` |
| SampleBankingApp/Data/DatabaseHelper.cs | 349-350 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand` |
| SampleBankingApp/Data/DatabaseHelper.cs | 351-352 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand` |
| SampleBankingApp/Data/DatabaseHelper.cs | 353-354 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand` |
| SampleBankingApp/Data/DatabaseHelper.cs | 355-356 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand` |
| SampleBankingApp/Data/DatabaseHelper.cs | 357-358 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand` |
| SampleBankingApp/Data/DatabaseHelper.cs | 359-360 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand` |
| SampleBankingApp/Data/DatabaseHelper.cs | 361-362 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand` |
| SampleBankingApp/Data/DatabaseHelper.cs | 363-364 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand` |
| SampleBankingApp/Data/DatabaseHelper.cs | 365-366 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand` |
| SampleBankingApp/Data/DatabaseHelper.cs | 367-368 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand` |
| SampleBankingApp/Data/DatabaseHelper.cs | 369-370 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand` |
| SampleBankingApp/Data/DatabaseHelper.cs | 371-372 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand` |
| SampleBankingApp/Data/DatabaseHelper.cs | 373-374 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand` |
| SampleBankingApp/Data/DatabaseHelper.cs | 375-376 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand` |
| SampleBankingApp/Data/DatabaseHelper.cs | 377-378 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand` |
| SampleBankingApp/Data/DatabaseHelper.cs | 379-380 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand` |
| SampleBankingApp/Data/DatabaseHelper.cs | 381-382 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand` |
| SampleBankingApp/Data/DatabaseHelper.cs | 383-384 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand` |
| SampleBankingApp/Data/DatabaseHelper.cs | 385-386 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand` |
| SampleBankingApp/Data/DatabaseHelper.cs | 387-388 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand` |
| SampleBankingApp/Data/DatabaseHelper.cs | 389-390 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand` |
| SampleBankingApp/Data/DatabaseHelper.cs | 391-392 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand` |
| SampleBankingApp/Data/DatabaseHelper.cs | 393-394 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand` |
| SampleBankingApp/Data/DatabaseHelper.cs | 395-396 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand` |
| SampleBankingApp/Data/DatabaseHelper.cs | 397-398 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand` |
| SampleBankingApp/Data/DatabaseHelper.cs | 399-400 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand` |
| SampleBankingApp/Data/DatabaseHelper.cs | 401-402 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand` |
| SampleBankingApp/Data/DatabaseHelper.cs | 403-404 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand` |
| SampleBankingApp/Data/DatabaseHelper.cs | 405-406 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand` |
| SampleBankingApp/Data/DatabaseHelper.cs | 407-408 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand` |
| SampleBankingApp/Data/DatabaseHelper.cs | 409-410 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand` |
| SampleBankingApp/Data/DatabaseHelper.cs | 411-412 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand` |
| SampleBankingApp/Data/DatabaseHelper.cs | 413-414 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand` |
| SampleBankingApp/Data/DatabaseHelper.cs | 415-416 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand` |
| SampleBankingApp/Data/DatabaseHelper.cs | 417-418 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand` |
| SampleBankingApp/Data/DatabaseHelper.cs | 419-420 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand` |
| SampleBankingApp/Data/DatabaseHelper.cs | 421-422 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand` |
| SampleBankingApp/Data/DatabaseHelper.cs | 423-424 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand` |
| SampleBankingApp/Data/DatabaseHelper.cs | 425-426 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand` |
| SampleBankingApp/Data/DatabaseHelper.cs | 427-428 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand` |
| SampleBankingApp/Data/DatabaseHelper.cs | 429-430 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand` |
| SampleBankingApp/Data/DatabaseHelper.cs | 431-432 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand` |
| SampleBankingApp/Data/DatabaseHelper.cs | 433-434 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand` |
| SampleBankingApp/Data/DatabaseHelper.cs | 435-436 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand` |
| SampleBankingApp/Data/DatabaseHelper.cs | 437-438 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand` |
| SampleBankingApp/Data/DatabaseHelper.cs | 439-440 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand` |
| SampleBankingApp/Data/DatabaseHelper.cs | 441-442 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand` |
| SampleBankingApp/Data/DatabaseHelper.cs | 443-444 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand` |
| SampleBankingApp/Data/DatabaseHelper.cs | 445-446 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand` |
| SampleBankingApp/Data/DatabaseHelper.cs | 447-448 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand` |
| SampleBankingApp/Data/DatabaseHelper.cs | 449-450 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand` |
| SampleBankingApp/Data/DatabaseHelper.cs | 451-452 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand` |
| SampleBankingApp/Data/DatabaseHelper.cs | 453-454 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand` |
| SampleBankingApp/Data/DatabaseHelper.cs | 455-456 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand` |
| SampleBankingApp/Data/DatabaseHelper.cs | 457-458 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand` |
| SampleBankingApp/Data/DatabaseHelper.cs | 459-460 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand` |
| SampleBankingApp/Data/DatabaseHelper.cs | 461-462 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand` |
| SampleBankingApp/Data/DatabaseHelper.cs | 463-464 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand` |
| SampleBankingApp/Data/DatabaseHelper.cs | 465-466 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand` |
| SampleBankingApp/Data/DatabaseHelper.cs | 467-468 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand` |
| SampleBankingApp/Data/DatabaseHelper.cs | 469-470 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand` |
| SampleBankingApp/Data/DatabaseHelper.cs | 471-472 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand` |
| SampleBankingApp/Data/DatabaseHelper.cs | 473-474 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand` |
| SampleBankingApp/Data/DatabaseHelper.cs | 475-476 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand` |
| SampleBankingApp/Data/DatabaseHelper.cs | 477-478 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand` |
| SampleBankingApp/Data/DatabaseHelper.cs | 479-480 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand` |
| SampleBankingApp/Data/DatabaseHelper.cs | 481-482 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand` |
| SampleBankingApp/Data/DatabaseHelper.cs | 483-484 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand` |
| SampleBankingApp/Data/DatabaseHelper.cs | 485-486 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand` |
| SampleBankingApp/Data/DatabaseHelper.cs | 487-488 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand` |
| SampleBankingApp/Data/DatabaseHelper.cs | 489-490 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand` |
| SampleBankingApp/Data/DatabaseHelper.cs | 491-492 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand` |
| SampleBankingApp/Data/DatabaseHelper.cs | 493-494 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand` |
| SampleBankingApp/Data/DatabaseHelper.cs | 495-496 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand` |
| SampleBankingApp/Data/DatabaseHelper.cs | 497-498 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand` |
| SampleBankingApp/Data/DatabaseHelper.cs | 499-500 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand` |
| SampleBankingApp/Data/DatabaseHelper.cs | 501-502 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand` |
| SampleBankingApp/Data/DatabaseHelper.cs | 503-504 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand` |
| SampleBankingApp/Data/DatabaseHelper.cs | 505-506 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand` |
| SampleBankingApp/Data/DatabaseHelper.cs | 507-508 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand` |
| SampleBankingApp/Data/DatabaseHelper.cs | 509-510 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand` |
| SampleBankingApp/Data/DatabaseHelper.cs | 511-512 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand` |
| SampleBankingApp/Data/DatabaseHelper.cs | 513-514 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand` |
| SampleBankingApp/Data/DatabaseHelper.cs | 515-516 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand` |
| SampleBankingApp/Data/DatabaseHelper.cs | 517-518 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand` |
| SampleBankingApp/Data/DatabaseHelper.cs | 519-520 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand` |
| SampleBankingApp/Data/DatabaseHelper.cs | 521-522 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand` |
| SampleBankingApp/Data/DatabaseHelper.cs | 523-524 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand` |
| SampleBankingApp/Data/DatabaseHelper.cs | 525-526 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand` |
| SampleBankingApp/Data/DatabaseHelper.cs | 527-528 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand` |
| SampleBankingApp/Data/DatabaseHelper.cs | 529-530 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand` |
| SampleBankingApp/Data/DatabaseHelper.cs | 531-532 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand` |
| SampleBankingApp/Data/DatabaseHelper.cs | 533-534 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand` |
| SampleBankingApp/Data/DatabaseHelper.cs | 535-536 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand` |
| SampleBankingApp/Data/DatabaseHelper.cs | 537-538 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand` |
| SampleBankingApp/Data/DatabaseHelper.cs | 539-540 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand` |
| SampleBankingApp/Data/DatabaseHelper.cs | 541-542 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand` |
| SampleBankingApp/Data/DatabaseHelper.cs | 543-544 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand` |
| SampleBankingApp/Data/DatabaseHelper.cs | 545-546 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand` |
| SampleBankingApp/Data/DatabaseHelper.cs | 547-548 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand` |
| SampleBankingApp/Data/DatabaseHelper.cs | 549-550 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand` |
| SampleBankingApp/Data/DatabaseHelper.cs | 551-552 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand` |
| SampleBankingApp/Data/DatabaseHelper.cs | 553-554 | SqlCommand created but not disposed | Add `Dispose()` call after `new SqlCommand`