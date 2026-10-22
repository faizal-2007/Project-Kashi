-- ============================================================================
-- PROJECT KASHI — BANKING MANAGEMENT SYSTEM
-- Script: procedures.sql
-- Purpose: ACID Transaction Stored Procedures for Core Banking Operations
-- Database: project_kashi
-- ============================================================================

USE project_kashi;

DROP PROCEDURE IF EXISTS sp_deposit_funds;
DROP PROCEDURE IF EXISTS sp_withdraw_funds;
DROP PROCEDURE IF EXISTS sp_transfer_funds;
DROP PROCEDURE IF EXISTS sp_get_customer_portfolio;
DROP PROCEDURE IF EXISTS sp_record_loan_payment;

DELIMITER $$

-- ----------------------------------------------------------------------------
-- PROCEDURE 1: sp_deposit_funds
-- Purpose: Safely credits funds into an active account with ACID guarantees.
-- ----------------------------------------------------------------------------
CREATE PROCEDURE sp_deposit_funds(
    IN p_account_id INT,
    IN p_amount DECIMAL(15, 2),
    IN p_description VARCHAR(255),
    IN p_ref_number VARCHAR(50),
    OUT p_status VARCHAR(100),
    OUT p_new_balance DECIMAL(15, 2)
)
proc_label: BEGIN
    DECLARE v_curr_balance DECIMAL(15, 2);
    DECLARE v_status ENUM('Active', 'Inactive', 'Closed');
    
    -- Error Handler triggers ROLLBACK on any SQL exception
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        SET p_status = 'ERROR: Database exception occurred during deposit. Rolled back.';
        SET p_new_balance = 0.00;
    END;

    IF p_amount <= 0 THEN
        SET p_status = 'REJECTED: Deposit amount must be strictly greater than zero.';
        SET p_new_balance = 0.00;
        LEAVE proc_label;
    END IF;

    START TRANSACTION;

    -- Row-level locking to prevent race conditions
    SELECT Balance, Status INTO v_curr_balance, v_status
    FROM ACCOUNT
    WHERE AccountID = p_account_id
    FOR UPDATE;

    IF v_status IS NULL THEN
        ROLLBACK;
        SET p_status = 'REJECTED: Target account does not exist.';
        SET p_new_balance = 0.00;
        LEAVE proc_label;
    END IF;

    IF v_status != 'Active' THEN
        ROLLBACK;
        SET p_status = CONCAT('REJECTED: Account is ', v_status, '. Deposits allowed only on Active accounts.');
        SET p_new_balance = v_curr_balance;
        LEAVE proc_label;
    END IF;

    -- Update balance
    UPDATE ACCOUNT
    SET Balance = Balance + p_amount
    WHERE AccountID = p_account_id;

    -- Record transaction ledger entry
    INSERT INTO BANK_TRANSACTION (
        AccountID, TransactionType, Amount, Description, ReferenceNumber, TransactionStatus
    ) VALUES (
        p_account_id, 'DEPOSIT', p_amount, 
        COALESCE(p_description, 'Branch/Cash Deposit'), 
        p_ref_number, 'SUCCESS'
    );

    COMMIT;

    SET p_new_balance = v_curr_balance + p_amount;
    SET p_status = 'SUCCESS: Deposit processed successfully.';
END$$

-- ----------------------------------------------------------------------------
-- PROCEDURE 2: sp_withdraw_funds
-- Purpose: Safely debits funds from an active account with balance validation.
-- ----------------------------------------------------------------------------
CREATE PROCEDURE sp_withdraw_funds(
    IN p_account_id INT,
    IN p_amount DECIMAL(15, 2),
    IN p_description VARCHAR(255),
    IN p_ref_number VARCHAR(50),
    OUT p_status VARCHAR(100),
    OUT p_new_balance DECIMAL(15, 2)
)
proc_label: BEGIN
    DECLARE v_curr_balance DECIMAL(15, 2);
    DECLARE v_status ENUM('Active', 'Inactive', 'Closed');

    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        SET p_status = 'ERROR: Database exception occurred during withdrawal. Rolled back.';
        SET p_new_balance = 0.00;
    END;

    IF p_amount <= 0 THEN
        SET p_status = 'REJECTED: Withdrawal amount must be greater than zero.';
        SET p_new_balance = 0.00;
        LEAVE proc_label;
    END IF;

    START TRANSACTION;

    SELECT Balance, Status INTO v_curr_balance, v_status
    FROM ACCOUNT
    WHERE AccountID = p_account_id
    FOR UPDATE;

    IF v_status IS NULL THEN
        ROLLBACK;
        SET p_status = 'REJECTED: Target account does not exist.';
        SET p_new_balance = 0.00;
        LEAVE proc_label;
    END IF;

    IF v_status != 'Active' THEN
        ROLLBACK;
        SET p_status = CONCAT('REJECTED: Account is ', v_status, '. Withdrawals allowed only on Active accounts.');
        SET p_new_balance = v_curr_balance;
        LEAVE proc_label;
    END IF;

    IF v_curr_balance < p_amount THEN
        ROLLBACK;
        SET p_status = CONCAT('REJECTED: Insufficient balance. Available: ', v_curr_balance, ', Requested: ', p_amount);
        SET p_new_balance = v_curr_balance;
        LEAVE proc_label;
    END IF;

    -- Debit balance
    UPDATE ACCOUNT
    SET Balance = Balance - p_amount
    WHERE AccountID = p_account_id;

    -- Record transaction
    INSERT INTO BANK_TRANSACTION (
        AccountID, TransactionType, Amount, Description, ReferenceNumber, TransactionStatus
    ) VALUES (
        p_account_id, 'WITHDRAWAL', p_amount, 
        COALESCE(p_description, 'Cash/ATM Withdrawal'), 
        p_ref_number, 'SUCCESS'
    );

    COMMIT;

    SET p_new_balance = v_curr_balance - p_amount;
    SET p_status = 'SUCCESS: Withdrawal completed successfully.';
