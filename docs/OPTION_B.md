# Dealer Desk: Cloud Run + Supabase

Selected 15 October 2026. Code and deployment configuration are reviewable work; account provisioning, billing activation and a live deployment are not performed by this change.

## Architecture

React/TypeScript → same-origin FastAPI → SQLAlchemy → Supabase PostgreSQL. Supabase Auth validates identity; trusted `app_metadata.dealer_role` supplies viewer/operator permissions. Browser access tokens stay in memory. A refresh token is stored in a Secure HttpOnly SameSite=Strict cookie in hosted mode. Cookie-auth routes verify Origin. API mutations require bearer access tokens, not cookies. No custom password database is introduced.

The downloadable local mode uses SQLite or Compose PostgreSQL and localhost-only access. It is a single-user local workspace, not an offline implementation of Supabase authentication. Hosted startup refuses local mode. Never expose local mode through a tunnel or external reverse proxy.

## Run locally

Python 3.12+, Node 24 and npm:

```text
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
```

On Linux/WSL use `.venv/bin/python`. In `frontend-v2`, run `npm ci` and `npm run build`. From the root run `python start.py` using the environment Python. Open http://127.0.0.1:8090. `--legacy` launches the preserved original app instead. `npm run dev` in frontend-v2 proxies API and auth to port 8090.

Local startup creates a fresh schema if needed. For versioned migrations run `python -m alembic upgrade head`. Hosted releases must use migrations before serving traffic; they never create tables automatically.

Default Compose: `docker compose up --build`. PostgreSQL: set a random URL-safe LOCAL_DB_PASSWORD in a private .env and run `docker compose -f compose-postgres.yml up --build`. All published local ports bind to loopback. Named volumes preserve data. Do not use volume deletion when upgrading.

## Supabase setup before deployment

1. Create a project only after cost/account approval. Choose a suitable region near Cloud Run. Record quotas, pause behavior and recovery limits from current provider documentation.
2. Use the SQLAlchemy psycopg URL format `postgresql+psycopg://...`. URL-encode credentials. Set `sslmode=require`. For IPv4-only clients, use a supported Supabase session pooler or IPv4 configuration; the direct database endpoint can require IPv6. Transaction-pooler configuration requires separate prepared-statement compatibility checks.
3. Runtime connection uses DATABASE_URL. MIGRATION_DATABASE_URL selects a migration-compatible direct/session connection. Do not copy either into browser bundles. Use a low connection pool and max Cloud Run instances initially.
4. Apply Alembic migrations. The migration enables RLS and removes browser `anon`/`authenticated` table grants. There are no browser table policies; business data is accessed through FastAPI. Use an appropriate server database role, not the public publishable key, for SQLAlchemy.
5. Provision users through Supabase Auth administration. Disable public signup for the pilot. Set `dealer_role` in **app_metadata** through trusted administration; user_metadata is deliberately ignored. Default users are viewers. Configure provider login rate limits, email/account recovery and redirects before real use.
6. Configure SUPABASE_URL and SUPABASE_PUBLISHABLE_KEY on the backend. No Supabase service-role key is required by the application. Client passwords are forwarded over HTTPS to Supabase and are not stored by Dealer Desk.

## Cloud Run preparation

Use the existing reviewed image and supply PORT through the platform. The image listens on 0.0.0.0. Store configuration and DB credentials using Secret Manager references. Set APP_ENV=hosted, AUTH_MODE=supabase, APP_ORIGIN to the exact HTTPS origin, DATABASE_URL and Supabase settings. AI_PROVIDER defaults disabled. Set PUBLIC_DEMO=true only for an isolated fictional-data database where anonymous reads are intended.

Create Artifact Registry, workload identity federation and a least-privilege deployment identity separately after approval. Configure GitHub variables GCP_PROJECT, GCP_REGION, GCP_WIF_PROVIDER, GCP_DEPLOYER_ACCOUNT and APP_ORIGIN. No long-lived Google JSON key is used. Protect the production GitHub environment with a required reviewer.

Configure the `dealer-migrate` Cloud Run Job with this image, command `python`, arguments `-m,alembic,upgrade,head`, a migration identity/secret and one task. Prevent overlapping manual migration executions. The release workflow serialises releases and waits for migrations before deploying. Configure a dedicated runtime identity and access policy on the service before invoking the workflow; the workflow preserves existing secrets and public/private access configuration.

The manual deploy workflow runs the full reusable verification workflow first, builds an image tagged with the commit, updates/executes the configured migration job, deploys and checks readiness. It does not create accounts or activate billing. Set min instances 0, max instances 1 initially; budgets are alerts, not guaranteed spending caps. Recheck Cloud Run, Artifact Registry, networking, Secret Manager and Supabase charges before enabling delivery.

Rollback: record the prior image/revision; route traffic to a known-compatible prior revision using Cloud Run controls. Do not automatically downgrade database migrations or delete data. Test compatibility and restore into a temporary database if necessary. Readiness is `/health`; liveness is `/live`. A public health check does not prove authenticated stock workflows work.

## Optional Gemini

Install requirements-ai.txt locally, or build with WITH_AI=true. Set AI_PROVIDER=gemini, AI_MODEL and GEMINI_API_KEY only on the backend. Hosted mode also requires AI_TERMS_CONFIRMED=true after account/region review. Current Gemini terms require Paid Services for API clients made available to UK/EEA/Swiss users; a free experimentation allowance is not an unconditional production entitlement. No customer text is sent. The model selects indexes from approved vehicle facts; the server validates them and renders the text. A draft is never saved or published automatically. Daily attempted-call limits are persisted across workers. Live provider verification remains separate from fixtures.

## Recovery and import

Use `python -m scripts.backup <private-output-path>`; PostgreSQL requires pg_dump. Use `python -m scripts.restore <backup> --target <new-database-url>` only against a new/empty database. Keep backups outside Git and test restoration.

Baseline conversion: migrate an empty V2 target, then run `python -m scripts.migrate_baseline <v1.sqlite3> --target <v2-url>` for the dry run. Add --apply only after checking counts. A consistent source backup is created before application. Original baseline records are never altered. Completed enquiries remain closed; only dated follow-ups become tasks; undated follow-ups are counted in the report. Fresh target IDs are mapped to preserve relationships. Repeat imports into nonempty stock/enquiry/task tables are refused.

After migrations, `python -m scripts.sample_v2` imports historical demo records only into empty stock. It never clears existing records. Operator exports contain private data; handle them as backups, not public artifacts.

## Evidence and limits

Run backend, frontend, HTTP, browser, migration, PostgreSQL and container jobs. Record actual results against the release commit. The PR is not a production-readiness certificate. Supabase live login/refresh/logout, recovery emails, regional deployment, hosted DB grants, backup restoration and quotas require account-based verification before public use.

Sources checked for this design: https://supabase.com/docs/guides/auth/passwords ; https://supabase.com/docs/guides/database/connecting-to-postgres ; https://cloud.google.com/run/docs/configuring/services/containers ; https://ai.google.dev/gemini-api/terms ; https://ai.google.dev/gemini-api/docs/structured-output . See the private source register for broader course coverage and research gaps.
