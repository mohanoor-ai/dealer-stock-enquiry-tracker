# Production-readiness gates

## 1. Connected local release
Persistent stock/enquiry/task workflow, validation, audit events, atomic stale-edit rejection, archive/restore, exports and validated backup/conversion. Preserve original data. Verify SQLite and PostgreSQL, React, real HTTP and browser behavior. The local edition is a single-user localhost workspace.

## 2. Controlled hosted pilot
Cloud Run + Supabase PostgreSQL/Auth. Verify trusted roles, denied viewer writes, session refresh/logout, password recovery administration, RLS/Data API grants, TLS, migrations, separate secrets, app identity, quotas and cold-start behavior. Use an isolated fictional database for anonymous reads. Hosted pilot is not automatic authorisation for real customer records.

## 3. Recovery and delivery
Protect production environment approval. Require all release checks on the exact commit. Retain immutable image and migration versions. Exercise safe application rollback and restore into a disposable database. Define a proposed pilot recovery objective (for example restore within four hours with at most 24 hours of loss) and approve it against actual backup capability before relying on it.

## 4. Operations and security
Choose an incident owner and response path; demonstrate alert → redacted evidence → diagnosis → approved action → recovery check. Record scan dispositions, dependency-update ownership, secrets rotation and audit retention. Exercise provider outage/AI quota failure. Define latency/availability/load targets against measured demand; a free allowance does not supply an uptime guarantee.

## 5. Real production approval
Recheck regional processing, privacy/retention/export/deletion obligations, access review, recovery-account ownership, backup custody and contracts. Test capacity/concurrency and abuse controls. Confirm provider limits, support and the cost of meeting the approved targets. Record acceptance of residual risks. Supabase Storage upload scanning, media access policies, multi-dealership isolation and external marketplace integrations require separate implementation and approval.

No gate passes because its configuration file exists. The release report and pull request record actual checks; provider accounts and live operations are pending external validation.
