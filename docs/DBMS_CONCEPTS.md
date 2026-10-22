# Core DBMS Concepts & Theory — Project Kashi

Comprehensive reference guide explaining the database management system (DBMS) theory, mathematical foundations, and real-world implementation applied in **Project Kashi — Banking Management System**.

---

## 1. Relational Database Concepts & Keys

An RDBMS structures data into two-dimensional **relations (tables)** comprised of **tuples (rows)** and **attributes (columns)** conforming to strict schema definitions.

### Types of Database Keys in Project Kashi:
1. **Super Key**: Any set of attributes that uniquely identifies a row in a relation.
2. **Candidate Key**: A minimal super key containing no extraneous attributes.
   * In `CUSTOMER`: Both `CustomerID` and `Email` and `Mobile` are candidate keys.
3. **Primary Key (PK)**: The candidate key officially chosen by the database designer to identify rows.
   * Example: `CustomerID` in `CUSTOMER`, `AccountNumber` or `AccountID` in `ACCOUNT`.
4. **Alternate / Secondary Key**: Candidate keys not chosen as the primary key.
   * Example: `Mobile` and `Email` in `CUSTOMER`, `IFSCCode` in `BRANCH`. Enforced using `UNIQUE` constraints.
5. **Foreign Key (FK)**: An attribute or collection of attributes in one table that references the primary key of another table, creating an association and enforcing referential integrity.
   * Example: `BranchID` in `ACCOUNT` references `BRANCH(BranchID)`.
6. **Composite Key**: A primary key composed of two or more attributes.
   * Example: `(CustomerID, AccountID)` in `ACCOUNT_HOLDER`.

---

## 2. ACID Properties in Banking Systems

Financial systems require absolute transactional reliability governed by the **ACID** model:

| ACID Property | Theoretical Definition | Implementation in Project Kashi |
| :--- | :--- | :--- |
| **Atomicity** | The "all-or-nothing" rule. Either all updates in a transaction succeed and are committed, or if any part fails, the entire transaction is rolled back. | In an inter-account transfer, debited funds cannot vanish if crediting the recipient account fails. Flask wraps both statements within `conn.commit()` and triggers `conn.rollback()` upon any failure. |
| **Consistency** | Transactions must bring the database from one valid state to another, maintaining all schema invariants, constraints, and business rules. | Balance invariants (`Balance >= 0.00`), foreign key constraints, and check conditions are enforced by both MySQL database triggers and Flask backend validation. |
| **Isolation** | Concurrent execution of transactions yields the same system state as if transactions were executed serially. Intermediary uncommitted states remain invisible to other users. | MySQL's InnoDB storage engine implements row-level locking via `SELECT ... FOR UPDATE`. In transfers, accounts are locked in a deterministic numerical order to avoid deadlocks. |
| **Durability** | Once a transaction has committed, its changes are permanently recorded in non-volatile storage and survive subsequent system crashes or power failures. | InnoDB uses write-ahead logging (WAL) via its redo log (`ib_logfile`) and flush-to-disk mechanisms ensuring committed balances persist across restarts. |

---

## 3. Advanced Relational Database Constructs

### A. Database Views (`sql/views.sql`)
* **Definition**: A stored query that acts as a virtual table. Views contain no stored physical data of their own but dynamically present data from underlying base tables upon execution.
* **Benefits**:
  1. Simplifies complex multi-table joins for frontend queries.
  2. Enhances security by restricting user access to specific columns (data abstraction).
* **Views in Project Kashi**:
  - `vw_customer_account_summary`: Combines customer profile with accounts and home branch details.
  - `vw_account_transaction_history`: Formats ledger entries with account holder and branch context.
  - `vw_branch_performance_summary`: Consolidates branch deposit totals and employee counts.
  - `vw_loan_payment_summary`: Aggregates repayments and calculates remaining principal debt.

### B. Stored Functions (`sql/functions.sql`)
* **Definition**: A deterministic or non-deterministic routine that accepts input parameters, performs calculations, and returns exactly **one scalar value**.
* **Key Characteristic**: Can be directly invoked within SQL `SELECT`, `WHERE`, and `HAVING` clauses.
* **Functions in Project Kashi**:
  - `fn_calculate_customer_age(p_dob)`: Calculates age in years using `TIMESTAMPDIFF()`.
  - `fn_get_account_balance(p_account_id)`: Fetches real-time account balance.
  - `fn_calculate_monthly_emi(principal, rate, tenure)`: Computes reducing-balance monthly loan EMI.
  - `fn_get_total_customer_balance(customer_id)`: Sums portfolio balances across all accounts.

### C. Stored Procedures (`sql/procedures.sql`)
* **Definition**: Pre-compiled batches of SQL statements stored inside the database server that can take `IN`, `OUT`, and `INOUT` parameters, execute transactional blocks, and return status codes or result sets.
* **Key Characteristic**: Called using the `CALL` statement; ideal for encapsulating atomic multi-step business transactions.
* **Procedures in Project Kashi**:
  - `sp_deposit_funds`: Validates account, locks row, updates balance, and inserts transaction log.
  - `sp_withdraw_funds`: Checks balance sufficiency and executes debit under row lock.
  - `sp_transfer_funds`: Executes inter-account transfer with ordered locking and paired ledger insertion.
  - `sp_record_loan_payment`: Credits repayment installment and auto-closes loan if fully repaid.

### D. Database Triggers (`sql/triggers.sql`)
* **Definition**: A specialized set of instructions that automatically execute ("fire") in response to a specified event (`INSERT`, `UPDATE`, or `DELETE`) on a particular table.
* **Execution Timing**: `BEFORE` (ideal for validation and rejection) or `AFTER` (ideal for audit logging and cascading synchronization).
* **Triggers in Project Kashi**:
  - `trg_validate_transaction_before_insert`: Validates amount $> 0$ and account status before inserting.
  - `trg_prevent_negative_balance_before_update`: Mathematical safety guard preventing balances $< 0$.
  - `trg_audit_account_update`: Logs balance and status modifications to the `ACCOUNT_AUDIT` table.
  - `trg_prevent_loan_amount_mutation`: Disallows tampering with loan principals once active.

---

## 4. SQL Injection Prevention & Security

**SQL Injection** occurs when malicious user input containing SQL fragments is concatenated directly into a query string:
```python
# VULNERABLE CODE (NEVER USED IN PROJECT KASHI):
query = f"SELECT * FROM CUSTOMER WHERE Email = '{user_email}'"
# If user_email is: ' OR '1'='1 --
# The query bypasses authentication or dumps the entire database!
```

**Project Kashi Solution — Parameterized Queries**:
Every database query in `db.py` and `app.py` uses parameterized query placeholders (`%s`):
```python
# SECURE PARAMETERIZED EXECUTION (PROJECT KASHI STANDARD):
cursor.execute(
    "SELECT * FROM CUSTOMER WHERE Email = %s", 
    (user_email,)
)
```
In parameterized queries, the database engine compiles the SQL execution plan **before** binding user input. User input is treated strictly as literal data, making SQL injection mathematically impossible.
