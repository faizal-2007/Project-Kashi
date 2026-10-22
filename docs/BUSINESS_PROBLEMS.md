# SQL Business Problems

All queries are in `sql/business_queries.sql` and use only the implemented schema. Sample values are from the demonstration data.

## 1. Display all customers with their accounts

**Purpose:** Join CUSTOMER, ACCOUNT_HOLDER, ACCOUNT, and BRANCH to list every customer/account pair.

```sql
SELECT c.CustomerID, CONCAT(c.FirstName, ' ', c.LastName) AS CustomerName,
       c.Mobile, a.AccountNumber, a.AccountType, a.Balance,
       a.Status AS AccountStatus, b.BranchName
FROM CUSTOMER c
JOIN ACCOUNT_HOLDER ah ON ah.CustomerID = c.CustomerID
JOIN ACCOUNT a ON a.AccountID = ah.AccountID
JOIN BRANCH b ON b.BranchID = a.BranchID
ORDER BY c.CustomerID, a.AccountID;
```

**Concepts:** INNER JOIN, CONCAT, aliases.

**Columns:** CustomerID, CustomerName, Mobile, AccountNumber, AccountType, Balance, AccountStatus, BranchName. Sample: Aarav Sharma has two accounts; Diya Patel appears on a shared account and her own closed account.

## 2. Customers with multiple accounts

```sql
SELECT c.CustomerID, CONCAT(c.FirstName, ' ', c.LastName) AS CustomerName,
       COUNT(DISTINCT ah.AccountID) AS NumberOfAccounts
FROM CUSTOMER c
JOIN ACCOUNT_HOLDER ah ON ah.CustomerID = c.CustomerID
GROUP BY c.CustomerID, c.FirstName, c.LastName
HAVING COUNT(DISTINCT ah.AccountID) > 1
ORDER BY NumberOfAccounts DESC, c.CustomerID;
```

**Purpose:** Find customers who are the best cross-sell candidates.

**Concepts:** GROUP BY, HAVING, COUNT(DISTINCT), aggregate filter.

**Sample:** Customers 1, 2, and 3 each hold 2 accounts.

## 3. Accounts with branch details

```sql
SELECT a.AccountNumber, a.AccountType, a.Balance, a.Status,
       b.BranchName, b.IFSCCode, b.City, b.State
FROM ACCOUNT a
JOIN BRANCH b ON b.BranchID = a.BranchID
ORDER BY b.BranchName, a.AccountNumber;
```

**Purpose:** Branch-wise account register.

**Concepts:** INNER JOIN, ORDER BY multiple columns.

## 4. Total balance by branch

```sql
SELECT b.BranchID, b.BranchName,
       COUNT(a.AccountID) AS AccountCount,
       COALESCE(SUM(a.Balance), 0) AS TotalBalance
FROM BRANCH b
LEFT JOIN ACCOUNT a ON a.BranchID = b.BranchID
GROUP BY b.BranchID, b.BranchName
ORDER BY TotalBalance DESC;
```

**Purpose:** Branch performance and deposit mobilisation.

**Concepts:** LEFT JOIN, GROUP BY, SUM, COALESCE.

**Sample result:** Mumbai Central 3 accounts, 562500.00; Bengaluru 2 accounts, 305000.00.

## 5. Accounts above 100000

```sql
SELECT a.AccountNumber, a.AccountType, a.Balance, a.Status, b.BranchName
FROM ACCOUNT a
JOIN BRANCH b ON b.BranchID = a.BranchID
WHERE a.Balance > 100000
ORDER BY a.Balance DESC;
```

**Purpose:** Identify high-value accounts.

**Concepts:** WHERE filter, JOIN, ORDER BY.

## 6. Total deposits by account

```sql
SELECT a.AccountNumber,
       COALESCE(SUM(CASE WHEN t.TransactionType = 'DEPOSIT'
                         AND t.TransactionStatus = 'SUCCESS'
                         THEN t.Amount ELSE 0 END), 0) AS TotalDeposits
FROM ACCOUNT a
LEFT JOIN BANK_TRANSACTION t ON t.AccountID = a.AccountID
GROUP BY a.AccountID, a.AccountNumber
ORDER BY TotalDeposits DESC;
```

