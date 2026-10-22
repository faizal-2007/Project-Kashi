-- Project Kashi - Banking Management System
-- MySQL 8.0 schema. WARNING: this script drops and recreates the project database.
-- Run it only for this academic project, never against a database containing real data.

DROP DATABASE IF EXISTS project_kashi;
CREATE DATABASE project_kashi
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;
USE project_kashi;

CREATE TABLE BRANCH (
    BranchID INT AUTO_INCREMENT PRIMARY KEY,
    BranchName VARCHAR(100) NOT NULL,
    IFSCCode CHAR(11) NOT NULL,
    Address VARCHAR(255) NOT NULL,
    City VARCHAR(80) NOT NULL,
    State VARCHAR(80) NOT NULL,
    ContactNumber VARCHAR(15) NOT NULL,
    CONSTRAINT uq_branch_ifsc UNIQUE (IFSCCode),
    CONSTRAINT chk_branch_ifsc CHECK (IFSCCode REGEXP '^[A-Z]{4}0[0-9]{6}$'),
    CONSTRAINT chk_branch_contact CHECK (ContactNumber REGEXP '^[0-9]{10,15}$')
) ENGINE=InnoDB;

CREATE TABLE CUSTOMER (
    CustomerID INT AUTO_INCREMENT PRIMARY KEY,
    FirstName VARCHAR(60) NOT NULL,
    LastName VARCHAR(60) NOT NULL,
    DateOfBirth DATE NOT NULL,
    Gender ENUM('Male', 'Female', 'Other') NOT NULL,
    Mobile VARCHAR(15) NOT NULL,
    Email VARCHAR(120) NOT NULL,
    Address VARCHAR(255) NOT NULL,
    City VARCHAR(80) NOT NULL,
    RegistrationDate DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_customer_mobile UNIQUE (Mobile),
    CONSTRAINT uq_customer_email UNIQUE (Email),
    CONSTRAINT chk_customer_mobile CHECK (Mobile REGEXP '^[0-9]{10,15}$'),
    CONSTRAINT chk_customer_email CHECK (Email LIKE '%_@_%._%'),
    CONSTRAINT chk_customer_dob CHECK (DateOfBirth BETWEEN '1900-01-01' AND '2100-12-31')
) ENGINE=InnoDB;

CREATE TABLE EMPLOYEE (
    EmployeeID INT AUTO_INCREMENT PRIMARY KEY,
    EmployeeName VARCHAR(100) NOT NULL,
    Mobile VARCHAR(15) NOT NULL,
    Email VARCHAR(120) NOT NULL,
    Designation VARCHAR(60) NOT NULL,
    Salary DECIMAL(12,2) NOT NULL,
    JoiningDate DATE NOT NULL,
    BranchID INT NOT NULL,
    CONSTRAINT uq_employee_mobile UNIQUE (Mobile),
    CONSTRAINT uq_employee_email UNIQUE (Email),
    CONSTRAINT chk_employee_mobile CHECK (Mobile REGEXP '^[0-9]{10,15}$'),
    CONSTRAINT chk_employee_email CHECK (Email LIKE '%_@_%._%'),
    CONSTRAINT chk_employee_salary CHECK (Salary > 0),
    CONSTRAINT fk_employee_branch FOREIGN KEY (BranchID)
        REFERENCES BRANCH (BranchID)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
) ENGINE=InnoDB;

CREATE TABLE ACCOUNT (
    AccountID INT AUTO_INCREMENT PRIMARY KEY,
    AccountNumber VARCHAR(12) NOT NULL,
    AccountType ENUM('Saving', 'Current', 'Salary') NOT NULL,
    OpeningDate DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    Balance DECIMAL(15,2) NOT NULL DEFAULT 0.00,
    Status ENUM('Active', 'Inactive', 'Closed') NOT NULL DEFAULT 'Active',
    BranchID INT NOT NULL,
    CONSTRAINT uq_account_number UNIQUE (AccountNumber),
    CONSTRAINT chk_account_number CHECK (AccountNumber REGEXP '^[0-9]{12}$'),
    CONSTRAINT chk_account_balance CHECK (Balance >= 0),
    CONSTRAINT fk_account_branch FOREIGN KEY (BranchID)
        REFERENCES BRANCH (BranchID)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
) ENGINE=InnoDB;

