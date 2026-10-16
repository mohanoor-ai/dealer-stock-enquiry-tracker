> Current implementation: see [Option B](OPTION_B.md) and [implementation status](IMPLEMENTATION_STATUS.md). The original notes below are retained as historical design context.

# API contract design decisions
Status: v2 design, not implemented by the baseline server.
Contract: openapi.yaml. OpenAPI 3.1 selected for compatibility with the planned backend/toolchain; no claim it is the newest release.

## Main choices
15 operations cover readiness, stock CRUD-with-archive, enquiry queue, follow-up tasks, dashboard and bounded change notifications.
Money uses integer pence. Unknown fields and blank required text are rejected.
Writes submit revision; compare-and-update must happen atomically in SQL. A stale revision returns 409 with current_revision. Frontend refreshes and asks the user to resolve the edit.
Creation is not automatically retried: otherwise a timeout could create duplicate records. A later idempotency design can add safe retries.
List pages have bounded limits and stable ID-descending order.
Follow-up due dates use a configured dealer timezone, default Europe/London. Overdue means an incomplete task dated before today. Closing an enquiry hides its tasks from open dashboard counts without deleting history.

## Shared state
Poll /api/changes every three seconds; drain pages, then refresh affected views. Events contain identifiers/revisions only. Fetch changes after successful local writes as well. Reconnect refreshes full state before advancing the cursor.
This meets the current product update target but is not WebSocket practice. The tutor's WebSocket approach remains a separate learning example and possible later implementation.

## Demo access
Bearer token is configured server-side and entered at runtime; never hardcode it in public browser assets. All /api routes require it. /health is public. A shared demo token is a limited teaching access mechanism, not a complete multi-user identity system. Rate limiting and reset/abuse policy must be implemented before public hosting.

## LLM boundary
Optional listing-draft routes are deliberately not part of this core contract. They will be designed separately after core workflows pass.

## Verification
openapi-spec-validator 0.9.0 passed structural validation. JSON Schema validation passed 14 positive/negative cases: valid vehicle; whitespace make; negative/fractional money; extra field; valid revision edit; empty edit; missing revision; invalid status; enquiry; valid/invalid dates; task completion; structured conflict error.
These checks do not prove runtime routes exist. Business transitions, date-relative rules, concurrent updates, authentication, rate limiting and response alignment still require implementation and runtime tests.

## Next
Prototype React forms against fixtures from this contract. In parallel, design SQLAlchemy models and migrations. Preserve baseline code until upgraded routes/tests are ready.