**Purpose:** Lifelong deposit value per account.

**Concepts:** LEFT JOIN, conditional SUM (CASE), GROUP BY.

## 7. Total withdrawals by account

```sql
SELECT a.AccountNumber,
       COALESCE(SUM(CASE WHEN t.TransactionType = 'WITHDRAWAL'
                         AND t.TransactionStatus = 'SUCCESS'
                         THEN t.Amount ELSE 0 END), 0) AS TotalWithdrawals
FROM ACCOUNT a
LEFT JOIN BANK_TRANSACTION t ON t.AccountID = a.AccountID
GROUP BY a.AccountID, a.AccountNumber
ORDER BY TotalWithdrawals DESC;
```

**Purpose:** Withdrawal behaviour reporting.

**Concepts:** Conditional aggregation, LEFT JOIN.

## 8. Transaction history for a selected customer

```sql
SELECT t.TransactionID, CONCAT(c.FirstName, ' ', c.LastName) AS CustomerName,
       a.AccountNumber, t.TransactionType, t.Amount, t.TransactionDate,
       t.ReferenceNumber, t.TransactionStatus
FROM CUSTOMER c
JOIN ACCOUNT_HOLDER ah ON ah.CustomerID = c.CustomerID
JOIN ACCOUNT a ON a.AccountID = ah.AccountID
JOIN BANK_TRANSACTION t ON t.AccountID = a.AccountID
WHERE c.CustomerID = 1
ORDER BY t.TransactionDate DESC;
```

**Purpose:** Consolidated statement for a customer across all accounts.

**Concepts:** Four-table join, WHERE, ORDER BY.

## 9. Customers without an account

```sql
SELECT c.CustomerID, CONCAT(c.FirstName, ' ', c.LastName) AS CustomerName,
       c.Mobile, c.Email
FROM CUSTOMER c
LEFT JOIN ACCOUNT_HOLDER ah ON ah.CustomerID = c.CustomerID
WHERE ah.CustomerID IS NULL
ORDER BY c.CustomerID;
```

**Purpose:** Follow-up list of registered customers without banking products.

**Concepts:** LEFT JOIN with `IS NULL` anti-join.

**Sample:** Nimisha Kulkarni (CustomerID 11) has no account.

## 10. Employees per branch

```sql
SELECT b.BranchID, b.BranchName, COUNT(e.EmployeeID) AS EmployeeCount
FROM BRANCH b
LEFT JOIN EMPLOYEE e ON e.BranchID = b.BranchID
GROUP BY b.BranchID, b.BranchName
ORDER BY EmployeeCount DESC, b.BranchName;
```

**Purpose:** Staffing report.

**Concepts:** LEFT JOIN, GROUP BY, COUNT.

## 11. Highest-balance account

```sql
SELECT a.AccountNumber, a.AccountType, a.Balance, b.BranchName,
       (SELECT GROUP_CONCAT(CONCAT(c.FirstName, ' ', c.LastName) SEPARATOR ', ')
        FROM ACCOUNT_HOLDER ah JOIN CUSTOMER c ON c.CustomerID = ah.CustomerID
        WHERE ah.AccountID = a.AccountID) AS AccountHolders
FROM ACCOUNT a
JOIN BRANCH b ON b.BranchID = a.BranchID
ORDER BY a.Balance DESC
LIMIT 1;
```

**Purpose:** Find the flagship account.

**Concepts:** Subquery, GROUP_CONCAT, ORDER BY LIMIT.

**Sample:** Account 100000000002 with 425000.00.

## 12. Customers with loans

```sql
SELECT DISTINCT c.CustomerID, CONCAT(c.FirstName, ' ', c.LastName) AS CustomerName,
       l.LoanID, l.LoanType, l.LoanAmount, l.LoanStatus
FROM CUSTOMER c
JOIN LOAN l ON l.CustomerID = c.CustomerID
ORDER BY c.CustomerID, l.LoanID;
```

