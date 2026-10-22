-- ============================================================================
-- PROJECT KASHI — BANKING MANAGEMENT SYSTEM
-- Script: sample_data.sql
-- Purpose: Realistic Academic Demonstration Data for all 8 Tables
-- Database: project_kashi
-- ============================================================================

USE project_kashi;

-- Clear existing data safely
SET FOREIGN_KEY_CHECKS = 0;
TRUNCATE TABLE LOAN_PAYMENT;
TRUNCATE TABLE LOAN;
TRUNCATE TABLE BANK_TRANSACTION;
TRUNCATE TABLE ACCOUNT_HOLDER;
TRUNCATE TABLE ACCOUNT;
TRUNCATE TABLE EMPLOYEE;
TRUNCATE TABLE CUSTOMER;
TRUNCATE TABLE BRANCH;
SET FOREIGN_KEY_CHECKS = 1;

-- ----------------------------------------------------------------------------
-- 1. INSERT BRANCH DATA
-- ----------------------------------------------------------------------------
INSERT INTO BRANCH (BranchID, BranchName, IFSCCode, Address, City, State, ContactNumber) VALUES
(1, 'Kashi Main Branch', 'KASH0001001', 'Dashashwamedh Ghat Road', 'Varanasi', 'Uttar Pradesh', '0542-2451001'),
(2, 'Varanasi Cantt Branch', 'KASH0001002', 'Cantonment Station Plaza', 'Varanasi', 'Uttar Pradesh', '0542-2451002'),
(3, 'New Delhi Central Branch', 'KASH0002001', 'Barakhamba Road, Connaught Place', 'New Delhi', 'Delhi', '011-23711001'),
(4, 'Mumbai Heritage Branch', 'KASH0003001', 'Horniman Circle, Fort', 'Mumbai', 'Maharashtra', '022-22661001'),
(5, 'Bengaluru Tech Branch', 'KASH0004001', '100 Feet Road, Indiranagar', 'Bengaluru', 'Karnataka', '080-25251001');

-- ----------------------------------------------------------------------------
-- 2. INSERT EMPLOYEE DATA
-- ----------------------------------------------------------------------------
INSERT INTO EMPLOYEE (EmployeeID, EmployeeName, Mobile, Email, Designation, Salary, JoiningDate, BranchID) VALUES
(1, 'Aditya Narayan Sharma', '9876543210', 'aditya.sharma@kashibank.com', 'Branch Manager', 85000.00, '2020-03-15', 1),
(2, 'Priya Kulkarni', '9876543211', 'priya.k@kashibank.com', 'Senior Cashier', 52000.00, '2021-06-10', 1),
(3, 'Rajesh Kumar Verma', '9876543212', 'rajesh.v@kashibank.com', 'Loan Officer', 60000.00, '2021-11-01', 1),
(4, 'Sunita Deshmukh', '9876543213', 'sunita.d@kashibank.com', 'Branch Manager', 88000.00, '2019-01-20', 2),
(5, 'Vikram Malhotra', '9876543214', 'vikram.m@kashibank.com', 'Assistant Manager', 65000.00, '2022-04-12', 3),
(6, 'Neha Sengupta', '9876543215', 'neha.s@kashibank.com', 'Branch Manager', 92000.00, '2018-09-01', 4),
(7, 'Ramesh Babu', '9876543216', 'ramesh.b@kashibank.com', 'Operations Officer', 58000.00, '2022-08-15', 5),
(8, 'Ananya Iyer', '9876543217', 'ananya.i@kashibank.com', 'Customer Relationship Exec', 45000.00, '2023-02-01', 5);

