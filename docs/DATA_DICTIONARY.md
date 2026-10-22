# Data Dictionary — Project Kashi

Complete technical data dictionary for all eight relational tables within the `project_kashi` MySQL 8.0 database.

---

## 1. Table: `BRANCH`
*Description: Physical and administrative branch centers.*

| Column Name | Data Type | Key | Nullable | Default | Constraints / Description |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `BranchID` | `INT` | **PK** | No | Auto Increment | Primary key identifying the branch uniquely. |
| `BranchName` | `VARCHAR(100)` | - | No | None | Official registered branch name. |
| `IFSCCode` | `VARCHAR(15)` | **UK** | No | None | Indian Financial System Code (Unique, min 8 chars). |
| `Address` | `VARCHAR(255)` | - | No | None | Street and locality address. |
| `City` | `VARCHAR(50)` | - | No | None | City of operation. |
| `State` | `VARCHAR(50)` | - | No | None | State / province. |
| `ContactNumber` | `VARCHAR(15)` | - | No | None | Official branch helpline telephone number. |
| `CreatedAt` | `DATETIME` | - | Yes | `CURRENT_TIMESTAMP` | System timestamp when branch record was inserted. |

---

## 2. Table: `EMPLOYEE`
*Description: Banking officers and branch staff members.*

| Column Name | Data Type | Key | Nullable | Default | Constraints / Description |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `EmployeeID` | `INT` | **PK** | No | Auto Increment | Unique primary key for employee. |
| `EmployeeName` | `VARCHAR(100)` | - | No | None | Employee full legal name. |
| `Mobile` | `VARCHAR(15)` | - | No | None | 10-digit contact mobile number. |
| `Email` | `VARCHAR(100)` | **UK** | No | None | Work email address. |
| `Designation` | `VARCHAR(50)` | - | No | None | Role (e.g., Branch Manager, Senior Cashier). |
| `Salary` | `DECIMAL(12,2)` | - | No | None | Monthly compensation (`CHECK (Salary > 0)`). |
| `JoiningDate` | `DATE` | - | No | None | Date of service commencement. |
| `BranchID` | `INT` | **FK** | No | None | References `BRANCH(BranchID)` on update cascade. |

---

## 3. Table: `CUSTOMER`
*Description: Personal details of individual account holders and borrowers.*

| Column Name | Data Type | Key | Nullable | Default | Constraints / Description |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `CustomerID` | `INT` | **PK** | No | Auto Increment | Unique primary key for each registered customer. |
| `FirstName` | `VARCHAR(50)` | - | No | None | Customer given name. |
| `LastName` | `VARCHAR(50)` | - | No | None | Customer surname/family name. |
| `DateOfBirth` | `DATE` | - | No | None | Legal birth date used for age verification. |
| `Gender` | `ENUM(...)` | - | No | None | Allowed values: `'Male'`, `'Female'`, `'Other'`. |
| `Mobile` | `VARCHAR(15)` | **UK** | No | None | Primary mobile number (`CHECK >= 10 chars`). |
| `Email` | `VARCHAR(100)` | **UK** | No | None | Unique registered email address. |
| `Address` | `VARCHAR(255)` | - | No | None | Physical residential street address. |
| `City` | `VARCHAR(50)` | - | No | None | City of residence. |
| `RegistrationDate` | `DATETIME` | - | Yes | `CURRENT_TIMESTAMP` | Account registration system timestamp. |

---

## 4. Table: `ACCOUNT`
*Description: Bank accounts maintaining balances.*

| Column Name | Data Type | Key | Nullable | Default | Constraints / Description |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `AccountID` | `INT` | **PK** | No | Auto Increment | Internal primary surrogate identifier. |
| `AccountNumber` | `VARCHAR(20)` | **UK** | No | None | Unique 10-digit customer-facing account number. |
| `AccountType` | `ENUM(...)` | - | No | None | Supported: `'Saving'`, `'Current'`, `'Salary'`. |
| `OpeningDate` | `DATETIME` | - | Yes | `CURRENT_TIMESTAMP` | Account activation timestamp. |
| `Balance` | `DECIMAL(15,2)` | - | No | `0.00` | Account liquidity balance (`CHECK (Balance >= 0.00)`). |
| `Status` | `ENUM(...)` | - | No | `'Active'` | Allowed: `'Active'`, `'Inactive'`, `'Closed'`. |
| `BranchID` | `INT` | **FK** | No | None | References `BRANCH(BranchID)`. |

