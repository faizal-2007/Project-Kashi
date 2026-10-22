-- Project Kashi - SQL business problems
-- Run after loading schema.sql and sample_data.sql.
USE project_kashi;

-- 1. Display all customers with their accounts.
SELECT
    c.CustomerID,
    CONCAT(c.FirstName, ' ', c.LastName) AS CustomerName,
    c.Mobile,
    a.AccountNumber,
    a.AccountType,
    a.Balance,
    a.Status AS AccountStatus,
    b.BranchName
FROM CUSTOMER c
JOIN ACCOUNT_HOLDER ah ON ah.CustomerID = c.CustomerID
JOIN ACCOUNT a ON a.AccountID = ah.AccountID
JOIN BRANCH b ON b.BranchID = a.BranchID
ORDER BY c.CustomerID, a.AccountID;

-- 2. Find customers who hold more than one account.
SELECT
    c.CustomerID,
    CONCAT(c.FirstName, ' ', c.LastName) AS CustomerName,
    COUNT(DISTINCT ah.AccountID) AS NumberOfAccounts
FROM CUSTOMER c
JOIN ACCOUNT_HOLDER ah ON ah.CustomerID = c.CustomerID
GROUP BY c.CustomerID, c.FirstName, c.LastName
HAVING COUNT(DISTINCT ah.AccountID) > 1
ORDER BY NumberOfAccounts DESC, c.CustomerID;

-- 3. Display accounts with their branch details.
SELECT
    a.AccountNumber,
    a.AccountType,
    a.Balance,
    a.Status,
    b.BranchName,
    b.IFSCCode,
    b.City,
    b.State
FROM ACCOUNT a
JOIN BRANCH b ON b.BranchID = a.BranchID
ORDER BY b.BranchName, a.AccountNumber;

-- 4. Calculate the total balance held by accounts in each branch.
SELECT
    b.BranchID,
    b.BranchName,
    COUNT(a.AccountID) AS AccountCount,
    COALESCE(SUM(a.Balance), 0) AS TotalBalance
FROM BRANCH b
LEFT JOIN ACCOUNT a ON a.BranchID = b.BranchID
GROUP BY b.BranchID, b.BranchName
ORDER BY TotalBalance DESC;

-- 5. Find accounts whose balance is above 100000.
SELECT
    a.AccountNumber,
    a.AccountType,
    a.Balance,
    a.Status,
    b.BranchName
FROM ACCOUNT a
JOIN BRANCH b ON b.BranchID = a.BranchID
WHERE a.Balance > 100000
ORDER BY a.Balance DESC;

-- 6. Calculate total successful deposits for every account.
SELECT
    a.AccountNumber,
    COALESCE(SUM(CASE
        WHEN t.TransactionType = 'DEPOSIT' AND t.TransactionStatus = 'SUCCESS'
        THEN t.Amount ELSE 0 END), 0) AS TotalDeposits
FROM ACCOUNT a
LEFT JOIN BANK_TRANSACTION t ON t.AccountID = a.AccountID
GROUP BY a.AccountID, a.AccountNumber
ORDER BY TotalDeposits DESC;

-- 7. Calculate total successful withdrawals for every account.
SELECT
    a.AccountNumber,
    COALESCE(SUM(CASE
        WHEN t.TransactionType = 'WITHDRAWAL' AND t.TransactionStatus = 'SUCCESS'
        THEN t.Amount ELSE 0 END), 0) AS TotalWithdrawals
FROM ACCOUNT a
LEFT JOIN BANK_TRANSACTION t ON t.AccountID = a.AccountID
GROUP BY a.AccountID, a.AccountNumber
ORDER BY TotalWithdrawals DESC;

-- 8. Display transaction history for a selected customer (CustomerID = 1).
SELECT
    t.TransactionID,
    CONCAT(c.FirstName, ' ', c.LastName) AS CustomerName,
    a.AccountNumber,
    t.TransactionType,
    t.Amount,
    t.TransactionDate,
    t.ReferenceNumber,
    t.TransactionStatus
FROM CUSTOMER c
JOIN ACCOUNT_HOLDER ah ON ah.CustomerID = c.CustomerID
JOIN ACCOUNT a ON a.AccountID = ah.AccountID
JOIN BANK_TRANSACTION t ON t.AccountID = a.AccountID
WHERE c.CustomerID = 1
ORDER BY t.TransactionDate DESC;

-- 9. Find customers who do not have an account.
SELECT
    c.CustomerID,
    CONCAT(c.FirstName, ' ', c.LastName) AS CustomerName,
    c.Mobile,
    c.Email
FROM CUSTOMER c
LEFT JOIN ACCOUNT_HOLDER ah ON ah.CustomerID = c.CustomerID
WHERE ah.CustomerID IS NULL
ORDER BY c.CustomerID;