-- ----------------------------------------------------------------------------
-- 3. INSERT CUSTOMER DATA
-- ----------------------------------------------------------------------------
INSERT INTO CUSTOMER (CustomerID, FirstName, LastName, DateOfBirth, Gender, Mobile, Email, Address, City, RegistrationDate) VALUES
(1, 'Aarav', 'Pandey', '1990-05-14', 'Male', '9811122233', 'aarav.pandey@example.com', 'B-12 Assi Ghat', 'Varanasi', '2023-01-10 10:30:00'),
(2, 'Divya', 'Tripathi', '1995-08-22', 'Female', '9822233344', 'divya.tripathi@example.com', 'Plot 45, Lanka Road', 'Varanasi', '2023-02-14 11:15:00'),
(3, 'Rohan', 'Kapoor', '1988-11-30', 'Male', '9833344455', 'rohan.kapoor@example.com', 'Flat 302, Green Park', 'New Delhi', '2023-03-05 14:20:00'),
(4, 'Meera', 'Nair', '1992-04-18', 'Female', '9844455566', 'meera.nair@example.com', '12/A Cuffe Parade', 'Mumbai', '2023-04-18 09:45:00'),
(5, 'Siddharth', 'Rao', '1985-07-09', 'Male', '9855566677', 'siddharth.rao@example.com', '77 Defence Colony, Indiranagar', 'Bengaluru', '2023-05-22 16:00:00'),
(6, 'Pooja', 'Singh', '1998-12-03', 'Female', '9866677788', 'pooja.singh@example.com', '10 Shivpur Colony', 'Varanasi', '2023-06-11 12:10:00'),
(7, 'Amit', 'Banerjee', '1982-03-25', 'Male', '9877788899', 'amit.banerjee@example.com', '54 Southern Avenue', 'Kolkata', '2023-07-19 15:30:00'),
(8, 'Kavita', 'Joshi', '1994-09-17', 'Female', '9888899900', 'kavita.joshi@example.com', '88 Model Town', 'New Delhi', '2023-08-01 10:00:00'),
(9, 'Faizan', 'Khan', '1996-01-28', 'Male', '9899900011', 'faizan.khan@example.com', '14 Nadesar Palace Road', 'Varanasi', '2023-09-15 13:40:00'),
(10, 'Sunil', 'Chopra', '1975-06-12', 'Male', '9800011122', 'sunil.chopra@example.com', '21 Linking Road, Bandra', 'Mumbai', '2023-10-05 17:15:00');

-- ----------------------------------------------------------------------------
-- 4. INSERT ACCOUNT DATA
-- ----------------------------------------------------------------------------
INSERT INTO ACCOUNT (AccountID, AccountNumber, AccountType, OpeningDate, Balance, Status, BranchID) VALUES
(1, '1001001001', 'Saving', '2023-01-10 10:45:00', 45000.00, 'Active', 1),
(2, '1001001002', 'Current', '2023-01-15 12:00:00', 125000.00, 'Active', 1),
(3, '1001001003', 'Salary', '2023-02-14 11:30:00', 68000.00, 'Active', 1),
(4, '1002001001', 'Saving', '2023-03-05 14:45:00', 92000.00, 'Active', 3),
(5, '1003001001', 'Saving', '2023-04-18 10:15:00', 210000.00, 'Active', 4),
(6, '1004001001', 'Salary', '2023-05-22 16:30:00', 85000.00, 'Active', 5),
(7, '1001001004', 'Saving', '2023-06-11 12:30:00', 32000.00, 'Active', 2),
(8, '1002001002', 'Current', '2023-08-01 10:30:00', 154000.00, 'Active', 3),
(9, '1001001005', 'Saving', '2023-09-15 14:00:00', 15000.00, 'Active', 1),
(10, '1003001002', 'Saving', '2023-10-05 17:30:00', 500000.00, 'Active', 4),
(11, '1001001006', 'Saving', '2023-11-10 09:00:00', 500.00, 'Inactive', 1),
(12, '1001001007', 'Current', '2023-12-01 11:00:00', 0.00, 'Closed', 2);

