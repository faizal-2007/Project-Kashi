# Application Workflow & Architecture — Project Kashi

This document details the three-layer architecture and operational workflows of **Project Kashi — Banking Management System**.

---

## 1. Three-Layer System Architecture

Project Kashi follows the classical enterprise **Three-Tier Architecture**:

```text
+-------------------------------------------------------------+
|             PRESENTATION LAYER (Frontend HTML/CSS)          |
|  - Raw semantic HTML5 forms & Jinja2 dynamic templates      |
|  - Custom CSS styling system with modern banking dashboard  |
|  - Minimal vanilla JS for state confirmation & alert timers |
+-------------------------------------------------------------+
                              |
                     HTTP POST / GET Requests
                              v
+-------------------------------------------------------------+
|             APPLICATION LOGIC LAYER (Python Flask)          |
|  - Flask WSGI web server & routing endpoints (app.py)       |
|  - Server-side input sanitization & business validation     |
|  - Atomic ACID transaction coordination & session handling  |
|  - Parameterized query dispatch layer (db.py)               |
+-------------------------------------------------------------+
                              |
                    MySQL Connector (TCP/IP 3306)
                              v
+-------------------------------------------------------------+
|              DATA STORAGE LAYER (MySQL 8.0 RDBMS)           |
|  - Relational tables in Third Normal Form (3NF)             |
|  - Constraints: PK, FK, UNIQUE, CHECK, NOT NULL             |
|  - Row-level pessimistic locking (SELECT ... FOR UPDATE)    |
|  - Triggers, Stored Procedures, Functions, and Views        |
+-------------------------------------------------------------+
```

---

## 2. Universal Data Lifecycle Flow

Every transactional operation in Project Kashi adheres to this strict sequence:

1. **User Form Submission**: The user fills in inputs on an HTML form and submits via HTTP POST.
2. **Flask Route Reception**: Flask intercepts the request at a designated endpoint (e.g., `@app.route('/transfer', methods=['POST'])`).
3. **Server-Side Validation**:
   - Compulsory presence checks (e.g., account IDs, non-empty fields).
   - Domain validation (e.g., amounts strictly $> 0$, 10-digit mobile number regex).
   - Logical validation (e.g., ensuring source account $\neq$ destination account).
4. **Database Transaction Initiation**: Flask opens a MySQL connection with `autocommit = False`.
5. **Pessimistic Row Locking**: Target account rows are locked using `SELECT ... FOR UPDATE`.
6. **Integrity Validation**: Account status (`'Active'`) and sufficient balance checks are verified against real-time database locks.
7. **Parameterized Execution**: SQL statements execute using `%s` placeholders, completely preventing SQL Injection vulnerabilities.
8. **Atomic Commit or Rollback**:
   - If **all** operations succeed $\rightarrow$ `conn.commit()`.
   - If **any** operation fails or throws an exception $\rightarrow$ `conn.rollback()`.
9. **Flash Notification & Redirect**: Flask renders a user-friendly flash alert and redirects to the updated account or ledger view.

---

## 3. Specific Operational Workflows

### A. Customer Registration Workflow
1. User enters demographic details in `customer_form.html`.
2. Flask validates name strings, 10-digit phone number, and standard email regex.
3. Flask verifies that neither `Email` nor `Mobile` already exists in `CUSTOMER`.
4. Executes:
   ```sql
   INSERT INTO CUSTOMER (FirstName, LastName, DateOfBirth, Gender, Mobile, Email, Address, City)
   VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
   ```
5. On success, redirects the user to `customer_detail.html` displaying their new `CustomerID`.

### B. Account Opening Workflow (Atomic Composite Operation)
1. User selects customer, branch, account type, and initial deposit amount.
2. Flask executes `open_account_transaction()` within a single transactional boundary:
   - Step 1: Generates a 10-digit account number.
   - Step 2: Inserts a record into `ACCOUNT` with the initial balance.
   - Step 3: Inserts an ownership row into `ACCOUNT_HOLDER` with `HolderType = 'Primary'`.
   - Step 4: If `opening_balance > 0`, inserts an initial `DEPOSIT` record into `BANK_TRANSACTION`.
   - Step 5: Issues `conn.commit()`.
3. If any step fails (e.g., foreign key violation), the entire sequence is rolled back, preventing orphaned accounts.

### C. Cash Deposit Workflow
1. User selects account and specifies deposit amount.
2. Flask validates `amount > 0`.
3. Locks the account row: `SELECT Balance, Status FROM ACCOUNT WHERE AccountID = %s FOR UPDATE`.
4. Verifies `Status == 'Active'`.
5. Increments balance: `UPDATE ACCOUNT SET Balance = Balance + %s WHERE AccountID = %s`.
6. Inserts immutable transaction entry:
   ```sql
   INSERT INTO BANK_TRANSACTION (AccountID, TransactionType, Amount, Description, ReferenceNumber, TransactionStatus)
   VALUES (%s, 'DEPOSIT', %s, %s, %s, 'SUCCESS');
   ```
7. Issues `conn.commit()`.

### D. Cash Withdrawal Workflow
1. User selects account and requests withdrawal amount.
2. Locks account row: `SELECT Balance, Status FROM ACCOUNT WHERE AccountID = %s FOR UPDATE`.
3. Verifies `Status == 'Active'`.
4. Verifies `Balance >= amount`. If insufficient, triggers immediate rollback and flashes an error message showing available balance.
5. Deducts balance: `UPDATE ACCOUNT SET Balance = Balance - %s WHERE AccountID = %s`.
6. Inserts `WITHDRAWAL` transaction into `BANK_TRANSACTION`.
7. Issues `conn.commit()`.

### E. Inter-Account Transfer Workflow (ACID Showcase)
1. User selects Source Account, Destination Account, and Transfer Amount.
2. **Deadlock Prevention**: Accounts are sorted by ID (`min_id = min(src, dest)`, `max_id = max(src, dest)`). Locks are acquired in strict ascending order:
   ```sql
   SELECT ... FROM ACCOUNT WHERE AccountID = min_id FOR UPDATE;
   SELECT ... FROM ACCOUNT WHERE AccountID = max_id FOR UPDATE;
   ```
3. Verifies both accounts exist and are in `'Active'` status.
4. Verifies source account has sufficient funds (`src_balance >= amount`).
5. Generates a shared common reference number (e.g., `TRF202610221600101X4`).
6. Executes dual updates:
   - Debit source: `UPDATE ACCOUNT SET Balance = Balance - %s WHERE AccountID = %s;`
   - Credit destination: `UPDATE ACCOUNT SET Balance = Balance + %s WHERE AccountID = %s;`
7. Inserts paired audit transactions sharing the identical `ReferenceNumber`:
   - `TRANSFER_OUT` row on source account.
   - `TRANSFER_IN` row on destination account.
8. Calls `conn.commit()`. If an exception occurs at any point, `conn.rollback()` restores both accounts to their original state.
