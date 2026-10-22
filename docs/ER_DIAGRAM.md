# Entity-Relationship Diagram

The diagram below is the logical ER model of the implemented `project_kashi` database. It matches `sql/schema.sql`.

```mermaid
erDiagram
    BRANCH ||--o{ EMPLOYEE : employs
    BRANCH ||--o{ ACCOUNT : hosts
    BRANCH ||--o{ LOAN : processes
    CUSTOMER ||--o{ ACCOUNT_HOLDER : holds
    ACCOUNT ||--o{ ACCOUNT_HOLDER : has
    CUSTOMER ||--o{ LOAN : applies_for
    ACCOUNT ||--o{ BANK_TRANSACTION : records
    LOAN ||--o{ LOAN_PAYMENT : receives

    BRANCH {
        int BranchID PK
        varchar BranchName
        char IFSCCode UK
        varchar Address
        varchar City
        varchar State
        varchar ContactNumber
    }
    CUSTOMER {
        int CustomerID PK
        varchar FirstName
        varchar LastName
        date DateOfBirth
        enum Gender
        varchar Mobile UK
        varchar Email UK
        varchar Address
        varchar City
        datetime RegistrationDate
    }
    EMPLOYEE {
        int EmployeeID PK
        varchar EmployeeName
        varchar Mobile UK
        varchar Email UK
        varchar Designation
        decimal Salary
        date JoiningDate
        int BranchID FK
    }
    ACCOUNT {
        int AccountID PK
        varchar AccountNumber UK
        enum AccountType
        datetime OpeningDate
        decimal Balance
        enum Status
        int BranchID FK
    }
    ACCOUNT_HOLDER {
        int CustomerID PK,FK
        int AccountID PK,FK
        datetime HolderSince
        enum HolderType
    }
    BANK_TRANSACTION {
        bigint TransactionID PK
        int AccountID FK
        enum TransactionType
        decimal Amount
        datetime TransactionDate
        varchar Description
        varchar ReferenceNumber UK
        varchar TransferGroupReference
        enum TransactionStatus
    }
    LOAN {
        int LoanID PK
        int CustomerID FK
        int BranchID FK
        enum LoanType
        decimal LoanAmount
        decimal InterestRate
        date StartDate
        int TenureMonths
        enum LoanStatus
    }
    LOAN_PAYMENT {
        int PaymentID PK
        int LoanID FK
        datetime PaymentDate
        decimal Amount
        enum PaymentMode
        varchar ReferenceNumber UK
    }
```

## ER model versus relational schema

An **ER model** describes entities, attributes, and business relationships at a conceptual level. It does not include physical storage details. The **relational schema** is the physical implementation: tables, column data types, primary keys, foreign keys, unique constraints, checks, defaults, and indexes.

- The ER model shows CUSTOMER and ACCOUNT as related.
- The relational schema implements that many-to-many relationship as the `ACCOUNT_HOLDER` junction table with the composite primary key `(CustomerID, AccountID)`.

## Why ACCOUNT_HOLDER is required

One customer can own several accounts, and one account can be shared by several customers (for example, a primary holder and a joint holder). A many-to-many relationship cannot be stored in either CUSTOMER or ACCOUNT without repeating data or limiting the relationship. `ACCOUNT_HOLDER` resolves it:

- Each row links exactly one customer to exactly one account.
- The composite primary key prevents the same customer from being linked twice to the same account.
- `HolderType` records whether the holder is `Primary` or `Joint`.
- A trigger enforces at most one `Primary` holder per account.

## Entities at a glance

| Entity | Logical table | Purpose |
|---|---|---|
| BRANCH | `BRANCH` | Bank branch master data and IFSC. |
| CUSTOMER | `CUSTOMER` | Person who uses banking services. |
| EMPLOYEE | `EMPLOYEE` | Staff member assigned to a branch. |
| ACCOUNT | `ACCOUNT` | Bank account with type, balance, and status. |
| ACCOUNT_HOLDER | `ACCOUNT_HOLDER` | Junction between customers and accounts. |
| TRANSACTION | `BANK_TRANSACTION` | Immutable financial activity record. |
| LOAN | `LOAN` | Loan application and lifecycle status. |
| LOAN_PAYMENT | `LOAN_PAYMENT` | Payment made against a loan. |

`BANK_TRANSACTION` is used as the physical table name because `TRANSACTION` is a reserved SQL keyword. The logical entity name remains TRANSACTION.