-- ----------------------------------------------------------------------------
-- 5. INSERT ACCOUNT_HOLDER RELATIONSHIPS
-- Demonstrating 1:N and M:N relationships (Primary and Joint holders)
-- ----------------------------------------------------------------------------
INSERT INTO ACCOUNT_HOLDER (CustomerID, AccountID, HolderSince, HolderType) VALUES
(1, 1, '2023-01-10 10:45:00', 'Primary'),
(1, 2, '2023-01-15 12:00:00', 'Primary'), -- Customer 1 owns multiple accounts
(2, 3, '2023-02-14 11:30:00', 'Primary'),
(3, 4, '2023-03-05 14:45:00', 'Primary'),
(4, 5, '2023-04-18 10:15:00', 'Primary'),
(5, 6, '2023-05-22 16:30:00', 'Primary'),
(6, 7, '2023-06-11 12:30:00', 'Primary'),
(8, 8, '2023-08-01 10:30:00', 'Primary'),
(3, 8, '2023-08-01 10:30:00', 'Joint'),   -- Joint account between Customer 8 & Customer 3
(9, 9, '2023-09-15 14:00:00', 'Primary'),
(10, 10, '2023-10-05 17:30:00', 'Primary'),
(2, 10, '2023-10-10 11:00:00', 'Joint'),  -- Joint account between Customer 10 & Customer 2
(6, 11, '2023-11-10 09:00:00', 'Primary'),
(1, 12, '2023-12-01 11:00:00', 'Primary');
-- Note: Customer 7 (Amit Banerjee) has no account initially to showcase queries finding customers without accounts!

-- ----------------------------------------------------------------------------
-- 6. INSERT BANK_TRANSACTION DATA
-- Deposits, withdrawals, and paired transfers
-- ----------------------------------------------------------------------------
INSERT INTO BANK_TRANSACTION (TransactionID, AccountID, TransactionType, Amount, TransactionDate, Description, ReferenceNumber, TransactionStatus) VALUES
(1, 1, 'DEPOSIT', 25000.00, '2023-01-10 10:50:00', 'Initial Account Opening Deposit', 'TXN20230110001', 'SUCCESS'),
(2, 1, 'DEPOSIT', 25000.00, '2023-01-20 14:30:00', 'Cash Deposit at Branch Counter', 'TXN20230120002', 'SUCCESS'),
(3, 1, 'WITHDRAWAL', 5000.00, '2023-02-05 16:15:00', 'ATM Cash Withdrawal', 'TXN20230205001', 'SUCCESS'),
(4, 2, 'DEPOSIT', 150000.00, '2023-01-15 12:05:00', 'Opening Capital Deposit', 'TXN20230115001', 'SUCCESS'),
(5, 2, 'WITHDRAWAL', 25000.00, '2023-02-28 11:45:00', 'Supplier Cheque Clearing', 'TXN20230228001', 'SUCCESS'),
(6, 3, 'DEPOSIT', 75000.00, '2023-02-14 11:35:00', 'Salary Credit - Feb 2023', 'TXN20230214001', 'SUCCESS'),
(7, 3, 'WITHDRAWAL', 7000.00, '2023-03-01 18:20:00', 'Utility Bill Payment', 'TXN20230301001', 'SUCCESS'),
(8, 4, 'DEPOSIT', 100000.00, '2023-03-05 14:50:00', 'Cheque Deposit', 'TXN20230305001', 'SUCCESS'),
(9, 4, 'WITHDRAWAL', 8000.00, '2023-04-10 13:10:00', 'POS Purchase', 'TXN20230410001', 'SUCCESS'),
(10, 5, 'DEPOSIT', 200000.00, '2023-04-18 10:20:00', 'Initial Fixed Deposit Transfer', 'TXN20230418001', 'SUCCESS'),
(11, 5, 'DEPOSIT', 10000.00, '2023-05-15 15:40:00', 'Online Inward Remittance', 'TXN20230515001', 'SUCCESS'),
(12, 6, 'DEPOSIT', 90000.00, '2023-05-22 16:35:00', 'Salary Credit', 'TXN20230522001', 'SUCCESS'),
(13, 6, 'WITHDRAWAL', 5000.00, '2023-06-02 09:30:00', 'Cash Withdrawal', 'TXN20230602001', 'SUCCESS'),
-- Transfer from Account 1 (Aarav) to Account 4 (Rohan) of Amount 5000.00
(14, 1, 'TRANSFER_OUT', 5000.00, '2023-06-15 11:00:00', 'Fund Transfer to Acc 1002001001', 'TRF20230615991', 'SUCCESS'),
(15, 4, 'TRANSFER_IN', 5000.00, '2023-06-15 11:00:00', 'Fund Received from Acc 1001001001', 'TRF20230615991', 'SUCCESS'),
-- Transfer from Account 5 (Meera) to Account 10 (Sunil) of Amount 10000.00
(16, 5, 'TRANSFER_OUT', 10000.00, '2023-07-20 14:00:00', 'Fund Transfer to Acc 1003001002', 'TRF20230720882', 'SUCCESS'),
(17, 10, 'TRANSFER_IN', 10000.00, '2023-07-20 14:00:00', 'Fund Received from Acc 1003001001', 'TRF20230720882', 'SUCCESS'),
(18, 7, 'DEPOSIT', 32000.00, '2023-06-11 12:35:00', 'Account Opening Deposit', 'TXN20230611001', 'SUCCESS'),
(19, 8, 'DEPOSIT', 154000.00, '2023-08-01 10:35:00', 'Partnership Deposit', 'TXN20230801001', 'SUCCESS'),
(20, 9, 'DEPOSIT', 15000.00, '2023-09-15 14:05:00', 'Savings Inflow', 'TXN20230915001', 'SUCCESS');

