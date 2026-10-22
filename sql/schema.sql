-- ============================================================================
-- PROJECT KASHI — BANKING MANAGEMENT SYSTEM
-- Script: schema.sql
-- Purpose: Complete Relational Schema Definition for MySQL 8.0+
-- Database: project_kashi
-- ============================================================================

CREATE DATABASE IF NOT EXISTS project_kashi;
USE project_kashi;

SET FOREIGN_KEY_CHECKS = 0;

-- Drop tables in reverse dependency order if recreating
DROP TABLE IF EXISTS LOAN_PAYMENT;
DROP TABLE IF EXISTS LOAN;
DROP TABLE IF EXISTS BANK_TRANSACTION;
DROP TABLE IF EXISTS TRANSACTION;
DROP TABLE IF EXISTS ACCOUNT_AUDIT;
DROP TABLE IF EXISTS ACCOUNT_HOLDER;
DROP TABLE IF EXISTS ACCOUNT;
DROP TABLE IF EXISTS EMPLOYEE;
DROP TABLE IF EXISTS CUSTOMER;
DROP TABLE IF EXISTS BRANCH;

SET FOREIGN_KEY_CHECKS = 1;

-- ----------------------------------------------------------------------------
-- TABLE 1: BRANCH
-- Purpose: Stores physical and administrative bank branch locations.
-- ----------------------------------------------------------------------------
CREATE TABLE BRANCH (
    BranchID INT AUTO_INCREMENT PRIMARY KEY,
    BranchName VARCHAR(100) NOT NULL,
    IFSCCode VARCHAR(15) NOT NULL UNIQUE,
    Address VARCHAR(255) NOT NULL,
    City VARCHAR(50) NOT NULL,
    State VARCHAR(50) NOT NULL,
    ContactNumber VARCHAR(15) NOT NULL,
    CreatedAt DATETIME DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_branch_ifsc CHECK (CHAR_LENGTH(IFSCCode) >= 8)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ----------------------------------------------------------------------------
-- TABLE 2: EMPLOYEE
-- Purpose: Stores staff members associated with specific branches.
-- ----------------------------------------------------------------------------
CREATE TABLE EMPLOYEE (
    EmployeeID INT AUTO_INCREMENT PRIMARY KEY,
    EmployeeName VARCHAR(100) NOT NULL,
    Mobile VARCHAR(15) NOT NULL,
    Email VARCHAR(100) NOT NULL UNIQUE,
    Designation VARCHAR(50) NOT NULL,
    Salary DECIMAL(12, 2) NOT NULL,
    JoiningDate DATE NOT NULL,
    BranchID INT NOT NULL,
    CONSTRAINT chk_emp_salary CHECK (Salary > 0),
    CONSTRAINT fk_emp_branch FOREIGN KEY (BranchID) 
        REFERENCES BRANCH(BranchID) 
        ON UPDATE CASCADE 
        ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ----------------------------------------------------------------------------
-- TABLE 3: CUSTOMER
-- Purpose: Stores individual banking customer personal details.
-- ----------------------------------------------------------------------------
CREATE TABLE CUSTOMER (
    CustomerID INT AUTO_INCREMENT PRIMARY KEY,
    FirstName VARCHAR(50) NOT NULL,
    LastName VARCHAR(50) NOT NULL,
    DateOfBirth DATE NOT NULL,
    Gender ENUM('Male', 'Female', 'Other') NOT NULL,
    Mobile VARCHAR(15) NOT NULL UNIQUE,
    Email VARCHAR(100) NOT NULL UNIQUE,
    Address VARCHAR(255) NOT NULL,
    City VARCHAR(50) NOT NULL,
    RegistrationDate DATETIME DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_cust_mobile CHECK (CHAR_LENGTH(Mobile) >= 10)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ----------------------------------------------------------------------------
-- TABLE 4: ACCOUNT
-- Purpose: Stores bank accounts held at specific branches.
-- ----------------------------------------------------------------------------
CREATE TABLE ACCOUNT (
    AccountID INT AUTO_INCREMENT PRIMARY KEY,
    AccountNumber VARCHAR(20) NOT NULL UNIQUE,
    AccountType ENUM('Saving', 'Current', 'Salary') NOT NULL,
    OpeningDate DATETIME DEFAULT CURRENT_TIMESTAMP,
    Balance DECIMAL(15, 2) NOT NULL DEFAULT 0.00,
    Status ENUM('Active', 'Inactive', 'Closed') NOT NULL DEFAULT 'Active',
    BranchID INT NOT NULL,
    CONSTRAINT chk_acc_balance CHECK (Balance >= 0.00),
    CONSTRAINT fk_acc_branch FOREIGN KEY (BranchID) 
        REFERENCES BRANCH(BranchID) 
        ON UPDATE CASCADE 
        ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ----------------------------------------------------------------------------
-- TABLE 5: ACCOUNT_HOLDER
-- Purpose: Resolves the Many-to-Many relationship between CUSTOMER and ACCOUNT.
-- ----------------------------------------------------------------------------
CREATE TABLE ACCOUNT_HOLDER (
    CustomerID INT NOT NULL,
    AccountID INT NOT NULL,
    HolderSince DATETIME DEFAULT CURRENT_TIMESTAMP,
    HolderType ENUM('Primary', 'Joint') NOT NULL DEFAULT 'Primary',
    PRIMARY KEY (CustomerID, AccountID),
    CONSTRAINT fk_holder_cust FOREIGN KEY (CustomerID) 
        REFERENCES CUSTOMER(CustomerID) 
        ON UPDATE CASCADE 
        ON DELETE CASCADE,
    CONSTRAINT fk_holder_acc FOREIGN KEY (AccountID) 
        REFERENCES ACCOUNT(AccountID) 
        ON UPDATE CASCADE 
        ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ----------------------------------------------------------------------------
-- TABLE 6: BANK_TRANSACTION (Logical Entity: TRANSACTION)
-- Purpose: Preserves immutable ledger of financial activity on accounts.
-- ----------------------------------------------------------------------------
CREATE TABLE BANK_TRANSACTION (
    TransactionID INT AUTO_INCREMENT PRIMARY KEY,
    AccountID INT NOT NULL,
    TransactionType ENUM('DEPOSIT', 'WITHDRAWAL', 'TRANSFER_IN', 'TRANSFER_OUT') NOT NULL,
    Amount DECIMAL(15, 2) NOT NULL,
    TransactionDate DATETIME DEFAULT CURRENT_TIMESTAMP,
    Description VARCHAR(255) NULL,
    ReferenceNumber VARCHAR(50) NOT NULL,
    TransactionStatus ENUM('SUCCESS', 'FAILED', 'PENDING') NOT NULL DEFAULT 'SUCCESS',
    CONSTRAINT chk_tx_amount CHECK (Amount > 0.00),
    CONSTRAINT fk_tx_acc FOREIGN KEY (AccountID) 
        REFERENCES ACCOUNT(AccountID) 
        ON UPDATE CASCADE 
        ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ----------------------------------------------------------------------------
-- TABLE 7: LOAN
-- Purpose: Records loan facilities extended to customers from specific branches.
-- ----------------------------------------------------------------------------
CREATE TABLE LOAN (
    LoanID INT AUTO_INCREMENT PRIMARY KEY,
    CustomerID INT NOT NULL,
    BranchID INT NOT NULL,
    LoanType ENUM('Home Loan', 'Education Loan', 'Personal Loan', 'Vehicle Loan') NOT NULL,
    LoanAmount DECIMAL(15, 2) NOT NULL,
    InterestRate DECIMAL(5, 2) NOT NULL,
    StartDate DATE NOT NULL,
    TenureMonths INT NOT NULL,
    LoanStatus ENUM('Applied', 'Approved', 'Disbursed', 'Active', 'Closed', 'Rejected') NOT NULL DEFAULT 'Active',
    CONSTRAINT chk_loan_amount CHECK (LoanAmount > 0.00),
    CONSTRAINT chk_loan_rate CHECK (InterestRate >= 0.00),
    CONSTRAINT chk_loan_tenure CHECK (TenureMonths > 0),
    CONSTRAINT fk_loan_cust FOREIGN KEY (CustomerID) 
        REFERENCES CUSTOMER(CustomerID) 
        ON UPDATE CASCADE 
        ON DELETE RESTRICT,
    CONSTRAINT fk_loan_branch FOREIGN KEY (BranchID) 
        REFERENCES BRANCH(BranchID) 
        ON UPDATE CASCADE 
        ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ----------------------------------------------------------------------------
-- TABLE 8: LOAN_PAYMENT
-- Purpose: Records repayments and installments against active loans.
-- ----------------------------------------------------------------------------
CREATE TABLE LOAN_PAYMENT (
    PaymentID INT AUTO_INCREMENT PRIMARY KEY,
    LoanID INT NOT NULL,
    PaymentDate DATETIME DEFAULT CURRENT_TIMESTAMP,
    Amount DECIMAL(15, 2) NOT NULL,
    PaymentMode ENUM('Cash', 'Cheque', 'Account Transfer', 'Online') NOT NULL,
    ReferenceNumber VARCHAR(50) NOT NULL UNIQUE,
    CONSTRAINT chk_pay_amount CHECK (Amount > 0.00),
    CONSTRAINT fk_pay_loan FOREIGN KEY (LoanID) 
        REFERENCES LOAN(LoanID) 
        ON UPDATE CASCADE 
        ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ----------------------------------------------------------------------------
-- INDEXES FOR PERFORMANCE OPTIMIZATION
-- ----------------------------------------------------------------------------
CREATE INDEX idx_acc_branch ON ACCOUNT(BranchID);
CREATE INDEX idx_tx_account ON BANK_TRANSACTION(AccountID);
CREATE INDEX idx_tx_ref ON BANK_TRANSACTION(ReferenceNumber);
CREATE INDEX idx_loan_cust ON LOAN(CustomerID);
CREATE INDEX idx_loan_branch ON LOAN(BranchID);
CREATE INDEX idx_pay_loan ON LOAN_PAYMENT(LoanID);
