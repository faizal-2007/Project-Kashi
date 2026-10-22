# Normalization

Normalization reduces redundancy and update anomalies. The implemented schema is in third normal form (3NF) for its ordinary business data.

## Unnormalized form (UNF)

A poor design might store everything in one row:

```text
AccountRow(
  AccountNumber, AccountType, Balance, Status,
  CustomerName, CustomerMobile, CustomerEmail,
  JointHolderName, JointHolderMobile,
  BranchName, IFSCCode, BranchCity,
  TransactionIDs, TransactionAmounts
)
```

Problems:
- Repeating the same customer data for every account.
- Repeating branch data for every account and employee.
- Multiple values in one column (`TransactionIDs`).
- A joint holder creates repeating groups or extra columns.
- Updating a customer's phone could require changing many rows and could create inconsistent values.

## First Normal Form (1NF)

1NF requires atomic values and no repeating groups.

The schema uses one value per column and separates repeated concepts into tables:
- Account transactions are rows in `BANK_TRANSACTION`, not a list in `ACCOUNT`.
- Joint holders are rows in `ACCOUNT_HOLDER`, not `JointHolder1`, `JointHolder2` columns.
- Each customer and each account has its own row.

## Second Normal Form (2NF)

2NF requires 1NF plus no partial dependency of a non-key attribute on part of a composite key.

`ACCOUNT_HOLDER(CustomerID, AccountID, HolderSince, HolderType)` has a composite key. `HolderSince` and `HolderType` describe the relationship between that customer and that account. They do not depend on `CustomerID` alone or `AccountID` alone. Therefore there is no partial dependency.

## Third Normal Form (3NF)

3NF requires 2NF plus no transitive dependency: non-key attributes depend only on the key.

Examples:

- In `ACCOUNT`, `BranchID` is the branch key. `BranchName`, `City`, and `IFSCCode` are stored in `BRANCH`, not copied into `ACCOUNT`. They depend on `BranchID`, not on `AccountID`.
- In `BANK_TRANSACTION`, customer name and branch name are not stored. They are obtained through joins from `ACCOUNT`, `ACCOUNT_HOLDER`, `CUSTOMER`, and `BRANCH`.
- In `LOAN`, the customer name and branch name are not duplicated; only `CustomerID` and `BranchID` are stored.
- `LOAN` does not store `OutstandingAmount`. It can always be calculated from the immutable payment history, so storing it would risk becoming stale and would be a derived, redundant field.

## Functional dependencies

```text
CustomerID -> FirstName, LastName, DateOfBirth, Gender, Mobile, Email, Address, City, RegistrationDate
BranchID -> BranchName, IFSCCode, Address, City, State, ContactNumber
EmployeeID -> EmployeeName, Mobile, Email, Designation, Salary, JoiningDate, BranchID
AccountID -> AccountNumber, AccountType, OpeningDate, Balance, Status, BranchID
(CustomerID, AccountID) -> HolderSince, HolderType
TransactionID -> all BANK_TRANSACTION attributes
LoanID -> CustomerID, BranchID, LoanType, LoanAmount, InterestRate, StartDate, TenureMonths, LoanStatus
PaymentID -> LoanID, PaymentDate, Amount, PaymentMode, ReferenceNumber
```

The transfer group is not a key. It is a non-key attribute of `BANK_TRANSACTION` that groups two transaction rows for reporting.

## Constraints used

| Constraint | Example | Benefit |
|---|---|---|
| PRIMARY KEY | `ACCOUNT.AccountID` | Unique row identity; automatic index. |
| FOREIGN KEY | `ACCOUNT.BranchID -> BRANCH` | Referential integrity. |
| UNIQUE | Mobile, email, IFSC, account number, reference number | Prevent duplicates. |
| NOT NULL | Required names and amounts | Prevent missing required data. |
| CHECK | `Balance >= 0`, `Amount > 0`, `InterestRate BETWEEN 0 AND 50` | Reject invalid values inside MySQL. |
| DEFAULT | RegistrationDate, Status, OpeningDate | Apply safe standard values. |
| AUTO_INCREMENT | ID columns | Generate surrogate keys. |
| Referential actions | ON UPDATE CASCADE, ON DELETE RESTRICT | Maintain links and preserve history. |

## Justified non-3NF-like fields

- `Balance` in `ACCOUNT` is a derived value if defined as the sum of all transactions. It is stored deliberately for fast, locked balance updates and is maintained inside the same transaction as the transaction row. This is a controlled denormalization for banking performance and concurrency.
- `TransferGroupReference` is nullable and is not a computed duplicate. It is an intentional business identifier shared by two rows so a transfer can be found as one operation.
- `TransactionStatus` records the result at the time of the attempt; a failed transaction remains in history even though it did not change a balance.
