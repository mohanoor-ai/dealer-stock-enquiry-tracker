# Dealer Desk

Vehicle stock, enquiries and follow-up tasks in one workspace. React/TypeScript → FastAPI → SQLAlchemy → SQLite locally or Supabase PostgreSQL when hosted. Supabase Auth provides hosted identity and viewer/operator access. Fictional demonstration data only until the production-readiness gates are completed.

## Run
Python 3.12+ and Node 24. Create a virtual environment and install requirements.txt. In frontend-v2 run `npm ci`, `npm run build`; then from the root run `python start.py` using the environment Python. Open http://127.0.0.1:8090. Windows/Linux launchers are in scripts. `python start.py --legacy` preserves the original baseline app.

`docker compose up --build` starts the local SQLite edition. `docker compose -f compose-postgres.yml up --build` uses PostgreSQL after configuring a private LOCAL_DB_PASSWORD. Initial installation/build needs internet. Prepared local assets work offline with AI disabled. No runtime or model is bundled.

## Behavior
Create, edit, search and filter stock; archive and restore; record enquiries; schedule and complete tasks; inspect dashboard totals; export operator records. Updates require the current revision. Stale edits return 409 instead of overwriting newer records. Shared refresh runs every three seconds while visible. The preserved prototype remains available to frontend tests; normal launch uses the real API.

## Checks
`python -m pytest -q`; `node --test tests/frontend.test.mjs`; in frontend-v2 `npm test` and `npm run build`. HTTP/browser/PostgreSQL jobs are distinct from synchronous service checks. Set TEST_POSTGRES_URL only to a disposable test database. `python scripts/browser_journey.py` needs Playwright and Chromium. CI records actual outcomes; an authored workflow is not a successful run.

## Deployment and recovery
See docs/OPTION_B.md for Cloud Run, Supabase, auth setup, migrations, provider terms, backup/restore and baseline conversion. The active openapi.yaml describes V2; docs/openapi-baseline.json records the preserved baseline. Cloud delivery is manual, environment-protected and gated by verification. No accounts, paid services or live deployment are created by this source change. Optional AI is disabled by default and never saves/publishes a draft automatically.

## Limits
Local mode is a single-user loopback workspace. Hosted mode requires Supabase and real account-based validation. Public demo reads must use an isolated fictional database. Supabase Storage media uploads and multi-dealership SaaS remain later scope. Read docs/IMPLEMENTATION_STATUS.md before claiming production readiness. Private learning material is maintained separately.
