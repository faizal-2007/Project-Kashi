# Entity-Relationship (ER) Diagram — Project Kashi

This document contains the visual and logical Entity-Relationship architecture of **Project Kashi — Banking Management System**.

---

## 1. Visual Mermaid ER Diagram

The following Mermaid diagram renders natively in GitHub Markdown viewers and VS Code:

```mermaid
erDiagram
    BRANCH ||--o{ EMPLOYEE : "employs"
    BRANCH ||--o{ ACCOUNT : "maintains"
    BRANCH ||--o{ LOAN : "disburses"
    CUSTOMER ||--o{ ACCOUNT_HOLDER : "holds"
    ACCOUNT ||--o{ ACCOUNT_HOLDER : "has_holders"
    CUSTOMER ||--o{ LOAN : "borrows"
    ACCOUNT ||--o{ BANK_TRANSACTION : "records"
    LOAN ||--o{ LOAN_PAYMENT : "repaid_by"

    BRANCH {
        int BranchID PK
        varchar BranchName
        varchar IFSCCode UK
        varchar Address
        varchar City
        varchar State
        varchar ContactNumber
        datetime CreatedAt
    }

    EMPLOYEE {
        int EmployeeID PK
        varchar EmployeeName
        varchar Mobile
        varchar Email UK
        varchar Designation
        decimal Salary
        date JoiningDate
        int BranchID FK
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
        int CustomerID PK_FK
        int AccountID PK_FK
        datetime HolderSince
        enum HolderType
    }

    BANK_TRANSACTION {
        int TransactionID PK
        int AccountID FK
        enum TransactionType
        decimal Amount
        datetime TransactionDate
        varchar Description
        varchar ReferenceNumber
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

---

## 2. Distinction Between ER Diagram and Relational Schema

| Dimension | Conceptual ER Diagram | Relational Schema |
| :--- | :--- | :--- |
| **Abstraction Level** | High-level conceptual model focusing on business entities and associations. | Logical and physical implementation model ready for RDBMS storage. |
| **Representation of M:N Relationships** | Drawn directly as a diamond relationship connecting two entities (e.g., `CUSTOMER` holds `ACCOUNT`). | Decomposed into an associative/bridge table (`ACCOUNT_HOLDER`) with foreign keys. |
| **Attributes** | Outlined as ellipses or logical property lists without implementation specifics. | Defined with strict MySQL data types (`INT`, `VARCHAR(50)`, `DECIMAL(15,2)`, `DATETIME`). |
| **Integrity Rules** | Outlined as business constraints. | Enforced via `PRIMARY KEY`, `FOREIGN KEY`, `CHECK`, `UNIQUE`, `NOT NULL`, and cascading actions (`ON UPDATE CASCADE`). |

---

## 3. Why `ACCOUNT_HOLDER` is Required to Represent Many-to-Many

In modern retail banking:
1. **Multiple accounts per customer**: A customer can hold both a Savings Account and a Current Account.
2. **Multiple customers per account**: Spouses or business partners can operate a single **Joint Account**.

If we placed `CustomerID` directly inside `ACCOUNT`, an account could only ever belong to **one** customer (disallowing Joint accounts). Conversely, placing `AccountID` inside `CUSTOMER` would prevent a customer from holding multiple accounts unless we violated First Normal Form (1NF) with a multi-valued repeating column.

Therefore, the associative entity **`ACCOUNT_HOLDER`** bridges `CUSTOMER` and `ACCOUNT` using a composite primary key `(CustomerID, AccountID)` and supports an attribute `HolderType` (`Primary` vs `Joint`).