---

## 5. Table: `ACCOUNT_HOLDER`
*Description: Associative table resolving M:N relationship between Customer and Account.*

| Column Name | Data Type | Key | Nullable | Default | Constraints / Description |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `CustomerID` | `INT` | **PK, FK**| No | None | References `CUSTOMER(CustomerID)` ON DELETE CASCADE. |
| `AccountID` | `INT` | **PK, FK**| No | None | References `ACCOUNT(AccountID)` ON DELETE CASCADE. |
| `HolderSince` | `DATETIME` | - | Yes | `CURRENT_TIMESTAMP` | Date and time holder was associated. |
| `HolderType` | `ENUM(...)` | - | No | `'Primary'` | Role on account: `'Primary'` or `'Joint'`. |

---

## 6. Table: `BANK_TRANSACTION`
*Description: Immutable ledger of debits, credits, and inter-account transfers.*

| Column Name | Data Type | Key | Nullable | Default | Constraints / Description |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `TransactionID` | `INT` | **PK** | No | Auto Increment | Unique sequential transaction record identifier. |
| `AccountID` | `INT` | **FK** | No | None | References target `ACCOUNT(AccountID)`. |
| `TransactionType` | `ENUM(...)` | - | No | None | `'DEPOSIT'`, `'WITHDRAWAL'`, `'TRANSFER_IN'`, `'TRANSFER_OUT'`. |
| `Amount` | `DECIMAL(15,2)` | - | No | None | Transaction value (`CHECK (Amount > 0.00)`). |
| `TransactionDate` | `DATETIME` | - | Yes | `CURRENT_TIMESTAMP` | Execution timestamp. |
| `Description` | `VARCHAR(255)` | - | Yes | `NULL` | Transaction narrative / remarks. |
| `ReferenceNumber` | `VARCHAR(50)` | - | No | None | Unique reference number (paired for EFT transfers). |
| `TransactionStatus`| `ENUM(...)` | - | No | `'SUCCESS'` | Status: `'SUCCESS'`, `'FAILED'`, `'PENDING'`. |

---

## 7. Table: `LOAN`
*Description: Credit and lending facilities extended to customers.*

| Column Name | Data Type | Key | Nullable | Default | Constraints / Description |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `LoanID` | `INT` | **PK** | No | Auto Increment | Unique loan identifier. |
| `CustomerID` | `INT` | **FK** | No | None | References borrowing `CUSTOMER(CustomerID)`. |
| `BranchID` | `INT` | **FK** | No | None | References sanctioning `BRANCH(BranchID)`. |
| `LoanType` | `ENUM(...)` | - | No | None | `'Home Loan'`, `'Education Loan'`, `'Personal Loan'`, `'Vehicle Loan'`. |
| `LoanAmount` | `DECIMAL(15,2)` | - | No | None | Sanctioned principal (`CHECK (LoanAmount > 0.00)`). |
| `InterestRate` | `DECIMAL(5,2)` | - | No | None | Annual interest percentage rate (`CHECK >= 0.00`). |
| `StartDate` | `DATE` | - | No | None | Sanction / disbursal date. |
| `TenureMonths` | `INT` | - | No | None | Repayment horizon in months (`CHECK > 0`). |
| `LoanStatus` | `ENUM(...)` | - | No | `'Active'` | `'Applied'`, `'Approved'`, `'Disbursed'`, `'Active'`, `'Closed'`, `'Rejected'`. |

---

## 8. Table: `LOAN_PAYMENT`
*Description: Installments and repayments against active loans.*

| Column Name | Data Type | Key | Nullable | Default | Constraints / Description |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `PaymentID` | `INT` | **PK** | No | Auto Increment | Repayment receipt primary key. |
| `LoanID` | `INT` | **FK** | No | None | References parent `LOAN(LoanID)`. |
| `PaymentDate` | `DATETIME` | - | Yes | `CURRENT_TIMESTAMP` | Timestamp of payment receipt. |
| `Amount` | `DECIMAL(15,2)` | - | No | None | Installment amount paid (`CHECK (Amount > 0.00)`). |
| `PaymentMode` | `ENUM(...)` | - | No | None | `'Cash'`, `'Cheque'`, `'Account Transfer'`, `'Online'`. |
| `ReferenceNumber` | `VARCHAR(50)` | **UK** | No | None | Unique banking transaction reference number. |
