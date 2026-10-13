# Checks
Install requirements in a virtual environment. Run `python -m pytest -q` and `node --test tests/frontend.test.mjs` (Node 18+).
Backend tests use a temporary real SQLite database. Frontend tests check money handling and central request behaviour. Integration tests cover the stock/enquiry journey. Browser end-to-end automation is not yet included.
Manual journey: add → search → edit price → reserve → create enquiry → complete follow-up → sell → archive → show archived → restore → restart and verify persistence.
