# 15 SQL Business Queries & Solutions — Project Kashi

Comprehensive documentation of the 15 enterprise banking analytics problems implemented in `sql/business_queries.sql` and interactively runnable via the web interface at `/business-queries`.

---

## Problem 1: All Customers with Linked Bank Accounts
* **Business Question**: Provide a complete list of customers showing their contact details, all accounts held, account types, balances, and home branches.
* **Purpose**: Customer 360-degree overview for branch managers and relationship managers.
* **DBMS Concepts**: Multi-table INNER JOIN, String Concatenation (`CONCAT`), Column Aliasing.
* **Expected Columns**: `CustomerID`, `FullName`, `Email`, `AccountNumber`, `AccountType`, `Balance`, `BranchName`.
* **SQL Query**:
```sql
SELECT 
    c.CustomerID,
    CONCAT(c.FirstName, ' ', c.LastName) AS FullName,
    c.Email,
    a.AccountNumber,
    a.AccountType,
    a.Balance,
    b.BranchName
FROM CUSTOMER c
JOIN ACCOUNT_HOLDER ah ON c.CustomerID = ah.CustomerID
JOIN ACCOUNT a ON ah.AccountID = a.AccountID
JOIN BRANCH b ON a.BranchID = b.BranchID
ORDER BY c.CustomerID, a.AccountNumber;
```

---

## Problem 2: Customers Holding Multiple Accounts
* **Business Question**: Which customers maintain more than one bank account across the bank?
* **Purpose**: Identify high-engagement retail and commercial clients for wealth management cross-selling.
* **DBMS Concepts**: `GROUP BY`, `HAVING COUNT(*) > 1`, Aggregate Filtering.
* **Expected Columns**: `CustomerID`, `FullName`, `Mobile`, `TotalAccountsOwned`.
* **SQL Query**:
```sql
SELECT 
    c.CustomerID,
    CONCAT(c.FirstName, ' ', c.LastName) AS FullName,
    c.Mobile,
    COUNT(ah.AccountID) AS TotalAccountsOwned
FROM CUSTOMER c
JOIN ACCOUNT_HOLDER ah ON c.CustomerID = ah.CustomerID
GROUP BY c.CustomerID, c.FirstName, c.LastName, c.Mobile
HAVING COUNT(ah.AccountID) > 1
ORDER BY TotalAccountsOwned DESC;
```

---

## Problem 3: Accounts with Branch Details & Branch Managers
* **Business Question**: Display all accounts alongside their respective home branch, location, and the presiding Branch Manager.
* **Purpose**: Organizational hierarchy and branch supervisory audit.
* **DBMS Concepts**: Multi-table JOIN, Conditional LEFT JOIN on employee designation.
* **Expected Columns**: `AccountNumber`, `AccountType`, `Balance`, `Status`, `BranchName`, `BranchCity`, `BranchManager`.
* **SQL Query**:
```sql
SELECT 
    a.AccountNumber,
    a.AccountType,
    a.Balance,
    a.Status,
    b.BranchName,
    b.City AS BranchCity,
    e.EmployeeName AS BranchManager
FROM ACCOUNT a
JOIN BRANCH b ON a.BranchID = b.BranchID
LEFT JOIN EMPLOYEE e ON b.BranchID = e.BranchID AND e.Designation = 'Branch Manager'
ORDER BY b.BranchName, a.AccountNumber;
```

---

## Problem 4: Total Deposits & Average Balance Per Branch
* **Business Question**: What is the total deposit volume and average account balance in each branch?
* **Purpose**: Evaluate branch financial performance, deposit market share, and liquidity distribution.
* **DBMS Concepts**: `GROUP BY`, Aggregate Functions (`SUM`, `AVG`, `COUNT`), `COALESCE` for null safety.
* **Expected Columns**: `BranchID`, `BranchName`, `ActiveAccountsCount`, `TotalDeposits`, `AverageBalance`.
* **SQL Query**:
```sql
SELECT 
    b.BranchID,
    b.BranchName,
    COUNT(a.AccountID) AS ActiveAccountsCount,
    COALESCE(SUM(a.Balance), 0.00) AS TotalDeposits,
    COALESCE(ROUND(AVG(a.Balance), 2), 0.00) AS AverageBalance
FROM BRANCH b
LEFT JOIN ACCOUNT a ON b.BranchID = a.BranchID AND a.Status = 'Active'
GROUP BY b.BranchID, b.BranchName
ORDER BY TotalDeposits DESC;
```

