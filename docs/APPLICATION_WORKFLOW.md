# Application Workflow

## Three-layer architecture

```text
Browser (HTML + CSS + JavaScript)
        |
        | HTTP GET / POST (form data, CSRF token)
        v
Flask application (app.py, db.py, config.py)
        |
        | parameterized mysql-connector-python calls
        v
MySQL 8.0 (project_kashi tables, constraints, views, routines, triggers)
```

1. **Presentation layer:** Jinja templates in `templates/`, styling in `static/css/style.css`, and small behaviours in `static/js/main.js`.
2. **Application layer:** Flask routes validate input, apply business rules, start transactions, and choose the response.
3. **Data layer:** MySQL stores data and enforces keys, checks, foreign keys, locks, triggers, and routines.

## General request flow

```text
HTML form
  -> POST request with CSRF token
  -> Flask route
  -> server-side validation
  -> parameterized SQL / MySQL transaction
  -> commit or rollback
  -> flash message
  -> redirect to a GET page
  -> Jinja renders database rows
```

## Customer registration

1. User opens `/customers/new`.
2. The route renders `customer_form.html` with a CSRF token.
3. The form posts first name, last name, date of birth, gender, mobile, email, address, and city.
4. Flask checks required fields, name lengths, allowed gender, mobile pattern, email pattern, date validity, and field lengths.
5. The application runs a parameterized `INSERT INTO CUSTOMER`.
6. Unique constraints reject duplicate mobile/email. The route converts that into a friendly message.
7. On success, Flask flashes a message and redirects to `/customers`; the new row is read from MySQL.

## Account opening

1. The form loads customers and branches from the database.
2. The user selects a customer, account type, branch, holder type, and optional initial deposit.
3. Flask validates IDs, type, holder type, and amount.
4. A 12-digit account number is generated with `secrets`.
5. One MySQL transaction performs:
   - `INSERT INTO ACCOUNT`;
   - `INSERT INTO ACCOUNT_HOLDER` with HolderType;
   - if the opening deposit is greater than zero, `INSERT INTO BANK_TRANSACTION` as a DEPOSIT.
6. Any failure rolls back all three steps. The account and holder cannot be half-created.
7. On success the user sees the generated account number.

## Deposit

1. User selects an active account and enters a positive amount.
2. Flask parses the amount as a decimal with at most two decimal places.
3. Inside a transaction, `SELECT ... FOR UPDATE` locks the account row.
4. The route verifies that the account exists and is Active.
5. It updates `Balance = Balance + amount`.
6. It inserts a `DEPOSIT` row with status `SUCCESS` and a unique reference.
7. `COMMIT` makes both changes durable. Any error calls `ROLLBACK`.

## Withdrawal

1. The account is locked with `FOR UPDATE`.
2. Flask verifies Active status.
3. It compares the balance with the requested amount.
4. If funds are insufficient, it raises a business error; the transaction rolls back.
5. Otherwise it subtracts the amount and inserts a `WITHDRAWAL` row.
6. The `chk_account_balance` constraint provides a second database-level guard against a negative balance.
7. Commit or rollback.

## Transfer

1. Flask validates two distinct account IDs and a positive amount.
2. It locks both account rows in ascending `AccountID` order using one `SELECT ... FOR UPDATE`.
3. It verifies that both accounts exist and are Active.
4. It checks the source balance.
5. It updates both balances.
6. It inserts two rows:
   - `TRANSFER_OUT` for the source;
   - `TRANSFER_IN` for the destination.
7. Both rows share a `TransferGroupReference`, while each has its own unique `ReferenceNumber`.
8. One `COMMIT` or one `ROLLBACK` covers all four changes.

## Account status

- Active, Inactive, and Closed are supported.
- The app blocks reopening a Closed account.
- It blocks closing an account with a non-zero balance.
- The `trg_account_status_before_update` trigger repeats these rules at database level.
- Only Active accounts can receive new deposits, withdrawals, or transfers.

## Loan workflow

```text
New application -> Pending
Pending -> Approved or Rejected
Approved + payment -> outstanding decreases
Outstanding reaches zero -> Closed by trigger
```

- A new loan always starts as `Pending`, regardless of what the user might want.
- The Approve/Reject buttons are POST routes protected by CSRF.
- Only a Pending loan can be approved or rejected; the row is locked during the decision.
- Payments are allowed only for Approved loans.
- `trg_loan_payment_before_insert` rejects overpayment.
- `trg_loan_payment_after_insert` changes the loan to `Closed` when total payments reach the loan amount.
- Outstanding is derived, not manually edited.

## Dashboard

The dashboard runs aggregate queries and `vw_branch_summary` on every request. It displays actual rows from MySQL. No customer or transaction numbers are hardcoded in the HTML.
