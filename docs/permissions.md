# Data and permissions
Public: project source, fictional demo data, tests, contract, clean guides and reviewed AI workflow notes.
Private: master prompt, learning records, commercial drafts, customer data and raw agent logs.
Never commit: credentials, .env, database files or runtime logs.
The local app has no authentication: use fictional data only and bind to localhost. Do not put real customers in a public demo.
Optional LLM call sends only a fixed educational question to local Ollama. No database access is given to the model. The bounded loop cannot execute proposals. MCP uses a fixed read-only database and returns counts. Configure host permissions separately.
The basic file guard is not a comprehensive secret scanner. External dependency/security scans and human review are pending.
