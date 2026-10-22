-- Project Kashi - database views
USE project_kashi;

CREATE OR REPLACE VIEW vw_customer_account_summary AS
SELECT
    c.CustomerID,
    CONCAT(c.FirstName, ' ', c.LastName) AS CustomerName,
    c.Mobile,
    c.Email,
    a.AccountID,
    a.AccountNumber,
    a.AccountType,
    a.Balance,
    a.Status AS AccountStatus,
    b.BranchName,
    b.City AS BranchCity,
    ah.HolderType,
    ah.HolderSince
FROM CUSTOMER c
LEFT JOIN ACCOUNT_HOLDER ah ON ah.CustomerID = c.CustomerID
LEFT JOIN ACCOUNT a ON a.AccountID = ah.AccountID
LEFT JOIN BRANCH b ON b.BranchID = a.BranchID;

CREATE OR REPLACE VIEW vw_account_details AS
SELECT
    a.AccountID,
    a.AccountNumber,
    a.AccountType,
    a.OpeningDate,
    a.Balance,
    a.Status,
    b.BranchID,
    b.BranchName,
    b.IFSCCode,
    b.City AS BranchCity,
    b.State AS BranchState,
    (SELECT COUNT(*) FROM ACCOUNT_HOLDER ah WHERE ah.AccountID = a.AccountID) AS HolderCount,
    (SELECT GROUP_CONCAT(CONCAT(c.FirstName, ' ', c.LastName) ORDER BY ah.HolderType SEPARATOR ', ')
       FROM ACCOUNT_HOLDER ah
       JOIN CUSTOMER c ON c.CustomerID = ah.CustomerID
      WHERE ah.AccountID = a.AccountID) AS HolderNames,
    (SELECT CONCAT(c.FirstName, ' ', c.LastName)
       FROM ACCOUNT_HOLDER ah
       JOIN CUSTOMER c ON c.CustomerID = ah.CustomerID
      WHERE ah.AccountID = a.AccountID AND ah.HolderType = 'Primary'
      LIMIT 1) AS PrimaryHolderName
FROM ACCOUNT a
JOIN BRANCH b ON b.BranchID = a.BranchID;

CREATE OR REPLACE VIEW vw_account_transaction_history AS
SELECT
    t.TransactionID,
    t.AccountID,
    a.AccountNumber,
    a.AccountType,
    b.BranchName,
    t.TransactionType,
    t.Amount,
    t.TransactionDate,
    t.Description,
    t.ReferenceNumber,
    t.TransferGroupReference,
    t.TransactionStatus,
    (SELECT GROUP_CONCAT(CONCAT(c.FirstName, ' ', c.LastName) ORDER BY ah.HolderType SEPARATOR ', ')
       FROM ACCOUNT_HOLDER ah
       JOIN CUSTOMER c ON c.CustomerID = ah.CustomerID
      WHERE ah.AccountID = a.AccountID) AS HolderNames
FROM BANK_TRANSACTION t
JOIN ACCOUNT a ON a.AccountID = t.AccountID
JOIN BRANCH b ON b.BranchID = a.BranchID;

CREATE OR REPLACE VIEW vw_branch_summary AS
SELECT
    b.BranchID,
    b.BranchName,
    b.IFSCCode,
    b.City,
    b.State,
    (SELECT COUNT(*) FROM EMPLOYEE e WHERE e.BranchID = b.BranchID) AS EmployeeCount,
    (SELECT COUNT(*) FROM ACCOUNT a WHERE a.BranchID = b.BranchID) AS AccountCount,
    (SELECT COUNT(*) FROM ACCOUNT a WHERE a.BranchID = b.BranchID AND a.Status = 'Active') AS ActiveAccountCount,
    (SELECT COALESCE(SUM(a.Balance), 0) FROM ACCOUNT a WHERE a.BranchID = b.BranchID) AS TotalBalance
FROM BRANCH b;

CREATE OR REPLACE VIEW vw_loan_payment_summary AS
SELECT
    l.LoanID,
    l.CustomerID,
    CONCAT(c.FirstName, ' ', c.LastName) AS CustomerName,
    l.BranchID,
    b.BranchName,
    l.LoanType,
    l.LoanAmount,
    l.InterestRate,
    l.StartDate,
    l.TenureMonths,
    l.LoanStatus,
    COALESCE(SUM(lp.Amount), 0) AS TotalPaid,
    GREATEST(l.LoanAmount - COALESCE(SUM(lp.Amount), 0), 0) AS OutstandingAmount,
    COUNT(lp.PaymentID) AS PaymentCount
FROM LOAN l
JOIN CUSTOMER c ON c.CustomerID = l.CustomerID
JOIN BRANCH b ON b.BranchID = l.BranchID
LEFT JOIN LOAN_PAYMENT lp ON lp.LoanID = l.LoanID
GROUP BY
    l.LoanID,
    l.CustomerID,
    c.FirstName,
    c.LastName,
    l.BranchID,
    b.BranchName,
    l.LoanType,
    l.LoanAmount,
    l.InterestRate,
    l.StartDate,
    l.TenureMonths,
    l.LoanStatus;

CREATE OR REPLACE VIEW vw_customer_loan_summary AS
SELECT
    c.CustomerID,
    CONCAT(c.FirstName, ' ', c.LastName) AS CustomerName,
    COUNT(l.LoanID) AS TotalLoans,
    COALESCE(SUM(CASE WHEN l.LoanStatus = 'Approved' THEN l.LoanAmount ELSE 0 END), 0) AS ApprovedLoanAmount,
    COALESCE(SUM(CASE WHEN l.LoanStatus = 'Pending' THEN 1 ELSE 0 END), 0) AS PendingLoanCount
FROM CUSTOMER c
LEFT JOIN LOAN l ON l.CustomerID = c.CustomerID
GROUP BY c.CustomerID, c.FirstName, c.LastName;
