# Troubleshooting

## Database connection

### `Access denied for user 'root'@'localhost'`
Set the correct `DB_USER` and `DB_PASSWORD` in `.env`. The setup commands also prompt for a password separately; the `.env` value and the command-line password must identify an account with the required privileges.

### `Unknown database 'project_kashi'`
Run the SQL scripts in order:

```cmd
mysql -u root -p < sql\schema.sql
mysql -u root -p < sql\views.sql
mysql -u root -p < sql\functions.sql
mysql -u root -p < sql\procedures.sql
mysql -u root -p < sql\triggers.sql
mysql -u root -p < sql\sample_data.sql
```

### `Can't connect to MySQL server on 'localhost'`
Start the MySQL Windows service:

```cmd
net start MySQL80
```

The service name may differ. Check it with `Get-Service *mysql*` in PowerShell.

### Functions fail with error 1418 / binary logging
The functions are declared `READS SQL DATA`. If your server still rejects creation, run the function script as an administrative MySQL user or set `log_bin_trust_function_creators` appropriately for the local academic instance. Do not weaken a shared production server.

### `mysql` is not recognized
Use the full path:

```cmd
"C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe" -u root -p
```

Or add the MySQL `bin` directory to PATH.

### PowerShell does not accept `<`
Run the redirect through CMD:

```powershell
cmd /c "mysql -u root -p < sql\schema.sql"
```

## Application

### `ModuleNotFoundError: No module named 'flask'`
Activate the virtual environment and install requirements:

```cmd
.venv\Scripts\activate
python -m pip install -r requirements.txt
```

### Port 5000 already in use
Stop the other process or change the port in `app.py`:

```python
app.run(debug=..., host="127.0.0.1", port=5001)
```

### CSRF token missing/invalid
Reload the page and submit the form again. Ensure `SECRET_KEY` is set and stable. Do not disable CSRF outside tests.

### Duplicate entry error
Customer mobile/email, employee mobile/email, IFSC, account number, and references are unique. Use different values or view the existing record.

### Transaction history cannot be updated/deleted
This is intentional. The triggers protect financial history. Insert a new correcting transaction in a real system; do not disable the trigger.

### Account cannot be closed
Close requires balance exactly 0. Withdraw or transfer the remaining funds first.

### Loan payment rejected
Payments are allowed only for Approved loans, and the amount cannot exceed the outstanding balance. Approve a Pending loan first.

### Dashboard shows a database error
Open `/health`. It returns a generic error when the configured database cannot be reached. Check `.env`, MySQL service, and the schema.

## Tests

### Tests are skipped
The conftest skips when it cannot connect to MySQL. Check `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`, and `TEST_DB_NAME`. The account needs permission to create/drop `project_kashi_test`.

### Test database is missing or schema is wrong
The test suite runs `sql/schema.sql`, views, functions, procedures, and triggers against `project_kashi_test`. Re-run pytest; it recreates the test database.

### Deprecation warnings from `stored_results`
They come from the installed connector and do not change the result. The tests still pass.

## Git

### `.env` appears in `git status`
It should be ignored. Confirm `.gitignore` contains `.env` and run `git rm --cached .env` if it was previously staged. Never commit a real password.

### GitHub repository name
GitHub does not allow a literal space in repository names. The local folder is `Project Kashi`; use `Project-Kashi` for the remote repository.