-- ----------------------------------------------------------------------------
-- 7. INSERT LOAN DATA
-- ----------------------------------------------------------------------------
INSERT INTO LOAN (LoanID, CustomerID, BranchID, LoanType, LoanAmount, InterestRate, StartDate, TenureMonths, LoanStatus) VALUES
(1, 1, 1, 'Home Loan', 2500000.00, 8.50, '2023-03-01', 180, 'Active'),
(2, 2, 1, 'Education Loan', 400000.00, 9.25, '2023-05-15', 60, 'Active'),
(3, 3, 3, 'Personal Loan', 300000.00, 11.50, '2023-07-10', 36, 'Active'),
(4, 5, 5, 'Vehicle Loan', 850000.00, 8.75, '2023-08-20', 48, 'Active'),
(5, 4, 4, 'Home Loan', 4500000.00, 8.40, '2023-09-01', 240, 'Active'),
(6, 6, 2, 'Personal Loan', 150000.00, 12.00, '2022-01-10', 12, 'Closed');

-- ----------------------------------------------------------------------------
-- 8. INSERT LOAN_PAYMENT DATA
-- ----------------------------------------------------------------------------
INSERT INTO LOAN_PAYMENT (PaymentID, LoanID, PaymentDate, Amount, PaymentMode, ReferenceNumber) VALUES
(1, 1, '2023-04-01 10:00:00', 24650.00, 'Account Transfer', 'LPAY2023040101'),
(2, 1, '2023-05-01 10:00:00', 24650.00, 'Account Transfer', 'LPAY2023050101'),
(3, 1, '2023-06-01 10:00:00', 24650.00, 'Online', 'LPAY2023060101'),
(4, 2, '2023-06-15 11:30:00', 8350.00, 'Online', 'LPAY2023061501'),
(5, 2, '2023-07-15 11:30:00', 8350.00, 'Online', 'LPAY2023071501'),
(6, 3, '2023-08-10 14:15:00', 9890.00, 'Account Transfer', 'LPAY2023081001'),
(7, 4, '2023-09-20 15:45:00', 21050.00, 'Cheque', 'LPAY2023092001'),
(8, 6, '2023-01-10 12:00:00', 155000.00, 'Cash', 'LPAY2023011099');