---

## Problem 5: High-Net-Worth Accounts (Above Bank Average)
* **Business Question**: Which accounts hold balances strictly higher than the overall average account balance across the entire bank?
* **Purpose**: Tiering customer accounts for priority banking and wealth advisory privileges.
* **DBMS Concepts**: Scalar Subquery, Dynamic Filtering against Nested Aggregate.
* **Expected Columns**: `AccountNumber`, `AccountType`, `Balance`, `Status`, `BranchName`.
* **SQL Query**:
```sql
SELECT 
    a.AccountNumber,
    a.AccountType,
    a.Balance,
    a.Status,
    b.BranchName
FROM ACCOUNT a
JOIN BRANCH b ON a.BranchID = b.BranchID
WHERE a.Balance > (
    SELECT AVG(Balance) FROM ACCOUNT WHERE Status = 'Active'
)
ORDER BY a.Balance DESC;
```

---

## Problem 6: Cash Flow Summary by Account (Inflows vs Outflows)
* **Business Question**: For every account, calculate the total inflows (deposits, inward transfers), total outflows (withdrawals, outward transfers), and net cash flow.
* **Purpose**: Profile transactional velocity, liquidity churn, and money-laundering thresholds.
* **DBMS Concepts**: Conditional Aggregation (`SUM(CASE ...)`), `LEFT JOIN`, `GROUP BY`.
* **Expected Columns**: `AccountNumber`, `AccountType`, `TotalInflow`, `TotalOutflow`, `NetTransactionVolume`.
* **SQL Query**:
```sql
SELECT 
    a.AccountNumber,
    a.AccountType,
    COALESCE(SUM(CASE WHEN t.TransactionType IN ('DEPOSIT', 'TRANSFER_IN') THEN t.Amount ELSE 0 END), 0.00) AS TotalInflow,
    COALESCE(SUM(CASE WHEN t.TransactionType IN ('WITHDRAWAL', 'TRANSFER_OUT') THEN t.Amount ELSE 0 END), 0.00) AS TotalOutflow,
    COALESCE(SUM(CASE WHEN t.TransactionType IN ('DEPOSIT', 'TRANSFER_IN') THEN t.Amount ELSE -t.Amount END), 0.00) AS NetTransactionVolume
FROM ACCOUNT a
LEFT JOIN BANK_TRANSACTION t ON a.AccountID = t.AccountID AND t.TransactionStatus = 'SUCCESS'
GROUP BY a.AccountID, a.AccountNumber, a.AccountType
ORDER BY NetTransactionVolume DESC;
```

---

## Problem 7: Customer Statement & Passbook Ledger (Customer #1)
* **Business Question**: Generate an official passbook statement showing all historical debits and credits across all accounts belonging to Customer #1.
* **Purpose**: Customer account statement generation and dispute resolution.
* **DBMS Concepts**: 4-Table JOIN (`CUSTOMER -> ACCOUNT_HOLDER -> ACCOUNT -> BANK_TRANSACTION`).
* **Expected Columns**: `TransactionID`, `ReferenceNumber`, `TransactionDate`, `AccountNumber`, `TransactionType`, `Amount`, `Description`.
* **SQL Query**:
```sql
SELECT 
    t.TransactionID,
    t.ReferenceNumber,
    t.TransactionDate,
    a.AccountNumber,
    t.TransactionType,
    t.Amount,
    t.Description
FROM BANK_TRANSACTION t
JOIN ACCOUNT a ON t.AccountID = a.AccountID
JOIN ACCOUNT_HOLDER ah ON a.AccountID = ah.AccountID
WHERE ah.CustomerID = 1
ORDER BY t.TransactionDate DESC;
```

---

