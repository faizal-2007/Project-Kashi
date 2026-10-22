# PROJECT REPORT — PROJECT KASHI: BANKING MANAGEMENT SYSTEM

**Academic B.Tech Computer Science and Engineering (CSE) DBMS Project**  
**Submission Date: 28 October 2026**

---

## 1. Title
**Project Kashi: A Normalized, ACID-Compliant Banking Management System Built with Python Flask and MySQL 8.0**

---

## 2. Abstract
Modern banking institutions require highly structured, consistent, and secure relational database architectures capable of enforcing absolute financial integrity. **Project Kashi** is an academic DBMS application developed for a B.Tech Computer Science student to demonstrate practical mastery of database concepts. Built using Python Flask and MySQL 8.0, the system features eight normalized tables adhering to Third Normal Form (3NF). It demonstrates Entity-Relationship modeling, primary/foreign key relationships, cardinalities, ACID transaction management with row-level locking, user-defined stored functions, procedures, triggers, views, and parameterized queries. The application delivers a clean institutional banking interface rendered with semantic HTML5 and vanilla CSS.

---

## 3. Introduction
Banking systems represent the quintessential use-case for Relational Database Management Systems (RDBMS). Unlike eventual consistency NoSQL systems, banking ledgers demand absolute transactional atomicity and mathematical consistency: money debited from one account must never disappear if crediting the destination fails. Project Kashi bridges academic database theory with production-style software engineering by pairing an expressive MySQL 8.0 schema with a Python Flask web application.

---

## 4. Problem Statement
Many student database projects rely on simplified flat tables, client-side calculations, or loose ORMs that obscure underlying SQL mechanisms. Such approaches often neglect:
1. Multi-account ownership and joint account modeling (M:N relationships).
2. Proper database normalization, leading to insertion, update, and deletion anomalies.
3. Concurrency control and race condition prevention during fund transfers.
4. Database-level invariant enforcement using triggers and constraints.
Project Kashi solves this by implementing an explicit, transparent, and auditable DBMS architecture directly in raw SQL and parameterized Python logic.

---

## 5. Project Objectives
* Design and implement an 8-table relational database normalized to Third Normal Form (3NF).
* Model Many-to-Many relationships between customers and accounts using an associative bridge table (`ACCOUNT_HOLDER`).
* Guarantee ACID properties across all deposit, withdrawal, and fund transfer operations.
* Avoid race conditions and deadlocks using deterministic ordered row-level locking (`SELECT ... FOR UPDATE`).
* Implement MySQL stored routines, views, and automated database triggers.
* Formulate at least 10 real-world analytical SQL business problems demonstrating complex joins, aggregations, and subqueries.
* Build an intuitive, responsive web application using raw HTML5 and CSS without frontend framework bloat.
* Provide comprehensive automated testing and academic documentation.

---

## 6. Project Scope
The project encompasses retail banking operations including:
* Customer registration, profile management, and KYC tracking.
* Account opening across multiple product types (Savings, Current, Salary) with initial deposits.
* Single and joint account ownership assignments.
* Counter deposits and balance updates with immutable transaction ledger entries.
* Cash and ATM withdrawals with balance sufficiency verification.
* Inter-account electronic fund transfers (EFT) sharing paired reference numbers.
* Loan origination, interest calculation, tenure tracking, and installment repayments with automatic loan closure.
* Branch network administration and employee personnel management.
* Out of scope: External payment gateway integrations (UPI/SWIFT), real-money hardware integration, and multi-tenant cloud clustering.

---

## 7. Technology Stack
* **Database Engine**: MySQL Server 8.0+ (InnoDB Storage Engine).
* **Backend Framework**: Python 3.10+ with Flask 3.0+.
* **Database Driver**: `mysql-connector-python` (Official Oracle driver).
* **Frontend**: Semantic HTML5, CSS3 (Executive Institutional Banking theme), minimal vanilla JavaScript.
* **Environment Configuration**: `python-dotenv`.
* **Testing Framework**: `pytest`.
* **Documentation**: Markdown, Mermaid Diagrams.

---

## 8. System Architecture
Project Kashi follows a modular architecture separating client presentation, server business rules, and database persistence. The application coordinates all database mutations through dedicated Python transaction routines in `db.py`, ensuring application logic and database state remain tightly synchronized.

