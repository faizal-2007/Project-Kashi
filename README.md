# Project Kashi - Banking Management System

An academic DBMS project built with **Python Flask**, **MySQL 8.0**, raw **HTML/CSS**, and minimal vanilla JavaScript. It demonstrates relational database design, ER modelling, normalization, joins, views, stored functions, stored procedures, triggers, transactions, and a working banking workflow.

> This is a local academic simulation. It is not a production banking system and must not be used for real money or real customer data.

## Features

- Live dashboard calculated from MySQL, not hardcoded values.
- Customer registration, listing, search, and details.
- Account opening with a unique 12-digit account number, account holder link, and optional initial deposit transaction.
- Account list, search, details, holder information, status changes, and transaction history.
- Deposit, withdrawal, and transfer operations with server-side validation and MySQL transactions.
- Row locking with `SELECT ... FOR UPDATE` and rollback on failure.
- Transfer creates linked `TRANSFER_OUT` and `TRANSFER_IN` records with a shared `TransferGroupReference`.
- Branch and employee management.
- Loan application, approval/rejection, payment recording, outstanding balance, and automatic closure when fully paid.
- CSRF protection on state-changing forms.
- Parameterized SQL throughout.
- 18 documented SQL business queries, 6 views, 4 stored functions, 4 stored procedures, and 8 triggers.
- 23 automated tests.

## Project structure

```text
Project Kashi/
|-- app.py
|-- config.py
|-- db.py
|-- requirements.txt
|-- .env.example
|-- .gitignore
|-- README.md
|-- sql/
|   |-- schema.sql
|   |-- views.sql
|   |-- functions.sql
|   |-- procedures.sql
|   |-- triggers.sql
|   |-- sample_data.sql
|   `-- business_queries.sql
|-- templates/            20+ Jinja pages
|-- static/css/style.css
|-- static/js/main.js
|-- docs/                 report, ER model, data dictionary, tests, viva
|-- tests/
|   |-- conftest.py
|   |-- test_app.py
|   `-- README.md
`-- screenshots/
    `-- README.md
```

## Technology stack

| Layer | Technology |
|---|---|
| Backend | Python 3.10+ and Flask 3.1 |
| Database | MySQL 8.0 with InnoDB |
| Connector | mysql-connector-python |
| Frontend | Raw HTML, CSS, minimal JavaScript |
| Templates | Jinja2 |
| Forms | Flask-WTF CSRF protection |
| Testing | pytest |
| Configuration | python-dotenv and environment variables |

## Prerequisites

1. Windows 10 or 11.
2. Python 3.10 or newer. This project was tested with Python 3.14.7.
3. MySQL Server 8.0 installed and running locally.
4. MySQL command-line client available.
5. A MySQL account that can create a database and tables. The examples use `root`, but you may use another account.

Check the tools:

```cmd
python --version
mysql --version
```

## 1. Open the project

Use Command Prompt (CMD) for the commands in this README:

```cmd
cd /d "C:\Projects\Project Kashi"
```

## 2. Create a virtual environment