## Problem 8: Customers Without Any Bank Accounts
* **Business Question**: Find all registered customers who do not currently own or hold any bank accounts.
* **Purpose**: Sales follow-up and dormant registration re-engagement campaigns.
* **DBMS Concepts**: `LEFT JOIN` with `IS NULL` check (Set difference emulation).
* **Expected Columns**: `CustomerID`, `FullName`, `Email`, `Mobile`, `RegistrationDate`.
* **SQL Query**:
```sql
SELECT 
    c.CustomerID,
    CONCAT(c.FirstName, ' ', c.LastName) AS FullName,
    c.Email,
    c.Mobile,
    c.RegistrationDate
FROM CUSTOMER c
LEFT JOIN ACCOUNT_HOLDER ah ON c.CustomerID = ah.CustomerID
WHERE ah.AccountID IS NULL;
```

---

## Problem 9: Branch Staffing and Payroll Expenditure
* **Business Question**: How many staff members work in each branch, what is the total monthly payroll, and what is the average salary?
* **Purpose**: Branch operational expense and personnel resource planning.
* **DBMS Concepts**: Multi-aggregate grouping (`COUNT`, `SUM`, `AVG`), Rounding.
* **Expected Columns**: `BranchName`, `City`, `EmployeeCount`, `TotalPayrollCost`, `AverageSalary`.
* **SQL Query**:
```sql
SELECT 
    b.BranchName,
    b.City,
    COUNT(e.EmployeeID) AS EmployeeCount,
    COALESCE(SUM(e.Salary), 0.00) AS TotalPayrollCost,
    COALESCE(ROUND(AVG(e.Salary), 2), 0.00) AS AverageSalary
FROM BRANCH b
LEFT JOIN EMPLOYEE e ON b.BranchID = e.BranchID
GROUP BY b.BranchID, b.BranchName, b.City
ORDER BY TotalPayrollCost DESC;
```

---

## Problem 10: Top Account by Balance in Each Branch
* **Business Question**: Identify the single account holding the highest balance for each individual branch.
* **Purpose**: Dedicated high-value VIP relationship management per branch.
* **DBMS Concepts**: Correlated Subquery in `WHERE` clause.
* **Expected Columns**: `BranchName`, `AccountNumber`, `AccountType`, `Balance`.
* **SQL Query**:
```sql
SELECT 
    b.BranchName,
    a.AccountNumber,
    a.AccountType,
    a.Balance
FROM ACCOUNT a
JOIN BRANCH b ON a.BranchID = b.BranchID
WHERE a.Balance = (
    SELECT MAX(sub_a.Balance)
    FROM ACCOUNT sub_a
    WHERE sub_a.BranchID = a.BranchID AND sub_a.Status = 'Active'
)
ORDER BY a.Balance DESC;
```

---

## Problem 11: Customers Holding Active Loans
* **Business Question**: Which customers currently service an active loan facility?
* **Purpose**: Credit risk assessment and active borrower tracking.
* **DBMS Concepts**: Multi-table INNER JOIN, Status Filter, Ordering.
* **Expected Columns**: `CustomerName`, `Mobile`, `LoanType`, `LoanAmount`, `InterestRate`, `TenureMonths`, `BranchName`.
* **SQL Query**:
```sql
SELECT 
    CONCAT(c.FirstName, ' ', c.LastName) AS CustomerName,
    c.Mobile,
    l.LoanType,
    l.LoanAmount,
    l.InterestRate,
    l.TenureMonths,
    b.BranchName
FROM LOAN l
JOIN CUSTOMER c ON l.CustomerID = c.CustomerID
JOIN BRANCH b ON l.BranchID = b.BranchID
WHERE l.LoanStatus = 'Active'
ORDER BY l.LoanAmount DESC;
```

---

## Problem 12: Loan Portfolio Breakdown by Category
* **Business Question**: What is the sanction exposure and average interest rate across loan categories (Home, Personal, Education, Vehicle)?
* **Purpose**: Portfolio diversification and lending asset management.
* **DBMS Concepts**: `GROUP BY`, Multi-aggregation (`COUNT`, `SUM`, `AVG`).
* **Expected Columns**: `LoanType`, `TotalLoansCount`, `TotalSanctionedAmount`, `AverageInterestRate`.
* **SQL Query**:
```sql
SELECT 
    LoanType,
    COUNT(LoanID) AS TotalLoansCount,
    SUM(LoanAmount) AS TotalSanctionedAmount,
    ROUND(AVG(InterestRate), 2) AS AverageInterestRate
FROM LOAN
GROUP BY LoanType
ORDER BY TotalSanctionedAmount DESC;
```

