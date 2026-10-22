-- ============================================================================
-- PROJECT KASHI — BANKING MANAGEMENT SYSTEM
-- Script: views.sql
-- Purpose: Database Views for Reporting, Security, and Simplified Querying
-- Database: project_kashi
-- ============================================================================

USE project_kashi;

-- ----------------------------------------------------------------------------
-- VIEW 1: vw_customer_account_summary
-- Purpose: Consolidates customer profiles with account details and balances.
-- Simplifies customer-centric dashboard lookups without complex manual joins.
-- ----------------------------------------------------------------------------
DROP VIEW IF EXISTS vw_customer_account_summary;
CREATE VIEW vw_customer_account_summary AS
SELECT 
    c.CustomerID,
    CONCAT(c.FirstName, ' ', c.LastName) AS CustomerFullName,
    c.Email,
    c.Mobile,
    c.City AS CustomerCity,
    a.AccountID,
    a.AccountNumber,
    a.AccountType,
    a.Balance,
    a.Status AS AccountStatus,
    ah.HolderType,
    ah.HolderSince,
    b.BranchID,
    b.BranchName,
    b.IFSCCode
FROM CUSTOMER c
JOIN ACCOUNT_HOLDER ah ON c.CustomerID = ah.CustomerID
JOIN ACCOUNT a ON ah.AccountID = a.AccountID
JOIN BRANCH b ON a.BranchID = b.BranchID;

-- ----------------------------------------------------------------------------
-- VIEW 2: vw_account_transaction_history
-- Purpose: Enriches transactions with account number, holder, and branch info.
-- Useful for generating comprehensive statements and passbook views.
-- ----------------------------------------------------------------------------
DROP VIEW IF EXISTS vw_account_transaction_history;
CREATE VIEW vw_account_transaction_history AS
SELECT 
    t.TransactionID,
    t.ReferenceNumber,
    t.TransactionDate,
    t.TransactionType,
    t.Amount,
    t.TransactionStatus,
    t.Description,
    a.AccountID,
    a.AccountNumber,
    a.AccountType,
    a.Balance AS CurrentBalance,
    b.BranchName,
    b.IFSCCode
FROM BANK_TRANSACTION t
JOIN ACCOUNT a ON t.AccountID = a.AccountID
JOIN BRANCH b ON a.BranchID = b.BranchID;

-- ----------------------------------------------------------------------------
-- VIEW 3: vw_branch_performance_summary
-- Purpose: Aggregates branch performance: account counts, total deposits,
-- staff count, and active loan exposure.
-- ----------------------------------------------------------------------------
DROP VIEW IF EXISTS vw_branch_performance_summary;
CREATE VIEW vw_branch_performance_summary AS
SELECT 
    b.BranchID,
    b.BranchName,
    b.City,
    b.IFSCCode,
    COUNT(DISTINCT a.AccountID) AS TotalAccounts,
    COALESCE(SUM(a.Balance), 0.00) AS TotalDepositBalance,
    COUNT(DISTINCT e.EmployeeID) AS TotalEmployees,
    COUNT(DISTINCT l.LoanID) AS TotalLoansExtended,
    COALESCE(SUM(l.LoanAmount), 0.00) AS TotalLoanExposure
FROM BRANCH b
LEFT JOIN ACCOUNT a ON b.BranchID = a.BranchID AND a.Status = 'Active'
LEFT JOIN EMPLOYEE e ON b.BranchID = e.BranchID
LEFT JOIN LOAN l ON b.BranchID = l.BranchID AND l.LoanStatus = 'Active'
GROUP BY b.BranchID, b.BranchName, b.City, b.IFSCCode;

-- ----------------------------------------------------------------------------
-- VIEW 4: vw_loan_payment_summary
-- Purpose: Aggregates total payments made per loan and calculates remaining
-- principal balance against original loan sanction amount.
-- ----------------------------------------------------------------------------
DROP VIEW IF EXISTS vw_loan_payment_summary;
CREATE VIEW vw_loan_payment_summary AS
SELECT 
    l.LoanID,
    CONCAT(c.FirstName, ' ', c.LastName) AS CustomerName,
    c.Mobile,
    l.LoanType,
    l.LoanAmount,
    l.InterestRate,
    l.TenureMonths,
    l.LoanStatus,
    b.BranchName,
    COALESCE(SUM(lp.Amount), 0.00) AS TotalAmountRepaid,
    (l.LoanAmount - COALESCE(SUM(lp.Amount), 0.00)) AS OutstandingPrincipal,
    COUNT(lp.PaymentID) AS TotalInstallmentsPaid
FROM LOAN l
JOIN CUSTOMER c ON l.CustomerID = c.CustomerID
JOIN BRANCH b ON l.BranchID = b.BranchID
LEFT JOIN LOAN_PAYMENT lp ON l.LoanID = lp.LoanID
GROUP BY 
    l.LoanID, c.FirstName, c.LastName, c.Mobile, l.LoanType, 
    l.LoanAmount, l.InterestRate, l.TenureMonths, l.LoanStatus, b.BranchName;
