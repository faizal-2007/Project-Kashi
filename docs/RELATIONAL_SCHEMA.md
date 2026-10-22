# Relational Schema

Notation: **PK** = primary key, **FK** = foreign key, **UK** = unique key, **NN** = not null.

## Table definitions

```text
BRANCH(
    BranchID PK,
    BranchName NN,
    IFSCCode NN UK,
    Address NN,
    City NN,
    State NN,
    ContactNumber NN
)

CUSTOMER(
    CustomerID PK,
    FirstName NN,
    LastName NN,
    DateOfBirth NN,
    Gender NN,
    Mobile NN UK,
    Email NN UK,
    Address NN,
    City NN,
    RegistrationDate NN DEFAULT CURRENT_TIMESTAMP
)

EMPLOYEE(
    EmployeeID PK,
    EmployeeName NN,
    Mobile NN UK,
    Email NN UK,
    Designation NN,
    Salary NN,
    JoiningDate NN,
    BranchID NN FK -> BRANCH(BranchID)
)

ACCOUNT(
    AccountID PK,
    AccountNumber NN UK,
    AccountType NN,
    OpeningDate NN DEFAULT CURRENT_TIMESTAMP,
    Balance NN DEFAULT 0.00,
    Status NN DEFAULT 'Active',
    BranchID NN FK -> BRANCH(BranchID)
)

ACCOUNT_HOLDER(
    CustomerID PK FK -> CUSTOMER(CustomerID),
    AccountID PK FK -> ACCOUNT(AccountID),
    HolderSince NN DEFAULT CURRENT_TIMESTAMP,
    HolderType NN DEFAULT 'Primary'
)

BANK_TRANSACTION(
    TransactionID PK,
    AccountID NN FK -> ACCOUNT(AccountID),
    TransactionType NN,
    Amount NN,
    TransactionDate NN DEFAULT CURRENT_TIMESTAMP,
    Description NULL,
    ReferenceNumber NULL UK,
    TransferGroupReference NULL,
    TransactionStatus NN DEFAULT 'SUCCESS'
)

LOAN(
    LoanID PK,
    CustomerID NN FK -> CUSTOMER(CustomerID),
    BranchID NN FK -> BRANCH(BranchID),
    LoanType NN,
    LoanAmount NN,
    InterestRate NN,
    StartDate NN,
    TenureMonths NN,
    LoanStatus NN DEFAULT 'Pending'
)

LOAN_PAYMENT(
    PaymentID PK,
    LoanID NN FK -> LOAN(LoanID),
    PaymentDate NN DEFAULT CURRENT_TIMESTAMP,
    Amount NN,
    PaymentMode NN,
    ReferenceNumber NULL UK
)
```

## Relationships represented by foreign keys

| Child table | Foreign key column | Parent table | Parent column |
|---|---|---|---|
| EMPLOYEE | BranchID | BRANCH | BranchID |
| ACCOUNT | BranchID | BRANCH | BranchID |
| ACCOUNT_HOLDER | CustomerID | CUSTOMER | CustomerID |
| ACCOUNT_HOLDER | AccountID | ACCOUNT | AccountID |
| BANK_TRANSACTION | AccountID | ACCOUNT | AccountID |
| LOAN | CustomerID | CUSTOMER | CustomerID |
| LOAN | BranchID | BRANCH | BranchID |
| LOAN_PAYMENT | LoanID | LOAN | LoanID |

All foreign keys use `ON UPDATE CASCADE` and `ON DELETE RESTRICT`. IDs are auto-increment surrogate keys and are not edited in normal operation, while restrictive deletes protect financial history.

## Additional design decision

`BANK_TRANSACTION.TransferGroupReference` was added so the two sides of a transfer can share a common identifier while every individual `ReferenceNumber` remains unique as required. It is `NULL` for deposits and withdrawals, and the check constraint `chk_transaction_transfer_reference` enforces this rule.

`ACCOUNT_HOLDER.HolderType` and the composite key support an account with one primary holder and several joint holders.

`LOAN` has no stored `OutstandingAmount` column. Outstanding balance is derived from `LoanAmount - SUM(LOAN_PAYMENT.Amount)` using the `fn_loan_outstanding` function and the `vw_loan_payment_summary` view. This avoids an update anomaly and keeps the schema in third normal form.

## Indexes

| Index | Table | Columns | Reason |
|---|---|---|---|
| `uq_customer_mobile` | CUSTOMER | Mobile | Prevent duplicate customers. |
| `uq_customer_email` | CUSTOMER | Email | Prevent duplicate customers. |
| `uq_branch_ifsc` | BRANCH | IFSCCode | Real-world branch uniqueness. |
| `uq_account_number` | ACCOUNT | AccountNumber | Unique account numbers. |
| `uq_transaction_reference` | BANK_TRANSACTION | ReferenceNumber | Reference uniqueness. |
| `idx_transaction_account_date` | BANK_TRANSACTION | AccountID, TransactionDate | Fast statement queries. |
| `idx_transaction_transfer_group` | BANK_TRANSACTION | TransferGroupReference | Find both transfer legs. |
| `idx_payment_loan_date` | LOAN_PAYMENT | LoanID, PaymentDate | Fast loan history. |
