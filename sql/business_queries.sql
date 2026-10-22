-- ============================================================================
-- PROJECT KASHI — BANKING MANAGEMENT SYSTEM
-- Script: business_queries.sql
-- Purpose: 15 Real-World SQL Business Queries with Explanations & Concepts
-- Database: project_kashi
-- ============================================================================

USE project_kashi;

-- ----------------------------------------------------------------------------
-- PROBLEM 1: Display all customers along with their linked bank accounts.
-- Purpose: Customer 360-degree overview of accounts held.
-- DBMS Concepts: Multi-table INNER JOIN, String Concatenation.
-- Expected Columns: CustomerID, FullName, Email, AccountNumber, AccountType, Balance, BranchName
-- ----------------------------------------------------------------------------
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

-- ----------------------------------------------------------------------------
-- PROBLEM 2: Find customers who hold multiple bank accounts.
-- Purpose: Identify high-engagement customers eligible for relationship banking.
-- DBMS Concepts: GROUP BY, HAVING COUNT(*) > 1, Aggregation.
-- Expected Columns: CustomerID, FullName, Mobile, TotalAccountsOwned
-- ----------------------------------------------------------------------------
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

-- ----------------------------------------------------------------------------
-- PROBLEM 3: Display all bank accounts with their branch details and manager name.
-- Purpose: Audit branch account ownership and managerial responsibility.
-- DBMS Concepts: Multi-table JOIN with self-filtering / conditional join on Employee designation.
-- Expected Columns: AccountNumber, AccountType, Balance, Status, BranchName, BranchCity, BranchManager
-- ----------------------------------------------------------------------------
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

-- ----------------------------------------------------------------------------
-- PROBLEM 4: Calculate the total deposits and average account balance for each branch.
-- Purpose: Assess financial performance and liquidity distribution per branch.
-- DBMS Concepts: GROUP BY, Aggregate functions (SUM, AVG, COUNT), Formatting.
-- Expected Columns: BranchID, BranchName, ActiveAccountsCount, TotalDeposits, AverageBalance
-- ----------------------------------------------------------------------------
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

-- ----------------------------------------------------------------------------
-- PROBLEM 5: Find accounts with balances above the overall bank-wide average balance.
-- Purpose: Identify high-net-worth accounts for premium wealth management services.
-- DBMS Concepts: Scalar Subquery, WHERE filter with nested SELECT.
-- Expected Columns: AccountNumber, AccountType, Balance, Status, BranchName
-- ----------------------------------------------------------------------------
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

-- ----------------------------------------------------------------------------
-- PROBLEM 6: Calculate total deposits, total withdrawals, and net volume by account.
-- Purpose: Profile transactional velocity and cash-flow activity per account.
-- DBMS Concepts: Conditional aggregation (SUM CASE), LEFT JOIN, GROUP BY.
-- Expected Columns: AccountNumber, AccountType, TotalDeposited, TotalWithdrawn, NetCashFlow
-- ----------------------------------------------------------------------------
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

-- ----------------------------------------------------------------------------
-- PROBLEM 7: Display complete transaction statement for a selected customer.
-- Purpose: Generate an official customer account statement / passbook view.
-- DBMS Concepts: 4-table JOIN (CUSTOMER -> ACCOUNT_HOLDER -> ACCOUNT -> BANK_TRANSACTION).
-- Expected Columns: TransactionID, ReferenceNumber, TransactionDate, AccountNumber, TransactionType, Amount, Description
-- ----------------------------------------------------------------------------
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

-- ----------------------------------------------------------------------------
-- PROBLEM 8: Find customers who have registered but do NOT own any bank accounts.
-- Purpose: Inactive lead detection for onboarding and sales follow-up.
-- DBMS Concepts: LEFT JOIN with NULL check, NOT EXISTS alternative.
-- Expected Columns: CustomerID, FullName, Email, Mobile, RegistrationDate
-- ----------------------------------------------------------------------------
SELECT 
    c.CustomerID,
    CONCAT(c.FirstName, ' ', c.LastName) AS FullName,
    c.Email,
    c.Mobile,
    c.RegistrationDate
FROM CUSTOMER c
LEFT JOIN ACCOUNT_HOLDER ah ON c.CustomerID = ah.CustomerID
WHERE ah.AccountID IS NULL;

-- ----------------------------------------------------------------------------
-- PROBLEM 9: Display the number of employees and total payroll expenditure per branch.
-- Purpose: Branch administrative cost and staffing evaluation.
-- DBMS Concepts: Aggregation, GROUP BY, LEFT JOIN.
-- Expected Columns: BranchName, City, EmployeeCount, TotalPayrollCost, AverageSalary
-- ----------------------------------------------------------------------------
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

-- ----------------------------------------------------------------------------
-- PROBLEM 10: Find the account with the highest balance in each branch.
-- Purpose: Identify top branch accounts for VIP client allocation.
-- DBMS Concepts: Correlated Subquery / Window Function emulation.
-- Expected Columns: BranchName, AccountNumber, AccountType, Balance
-- ----------------------------------------------------------------------------
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

-- ----------------------------------------------------------------------------
-- PROBLEM 11: Display customers who currently hold an active loan.
-- Purpose: Credit monitoring and customer debt exposure analysis.
-- DBMS Concepts: Multi-table JOIN with status filtering.
-- Expected Columns: CustomerName, Mobile, LoanType, LoanAmount, InterestRate, TenureMonths, BranchName
-- ----------------------------------------------------------------------------
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

-- ----------------------------------------------------------------------------
-- PROBLEM 12: Calculate total loan amounts and active count grouped by loan category.
-- Purpose: Portfolio risk distribution across asset classes (Home, Education, Vehicle, Personal).
-- DBMS Concepts: GROUP BY, Aggregate functions (COUNT, SUM, AVG).
-- Expected Columns: LoanType, TotalLoansCount, TotalSanctionedAmount, AverageInterestRate
-- ----------------------------------------------------------------------------
SELECT 
    LoanType,
    COUNT(LoanID) AS TotalLoansCount,
    SUM(LoanAmount) AS TotalSanctionedAmount,
    ROUND(AVG(InterestRate), 2) AS AverageInterestRate
FROM LOAN
GROUP BY LoanType
ORDER BY TotalSanctionedAmount DESC;

-- ----------------------------------------------------------------------------
-- PROBLEM 13: Display loan repayment progress: Sanctioned Amount vs Total Paid vs Outstanding.
-- Purpose: Credit recovery tracking and non-performing asset risk mitigation.
-- DBMS Concepts: Aggregation over child table with LEFT JOIN, arithmetic in SELECT.
-- Expected Columns: LoanID, BorrowerName, LoanType, SanctionedAmount, TotalRepaid, OutstandingBalance
-- ----------------------------------------------------------------------------
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

-- ----------------------------------------------------------------------------
-- PROBLEM 14: Identify inactive and zero-balance accounts requiring review or closure.
-- Purpose: Bank operational compliance to purge dormant accounts.
-- DBMS Concepts: Boolean compound filter with OR, IN, comparison operators.
-- Expected Columns: AccountNumber, AccountType, Balance, Status, BranchName, OpeningDate
-- ----------------------------------------------------------------------------
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

-- ----------------------------------------------------------------------------
-- PROBLEM 15: Find all fund transfers with matching sender and receiver transactions.
-- Purpose: Inter-account transfer audit and reconciliation.
-- DBMS Concepts: Self-join on BANK_TRANSACTION using ReferenceNumber.
-- Expected Columns: ReferenceNumber, TransferDate, SenderAccount, ReceiverAccount, TransferredAmount
-- ----------------------------------------------------------------------------
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
