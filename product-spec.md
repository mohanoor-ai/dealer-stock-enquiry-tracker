# Dealer Desk — course-aligned product specification
Status: target design for the upgrade, not a claim that these features exist.
Baseline: the existing local dealer tracker. Preserve its history.
Purpose: demonstrate the 2026 AI-assisted engineering workflow using a useful, focused dealer application.

## Users and problem
A small dealer's stock and follow-up work are scattered. Sales staff need accurate vehicle availability and a clear enquiry queue. A manager needs stock totals and overdue work.
The assessed demo uses fictional vehicles and customers. Real customer operations require a separate production review.

## Main journeys
1. Staff add a vehicle, check its details and change availability.
2. Staff record an enquiry, set a follow-up and move it through new/contacted/closed.
3. Staff complete a follow-up; the dashboard updates without losing the enquiry history.
4. Two authorised demo browser sessions see stock changes, with revision checks preventing silent overwrites.
5. An optional assistant drafts a listing from approved vehicle fields; staff review before accepting. It never publishes.

## Vehicle data
ID; make; model; year; integer price_pence; status (available/reserved/sold); approved descriptive facts; archived flag; created/updated timestamps; revision number.
Input length/range limits appear in the contract. No registration number, external vehicle history or real customer data is required.

## Enquiry and task data
Enquiry ID, vehicle ID, fictional display name, bounded message, status, timestamps.
Follow-up ID, enquiry ID, due date, completion state and timestamps.
Foreign keys preserve relationships. Record an audit event for material state changes without storing customer messages in operational logs.

## Acceptance criteria
V1: Valid stock returns 201 and an ID. Blank fields, negative/fractional pence and unknown fields are rejected. Values survive process restarts.
V2: Search/filter/pagination operate on active stock by default. Archived records remain retrievable through an explicit filter.
V3: Stock editing uses a revision value. A stale update returns 409 and the browser offers refresh; it never overwrites silently.
V4: Available may become reserved or sold; reserved may become available or sold; sold may return to available for an explicit correction. Each change is audited.
E1: An enquiry references an existing, unarchived vehicle; missing IDs return 404 and archived-stock requests return 409.
E2: Follow-up date validation is explicit. A task can complete/reopen. Dashboard open/overdue counts agree with persisted tasks.
U1: The browser has accessible forms, loading/error/empty states and one central API client. User text renders safely.
U2: Two sessions observe shared stock state within five seconds using a documented connection/reconnection strategy.
D1: The same application supports SQLite local development and PostgreSQL through DATABASE_URL. Versioned migrations run from documented commands.
T1: Unit, real-database integration and browser workflow tests have separate commands. No failing test or empty required test suite is treated as success.
R1: A clean checkout runs using documented commands; Compose starts app/database and retains records after container replacement.
R2: Delivery runs only after checks pass; a post-deploy health/journey check records the deployed commit. Rollback is documented and exercised.
O1: One important API journey emits bounded metrics, redacted logs and traces. An alert represents actual user impact.
O2: A responder collects allowlisted, read-only evidence and proposes a structured action. It cannot execute arbitrary model-generated commands.
A1: The extension pack demonstrates instructions, reusable procedure, specialist review, read-only MCP tool, guardrail and explicit permissions.
S1: Actual deterministic scan results, human dispositions and operational evidence are retained. A markdown claim is not a scan result.

## Optional LLM acceptance
L1: Model/provider/version are configured explicitly. Credentials remain outside Git.
L2: Only approved stock facts are sent. Structured output is validated and unsupported claims rejected or flagged.
L3: Timeout, unavailable provider and invalid responses leave core stock/enquiry functions usable.
L4: Offline fixtures are clearly labelled; they are not called live model results.
L5: Fixed evaluation examples include missing facts, malicious text and false vehicle claims. Human acceptance is required; no automatic publishing.
This is a product enhancement, not an explicit final-rubric requirement.

## Access and data
Local offline learning stays separate from the public app.
Public demo: fictional data only; authenticated demo sessions if implementing collaboration. Public mutating demo access must have rate limits and reset/abuse controls before hosting.
MCP returns aggregate stock data, not customer messages. Agents have no production write credentials. Do not commit .env, runtime databases or raw sensitive logs.

## Target architecture
React + TypeScript + Vite → central API client → OpenAPI-defined FastAPI/Pydantic routes → SQLAlchemy → SQLite or PostgreSQL.
Alembic migrations; uv/locked dependencies; pytest; Vitest/Testing Library; Playwright; Docker Compose; GitHub Actions.
OpenTelemetry → Collector → Prometheus/Loki/Tempo → Grafana.
Official Python MCP SDK and a bounded evidence responder.
React, Alembic and test-library choices are project decisions; the rubric does not mandate all of them.
Before adding dependencies verify official compatibility and lock versions.

## Non-goals
Marketplace publishing, payment processing, HPI/valuation, real customers, multi-tenant SaaS, autonomous production fixes, unrestricted tools, model training or RAG.
Cloud selection remains open: tutor-aligned AWS deployment or another suitable container host. No paid provisioning until authorised.

## Definition of done
Demonstrated acceptance checks; public deployment evidence; successful hosted CI/CD; source-to-module map; actual reviewed AI-use journal; extension demo; security/operations artifacts; truthful README and exact evaluation commit.
The 2026 rubric remains draft. Video transcripts are not yet verified. This plan is not a grade guarantee.
