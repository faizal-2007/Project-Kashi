# DBMS Viva Voce Preparation Guide (45 Questions & Answers) — Project Kashi

Comprehensive viva questions with concise, beginner-friendly, and technically sound answers specifically tailored to **Project Kashi — Banking Management System**.

---

### Q1: What is the purpose of Project Kashi?
**Answer**: Project Kashi is an academic DBMS project demonstrating the end-to-end implementation of a relational database management system using MySQL 8.0 integrated with a Python Flask web application. It showcases entity-relationship modeling, database normalization (up to 3NF), relational constraints, ACID-compliant transactions, stored procedures, functions, views, triggers, and secure parameterized queries.

### Q2: What is the Three-Tier Architecture of this application?
**Answer**:
1. **Presentation Layer (Frontend)**: Semantic HTML5, CSS3, and vanilla JavaScript rendered dynamically via Flask Jinja2 templates.
2. **Application Logic Layer (Backend)**: Python with Flask (`app.py`), handling business validation, route dispatching, and transaction coordination.
3. **Data Layer (Storage)**: MySQL 8.0 relational database (`project_kashi`) managing relational tables, indexes, constraints, and procedural logic.

### Q3: What is the difference between an ER Diagram and a Relational Schema?
**Answer**: An ER diagram is a high-level conceptual model representing real-world entities, attributes, and relationships (including direct Many-to-Many connections). A Relational Schema is a logical/physical implementation design that represents data as two-dimensional tables with specific data types, primary keys, foreign keys, and decomposed associative bridge tables (such as `ACCOUNT_HOLDER`).

### Q4: Why is `ACCOUNT_HOLDER` needed instead of putting `CustomerID` in `ACCOUNT`?
**Answer**: Putting `CustomerID` inside `ACCOUNT` would enforce a 1:N relationship, restricting every account to only a single customer. In reality, retail banking requires **Many-to-Many** relationships: a customer can own multiple accounts, and multiple customers can share a single **Joint Account**. The bridge table `ACCOUNT_HOLDER` resolves this with a composite primary key `(CustomerID, AccountID)`.

### Q5: What is a Primary Key? Identify them in Project Kashi.
**Answer**: A Primary Key is an attribute or set of attributes that uniquely identifies each tuple (row) in a table and cannot contain `NULL` values. Examples: `CustomerID` in `CUSTOMER`, `BranchID` in `BRANCH`, `AccountID` in `ACCOUNT`, and `TransactionID` in `BANK_TRANSACTION`.

### Q6: What is a Foreign Key? Give an example from your project.
**Answer**: A Foreign Key is a field in a child table that points to the Primary Key of a parent table, establishing referential integrity. In `ACCOUNT`, `BranchID` is a Foreign Key referencing `BRANCH(BranchID)`.

### Q7: What is a Composite Key?
**Answer**: A primary key made up of two or more columns combined together to guarantee uniqueness. In `ACCOUNT_HOLDER`, the combination `(CustomerID, AccountID)` is a composite primary key.

### Q8: What is a Candidate Key vs. an Alternate Key?
**Answer**: A Candidate Key is any minimal column set that uniquely identifies a row. The candidate key selected by the designer becomes the Primary Key. The remaining candidate keys are called Alternate Keys (enforced using `UNIQUE` constraints, such as `Email` and `Mobile` in `CUSTOMER`, or `IFSCCode` in `BRANCH`).

### Q9: What is First Normal Form (1NF) and how did you apply it?
**Answer**: 1NF requires that all attribute values be atomic (indivisible) with no repeating groups or multi-valued lists. In Project Kashi, addresses are split into atomic columns (`Address`, `City`, `State`), and multiple account holders are split into separate rows in `ACCOUNT_HOLDER` rather than comma-separated strings.

### Q10: What is Second Normal Form (2NF)?
**Answer**: A table is in 2NF if it is in 1NF and contains no **partial functional dependencies**—meaning no non-prime attribute depends on only a subset of a composite candidate key. In `ACCOUNT_HOLDER(CustomerID, AccountID)`, non-prime attributes like `HolderType` depend on the *entire* composite key.

### Q11: What is Third Normal Form (3NF)?
**Answer**: A table is in 3NF if it is in 2NF and contains no **transitive dependencies** ($X \rightarrow Y \rightarrow Z$). In `ACCOUNT`, we store `BranchID` as a foreign key rather than storing `BranchName` and `IFSCCode` directly, preventing `AccountID -> BranchID -> BranchName`.

### Q12: What are Insertion, Update, and Deletion Anomalies?
**Answer**:
* **Insertion Anomaly**: Inability to record data about one entity without including unrelated data of another entity.
* **Update Anomaly**: Redundant data requiring updates across multiple rows, risking inconsistency if partially completed.
* **Deletion Anomaly**: Unintentional loss of unintended data when deleting a record (e.g., losing customer KYC history when closing their only account).

### Q13: What does ACID stand for?
**Answer**:
* **Atomicity**: All updates in a transaction succeed together, or all fail and are rolled back.
* **Consistency**: The database transitions from one valid state to another without violating constraints.
* **Isolation**: Concurrent transactions do not interfere with each other or expose uncommitted data.
* **Durability**: Committed updates permanently persist in non-volatile storage despite power or system failures.

