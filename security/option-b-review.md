# Option B implementation review

Controls: server validation/bounds, parameterised SQLAlchemy, transactional revision matching, trusted Supabase app_metadata roles, no service-role key in browser, access tokens in memory, refresh cookie HttpOnly/Secure in hosted mode, Origin checks for cookie-auth routes, login and AI database quotas, hosted mode rejects local auth/SQLite, sample-only anonymous reads explicitly configured, RLS/revoked Data API grants in the PostgreSQL migration, no raw customer inputs in operational logs, server-rendered AI facts, explicit backup/conversion.

Limits to verify before real production: live session/recovery lifecycle, refresh rotation and expiry, distributed abuse behavior, actual Supabase grants/runtime role, HTTPS proxy configuration, provider privacy/terms, account recovery, export retention, load/performance, observability incident exercise and recovery drill. No multi-tenant isolation or media upload path is implemented. A read-only MCP credential must be supplied independently of the application runtime credential.

The JavaScript installer audited its installed dependency set and reported no findings during local preparation; that is not a full application audit. Deterministic secret/dependency/container scans and their actual output are required before a production claim. The private-file guard is a filename policy, not a secret scanner.