CREATE TABLE ACCOUNT_HOLDER (
    CustomerID INT NOT NULL,
    AccountID INT NOT NULL,
    HolderSince DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    HolderType ENUM('Primary', 'Joint') NOT NULL DEFAULT 'Primary',
    PRIMARY KEY (CustomerID, AccountID),
    CONSTRAINT fk_holder_customer FOREIGN KEY (CustomerID)
        REFERENCES CUSTOMER (CustomerID)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,
    CONSTRAINT fk_holder_account FOREIGN KEY (AccountID)
        REFERENCES ACCOUNT (AccountID)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
) ENGINE=InnoDB;

CREATE TABLE BANK_TRANSACTION (
    TransactionID BIGINT AUTO_INCREMENT PRIMARY KEY,
    AccountID INT NOT NULL,
    TransactionType ENUM('DEPOSIT', 'WITHDRAWAL', 'TRANSFER_IN', 'TRANSFER_OUT') NOT NULL,
    Amount DECIMAL(15,2) NOT NULL,
    TransactionDate DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    Description VARCHAR(255) NULL,
    ReferenceNumber VARCHAR(60) NULL,
    TransferGroupReference VARCHAR(50) NULL,
    TransactionStatus ENUM('SUCCESS', 'FAILED', 'PENDING') NOT NULL DEFAULT 'SUCCESS',
    CONSTRAINT uq_transaction_reference UNIQUE (ReferenceNumber),
    CONSTRAINT chk_transaction_amount CHECK (Amount > 0),
    CONSTRAINT chk_transaction_transfer_reference CHECK (
        (TransactionType IN ('TRANSFER_IN', 'TRANSFER_OUT') AND TransferGroupReference IS NOT NULL)
        OR
        (TransactionType IN ('DEPOSIT', 'WITHDRAWAL') AND TransferGroupReference IS NULL)
    ),
    CONSTRAINT fk_transaction_account FOREIGN KEY (AccountID)
        REFERENCES ACCOUNT (AccountID)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,
    INDEX idx_transaction_account_date (AccountID, TransactionDate),
    INDEX idx_transaction_type (TransactionType),
    INDEX idx_transaction_transfer_group (TransferGroupReference)
) ENGINE=InnoDB;

CREATE TABLE LOAN (
    LoanID INT AUTO_INCREMENT PRIMARY KEY,
    CustomerID INT NOT NULL,
    BranchID INT NOT NULL,
    LoanType ENUM('Home Loan', 'Education Loan', 'Personal Loan', 'Vehicle Loan') NOT NULL,
    LoanAmount DECIMAL(15,2) NOT NULL,
    InterestRate DECIMAL(5,2) NOT NULL,
    StartDate DATE NOT NULL,
    TenureMonths INT NOT NULL,
    LoanStatus ENUM('Pending', 'Approved', 'Rejected', 'Closed') NOT NULL DEFAULT 'Pending',
    CONSTRAINT chk_loan_amount CHECK (LoanAmount > 0),
    CONSTRAINT chk_loan_interest CHECK (InterestRate BETWEEN 0 AND 50),
    CONSTRAINT chk_loan_tenure CHECK (TenureMonths BETWEEN 1 AND 600),
    CONSTRAINT fk_loan_customer FOREIGN KEY (CustomerID)
        REFERENCES CUSTOMER (CustomerID)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,
    CONSTRAINT fk_loan_branch FOREIGN KEY (BranchID)
        REFERENCES BRANCH (BranchID)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
) ENGINE=InnoDB;

CREATE TABLE LOAN_PAYMENT (
    PaymentID INT AUTO_INCREMENT PRIMARY KEY,
    LoanID INT NOT NULL,
    PaymentDate DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    Amount DECIMAL(15,2) NOT NULL,
    PaymentMode ENUM('Cash', 'Cheque', 'NEFT', 'UPI', 'Card') NOT NULL,
    ReferenceNumber VARCHAR(60) NULL,
    CONSTRAINT uq_payment_reference UNIQUE (ReferenceNumber),
    CONSTRAINT chk_payment_amount CHECK (Amount > 0),
    CONSTRAINT fk_payment_loan FOREIGN KEY (LoanID)
        REFERENCES LOAN (LoanID)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,
    INDEX idx_payment_loan_date (LoanID, PaymentDate)
) ENGINE=InnoDB;
