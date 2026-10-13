# Module-to-project learning and evidence map
Status: planned work. Existing baseline results are described separately in the README. Do not mark rows done because files were generated.
Assessment source: https://github.com/DataTalksClub/ai-dev-tools-zoomcamp/blob/main/project/README.md
2026 modules govern this map. Supplied 20-video playlist is 2025 supplemental material; transcripts remain unavailable after HTTP 429.

| Module | Understand | Practise | Project deliverable | Check | Evidence |
|---|---|---|---|---|---|
| 1 | Specification and context | Rewrite vague requests as behaviour and failure cases | product-spec.md; AGENTS.md; task backlog | A reviewer can derive concrete checks without guessing | Reviewed spec diff and decisions |
| 1 | PM → engineer → QA; loops and dependency graphs | Groom one task, implement, review independently, fix failures | Role procedures and small commits | QA cites acceptance criteria; failure returns to implementation | Actual prompts, diff, commands and review outcomes |
| 2 | Frontend state and central communication | Prototype forms with mock responses, then replace mocks | React/TypeScript UI and API client | Success/loading/error/empty scenarios | Frontend tests and screenshots |
| 2 | API contract before implementation | Specify stock/enquiry/revision responses | OpenAPI with examples, error schemas and response models | Runtime contract checks against reviewed design | Contract commit preceding new route implementation |
| 2 | Validation and persistence | Add bounds, relationships and safe updates | FastAPI/Pydantic; SQLAlchemy; SQLite | Restart persistence, invalid input and missing IDs | Tests and migration output |
| 2 | Shared updates | Two browser sessions and stale edit | Live-update channel and revision checking | Cross-session update; 409 conflict; reconnect behaviour | Browser trace and demo |
| 3 | Real integration versus mocks | Run workflow against PostgreSQL | Separate integration suite | Add/update/enquiry/task/restart journey | Test output tied to commit |
| 3 | Container packaging | Run full stack in Compose | Multi-stage frontend/app build; database volume | Clean start and data retention | Actual Docker run output |
| 3 | Browser checks | Exercise actual forms/API/database | Playwright journey | Success and meaningful failure paths | Browser report, trace and screenshots |
| 3 | CI and CD | Gate deployment, verify release | GitHub workflow and chosen host configuration | Test failure blocks delivery; deployed commit is confirmed | Hosted Actions/deployment/smoke results |
| 3 | Release and rollback | Promote/check/revert a demo release | Release checklist and rollback procedure | Prior version restored; database compatibility checked | Recorded release exercise |
| 4 | Metrics/logs/traces | Instrument one important request | OpenTelemetry and telemetry Compose overlay | One request correlates across signals | Dashboard/exported trace with redacted logs |
| 4 | Alert and evidence | Controlled demo failure, allowlisted queries | Alert; collector; read-only responder | Proposed action contains evidence; forbidden actions fail | Incident packet and recovery/escalation record |
| 4 | Deterministic security plus review | Scan source/dependencies and examine findings | Scan artifacts, policy and dispositions | Findings addressed or explicitly accepted | Actual tool/version/results and human review |
| 5 | Reusable procedure and specialist | Review an API task separately | Workflow and configured specialist | Specialist receives scoped context and reports evidence | Host run transcript with sensitive data removed |
| 5 | MCP and tool permissions | Discover/call read-only stock tool | Official-SDK MCP server | Protocol handshake and denied writes/private data | Client test and host demonstration |
| 5 | Hooks and bounded loops | Trigger guard and round limit | Guardrail and custom agent/extension | Guard blocks forbidden action; loop stops | Actual execution output and permissions note |

## Optional archived-course extension
The 2025 agent module teaches LLM API/function calling. Add a listing-draft feature only after core delivery: approved inputs → model adapter → validated output → human acceptance. Test provider failures and unsupported claims. Record model settings and evaluations. Do not imply it is mandatory under the current rubric.

## Homework boundaries
Homework 1: Django chores. Homework 2: one prescribed full-stack idea and SQLAlchemy. Homework 3: Agent Relay with kind/kubectl/act. Homework 4: Order Tracker telemetry/responder. This dealer project applies the transferable skills, but does not constitute completion of those separate assignments.

## Teaching style
For each task: everyday analogy → accurate explanation → annotated code → prediction → exercise → hint → solution → check → teach-back.
Simple names, focused functions, clear loops and necessary classes. Do not add architecture solely to increase tool count.

## Public/private boundary
Public evidence contains fictional records, redacted logs and actual results only. Personal progress, master prompt, commercial drafts, keys and runtime databases stay private.
