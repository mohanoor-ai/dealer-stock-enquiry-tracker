# Upgrade backlog
Status: planned, not completed. Work one acceptance-tested change at a time.
Dependencies are explicit. Preserve baseline on main; work on development branch.

| Task | Goal | Depends on | Done when |
|---|---|---|---|
| U01 | Review target scope and architecture decisions | None | Spec and map reviewed; choices recorded |
| U02 | Define API contract and error/response models | U01 | Reviewed stock/enquiry/task/revision design and examples |
| U03 | Scaffold React/TypeScript/Vite with central mock client | U02 | Forms and state tests pass against fixtures |
| U04 | Add SQLAlchemy models and Alembic migrations | U02 | SQLite migration/rollback tested; seed is fictional |
| U05 | Implement contract-defined routes | U04 | Validation, relationships and stale-update checks pass |
| U06 | Connect real API and shared updates | U03,U05 | Two sessions update; conflict/reconnect behaviour verified |
| U07 | Add PostgreSQL Compose configuration | U04,U05 | Real database integration suite and persistence pass |
| U08 | Add full browser journey tests | U06,U07 | UI/API/database journey passes and catches a deliberate failure |
| U09 | Verify container and CI gates | U07,U08 | Clean Compose run; hosted checks pass; failures block delivery |
| U10 | Select/provision authorised hosting and CD | U09 | Live fictional-data demo, evaluated commit, smoke/rollback evidence |
| U11 | Instrument request and alert | U07 | Metric/log/trace correlation and useful failure alert |
| U12 | Implement bounded evidence responder | U11 | Allowlisted read-only evidence; structured proposal; no arbitrary execution |
| U13 | Demonstrate extension pack | U05 | Workflow, specialist, MCP, hook and bounded loop show actual host evidence |
| U14 | Run security audits and review findings | U09,U12,U13 | Actual artifacts, dispositions and data/tool policy |
| U15 | Optional LLM listing draft | U05,U09 | Facts-only evaluation, timeout/failure path and human acceptance |
| U16 | Upgrade offline lessons and code walkthroughs | U01 onwards | Lessons match implemented milestones and source coverage |
| U17 | Final reproducibility/submission check | U10,U14,U16 | README/demo/evidence matrix/exact commit checked |

## First implementation slice
U02: define and review the stock/enquiry/task contract before rebuilding routes.
Then U03 and U04 can be developed independently, followed by U05.

## Task record template
Task and acceptance criteria:
Source/module:
Files changed:
AI prompt:
Developer decisions/review:
Check commands and actual results:
Independent review:
Unresolved concern:
Commit:

## External blockers
No paid cloud resource or real provider credentials selected. Transcript download blocked by HTTP 429. Container/browser tooling must be verified in a working runtime. These are unresolved checks, not completed tasks.