**Purpose:** Borrower list.

**Concepts:** INNER JOIN, DISTINCT.

## 13. Total loan amount by type

```sql
SELECT LoanType, COUNT(*) AS LoanCount, SUM(LoanAmount) AS TotalLoanAmount,
       ROUND(AVG(InterestRate), 2) AS AverageInterestRate
FROM LOAN
WHERE LoanStatus IN ('Approved', 'Closed')
GROUP BY LoanType
ORDER BY TotalLoanAmount DESC;
```

**Purpose:** Loan-portfolio concentration by product.

**Concepts:** GROUP BY, SUM, AVG, ROUND, IN filter.

## 14. Loan-payment history

```sql
SELECT lp.PaymentID, CONCAT(c.FirstName, ' ', c.LastName) AS CustomerName,
       l.LoanID, l.LoanType, lp.PaymentDate, lp.Amount, lp.PaymentMode, lp.ReferenceNumber
FROM LOAN_PAYMENT lp
JOIN LOAN l ON l.LoanID = lp.LoanID
JOIN CUSTOMER c ON c.CustomerID = l.CustomerID
ORDER BY lp.PaymentDate DESC;
```

**Purpose:** Repayment audit trail.

**Concepts:** Multi-table join, ORDER BY.

## 15. Inactive and closed accounts

```sql
SELECT a.AccountNumber, a.AccountType, a.Balance, a.Status, b.BranchName
FROM ACCOUNT a
JOIN BRANCH b ON b.BranchID = a.BranchID
WHERE a.Status IN ('Inactive', 'Closed')
ORDER BY a.Status, a.AccountNumber;
```

**Purpose:** Dormant-account review.

**Concepts:** IN filter, JOIN.

**Sample:** Account 100000000011 (Inactive) and 100000000012 (Closed).

## 16. Successful transaction volume by branch

```sql
SELECT b.BranchName, COUNT(t.TransactionID) AS TransactionCount,
       COALESCE(SUM(t.Amount), 0) AS TransactionValue
FROM BRANCH b
JOIN ACCOUNT a ON a.BranchID = b.BranchID
JOIN BANK_TRANSACTION t ON t.AccountID = a.AccountID
WHERE t.TransactionStatus = 'SUCCESS'
GROUP BY b.BranchID, b.BranchName
ORDER BY TransactionValue DESC;
```

**Purpose:** Branch activity ranking.

**Concepts:** Three-table join, WHERE, GROUP BY, SUM.

## 17. Customers above the average account balance

```sql
SELECT c.CustomerID, CONCAT(c.FirstName, ' ', c.LastName) AS CustomerName,
       SUM(a.Balance) AS CombinedBalance
FROM CUSTOMER c
JOIN ACCOUNT_HOLDER ah ON ah.CustomerID = c.CustomerID
JOIN ACCOUNT a ON a.AccountID = ah.AccountID
GROUP BY c.CustomerID, c.FirstName, c.LastName
HAVING SUM(a.Balance) > (SELECT AVG(Balance) FROM ACCOUNT)
ORDER BY CombinedBalance DESC;
```

**Purpose:** Premium-customer identification.

**Concepts:** HAVING, subquery in comparison, SUM.

## 18. Monthly deposit and withdrawal totals

```sql
SELECT DATE_FORMAT(TransactionDate, '%Y-%m') AS TransactionMonth,
       SUM(CASE WHEN TransactionType = 'DEPOSIT' THEN Amount ELSE 0 END) AS DepositTotal,
       SUM(CASE WHEN TransactionType = 'WITHDRAWAL' THEN Amount ELSE 0 END) AS WithdrawalTotal,
       COUNT(*) AS TransactionCount
FROM BANK_TRANSACTION
WHERE TransactionStatus = 'SUCCESS'
GROUP BY DATE_FORMAT(TransactionDate, '%Y-%m')
ORDER BY TransactionMonth;
```

**Purpose:** Month-wise cash-flow trend.

**Concepts:** Date function, conditional aggregation, GROUP BY.
