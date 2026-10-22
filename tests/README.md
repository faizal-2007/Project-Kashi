# Tests

## Requirements

- Running MySQL server.
- `.env` with `DB_*` credentials and `TEST_DB_NAME` (default `project_kashi_test`).
- Test user permission to create and drop the test database and to create tables, views, routines, and triggers.

## Run

From the project root, after activating the virtual environment:

```cmd
python -m pytest -q
```

## What the suite does

1. Connects to MySQL without selecting a database.
2. Recreates `project_kashi_test` by running `sql/schema.sql` with the database name substituted.
3. Loads views, functions, procedures, and triggers.
4. Truncates project tables before each test and inserts one test branch.
5. Runs Flask route tests through the test client with CSRF disabled only for tests.
6. Runs database tests against the separate test schema.

No sample data or real customer data is used. The application's main database is not modified.

## Verified result

```text
23 passed, 4 warnings in 10.85s
```

The warnings are connector deprecations for `stored_results()`.

## If tests skip

The skip message states that MySQL is unavailable. Check `.env` and start the MySQL service. Do not modify the test suite to hide a connection problem.

## Manual checks

See `docs/TEST_CASES.md` for browser-based checks and `docs/SCREENSHOTS.md` for evidence capture.
