# Release and rollback checklist

Record the evaluated commit and required CI URLs. Confirm backend/contract/React/migration/PostgreSQL/browser/container jobs actually passed. Verify that a failed required check prevents delivery. Use the protected production environment; do not use a separate deploy-on-push mechanism.

Before migration: take a private database backup, confirm restore instructions and schema compatibility, and stop baseline writes before explicit data conversion. Before traffic: run the configured single-task migration job to completion. Deploy the immutable image and check /health plus an authenticated stock→enquiry→task journey using fictional records. Check viewer denial, record persistence and a second browser session.

Keep the preceding compatible Cloud Run revision available. If readiness/journey fails, stop promotion and restore traffic to that revision. Do not automatically reverse migrations. If data restoration is needed, restore into a separate database, reconcile records and obtain the operator's decision before replacing the live connection. Record timings, commands and actual results without credentials.

The application and migration jobs use separate identities/secret references. Recheck provider region, quotas, billing exposure and Gemini deployment terms. No zero-cost availability guarantee or production approval is implied by passing CI.