---

## 9. Three-Layer Application Architecture
1. **Presentation Layer (Frontend)**: User-facing HTML templates styled with `style.css`. Renders dashboard indicators, form controls, and transaction tables dynamically using Jinja2 expressions.
2. **Application Logic Layer (Backend)**: Flask application (`app.py`) listening on HTTP port 5000. Validates inputs, handles HTTP routing, orchestrates transaction boundaries, and prevents SQL injection.
3. **Data Layer (Database)**: MySQL 8.0 storing physical data pages on disk, enforcing relational integrity via foreign keys, triggers, and InnoDB ACID logs (write-ahead redo log and undo log).

---

## 10. ER Diagram
The conceptual Entity-Relationship diagram captures eight entities: `BRANCH`, `EMPLOYEE`, `CUSTOMER`, `ACCOUNT`, `ACCOUNT_HOLDER`, `BANK_TRANSACTION`, `LOAN`, and `LOAN_PAYMENT`. Complete Mermaid diagrams are provided in [`docs/ER_DIAGRAM.md`](ER_DIAGRAM.md) and [`docs/ER_DIAGRAM.mmd`](ER_DIAGRAM.mmd).

---

## 11. Entity Definitions
1. **BRANCH**: Represents an administrative physical branch center with IFSC routing.
2. **EMPLOYEE**: Bank staff assigned to specific branches with designations and salaries.
3. **CUSTOMER**: Banking clients with personal demographics and contact details.
4. **ACCOUNT**: Deposit accounts with balances, types, and operational statuses.
5. **ACCOUNT_HOLDER**: Associative bridge entity connecting customers with accounts.
6. **BANK_TRANSACTION**: Historical ledger recording financial account debits and credits.
7. **LOAN**: Credit contracts sanctioned by branches to borrowers.
8. **LOAN_PAYMENT**: Installments and repayments against active loan contracts.

---

## 12. Attribute Definitions
Attributes are strictly specified with domain boundaries (e.g., `Salary` $> 0$, `Balance` $\ge 0$, `Email` unique, 10-digit `Mobile` numbers). Detailed attribute listings are documented in [`docs/DATA_DICTIONARY.md`](DATA_DICTIONARY.md).

---

## 13. Data Types
* `INT AUTO_INCREMENT`: Efficient 4-byte integer surrogate primary keys.
* `VARCHAR(N)`: Variable-length strings for text, names, emails, and street addresses.
* `DECIMAL(15, 2)`: Fixed-point exact numeric type for all balances and amounts, avoiding IEEE floating-point rounding inaccuracies.
* `ENUM(...)`: Strict enumeration for constrained states (Account types, statuses, genders, payment modes).
* `DATE` & `DATETIME`: Calendar dates (`YYYY-MM-DD`) and full ISO timestamps.

---

## 14. Primary Keys
* `BRANCH.BranchID`
* `EMPLOYEE.EmployeeID`
* `CUSTOMER.CustomerID`
* `ACCOUNT.AccountID`
* `ACCOUNT_HOLDER.(CustomerID, AccountID)` (Composite PK)
* `BANK_TRANSACTION.TransactionID`
* `LOAN.LoanID`
* `LOAN_PAYMENT.PaymentID`

---

## 15. Foreign Keys
All foreign keys utilize `ON UPDATE CASCADE` to propagate primary key shifts and `ON DELETE RESTRICT` to protect financial audit trails, with the exception of `ACCOUNT_HOLDER` which uses `ON DELETE CASCADE` to clean up association links upon account closure.

---

## 16. Constraints
1. **Entity Integrity**: Guaranteed via Primary Keys and `AUTO_INCREMENT`.
2. **Referential Integrity**: Guaranteed via Foreign Keys referencing existing parent rows.
3. **Domain Integrity**: Enforced via `CHECK` expressions (`chk_acc_balance`, `chk_tx_amount`, `chk_loan_rate`), `NOT NULL`, and `ENUM` values.
4. **Uniqueness**: Enforced via `UNIQUE` constraints on `IFSCCode`, `AccountNumber`, `Email`, and `Mobile`.

---

