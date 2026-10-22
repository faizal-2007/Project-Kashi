# Relationships and Cardinality

Cardinality is read as: `left symbol ||--o{ right` means one left row relates to zero or more right rows.

| # | Relationship | Entities | Cardinality | Participation | Foreign key | Business meaning | Integrity rule |
|---|---|---|---|---|---|---|---|
| 1 | Employs | BRANCH - EMPLOYEE | One-to-many | Branch: partial; Employee: total | `EMPLOYEE.BranchID` | A branch has many employees; an employee works at one branch. | Cannot delete a branch that has employees. |
| 2 | Hosts | BRANCH - ACCOUNT | One-to-many | Branch: partial; Account: total | `ACCOUNT.BranchID` | A branch maintains many accounts; an account belongs to one branch. | Cannot delete a branch that has accounts. |
| 3 | Holds / Has | CUSTOMER - ACCOUNT via ACCOUNT_HOLDER | Many-to-many | Both partial individually, total through the junction | `ACCOUNT_HOLDER.CustomerID`, `ACCOUNT_HOLDER.AccountID` | Customers may share accounts; customers may hold many accounts. | Composite PK prevents duplicate links; both FKs restrict deletes. |
| 4 | Applies for | CUSTOMER - LOAN | One-to-many | Customer: partial; Loan: total | `LOAN.CustomerID` | One customer may have several loans; each loan belongs to one customer. | Loan cannot exist without a customer. |
| 5 | Processes | BRANCH - LOAN | One-to-many | Branch: partial; Loan: total | `LOAN.BranchID` | The branch that processes a loan. | Loan cannot reference a missing branch. |
| 6 | Records | ACCOUNT - BANK_TRANSACTION | One-to-many | Account: partial; Transaction: total | `BANK_TRANSACTION.AccountID` | An account has many transaction records; each record belongs to one account. | Account with history cannot be deleted. |
| 7 | Receives | LOAN - LOAN_PAYMENT | One-to-many | Loan: partial; Payment: total | `LOAN_PAYMENT.LoanID` | A loan can receive many payments; each payment belongs to one loan. | Loan with payments cannot be deleted. |

## Minimum and maximum participation

| Relationship | Minimum | Maximum |
|---|---|---|
| BRANCH - EMPLOYEE | A branch can have 0 employees; an employee must have 1 branch. | A branch can have many employees; an employee has exactly 1 branch. |
| BRANCH - ACCOUNT | A branch can have 0 accounts; an account must have 1 branch. | A branch can have many accounts; an account has exactly 1 branch. |
| CUSTOMER - ACCOUNT | A customer can have 0 accounts; an account has at least 1 primary holder in application logic. | A customer can hold many accounts; an account can have many joint holders. |
| CUSTOMER - LOAN | A customer can have 0 loans; a loan must have 1 customer. | A customer can have many loans; a loan has exactly 1 customer. |
| BRANCH - LOAN | A branch can have 0 loans; a loan must have 1 branch. | A branch can have many loans; a loan has exactly 1 branch. |
| ACCOUNT - BANK_TRANSACTION | An account can have 0 transactions; a transaction must have 1 account. | An account can have many transactions; a transaction has exactly 1 account. |
| LOAN - LOAN_PAYMENT | A loan can have 0 payments; a payment must have 1 loan. | A loan can have many payments; a payment has exactly 1 loan. |

## Referential actions

- `ON UPDATE CASCADE` keeps child references consistent if a surrogate key ever changes. In normal use the keys never change.
- `ON DELETE RESTRICT` prevents deletion of parent rows that still have children. This preserves account and transaction history.
- The application never deletes customers, accounts, transactions, loans, or payments during ordinary operations. Histories are shown instead.
- Triggers add three more layers of protection: transaction immutability, primary-holder uniqueness, and loan-payment validation.
