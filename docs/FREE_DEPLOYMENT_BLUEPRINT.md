> Current implementation: see [Option B](OPTION_B.md) and [implementation status](IMPLEMENTATION_STATUS.md). The original notes below are retained as historical design context.

# Dealer Desk: free deployment blueprint
Status: design, not a tested deployment. Reviewed 14 October 2026.

## Decision
Build React and serve its compiled assets from FastAPI in one Docker image. Deploy that image to a Render Free web service. Store hosted data in Neon Free PostgreSQL. Optional listing drafts use Groq through the backend. Use the same image locally with PostgreSQL in Docker Compose; support SQLite for the lightweight offline edition.

One browser origin simplifies secure cookies and avoids cross-site login problems. Keep provider calls in small functions so hosts and AI providers can change without rewriting business logic.

Render Free sleeps after 15 minutes idle, has ephemeral disk and no production availability guarantee. It is a public educational pilot, not an always-on dealership service. Do not store hosted SQLite, uploads or backups on its disk. Do not use Render Free Postgres: it expires after 30 days. No automatic paid upgrades.

## Free services
- Website/API/TLS/subdomain: Render Free; 750 instance hours per workspace per month, shared by services. Account bandwidth/build limits also apply.
- Database: Neon Free. Current documentation lists 1 GB storage/project, 100 CU-hours/project, 5 GB outbound transfer/project and scale-to-zero after five minutes. No uptime SLA. Check quotas before launch.
- AI: Groq Free, optional and model-dependent quotas. Choose an available model during setup, rather than hard-coding a model that may be retired.
- Source and checks: public GitHub repository and standard GitHub-hosted Actions runners, subject to GitHub policies.
- Local AI: optional Ollama, after downloading a suitable model. Hardware capacity determines speed. Default offline edition works with AI disabled.
- Monitoring: structured application logs, health checks and provider dashboards initially. Full course telemetry stack runs as an optional local Compose profile rather than consuming limited hosted resources.
- Domain: provider subdomain. A custom domain is optional and not included in the zero-cost promise.

Sources: https://render.com/docs/free ; https://neon.com/docs/introduction/plans ; https://console.groq.com/docs/rate-limits

## Features to finish
1. Persistent vehicle stock, historical educational sample import, filters, archive and status changes.
2. Enquiries linked to stock, follow-up tasks and dashboard counts.
3. Per-record revisions: two users editing the same record get a clear conflict instead of silently overwriting.
4. Login, operator/viewer permissions, session expiry and audit events.
5. Optional AI listing draft from approved vehicle facts only; human review before saving.
6. Safe read-only MCP tools and a bounded incident assistant as separate optional components.
7. Private learning companion: module lessons, how-tos, exercises, answers and learning-in-public drafts. Never publish private notes with the product.

## Ordered implementation and acceptance gates
### 1. Complete the application
Implement the documented v2 API with SQLAlchemy transactions, Alembic migrations, pagination and revision checks. Connect React to live data. Keep the prototype explicitly separate.
Pass: create vehicle, enquiry and task; restart app; all records remain; concurrent stale update returns 409. Run against SQLite and PostgreSQL.

### 2. Add security
Use individual users with Argon2 password hashes and server-side sessions stored in the database. Secure HttpOnly SameSite cookies on hosted HTTPS; CSRF checks on writes; login throttling; role checks on every route. No public signup initially. Provision initial admin through a one-time local command against the database; no default password or public bootstrap endpoint.
Separate public sample-only demo from private operator data. Public demo is read-only initially.
Pass: unauthenticated and viewer writes denied; session expires; CSRF rejected; secrets and customer messages absent from logs.

### 3. Add optional AI
A small provider adapter accepts approved facts and returns a draft. Backend only holds API keys. Enforce input/output limits, timeout, daily per-user quota and a shared database quota. Return a clear unavailable response on 429 or provider failure; stock workflows remain usable. Never send customer details. Treat model output as untrusted; it must not execute tools, SQL or HTML.
Pass: provider mocked in CI; timeout, quota and invented fact cases checked; one real call verified separately with an account key.

### 4. Package and verify
Multi-stage Docker build: Node builds React, Python runs API and serves static files. Pin dependencies with existing lockfiles. Non-root runtime; expose PORT; separate liveness and database readiness endpoints. Run database migrations once per release before traffic, with a database migration lock if launch-time migration is required on the free host.
Compose: app plus persistent PostgreSQL volume, optional local telemetry and Ollama profiles.
Pass: clean machine can start with one documented command, visit printed localhost/LAN URL, and complete the stock-to-follow-up journey. Offline run requires downloaded images/dependencies; include an offline preparation command.

### 5. CI and release
Backend tests, frontend tests/build, PostgreSQL integration tests and Playwright user journey must pass before deploy. Pin third-party Actions to reviewed commit SHAs. Build release ZIP and Docker image from the same tagged commit. Deployment occurs only after checks pass; disable an independent deploy-on-push path that could bypass checks.
Pass: failed test prevents deployment. Release records commit, migrations and checks. Rollback guide covers image rollback and database compatibility; do not automatically reverse data migrations.

### 6. Free cloud pilot
Create Neon database in a nearby region. Set database URL and session secrets in Render settings, never git. Use pooled database connection for app and direct connection for migrations/backup. Configure a small connection pool and TLS. Deploy the verified container; no persistent Render disk.
Pass: HTTPS, login, CRUD, persistence across redeploy, quota behavior, clean logs and a second-device check. Display useful retry feedback after idle startup.

### 7. Recovery and submission
Provide a local pg_dump backup script and restore instructions. Store private backups outside git; test restoring to a temporary database. Export current user data before deleting or changing a service. Include architecture, module evidence, test results, screenshots and a live demo URL in public README. Include learning notes and tutor-transcript coverage in private docs with verified/unverified sources clearly labelled.

## Downloadable delivery
Target files: Dockerfile, compose.yaml, .env.example, scripts/start.ps1, scripts/start.sh, scripts/prepare-offline.ps1, scripts/backup.ps1, scripts/restore.ps1, deployment instructions, release ZIP and checksums.
These are delivery requirements, not claims that those files are already implemented.
Windows target: F:\AiProjects\dealer-stock-enquiry-tracker. Start script should check tools, create only missing configuration, preserve existing data and print browser addresses. Never overwrite the user's installation during upgrade.

## Environment contract
DATABASE_URL: runtime PostgreSQL URL or local SQLite URL.
MIGRATION_DATABASE_URL: direct PostgreSQL URL; never expose in browser.
SESSION_SECRET: securely generated, no default.
APP_ENV: local or hosted; hosted requires secure cookies.
AI_PROVIDER: disabled, groq or ollama.
AI_MODEL: configured during setup.
GROQ_API_KEY: backend secret only.
AI_DAILY_LIMIT: server-enforced limit.
PUBLIC_DEMO: read-only sample deployment.
PORT: supplied by host.
Keep private customer data, credentials, database files, logs, exports and learning notes out of the public repository.

## Current limitation
The upgraded frontend, database models and API contract exist, but the complete v2 live API, individual authentication, production container and cloud deployment still need implementation and verification. The local execution environment is disconnected, so no new runtime checks are claimed.

