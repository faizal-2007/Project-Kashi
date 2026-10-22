# Testing Documentation

## Test environment actually used

| Item | Value |
|---|---|
| Operating system | Windows |
| Python | 3.14.7 |
| Flask | 3.1.3 |
| MySQL Server | 8.0.46 Community |
| Connector | mysql-connector-python 9.7.0 |
| Test database | `project_kashi_test` |
| Test framework | pytest 9.1.1 |
| Execution date | 22 October 2026 |

The tests ran against a separate, isolated local MySQL 8.0.46 instance created for testing. The schema and all database objects were loaded before the tests. No real customer data was used.

## Command used

```cmd
python -m pytest -q
```

## Actual result

```text
.......................                                                  [100%]
23 passed, 4 warnings in 10.85s
```

The four warnings are deprecation notices for the `stored_results()` accessor in the installed MySQL connector. They do not affect test results.

## Automated test cases

| ID | Test | Expected result | Actual result |
|---|---|---|---|
| AT-01 | Application startup and dashboard | 200, live dashboard headings | Passed |
| AT-02 | `/health` database check | 200, status ok | Passed |
| AT-03 | Customer creation | Customer stored in MySQL | Passed |
| AT-04 | Duplicate customer | Friendly duplicate error, one row | Passed |
| AT-05 | Invalid customer form | Rejected, no row inserted | Passed |
| AT-06 | Account opening | ACCOUNT, ACCOUNT_HOLDER, initial DEPOSIT all created | Passed |
| AT-07 | Deposit | Balance +250.50 and one transaction | Passed |
| AT-08 | Withdrawal | Balance -300 and one transaction | Passed |
| AT-09 | Insufficient balance | Rejected, balance unchanged, no transaction | Passed |
| AT-10 | Zero deposit | Rejected, no transaction | Passed |
| AT-11 | Transfer success | Both balances updated, two linked rows | Passed |
| AT-12 | Transfer rollback | No balances changed, no transaction rows | Passed |
| AT-13 | Transfer to same account | Rejected, no rows | Passed |
| AT-14 | Transaction history/filter | Page renders matching rows | Passed |
| AT-15 | Branch and employee creation | Rows inserted with FK | Passed |
| AT-16 | Loan workflow + payment trigger | Pending -> Approved -> Closed | Passed |
| AT-17 | Account status rules | Non-zero close blocked; zero close allowed | Passed |
| AT-18 | Missing records | 404 responses | Passed |
| AT-19 | Views, functions, procedures | All return expected data | Passed |
| AT-20 | Transaction immutability | UPDATE and DELETE rejected by triggers | Passed |
| AT-21 | Inactive account transaction | Insert rejected by trigger | Passed |
| AT-22 | Primary-holder and status triggers | Duplicate primary and non-zero close rejected | Passed |
| AT-23 | Loan overpayment trigger | Overpayment rejected | Passed |

## Manual test cases

These should be repeated in a browser during the demonstration.

| ID | Scenario | Steps | Expected result |
|---|---|---|---|
| MT-01 | Dashboard | Open `/` | Counts match `SELECT COUNT(*)` in MySQL; recent transactions shown. |
| MT-02 | Register customer | Fill `/customers/new` with valid data | Success flash; customer appears in list and detail page. |
| MT-03 | Duplicate mobile | Register the same mobile again | Error flash; no duplicate row. |
| MT-04 | Open account | Choose customer/branch, deposit 10,000 | Account appears with balance 10,000 and one DEPOSIT row. |
| MT-05 | Deposit | Deposit 5,000 | Balance becomes 15,000; new transaction row. |
| MT-06 | Withdraw too much | Withdraw 999,999 | Error; balance and history unchanged. |
| MT-07 | Transfer | Transfer 2,000 to a second active account | Both balances change; two linked rows. |
| MT-08 | Transfer rollback | Transfer more than source balance | Error; both balances unchanged. |
| MT-09 | Closed account | Close a zero-balance account; try deposit | Deposit rejected because status is Closed. |
| MT-10 | Loan | Create loan, approve, pay partly, pay the rest | Status Pending -> Approved -> Closed; outstanding reaches zero. |
| MT-11 | CSRF | Submit an old form after token expiry | Friendly CSRF error page, not a server crash. |
| MT-12 | DB unavailable | Stop MySQL and open `/` | Friendly database error page; terminal logs the error. |

## What was not executed

- No browser screenshots were captured automatically. See `docs/SCREENSHOTS.md`.
- The student's personal MySQL server credentials were not available, so the application was tested on an isolated local MySQL instance. The same SQL scripts are provided for the student's server.
- No production security, penetration, or load testing was performed.

## How to verify a database state

```cmd
mysql -u root -p -e "USE project_kashi; SELECT AccountNumber, Balance, Status FROM ACCOUNT; SELECT * FROM BANK_TRANSACTION ORDER BY TransactionID DESC LIMIT 5;"
```