---

## Problem 13: Loan Repayment Progress (Sanctioned vs Repaid vs Outstanding)
* **Business Question**: Track recovery for each loan: sanctioned amount, total repayments received, and remaining principal balance.
* **Purpose**: Credit recovery tracking and Non-Performing Asset (NPA) early warning detection.
* **DBMS Concepts**: Multi-table Aggregation with `LEFT JOIN`, Arithmetic subtraction across tables.
* **Expected Columns**: `LoanID`, `BorrowerName`, `LoanType`, `SanctionedAmount`, `TotalRepaid`, `OutstandingBalance`.
* **SQL Query**:
```sql
SELECT 
    l.LoanID,
    CONCAT(c.FirstName, ' ', c.LastName) AS BorrowerName,
    l.LoanType,
    l.LoanAmount AS SanctionedAmount,
    COALESCE(SUM(lp.Amount), 0.00) AS TotalRepaid,
    (l.LoanAmount - COALESCE(SUM(lp.Amount), 0.00)) AS OutstandingBalance
FROM LOAN l
JOIN CUSTOMER c ON l.CustomerID = c.CustomerID
LEFT JOIN LOAN_PAYMENT lp ON l.LoanID = lp.LoanID
GROUP BY l.LoanID, c.FirstName, c.LastName, l.LoanType, l.LoanAmount
ORDER BY OutstandingBalance DESC;
```

---

## Problem 14: Inactive and Zero-Balance Accounts Audit
* **Business Question**: Identify accounts that are either flagged as Inactive, Closed, or have zero balance.
* **Purpose**: Dormancy management and regulatory bank audit compliance.
* **DBMS Concepts**: Boolean Compound Logic (`OR`, `IN`).
* **Expected Columns**: `AccountNumber`, `AccountType`, `Balance`, `Status`, `BranchName`, `OpeningDate`.
* **SQL Query**:
```sql
SELECT 
    a.AccountNumber,
    a.AccountType,
    a.Balance,
    a.Status,
    b.BranchName,
    a.OpeningDate
FROM ACCOUNT a
JOIN BRANCH b ON a.BranchID = b.BranchID
WHERE a.Status IN ('Inactive', 'Closed') OR a.Balance = 0.00
ORDER BY a.Balance ASC, a.OpeningDate DESC;
```

---

## Problem 15: Inter-Account Transfer Audit with Matching Counterparts
* **Business Question**: Reconcile electronic fund transfers by pairing each `TRANSFER_OUT` record with its matching `TRANSFER_IN` counterpart.
* **Purpose**: Inter-bank and intra-bank electronic fund clearing reconciliation and fraud prevention.
* **DBMS Concepts**: Self-Join on `BANK_TRANSACTION` using matching `ReferenceNumber`.
* **Expected Columns**: `ReferenceNumber`, `TransferDate`, `SenderAccount`, `ReceiverAccount`, `TransferredAmount`.
* **SQL Query**:
```sql
SELECT 
    t_out.ReferenceNumber,
    t_out.TransactionDate AS TransferDate,
    acc_from.AccountNumber AS SenderAccount,
    acc_to.AccountNumber AS ReceiverAccount,
    t_out.Amount AS TransferredAmount
FROM BANK_TRANSACTION t_out
JOIN BANK_TRANSACTION t_in ON t_out.ReferenceNumber = t_in.ReferenceNumber
JOIN ACCOUNT acc_from ON t_out.AccountID = acc_from.AccountID
JOIN ACCOUNT acc_to ON t_in.AccountID = acc_to.AccountID
WHERE t_out.TransactionType = 'TRANSFER_OUT' 
  AND t_in.TransactionType = 'TRANSFER_IN'
ORDER BY t_out.TransactionDate DESC;
```
