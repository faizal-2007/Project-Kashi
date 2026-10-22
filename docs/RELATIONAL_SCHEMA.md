# Relational Schema — Project Kashi

This document formalizes the relational database schema implemented in **Project Kashi — Banking Management System** on MySQL 8.0+.

---

## 1. Formal Relational Schema Notation

Primary keys are **underlined**, foreign keys are marked with an arrow ($\rightarrow$) referencing their target parent relation.

1. **BRANCH** (
   <u>BranchID</u>, BranchName, IFSCCode, Address, City, State, ContactNumber, CreatedAt
)

2. **EMPLOYEE** (
   <u>EmployeeID</u>, EmployeeName, Mobile, Email, Designation, Salary, JoiningDate, BranchID $\rightarrow$ BRANCH(BranchID)
)

3. **CUSTOMER** (
   <u>CustomerID</u>, FirstName, LastName, DateOfBirth, Gender, Mobile, Email, Address, City, RegistrationDate
)

4. **ACCOUNT** (
   <u>AccountID</u>, AccountNumber, AccountType, OpeningDate, Balance, Status, BranchID $\rightarrow$ BRANCH(BranchID)
)

5. **ACCOUNT_HOLDER** (
   <u>CustomerID $\rightarrow$ CUSTOMER(CustomerID), AccountID $\rightarrow$ ACCOUNT(AccountID)</u>, HolderSince, HolderType
)

6. **BANK_TRANSACTION** (
   <u>TransactionID</u>, AccountID $\rightarrow$ ACCOUNT(AccountID), TransactionType, Amount, TransactionDate, Description, ReferenceNumber, TransactionStatus
)

7. **LOAN** (
   <u>LoanID</u>, CustomerID $\rightarrow$ CUSTOMER(CustomerID), BranchID $\rightarrow$ BRANCH(BranchID), LoanType, LoanAmount, InterestRate, StartDate, TenureMonths, LoanStatus
)

8. **LOAN_PAYMENT** (
   <u>PaymentID</u>, LoanID $\rightarrow$ LOAN(LoanID), PaymentDate, Amount, PaymentMode, ReferenceNumber
)

---

## 2. Integrity Constraints & Referential Actions

| Relationship | Child Table | Foreign Key | Parent Table | On Update | On Delete | Business Rationale |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| Branch Staff | `EMPLOYEE` | `BranchID` | `BRANCH` | CASCADE | RESTRICT | Prevents accidental deletion of a branch if employees are currently active there. |
| Account Branch | `ACCOUNT` | `BranchID` | `BRANCH` | CASCADE | RESTRICT | Prevents deletion of branches that still maintain active customer deposit accounts. |
| Account Ownership | `ACCOUNT_HOLDER` | `CustomerID` | `CUSTOMER` | CASCADE | CASCADE | When a customer profile is expunged, their ownership mappings are removed. |
| Account Mapping | `ACCOUNT_HOLDER` | `AccountID` | `ACCOUNT` | CASCADE | CASCADE | When an account record is expunged, its ownership associations are purged. |
| Transaction Ledger | `BANK_TRANSACTION` | `AccountID` | `ACCOUNT` | CASCADE | RESTRICT | **Immutable audit rule**: Financial transactions cannot be orphaned; an account with past transactions cannot be deleted. |
| Loan Facility | `LOAN` | `CustomerID` | `CUSTOMER` | CASCADE | RESTRICT | A borrower cannot be deleted while debt obligations remain open. |
| Loan Disbursal | `LOAN` | `BranchID` | `BRANCH` | CASCADE | RESTRICT | Branch cannot be deleted while carrying loan liabilities. |
| Loan Repayment | `LOAN_PAYMENT` | `LoanID` | `LOAN` | CASCADE | RESTRICT | Repayment receipts cannot be orphaned or deleted arbitrarily. |