END$$

-- ----------------------------------------------------------------------------
-- PROCEDURE 3: sp_transfer_funds
-- Purpose: Complete inter-account transfer enforcing ACID properties and
-- ordered locking to prevent deadlocks.
-- ----------------------------------------------------------------------------
CREATE PROCEDURE sp_transfer_funds(
    IN p_src_acc_id INT,
    IN p_dest_acc_id INT,
    IN p_amount DECIMAL(15, 2),
    IN p_description VARCHAR(255),
    IN p_ref_number VARCHAR(50),
    OUT p_status VARCHAR(100)
)
proc_label: BEGIN
    DECLARE v_src_balance DECIMAL(15, 2);
    DECLARE v_src_status ENUM('Active', 'Inactive', 'Closed');
    DECLARE v_dest_balance DECIMAL(15, 2);
    DECLARE v_dest_status ENUM('Active', 'Inactive', 'Closed');
    DECLARE v_first_lock INT;
    DECLARE v_second_lock INT;

    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        SET p_status = 'ERROR: Database exception occurred during transfer. Entire transfer rolled back.';
    END;

    -- Validation
    IF p_src_acc_id = p_dest_acc_id THEN
        SET p_status = 'REJECTED: Source and destination accounts cannot be identical.';
        LEAVE proc_label;
    END IF;

    IF p_amount <= 0 THEN
        SET p_status = 'REJECTED: Transfer amount must be greater than zero.';
        LEAVE proc_label;
    END IF;

    -- Order locks to prevent deadlock
    IF p_src_acc_id < p_dest_acc_id THEN
        SET v_first_lock = p_src_acc_id;
        SET v_second_lock = p_dest_acc_id;
    ELSE
        SET v_first_lock = p_dest_acc_id;
        SET v_second_lock = p_src_acc_id;
    END IF;

    START TRANSACTION;

    -- Lock accounts in fixed order
    SELECT Balance, Status INTO v_src_balance, v_src_status
    FROM ACCOUNT WHERE AccountID = p_src_acc_id FOR UPDATE;

    SELECT Balance, Status INTO v_dest_balance, v_dest_status
    FROM ACCOUNT WHERE AccountID = p_dest_acc_id FOR UPDATE;

    -- Check existence
    IF v_src_status IS NULL OR v_dest_status IS NULL THEN
        ROLLBACK;
        SET p_status = 'REJECTED: One or both specified accounts do not exist.';
        LEAVE proc_label;
    END IF;

    -- Check account status
    IF v_src_status != 'Active' OR v_dest_status != 'Active' THEN
        ROLLBACK;
        SET p_status = 'REJECTED: Both source and destination accounts must be Active.';
        LEAVE proc_label;
    END IF;

    -- Check source balance
    IF v_src_balance < p_amount THEN
        ROLLBACK;
        SET p_status = CONCAT('REJECTED: Insufficient funds in source account. Available: ', v_src_balance);
        LEAVE proc_label;
    END IF;

    -- Debit source
    UPDATE ACCOUNT SET Balance = Balance - p_amount WHERE AccountID = p_src_acc_id;

    -- Credit destination
    UPDATE ACCOUNT SET Balance = Balance + p_amount WHERE AccountID = p_dest_acc_id;

    -- Insert TRANSFER_OUT on source
    INSERT INTO BANK_TRANSACTION (
        AccountID, TransactionType, Amount, Description, ReferenceNumber, TransactionStatus
    ) VALUES (
        p_src_acc_id, 'TRANSFER_OUT', p_amount,
        COALESCE(p_description, CONCAT('Transfer to Account #', p_dest_acc_id)),
        p_ref_number, 'SUCCESS'
    );

    -- Insert TRANSFER_IN on destination with the SAME reference number
    INSERT INTO BANK_TRANSACTION (
        AccountID, TransactionType, Amount, Description, ReferenceNumber, TransactionStatus
    ) VALUES (
        p_dest_acc_id, 'TRANSFER_IN', p_amount,
        COALESCE(p_description, CONCAT('Transfer from Account #', p_src_acc_id)),
        p_ref_number, 'SUCCESS'
    );

    COMMIT;
    SET p_status = 'SUCCESS: Fund transfer completed successfully.';
