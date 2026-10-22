# Screenshot Capture Guide

No screenshots were captured in this environment. The application was tested with Flask's test client and an isolated MySQL server, not with a screenshot-capable browser. Do not submit invented images. Capture real screenshots from your own running application.

## Preparation

1. Ensure `.env` points to the real local `project_kashi` database.
2. Load `sql/sample_data.sql`.
3. Start the app with `python app.py`.
4. Open <http://127.0.0.1:5000>.
5. Use a 1440x900 browser window for consistent framing.
6. Hide personal data and passwords. The sample data uses example.com addresses and fictional names.

## Required screenshots

Save files in `screenshots/` using these recommended names.

| # | Filename | Page / evidence | What to show |
|---|---|---|---|
| 1 | `01-dashboard.png` | `/` | Six live statistics cards, recent transactions, branch overview. |
| 2 | `02-customer-registration.png` | `/customers/new` | Completed or blank customer form. |
| 3 | `03-customer-list.png` | `/customers` | Search box, customer rows, account/loan counts. |
| 4 | `04-account-opening.png` | `/accounts/open` | Customer, type, branch, initial deposit fields. |
| 5 | `05-account-detail.png` | `/accounts/1` | Balance, status, holders, transaction history. |
| 6 | `06-deposit-result.png` | `/deposit` plus detail | Success flash and updated balance. |
| 7 | `07-withdrawal-result.png` | `/withdraw` plus detail | Success flash or insufficient-balance rejection. |
| 8 | `08-transfer-result.png` | `/transfer` plus `/transactions` | Both transfer entries and common group reference. |
| 9 | `09-transaction-history.png` | `/transactions` | Filters and transaction table. |
| 10 | `10-mysql-tables.png` | MySQL client | `SHOW TABLES;` and `DESCRIBE ACCOUNT;`. |
| 11 | `11-er-diagram.png` | GitHub-rendered `docs/ER_DIAGRAM.md` | Mermaid ER diagram. |
| 12 | `12-sql-query-output.png` | MySQL client | Output of a business query from `sql/business_queries.sql`. |
| 13 | `13-trigger-example.png` | MySQL client | `SHOW TRIGGERS;` or an error caused by the immutability trigger. |
| 14 | `14-loan-workflow.png` | `/loans/1` | Loan details, payments, outstanding, status. |
| 15 | `15-branch-employee.png` | `/branches` and `/employees` | Branch summary and staff records. |

## Suggested MySQL screenshots

```cmd
mysql -u root -p -e "USE project_kashi; SHOW TABLES;"
mysql -u root -p -e "USE project_kashi; DESCRIBE ACCOUNT;"
mysql -u root -p -e "USE project_kashi; SHOW TRIGGERS;"
mysql -u root -p -e "USE project_kashi; SELECT * FROM vw_branch_summary;"
```

Demonstrate a trigger rejection without damaging the sample data:

```sql
UPDATE BANK_TRANSACTION SET Amount = 1 WHERE TransactionID = 1;
-- Expected: ERROR 1644 transaction history is immutable
```

## Include in the report

Insert the images into `docs/PROJECT_REPORT.md` or your final report with captions such as:

```markdown
![Dashboard](screenshots/01-dashboard.png)
*Figure 1: Live dashboard calculated from MySQL.*
```

Only add images that actually exist. The repository currently contains this instruction file and a placeholder README, not screenshot images.