-- 10. Display the number of employees in each branch.
SELECT
    b.BranchID,
    b.BranchName,
    COUNT(e.EmployeeID) AS EmployeeCount
FROM BRANCH b
LEFT JOIN EMPLOYEE e ON e.BranchID = b.BranchID
GROUP BY b.BranchID, b.BranchName
ORDER BY EmployeeCount DESC, b.BranchName;

-- 11. Find the account with the highest balance.
SELECT
    a.AccountNumber,
    a.AccountType,
    a.Balance,
    b.BranchName,
    (SELECT GROUP_CONCAT(CONCAT(c.FirstName, ' ', c.LastName) SEPARATOR ', ')
       FROM ACCOUNT_HOLDER ah
       JOIN CUSTOMER c ON c.CustomerID = ah.CustomerID
      WHERE ah.AccountID = a.AccountID) AS AccountHolders
FROM ACCOUNT a
JOIN BRANCH b ON b.BranchID = a.BranchID
ORDER BY a.Balance DESC
LIMIT 1;

-- 12. Display customers who have loans.
SELECT DISTINCT
    c.CustomerID,
    CONCAT(c.FirstName, ' ', c.LastName) AS CustomerName,
    l.LoanID,
    l.LoanType,
    l.LoanAmount,
    l.LoanStatus
FROM CUSTOMER c
JOIN LOAN l ON l.CustomerID = c.CustomerID
ORDER BY c.CustomerID, l.LoanID;

-- 13. Calculate total loan amounts by loan type for approved or closed loans.
SELECT
    LoanType,
    COUNT(*) AS LoanCount,
    SUM(LoanAmount) AS TotalLoanAmount,
    ROUND(AVG(InterestRate), 2) AS AverageInterestRate
FROM LOAN
WHERE LoanStatus IN ('Approved', 'Closed')
GROUP BY LoanType
ORDER BY TotalLoanAmount DESC;

-- 14. Display loan-payment history.
SELECT
    lp.PaymentID,
    CONCAT(c.FirstName, ' ', c.LastName) AS CustomerName,
    l.LoanID,
    l.LoanType,
    lp.PaymentDate,
    lp.Amount,
    lp.PaymentMode,
    lp.ReferenceNumber
FROM LOAN_PAYMENT lp
JOIN LOAN l ON l.LoanID = lp.LoanID
JOIN CUSTOMER c ON c.CustomerID = l.CustomerID
ORDER BY lp.PaymentDate DESC;

-- 15. Identify inactive or closed accounts.
SELECT
    a.AccountNumber,
    a.AccountType,
    a.Balance,
    a.Status,
    b.BranchName
FROM ACCOUNT a
JOIN BRANCH b ON b.BranchID = a.BranchID
WHERE a.Status IN ('Inactive', 'Closed')
ORDER BY a.Status, a.AccountNumber;

-- 16. Show successful transaction volume by branch.
SELECT
    b.BranchName,
    COUNT(t.TransactionID) AS TransactionCount,
    COALESCE(SUM(t.Amount), 0) AS TransactionValue
FROM BRANCH b
JOIN ACCOUNT a ON a.BranchID = b.BranchID
JOIN BANK_TRANSACTION t ON t.AccountID = a.AccountID
WHERE t.TransactionStatus = 'SUCCESS'
GROUP BY b.BranchID, b.BranchName
ORDER BY TransactionValue DESC;

-- 17. Find customers whose combined account balance is above the overall average account balance.
SELECT
    c.CustomerID,
    CONCAT(c.FirstName, ' ', c.LastName) AS CustomerName,
    SUM(a.Balance) AS CombinedBalance
FROM CUSTOMER c
JOIN ACCOUNT_HOLDER ah ON ah.CustomerID = c.CustomerID
JOIN ACCOUNT a ON a.AccountID = ah.AccountID
GROUP BY c.CustomerID, c.FirstName, c.LastName
HAVING SUM(a.Balance) > (SELECT AVG(Balance) FROM ACCOUNT)
ORDER BY CombinedBalance DESC;

-- 18. Show the monthly value of successful deposits and withdrawals.
SELECT
    DATE_FORMAT(TransactionDate, '%Y-%m') AS TransactionMonth,
    SUM(CASE WHEN TransactionType = 'DEPOSIT' THEN Amount ELSE 0 END) AS DepositTotal,
    SUM(CASE WHEN TransactionType = 'WITHDRAWAL' THEN Amount ELSE 0 END) AS WithdrawalTotal,
    COUNT(*) AS TransactionCount
FROM BANK_TRANSACTION
WHERE TransactionStatus = 'SUCCESS'
GROUP BY DATE_FORMAT(TransactionDate, '%Y-%m')
ORDER BY TransactionMonth;