### Q14: How does Project Kashi demonstrate Atomicity?
**Answer**: During fund transfer or account opening, multiple SQL queries execute sequentially (`UPDATE`, `INSERT`). If any query fails, Python catches the exception and immediately invokes `conn.rollback()`, ensuring changes are reverted completely.

### Q15: How is Isolation maintained during money transfers?
**Answer**: Using MySQL's InnoDB row-level locking via `SELECT ... FOR UPDATE`. Accounts are locked in ascending order of their IDs (`min_id` then `max_id`) so that no concurrent process can read or mutate the balance mid-transfer.

### Q16: Why lock accounts in numerical order during a transfer?
**Answer**: To prevent **deadlocks**. If User 1 transfers from Account 1 to Account 2 (locking 1 then 2) while User 2 concurrently transfers from Account 2 to Account 1 (locking 2 then 1), both threads could wait indefinitely for each other. Locking in ascending ID order guarantees both threads request locks in the identical sequence.

### Q17: What is the difference between `COMMIT` and `ROLLBACK`?
**Answer**: `COMMIT` permanently saves all modifications made during the current transaction to disk. `ROLLBACK` undoes all modifications made since the start of the transaction, restoring the database to its pre-transaction state.

### Q18: What is SQL Injection and how is it prevented in your code?
**Answer**: SQL Injection occurs when malicious user input containing SQL code is concatenated directly into a query. Project Kashi completely prevents SQL Injection by using **parameterized queries** with `%s` placeholders (`cursor.execute(sql, (param1, param2))`). The SQL query structure is compiled first, and parameters are treated purely as literal values.

### Q19: What is a Database View and why did you use it?
**Answer**: A View is a virtual table defined by a stored query that contains no physical data of its own. In Project Kashi, views like `vw_customer_account_summary` simplify queries for complex multi-table joins and encapsulate reporting logic.

### Q20: What is a Stored Function? How does it differ from a Stored Procedure?
**Answer**: A Stored Function returns exactly one scalar value and can be embedded directly within `SELECT` or `WHERE` clauses (e.g., `fn_calculate_customer_age(DateOfBirth)`). A Stored Procedure is invoked with `CALL`, can return zero or multiple values through `OUT` parameters or result sets, and can manage explicit transaction blocks (`START TRANSACTION`, `COMMIT`).

### Q21: What is a Database Trigger? Which triggers did you create?
**Answer**: A trigger is procedural SQL code that automatically executes before or after an `INSERT`, `UPDATE`, or `DELETE` event on a table. In Project Kashi:
1. `trg_validate_transaction_before_insert`: Enforces positive amounts and blocks transactions on closed accounts.
2. `trg_prevent_negative_balance_before_update`: Mathematical safety guard preventing balances from falling below zero.
3. `trg_audit_account_update`: Automatically logs balance changes to an `ACCOUNT_AUDIT` table.
4. `trg_prevent_loan_amount_mutation`: Blocks tampering with active loan principal amounts.

### Q22: What is the difference between `INNER JOIN` and `LEFT JOIN`?
**Answer**: `INNER JOIN` returns only records that have matching values in both tables. `LEFT JOIN` returns all records from the left table, along with matched values from the right table, or `NULL` if no match exists (used in Problem 8 to find customers without accounts).

### Q23: What is the difference between `WHERE` and `HAVING`?
**Answer**: `WHERE` filters individual rows *before* any grouping occurs. `HAVING` filters aggregated groups *after* the `GROUP BY` clause has been evaluated (e.g., `HAVING COUNT(ah.AccountID) > 1`).

### Q24: What is a Subquery? Give an example from your project.
**Answer**: A query nested inside another query. In Business Problem 5, a scalar subquery `(SELECT AVG(Balance) FROM ACCOUNT)` calculates the overall bank average balance, and the outer query filters accounts whose balance exceeds this number.

### Q25: What is a Correlated Subquery?
**Answer**: A subquery that references columns from the outer query for each row processed. In Business Problem 10, the inner subquery finds the maximum balance for the specific branch of the outer query's current row.

### Q26: Why is `DECIMAL(15,2)` used for money instead of `FLOAT` or `DOUBLE`?
**Answer**: `FLOAT` and `DOUBLE` are approximate floating-point types subject to binary rounding errors (e.g., $0.1 + 0.2 = 0.30000000000000004$). `DECIMAL` is an exact fixed-point numerical representation critical for financial accounting where rounding discrepancies are unacceptable.

### Q27: What is the purpose of `CHECK` constraints in MySQL?
**Answer**: A `CHECK` constraint specifies a boolean condition that every row in the table must satisfy. Examples: `CHECK (Balance >= 0.00)`, `CHECK (Amount > 0.00)`, and `CHECK (Salary > 0)`.

### Q28: What is an index and why is it useful?
**Answer**: An index is an auxiliary data structure (typically a B-Tree) that speeds up data retrieval on frequently queried columns without scanning the entire table. We indexed Foreign Keys (`AccountID`, `BranchID`, `CustomerID`) and `ReferenceNumber`.

