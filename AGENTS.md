# Working rules
Use simple English, small named functions and clear loops. Use classes for input models where helpful. No unnecessary framework or abstraction.
Read product-spec.md and openapi.yaml before editing routes. Keep all browser requests in frontend/api.js. Use parameterised SQL. Do not add real customer data or secrets.
Run: python start.py. Tests: python -m pytest; node --test tests/frontend.test.mjs. Guard: python scripts/check_public_files.py.
One task at a time: describe expected behaviour, implement, inspect diff, verify, commit.
The learning companion, master prompt and personal records are outside this public repository.
