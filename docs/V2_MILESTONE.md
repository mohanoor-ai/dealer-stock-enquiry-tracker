> Current implementation: see [Option B](OPTION_B.md) and [implementation status](IMPLEMENTATION_STATUS.md). The original notes below are retained as historical design context.

# V2 frontend and database milestone

## Run the interface
Node 22.12+ recommended (tested with Node 24). In frontend-v2:
```
npm ci
npm run dev
npm run build
npm test
```
Open the address Vite prints. Default mode uses clearly labelled in-memory fictional fixtures. Refreshing the page resets them. The central api.ts client also has live mode for the future v2 routes; the baseline backend does not implement those responses yet.

## Database development
Python 3.12+ and uv:
```
uv sync
uv run alembic upgrade head
uv run python scripts/check_v2_database.py
```
Default database is data/dealer-v2.sqlite3. DATABASE_URL can select PostgreSQL using postgresql+psycopg://...; PostgreSQL runtime testing is pending. Credentials must stay outside Git. Migrations use distinct v2 tables so baseline records are not silently overwritten. No baseline-to-v2 data conversion is claimed.

## What passed
TypeScript compilation and production Vite build; four Vitest/Testing Library tests: money validation, stale edit, enquiry/task journey, search empty state. SQLite migration up/down/up; records survive a new engine/session; price and relationship constraints reject bad data.
No browser end-to-end run, live v2 routes, shared polling, PostgreSQL integration, cloud deployment or completed production authentication is claimed.

## Code walkthrough
App.tsx uses ordinary React functions and state. api.ts owns fetch, timeout and pagination. mock.ts supplies limited prototype responses and must not be mistaken for server validation. Types mirror the reviewed contract.
SQLAlchemy classes describe persisted tables. A record mixin supplies IDs/revisions/timestamps. build_engine enables SQLite foreign keys. Alembic records schema versions; inspect generated migrations before running them.

## AI-use record
ChatGPT drafted the prototype and models following product-spec.md and the prior API contract. Review found a TypeScript CSS declaration gap and ambiguous test selectors; both were corrected. Local tests then passed. Human learner review and independent host QA remain to be recorded.

## Next
Implement v2 validation/response models, error envelopes, token boundary, routes and atomic revision updates; connect the real database to frontend flows. Then test PostgreSQL and shared state.

