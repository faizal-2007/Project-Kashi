# Relationships and Cardinalities — Project Kashi

Comprehensive documentation of all inter-entity relationships, cardinality ratios, and participation constraints within **Project Kashi — Banking Management System**.

---

## 1. Summary Matrix of Relationships

| # | Relationship Name | Entity 1 | Entity 2 | Cardinality | Min/Max Participation | Foreign Key Used |
| :---: | :--- | :--- | :--- | :---: | :---: | :--- |
| **1** | Branch Staffing (`employs`) | `BRANCH` | `EMPLOYEE` | **1 : N** | `BRANCH` (1, N) &bull; `EMPLOYEE` (1, 1) | `EMPLOYEE.BranchID -> BRANCH.BranchID` |
| **2** | Account Maintenance (`maintains`) | `BRANCH` | `ACCOUNT` | **1 : N** | `BRANCH` (0, N) &bull; `ACCOUNT` (1, 1) | `ACCOUNT.BranchID -> BRANCH.BranchID` |
| **3** | Account Ownership (`holds`) | `CUSTOMER` | `ACCOUNT` | **M : N** | `CUSTOMER` (0, N) &bull; `ACCOUNT` (1, N) | Resolved via `ACCOUNT_HOLDER` composite PK |
| **4** | Borrower Facility (`borrows`) | `CUSTOMER` | `LOAN` | **1 : N** | `CUSTOMER` (0, N) &bull; `LOAN` (1, 1) | `LOAN.CustomerID -> CUSTOMER.CustomerID` |
| **5** | Loan Disbursal (`sanctions`) | `BRANCH` | `LOAN` | **1 : N** | `BRANCH` (0, N) &bull; `LOAN` (1, 1) | `LOAN.BranchID -> BRANCH.BranchID` |
| **6** | Transaction Ledger (`records`) | `ACCOUNT` | `BANK_TRANSACTION` | **1 : N** | `ACCOUNT` (0, N) &bull; `BANK_TRANSACTION` (1, 1) | `BANK_TRANSACTION.AccountID -> ACCOUNT.AccountID` |
| **7** | Loan Repayment (`repaid_by`) | `LOAN` | `LOAN_PAYMENT` | **1 : N** | `LOAN` (0, N) &bull; `LOAN_PAYMENT` (1, 1) | `LOAN_PAYMENT.LoanID -> LOAN.LoanID` |

---

## 2. In-Depth Relationship Specifications

### 1. `BRANCH` to `EMPLOYEE`
* **Cardinality**: One-to-Many ($1 : N$).
* **Business Meaning**: A physical branch employs one or more staff members (Branch Manager, Senior Cashier, Loan Officer). Every employee belongs to exactly one branch.
* **Participation**: Total on `EMPLOYEE` (every employee must have an assigned `BranchID`); Partial on `BRANCH` (a newly registered branch may temporarily have 0 employees).
* **Integrity Rule**: `ON UPDATE CASCADE`, `ON DELETE RESTRICT` (a branch cannot be deleted if active staff members are linked to it).

### 2. `BRANCH` to `ACCOUNT`
* **Cardinality**: One-to-Many ($1 : N$).
* **Business Meaning**: A branch maintains and services multiple customer deposit accounts. Each account is homed at exactly one designated home branch whose IFSC routing code governs its clearance.
* **Participation**: Total on `ACCOUNT` (every account must have a valid `BranchID`); Partial on `BRANCH`.
* **Integrity Rule**: `ON UPDATE CASCADE`, `ON DELETE RESTRICT`.

### 3. `CUSTOMER` to `ACCOUNT` (via `ACCOUNT_HOLDER`)
* **Cardinality**: Many-to-Many ($M : N$).
* **Business Meaning**: A customer can hold multiple bank accounts (e.g., a Savings account and a Current account). An account can have one or more authorized holders (e.g., Primary holder and Joint holder).
* **Bridge Entity**: Implemented via `ACCOUNT_HOLDER(CustomerID, AccountID)`.
* **Participation**: Partial on `CUSTOMER` (a registered customer may not yet have an opened account); Total on `ACCOUNT` (an account must have at least one Primary holder).
* **Integrity Rule**: `ON UPDATE CASCADE`, `ON DELETE CASCADE` (deleting an association row cleans up ownership without dropping the parent entities).

### 4. `CUSTOMER` to `LOAN`
* **Cardinality**: One-to-Many ($1 : N$).
* **Business Meaning**: A customer can borrow zero, one, or multiple loans over their banking lifetime. Each loan contract is underwritten for a single primary borrowing customer.
* **Participation**: Partial on `CUSTOMER` (most customers only maintain deposit accounts and do not borrow loans); Total on `LOAN` (every loan requires a valid `CustomerID`).
* **Integrity Rule**: `ON UPDATE CASCADE`, `ON DELETE RESTRICT`.

### 5. `BRANCH` to `LOAN`
* **Cardinality**: One-to-Many ($1 : N$).
* **Business Meaning**: A branch sanctions and disburses credit facilities out of its allocated credit quota.
* **Participation**: Partial on `BRANCH`; Total on `LOAN`.
* **Integrity Rule**: `ON UPDATE CASCADE`, `ON DELETE RESTRICT`.

### 6. `ACCOUNT` to `BANK_TRANSACTION`
* **Cardinality**: One-to-Many ($1 : N$).
* **Business Meaning**: An account accumulates a chronological series of financial transactions (deposits, cash withdrawals, outward and inward EFT transfers). Each transaction row represents a discrete ledger entry tied to exactly one account.
* **Participation**: Partial on `ACCOUNT` (a freshly opened zero-balance account may have 0 transactions); Total on `BANK_TRANSACTION` (a transaction cannot exist in a vacuum without a linked account).
* **Integrity Rule**: `ON UPDATE CASCADE`, `ON DELETE RESTRICT` (auditing invariant: financial records can never be orphaned or deleted).

### 7. `LOAN` to `LOAN_PAYMENT`
* **Cardinality**: One-to-Many ($1 : N$).
* **Business Meaning**: An active loan facility accepts multiple repayments or monthly EMI installments across its tenure until the outstanding principal is zeroed and closed.
* **Participation**: Partial on `LOAN` (a newly disbursed loan starts with 0 payments); Total on `LOAN_PAYMENT`.
* **Integrity Rule**: `ON UPDATE CASCADE`, `ON DELETE RESTRICT`.