## 17. Relationships and Cardinalities
* `BRANCH` to `EMPLOYEE`: $1 : N$ (Mandatory on Employee, Optional on Branch).
* `BRANCH` to `ACCOUNT`: $1 : N$ (Mandatory on Account, Optional on Branch).
* `CUSTOMER` to `ACCOUNT`: $M : N$ (Resolved via `ACCOUNT_HOLDER`).
* `CUSTOMER` to `LOAN`: $1 : N$.
* `BRANCH` to `LOAN`: $1 : N$.
* `ACCOUNT` to `BANK_TRANSACTION`: $1 : N$.
* `LOAN` to `LOAN_PAYMENT`: $1 : N$.
Full cardinality tables are documented in [`docs/RELATIONSHIPS_AND_CARDINALITY.md`](RELATIONSHIPS_AND_CARDINALITY.md).

---

## 18. Relational Schema
The formal schema representation is documented in [`docs/RELATIONAL_SCHEMA.md`](RELATIONAL_SCHEMA.md), detailing underline primary keys and foreign key reference mappings.

---

## 19. Normalization
The database was systematically normalized from Unnormalized Form (UNF) through First Normal Form (1NF: atomic values, no repeating groups), Second Normal Form (2NF: removal of partial dependencies on composite keys), and Third Normal Form (3NF: elimination of transitive dependencies such as branch attributes from accounts). Detailed derivations appear in [`docs/NORMALIZATION.md`](NORMALIZATION.md).

---

## 20. Database Implementation
The physical database is defined in `sql/schema.sql` and populated with realistic test records in `sql/sample_data.sql`. It leverages MySQL 8.0's InnoDB storage engine with `utf8mb4` encoding.

---

## 21. Flask Backend Implementation
The application logic in `app.py` exposes 15 dedicated endpoints covering customer lifecycle, account management, deposit/withdrawal transactions, fund transfers, employee/branch management, and loan servicing.

---

## 22. HTML Frontend Implementation
Templates located in `templates/` utilize Jinja2 template inheritance extending `templates/base.html`. Pages include dashboard metric cards, search inputs, responsive data tables, status badges, and transaction confirmation prompts.

---

## 23. Database Connectivity
Managed through `db.py` using `mysql.connector`. Connections are acquired on demand and safely closed within `finally` blocks. Database connection state is continuously monitored; if MySQL is unavailable, the application presents a friendly notice and offline mode rather than an unhandled 500 error.

---

## 24. Customer Registration Workflow
HTML Form $\rightarrow$ Flask `POST /customers/register` $\rightarrow$ Regex validation (10-digit phone, RFC-compliant email) $\rightarrow$ Uniqueness check $\rightarrow$ Parameterized `INSERT INTO CUSTOMER` $\rightarrow$ Redirect to `customer_detail.html`.

---

## 25. Account-Opening Workflow
HTML Form $\rightarrow$ Flask `POST /accounts/open` $\rightarrow$ Atomic transaction: generates 10-digit account number $\rightarrow$ inserts `ACCOUNT` $\rightarrow$ inserts `ACCOUNT_HOLDER` $\rightarrow$ if initial balance $> 0$, records initial `DEPOSIT` in `BANK_TRANSACTION` $\rightarrow$ `conn.commit()`.

---

## 26. Deposit Workflow
Form selection $\rightarrow$ validation `amount > 0` $\rightarrow$ `SELECT Balance, Status FROM ACCOUNT FOR UPDATE` $\rightarrow$ check `Status == 'Active'` $\rightarrow$ `UPDATE ACCOUNT SET Balance = Balance + amount` $\rightarrow$ `INSERT INTO BANK_TRANSACTION` $\rightarrow$ `conn.commit()`.

---

## 27. Withdrawal Workflow
Form selection $\rightarrow$ validation `amount > 0` $\rightarrow$ `SELECT Balance, Status FROM ACCOUNT FOR UPDATE` $\rightarrow$ check available balance $\ge$ amount $\rightarrow$ `UPDATE ACCOUNT SET Balance = Balance - amount` $\rightarrow$ `INSERT INTO BANK_TRANSACTION` $\rightarrow$ `conn.commit()`.

---

## 28. Transfer Workflow
Selection of source and destination $\rightarrow$ verification `src != dest` $\rightarrow$ **Ordered row locking** (`min(src, dest)` then `max(src, dest)`) to prevent deadlocks $\rightarrow$ balance sufficiency check $\rightarrow$ dual balance update $\rightarrow$ paired insertions of `TRANSFER_OUT` and `TRANSFER_IN` sharing identical `ReferenceNumber` $\rightarrow$ `conn.commit()`.

