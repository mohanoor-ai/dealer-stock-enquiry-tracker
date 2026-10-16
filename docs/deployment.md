> Current implementation: see [Option B](OPTION_B.md) and [implementation status](IMPLEMENTATION_STATUS.md). The original notes below are retained as historical design context.

# Deployment exercise — pending
The application is not deployed. No hosting account or billing action was performed.
1. Choose an approved container host and create a fictional-data demo service.
2. Build this Dockerfile. Listen on the port required by the host (change the command if necessary).
3. Mount a durable /data volume and set DEALER_DB. Confirm the host supports SQLite storage and one app instance.
4. Add TLS and access/abuse controls before widening use. Never upload customer data.
5. Run tests and the guard; deploy the evaluated commit. Check /health and the browser create/search/enquiry journey.
6. Record public URL, commit, deployment time, checks and rollback instructions.
7. Configure provider-specific delivery using secrets stored in GitHub settings. Gate deployment on passing tests and run a post-deploy smoke check. CI alone does not earn full CD evidence.
Course module 3 also teaches Postgres and staging/production separation; these are further exercises, not implemented here.
GitHub Pages alone cannot run the Python backend.