```cmd
python -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## 3. Configure environment variables

Copy the example file:

```cmd
copy .env.example .env
notepad .env
```

Set your own MySQL password and a private Flask secret:

```env
SECRET_KEY=put-a-long-random-value-here
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_actual_mysql_password
DB_NAME=project_kashi
TEST_DB_NAME=project_kashi_test
FLASK_DEBUG=1
```

`.env` is ignored by Git. Never commit real credentials. If your MySQL account has no password, leave `DB_PASSWORD=` empty.

## 4. Create the database and load the SQL scripts

The scripts must be run **in this order**. `schema.sql` drops and recreates only the `project_kashi` database, so do not run it against a database containing important data.

```cmd
mysql -u root -p < sql\schema.sql
mysql -u root -p < sql\views.sql
mysql -u root -p < sql\functions.sql
mysql -u root -p < sql\procedures.sql
mysql -u root -p < sql\triggers.sql
mysql -u root -p < sql\sample_data.sql
```

Enter your MySQL password when prompted. If `mysql` is not recognized, use the full path, for example:

```cmd
"C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe" -u root -p < sql\schema.sql
```

In PowerShell, redirection with `<` is not supported. Run the same command through CMD:

```powershell
cmd /c "mysql -u root -p < sql\schema.sql"
```

Verify the data:

```cmd
mysql -u root -p -e "USE project_kashi; SHOW TABLES; SELECT COUNT(*) AS customers FROM CUSTOMER;"
```

## 5. Run the Flask application

```cmd
python app.py
```

Open <http://127.0.0.1:5000> in a browser.

If MySQL is unavailable, the terminal prints a clear database-connection warning and pages show a friendly database error. Fix `.env` and the MySQL service, then restart Flask.

## 6. Run the tests

The test suite uses a separate database named `project_kashi_test` and recreates it with the same schema. The MySQL user in `.env` needs `CREATE DATABASE`, `DROP DATABASE`, and table/trigger privileges.

```cmd
python -m pytest -q
```

The automated tests were executed successfully against MySQL 8.0.46:

```text
23 passed
```

Tests may be skipped if the configured MySQL test server cannot be reached. Read the skip message and see `docs/TROUBLESHOOTING.md`.

To run only one test:

```cmd
python -m pytest tests/test_app.py::test_transfer_success_creates_two_linked_entries -q
```

## 7. SQL files

| File | Purpose |
|---|---|
| `sql/schema.sql` | Creates the 8 core tables, constraints, indexes, and foreign keys. |
| `sql/views.sql` | Creates 6 reporting views. |
| `sql/functions.sql` | Creates 4 stored functions. |
| `sql/procedures.sql` | Creates 4 stored procedures. |
| `sql/triggers.sql` | Creates 8 integrity/automation triggers. |
| `sql/sample_data.sql` | Loads demonstration branches, customers, accounts, transactions, loans, and payments. |
| `sql/business_queries.sql` | Contains 18 documented reporting queries. |

Run a business query file:

```cmd
mysql -u root -p --table < sql\business_queries.sql
```

## 8. Main routes

| Method | Route | Purpose |
|---|---|---|
| GET | `/` | Dashboard |
| GET | `/customers` | Customer list and search |
| GET/POST | `/customers/new` | Register a customer |
| GET | `/customers/<id>` | Customer details |
| GET | `/accounts` | Account list and search |
| GET/POST | `/accounts/open` | Open an account |
| GET | `/accounts/<id>` | Account details |
| POST | `/accounts/<id>/status` | Change account status |
| GET/POST | `/deposit` | Deposit money |
| GET/POST | `/withdraw` | Withdraw money |
| GET/POST | `/transfer` | Transfer money |
| GET | `/transactions` | Transaction history and filters |
| GET | `/branches` | Branch list |
| GET/POST | `/branches/new` | Create branch |
| GET | `/employees` | Employee list |
| GET/POST | `/employees/new` | Create employee |
| GET | `/loans` | Loan list |
| GET/POST | `/loans/new` | Submit loan application |
| GET | `/loans/<id>` | Loan details and payment form |
| POST | `/loans/<id>/decision/approve` | Approve pending loan |
| POST | `/loans/<id>/decision/reject` | Reject pending loan |
| POST | `/loans/<id>/pay` | Record loan payment |
| GET/POST | `/loans/payments` | Loan payment history and form |
| GET | `/health` | JSON database health check |

## 9. Database credentials and security notes

- Use environment variables; no database password is written in source code.
- All application SQL uses parameter placeholders (`%s`).
- Jinja autoescaping protects displayed user text.
- POST forms use CSRF tokens from Flask-WTF.
- Database exceptions are logged; user-facing messages stay friendly.
- The app is still an academic demo. It has no authentication, authorization, audit login, HTTPS, or production hardening.
- Do not reuse the example `SECRET_KEY`.
- Do not load real personal or financial data.

## 10. Documentation index

- `docs/PROJECT_REPORT.md` - complete report with all required sections.
- `docs/ER_DIAGRAM.md` and `docs/ER_DIAGRAM.mmd` - Mermaid ER diagram and explanation.
- `docs/RELATIONAL_SCHEMA.md` - relational schema with keys.
- `docs/DATA_DICTIONARY.md` - every table and column.
- `docs/RELATIONSHIPS_AND_CARDINALITY.md` - relationship table and integrity rules.
- `docs/NORMALIZATION.md` - 1NF, 2NF, 3NF examples.
- `docs/APPLICATION_WORKFLOW.md` - request-to-database flow for every operation.
- `docs/DBMS_CONCEPTS.md` - DBMS concepts demonstrated by the project.
- `docs/BUSINESS_PROBLEMS.md` - 18 SQL business problems with queries.
- `docs/TEST_CASES.md` - automated and manual test evidence.
- `docs/VIVA_QUESTIONS.md` - 45 viva questions and answers.
- `docs/TROUBLESHOOTING.md` - common MySQL/Flask errors.
- `docs/SCREENSHOTS.md` - exact screenshot capture checklist.
- `screenshots/README.md` - where to save screenshots.

## 11. Common problems

**`mysql` is not recognized:** add `C:\Program Files\MySQL\MySQL Server 8.0\bin` to PATH or call `mysql.exe` using its full path.

**Access denied for user 'root':** set the real MySQL password in `.env`; the setup commands ask for the password separately.

**Unknown database 'project_kashi':** run `sql\schema.sql` and the remaining SQL scripts in the documented order.

**Duplicate entry:** customer mobile/email, IFSC, account number, and transaction references have unique constraints. Use different values or use the existing record.

**Trigger error about transaction history:** transaction records are intentionally immutable. Do not update or delete them; create a new correcting operation instead.

**CSRF token error:** reload the form; do not leave a form open indefinitely or reuse an old POST.

**Tests skipped:** set the correct `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`, and `TEST_DB_NAME`, then rerun.

## 12. Git and GitHub

Initialize the repository and commit:

```cmd
git init
git add .
git commit -m "Complete Project Kashi banking management system"
git branch -M main
```

Check that `.env`, `.venv`, and `__pycache__` are not staged:

```cmd
git status
```

Create a GitHub repository and push using GitHub CLI:

```cmd
gh repo create Project-Kashi --public --source . --remote origin --push
```

GitHub repository names cannot contain literal spaces. The local folder is named `Project Kashi`; the remote repository uses `Project-Kashi`. If you prefer a private repository, replace `--public` with `--private`.

Without GitHub CLI, create an empty repository in the GitHub website and run:

```cmd
git remote add origin https://github.com/YOUR-USERNAME/Project-Kashi.git
git push -u origin main
```

## 13. Submission note

The database design, Flask code, SQL routines, tests, and documentation are included. Screenshots must still be captured locally from a running application; see `docs/SCREENSHOTS.md`. The project was tested on an isolated local MySQL instance and does not contain any real bank data.
