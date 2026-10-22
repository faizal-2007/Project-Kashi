# Database Normalization & Integrity — Project Kashi

This document explains the mathematical theory, functional dependencies, and practical steps undertaken to normalize the **Project Kashi — Banking Management System** relational database into **Third Normal Form (3NF)**.

---

## 1. Why Customer Information Should Not Be Repeated in Account Records

Consider a naive banking design where customer demographics (Name, DOB, Mobile, Address, City) are directly stored in an `ACCOUNT` record:

```text
ACCOUNT_NAIVE (AccountNumber, CustomerName, Mobile, Email, Address, City, Balance, BranchName, BranchAddress)
```

This unnormalized design introduces three critical database anomalies:

1. **Insertion Anomaly**: If a customer registers with the bank but has not yet opened an account, we cannot store their personal information without inserting dummy null values for `AccountNumber` and `Balance`.
2. **Update Anomaly**: If a customer moves to a new city and has 4 accounts (Savings, Current, Fixed, Salary), their address must be updated across all 4 separate rows. If one row fails to update, the database falls into an inconsistent state.
3. **Deletion Anomaly**: If a customer closes their only bank account, deleting the account record inadvertently erases all customer contact history, KYC verification, and personal identity data from the bank's records!

By isolating entities into distinct relations (`CUSTOMER`, `ACCOUNT`, and `ACCOUNT_HOLDER`), each real-world fact is recorded in exactly one place.

---

## 2. Normalization Progression Step-by-Step

### A. Unnormalized Form (UNF)
In UNF, records contain repeating groups and non-atomic composite fields:
* Example: `AccountHolders` column storing comma-separated values: `"Aarav Pandey, Divya Tripathi"`.
* Example: A single row containing an array of multiple transactions `[TXN01, TXN02, TXN03]`.

### B. First Normal Form (1NF)
**Rules for 1NF**:
1. All attributes must contain atomic (indivisible) values.
2. There must be no repeating groups or multi-valued columns.
3. Each table must have a designated primary key.

**Application in Project Kashi**:
* Decomposed comma-separated holder names into individual atomic rows in `ACCOUNT_HOLDER`.
* Split full addresses into distinct columns (`Address`, `City`, `State`).
* Split transactions into discrete atomic entries in `BANK_TRANSACTION`.

### C. Second Normal Form (2NF)
**Rules for 2NF**:
1. The table must already satisfy 1NF.
2. No non-prime attribute may be **partially functionally dependent** on any candidate key (applies to relations with composite candidate keys).

**Application in Project Kashi**:
Consider the associative table `ACCOUNT_HOLDER`:
* Candidate Key: Composite Key `(CustomerID, AccountID)`.
* Functional Dependencies:
  * `{CustomerID, AccountID} -> HolderSince, HolderType` (Fully dependent on the whole key).
  * If we had mistakenly put `CustomerName` in this table, `{CustomerID} -> CustomerName` would be a **partial dependency**, violating 2NF.
  * In Project Kashi, `CustomerName` resides strictly in `CUSTOMER`, ensuring complete 2NF compliance.

### D. Third Normal Form (3NF)
**Rules for 3NF**:
1. The table must already satisfy 2NF.
2. There must be no **transitive functional dependencies** (no non-prime attribute should determine another non-prime attribute: $X \rightarrow Y \rightarrow Z$).

**Application in Project Kashi**:
Consider the `ACCOUNT` relation:
* In a non-3NF table, one might include branch details:
  * `AccountID -> BranchID`
  * `BranchID -> BranchName, IFSCCode, City, State`
  * Therefore: `AccountID -> BranchName` is a **transitive dependency** through `BranchID`.
* **Resolution**: Project Kashi extracts branch attributes into a dedicated `BRANCH` table with primary key `BranchID`. The `ACCOUNT` table simply stores the foreign key reference `BranchID`.

---

## 3. Functional Dependencies (FDs) Summary

* **CUSTOMER**:
  $$\text{CustomerID} \rightarrow \text{FirstName, LastName, DateOfBirth, Gender, Mobile, Email, Address, City, RegistrationDate}$$
  $$\text{Mobile} \rightarrow \text{CustomerID}$$ (Alternate Key)
  $$\text{Email} \rightarrow \text{CustomerID}$$ (Alternate Key)

* **BRANCH**:
  $$\text{BranchID} \rightarrow \text{BranchName, IFSCCode, Address, City, State, ContactNumber, CreatedAt}$$
  $$\text{IFSCCode} \rightarrow \text{BranchID}$$ (Alternate Key)

* **EMPLOYEE**:
  $$\text{EmployeeID} \rightarrow \text{EmployeeName, Mobile, Email, Designation, Salary, JoiningDate, BranchID}$$

* **ACCOUNT**:
  $$\text{AccountID} \rightarrow \text{AccountNumber, AccountType, OpeningDate, Balance, Status, BranchID}$$
  $$\text{AccountNumber} \rightarrow \text{AccountID}$$ (Alternate Key)

* **ACCOUNT_HOLDER**:
  $$\{\text{CustomerID, AccountID}\} \rightarrow \text{HolderSince, HolderType}$$

* **BANK_TRANSACTION**:
  $$\text{TransactionID} \rightarrow \text{AccountID, TransactionType, Amount, TransactionDate, Description, ReferenceNumber, TransactionStatus}$$

* **LOAN**:
  $$\text{LoanID} \rightarrow \text{CustomerID, BranchID, LoanType, LoanAmount, InterestRate, StartDate, TenureMonths, LoanStatus}$$

* **LOAN_PAYMENT**:
  $$\text{PaymentID} \rightarrow \text{LoanID, PaymentDate, Amount, PaymentMode, ReferenceNumber}$$

---

## 4. Role of SQL Constraints in Enforcing Invariants

1. **PRIMARY KEY**: Uniquely identifies each tuple and automatically enforces uniqueness and `NOT NULL`.
2. **FOREIGN KEY**: Guarantees referential integrity; disallows orphaned records and validates that relationships point to existing parent rows.
3. **UNIQUE**: Prevents duplicate real-world identifiers (e.g., IFSC codes, Account numbers, Mobile numbers, and Repayment Reference numbers).
4. **NOT NULL**: Prevents incomplete records on mandatory business fields (e.g., Customer names, loan amounts, transaction timestamps).
5. **CHECK**: Enforces domain-specific numerical boundaries (`Balance >= 0`, `Amount > 0`, `Salary > 0`, `TenureMonths > 0`).
6. **DEFAULT**: Automatically populates timestamps (`CURRENT_TIMESTAMP`) and initial states (`'Active'`, `0.00`).
7. **AUTO_INCREMENT**: Generates collision-free surrogate keys efficiently at the database engine level.
8. **Referential Actions**: `ON UPDATE CASCADE` propagates primary key modifications; `ON DELETE RESTRICT` protects audit trails from unauthorized erasure.