### Q29: What happens when an account is marked 'Closed'?
**Answer**: In accordance with regulatory banking compliance, we do not physically delete the account row (`DELETE FROM ACCOUNT`), because that would destroy historical ledger audits. Instead, its `Status` is set to `'Closed'`, and database triggers and application code disallow subsequent deposits or withdrawals.

### Q30: What is the purpose of `ReferenceNumber` in `BANK_TRANSACTION`?
**Answer**: It acts as a reconciliation tracking code. For inter-account transfers, both the `TRANSFER_OUT` debit row and the `TRANSFER_IN` credit row share the identical `ReferenceNumber`, linking both halves of the transfer for audit.

### Q31: How is loan repayment handled in your project?
**Answer**: When an installment is paid via `/loans/<id>/payments`, a record is inserted into `LOAN_PAYMENT`. If the sum of repayments equals or exceeds the original sanctioned loan principal, the system automatically transitions the loan status from `'Active'` to `'Closed'`.

### Q32: What is the role of Flask Jinja2 templating?
**Answer**: Jinja2 dynamically renders server-side data from Python into HTML pages using template inheritance (`base.html`), variables (`{{ customer.FirstName }}`), loops (`{% for a in accounts %}`), and custom filters (`{{ balance | currency }}`).

### Q33: How does the application prevent negative balances?
**Answer**: Through defense in depth:
1. Frontend checks amount $> 0$.
2. Flask backend validates available balance before issuing updates.
3. Database `CHECK (Balance >= 0.00)` constraint blocks negative numbers.
4. Database trigger `trg_prevent_negative_balance_before_update` raises SQLSTATE `'45000'` if violated.

### Q34: What is the purpose of the `.env` file?
**Answer**: It separates configuration and sensitive credentials (such as database passwords and secret keys) from source code, preventing security breaches when pushing to public repositories.

### Q35: What is the role of `mysql-connector-python`?
**Answer**: It is the official MySQL database driver for Python that implements the Python DB-API 2.0 specification, enabling Flask to send SQL commands and receive dictionary results over TCP/IP.

### Q36: What is a Self-Join? Give an example from your project.
**Answer**: A self-join is a regular join in which a table is joined with itself. In Business Problem 15, `BANK_TRANSACTION` is joined with itself on `ReferenceNumber` to match `TRANSFER_OUT` and `TRANSFER_IN` pairs.

### Q37: How do you handle database disconnection in Flask?
**Answer**: The app checks connectivity via `test_connection()`. If the database is offline, routes catch connection errors gracefully, display an offline warning badge on the dashboard, and inform the user how to configure their `.env` file without crashing with a 500 stacktrace.

### Q38: What is referential action `ON DELETE RESTRICT`?
**Answer**: It rejects the deletion of a parent record if any child records currently reference it. For example, a `BRANCH` cannot be deleted if active accounts or employees reference its `BranchID`.

### Q39: What is referential action `ON DELETE CASCADE`?
**Answer**: When a parent record is deleted, all dependent child rows referencing it are automatically deleted as well. In `ACCOUNT_HOLDER`, deleting a customer or account cleans up their association record.

### Q40: What is the difference between `CHAR` and `VARCHAR`?
**Answer**: `CHAR` is fixed-length (padded with spaces if shorter), while `VARCHAR` is variable-length (only uses storage required for actual characters plus 1-2 length bytes). `VARCHAR` is used for dynamic text like names and emails.

### Q41: What is the difference between `DATETIME` and `TIMESTAMP` in MySQL?
**Answer**: `DATETIME` stores dates and times as literal numbers from 1000 to 9999 without timezone awareness. `TIMESTAMP` stores seconds since the Unix Epoch (UTC) and converts to the connection's current timezone.

### Q42: What is an Aggregate Function? Name five used in your project.
**Answer**: A function that performs a calculation on multiple values and returns a single summary value. Examples: `COUNT()`, `SUM()`, `AVG()`, `MIN()`, and `MAX()`.

### Q43: What is the difference between `DROP`, `TRUNCATE`, and `DELETE`?
**Answer**:
* `DELETE`: DML command that removes specific rows based on a `WHERE` clause and can be rolled back.
* `TRUNCATE`: DDL command that deallocates all table data pages rapidly and resets auto-increment counters.
* `DROP`: DDL command that removes both table data and the table schema definition permanently from the database.

### Q44: What are the main limitations of Project Kashi?
**Answer**: It is designed as an educational simulation. It does not integrate external payment gateways (e.g., UPI, IMPS, SWIFT), does not support production multi-factor authentication (MFA), and uses a single local MySQL server rather than distributed read replicas.

### Q45: How would you scale this application in the future?
**Answer**:
1. Implement JWT / OAuth2 authentication with Role-Based Access Control (RBAC).
2. Integrate Redis for session caching and caching branch lookups.
3. Implement database replication with read-only replicas for reporting queries.
4. Add automated interest calculation cron jobs for savings accounts.