---

## 29. SQL Business Queries
Fifteen analytical queries are defined in `sql/business_queries.sql` and interactively executable via the web UI at `/business-queries`, covering multi-table joins, conditional aggregations, subqueries, and set differences.

---

## 30. Views
Defined in `sql/views.sql`:
1. `vw_customer_account_summary`: Combines customer profiles with linked accounts and branch data.
2. `vw_account_transaction_history`: Formats chronological statement entries.
3. `vw_branch_performance_summary`: Aggregates active accounts, total deposit volume, and staff counts.
4. `vw_loan_payment_summary`: Computes total repaid amounts and outstanding loan principal.

---

## 31. Stored Functions
Defined in `sql/functions.sql`:
1. `fn_calculate_customer_age(p_dob)`: Calculates age in years.
2. `fn_get_account_balance(p_account_id)`: Fetches real-time account balance.
3. `fn_calculate_monthly_emi(principal, rate, tenure)`: Implements standard reducing-balance EMI formula.
4. `fn_get_total_customer_balance(customer_id)`: Aggregates total customer balance across multiple accounts.

---

## 32. Stored Procedures
Defined in `sql/procedures.sql`:
1. `sp_deposit_funds`: Encapsulates atomic deposit with row-level locking.
2. `sp_withdraw_funds`: Executes atomic withdrawal with balance validation.
3. `sp_transfer_funds`: Implements deadlock-free inter-account fund transfer.
4. `sp_get_customer_portfolio`: Retrieves multi-table customer portfolio.
5. `sp_record_loan_payment`: Records installment and auto-closes loan upon full payoff.

---

## 33. Triggers
Defined in `sql/triggers.sql`:
1. `trg_validate_transaction_before_insert`: Enforces positive amounts and blocks inactive accounts.
2. `trg_prevent_negative_balance_before_update`: Prevents account balances from falling below zero.
3. `trg_audit_account_update`: Records balance and status alterations to `ACCOUNT_AUDIT`.
4. `trg_prevent_loan_amount_mutation`: Protects active loan principal amounts from modification.

---

## 34. ACID Properties and Transactions
Detailed explanation of how MySQL InnoDB and Python Flask coordinate transactions to satisfy Atomicity, Consistency, Isolation, and Durability, with specific examples from fund transfer workflows.

---

## 35. Security Considerations
* **Parameterized Queries**: 100% of SQL statements utilize parameter placeholders (`%s`), preventing SQL injection.
* **Separation of Secrets**: Database credentials and secret keys reside in `.env`, excluded from version control via `.gitignore`.
* **State Mutation via POST**: Financial balance updates require HTTP POST with client confirmation prompts.
* **Graceful Degradation**: Database errors are caught and surfaced via friendly user alerts rather than exposing raw server stack traces.

---

## 36. Testing and Results
Automated test suite (`tests/test_app.py`) includes 25 unit and integration test cases covering route rendering, 404 handling, input validation, and transaction business logic. All 25 tests pass in approximately 1.1 seconds.

---

## 37. Screenshots
A directory (`screenshots/`) and capture checklist ([`docs/SCREENSHOTS.md`](SCREENSHOTS.md)) outline 13 recommended screenshots documenting the working system.

---

## 38. Limitations
As an academic project:
* Operates on a single local MySQL server without geo-distributed replication.
* Does not connect to live clearing houses (RBI / NPCI / NEFT networks).
* Uses basic session mechanisms rather than enterprise single sign-on (SSO) or multi-factor authentication (MFA).

---

## 39. Future Enhancements
* Role-based access control (RBAC) separating Teller, Branch Manager, and Customer roles.
* Customer net banking portal with personal transaction downloads (PDF/CSV passbook exports).
* Automated interest calculation scheduled tasks (cron jobs).
* Containerization using Docker and Docker Compose.

---

## 40. Conclusion
Project Kashi successfully demonstrates how core DBMS theory directly translates into reliable, secure software engineering. By combining normalized relational schemas, strict integrity constraints, ACID-compliant transaction boundaries, procedural database routines, and secure parameterized queries, the project provides a comprehensive academic banking management system ready for evaluation.
