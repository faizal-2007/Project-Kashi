# DBMS Concepts Demonstrated

| Concept | Where it appears |
|---|---|
| Entity | CUSTOMER, BRANCH, ACCOUNT, LOAN, etc. |
| Attribute | Columns such as Mobile, Balance, LoanAmount. |
| Relationship | ACCOUNT_HOLDER connects CUSTOMER and ACCOUNT. |
| Cardinality | One-to-many and many-to-many relationships documented in `RELATIONSHIPS_AND_CARDINALITY.md`. |
| Primary key | Every table has a PK; ACCOUNT_HOLDER uses a composite PK. |
| Foreign key | EMPLOYEE, ACCOUNT, ACCOUNT_HOLDER, BANK_TRANSACTION, LOAN, LOAN_PAYMENT. |
| Composite key | `ACCOUNT_HOLDER(CustomerID, AccountID)`. |
| Unique constraint | Customer mobile/email, IFSC, account number, references. |
| CHECK constraint | Positive amounts, non-negative balances, interest range, IFSC/mobile pattern. |
| DEFAULT | RegistrationDate, OpeningDate, TransactionDate, Status. |
| AUTO_INCREMENT | All surrogate IDs. |
| Referential integrity | `ON DELETE RESTRICT` and `ON UPDATE CASCADE`. |
| Normalization | 1NF, 2NF, 3NF analysis with actual tables. |
| JOIN | Customer/account, account/branch, transaction/account, loan/customer. |
| LEFT JOIN | Customers without accounts, branches without employees/accounts, loans without payments. |
| GROUP BY | Balances by branch, loans by type, monthly transaction totals. |
| HAVING | Customers with more than one account; above-average combined balances. |
| Aggregate functions | COUNT, SUM, AVG. |
| Subquery | Highest-balance account holders; customer account counts; customers above average balance. |
| View | 6 views used for reporting. |
| Stored function | Age, account tenure, outstanding loan, branch balance. |
| Stored procedure | Customer accounts, account statement, branch summary, loan approval. |
| Trigger | Transaction immutability, active-account check, primary-holder rule, loan payment rules, account status rules. |
| Transaction | Deposit, withdrawal, transfer, account opening, loan payment, status updates. |
| ACID | See below. |
| Row locking | `SELECT ... FOR UPDATE` on account and loan rows. |
| SQL injection prevention | Parameterized queries throughout. |
| Input validation | Both backend Python and database constraints. |
| CSRF protection | Flask-WTF on every POST form. |
| Indexing | Transaction account/date, transfer group, loan payments, unique keys. |

## ACID in Project Kashi

### Atomicity

A transfer changes two balances and inserts two transaction rows. If any step fails, the MySQL transaction rolls back all four changes. Account opening similarly commits the account, holder, and opening transaction together.

### Consistency

Constraints protect valid states:
- no duplicate mobile/email/IFSC/account number;
- no negative balance;
- no non-positive transaction amount;
- no transaction on an inactive/closed account;
- no overpaid loan;
- no second primary holder.

Application rules add business consistency: source must have sufficient funds, accounts must be distinct, and closed accounts cannot be reopened.

### Isolation

InnoDB provides transaction isolation. The application explicitly uses `SELECT ... FOR UPDATE` so two simultaneous withdrawals or transfers cannot both read the same old balance and overwrite each other. Transfer rows are locked in a consistent order to reduce deadlock.

### Durability

After `COMMIT`, MySQL writes the changes to its InnoDB storage and transaction log. The Flask process does not keep the authoritative balance in memory; it reads it from MySQL.

## SQL injection example

Unsafe (not used):

```python
cursor.execute("SELECT * FROM CUSTOMER WHERE Mobile = '" + mobile + "'")
```

Safe (used):

```python
cursor.execute("SELECT * FROM CUSTOMER WHERE Mobile = %s", (mobile,))
```

The connector sends the value separately from the SQL text. The database does not interpret user text as SQL syntax.

## Why backend and database validation are both needed

HTML validation can be bypassed with a crafted request. Flask validation catches bad input before SQL. Database constraints catch invalid data even if a future script or direct SQL statement bypasses Flask. Together they protect the data.