END$$

-- ----------------------------------------------------------------------------
-- PROCEDURE 4: sp_get_customer_portfolio
-- Purpose: Returns detailed financial snapshot for a given customer.
-- ----------------------------------------------------------------------------
CREATE PROCEDURE sp_get_customer_portfolio(IN p_customer_id INT)
BEGIN
    -- Customer personal info
    SELECT CustomerID, CONCAT(FirstName, ' ', LastName) AS FullName, Email, Mobile, City, RegistrationDate
    FROM CUSTOMER
    WHERE CustomerID = p_customer_id;

    -- Linked accounts
    SELECT a.AccountID, a.AccountNumber, a.AccountType, a.Balance, a.Status, ah.HolderType, b.BranchName
    FROM ACCOUNT a
    JOIN ACCOUNT_HOLDER ah ON a.AccountID = ah.AccountID
    JOIN BRANCH b ON a.BranchID = b.BranchID
    WHERE ah.CustomerID = p_customer_id;

    -- Active loans
    SELECT LoanID, LoanType, LoanAmount, InterestRate, StartDate, TenureMonths, LoanStatus
    FROM LOAN
    WHERE CustomerID = p_customer_id;
END$$

-- ----------------------------------------------------------------------------
-- PROCEDURE 5: sp_record_loan_payment
-- Purpose: Records repayment against a loan and checks if loan should be closed.
-- ----------------------------------------------------------------------------
CREATE PROCEDURE sp_record_loan_payment(
    IN p_loan_id INT,
    IN p_amount DECIMAL(15, 2),
    IN p_payment_mode ENUM('Cash', 'Cheque', 'Account Transfer', 'Online'),
    IN p_ref_number VARCHAR(50),
    OUT p_status VARCHAR(100)
)
proc_label: BEGIN
    DECLARE v_loan_status ENUM('Applied', 'Approved', 'Disbursed', 'Active', 'Closed', 'Rejected');
    DECLARE v_total_sanction DECIMAL(15, 2);
    DECLARE v_total_paid DECIMAL(15, 2);

    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        SET p_status = 'ERROR: Database exception while recording loan repayment.';
    END;

    IF p_amount <= 0 THEN
        SET p_status = 'REJECTED: Payment amount must be positive.';
        LEAVE proc_label;
    END IF;

    START TRANSACTION;

    SELECT LoanStatus, LoanAmount INTO v_loan_status, v_total_sanction
    FROM LOAN WHERE LoanID = p_loan_id FOR UPDATE;

    IF v_loan_status IS NULL THEN
        ROLLBACK;
        SET p_status = 'REJECTED: Loan ID not found.';
        LEAVE proc_label;
    END IF;

    IF v_loan_status != 'Active' THEN
        ROLLBACK;
        SET p_status = CONCAT('REJECTED: Cannot pay against loan with status ', v_loan_status);
        LEAVE proc_label;
    END IF;

    INSERT INTO LOAN_PAYMENT (LoanID, Amount, PaymentMode, ReferenceNumber)
    VALUES (p_loan_id, p_amount, p_payment_mode, p_ref_number);

    -- Calculate total repaid to date
    SELECT COALESCE(SUM(Amount), 0.00) INTO v_total_paid
    FROM LOAN_PAYMENT WHERE LoanID = p_loan_id;

    -- If total payments equal or exceed sanctioned principal, mark loan as Closed
    IF v_total_paid >= v_total_sanction THEN
        UPDATE LOAN SET LoanStatus = 'Closed' WHERE LoanID = p_loan_id;
        SET p_status = 'SUCCESS: Payment recorded. Loan has been fully repaid and CLOSED.';
    ELSE
        SET p_status = CONCAT('SUCCESS: Payment recorded. Outstanding principal: ', (v_total_sanction - v_total_paid));
    END IF;

    COMMIT;
END$$

DELIMITER ;
