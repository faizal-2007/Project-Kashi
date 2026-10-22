-- ============================================================================
-- PROJECT KASHI — BANKING MANAGEMENT SYSTEM
-- Script: triggers.sql
-- Purpose: Database Triggers for Integrity Enforcement, Invariants, and Auditing
-- Database: project_kashi
-- ============================================================================

USE project_kashi;

-- ----------------------------------------------------------------------------
-- AUDIT TABLE: ACCOUNT_AUDIT
-- Purpose: Stores audit logs whenever an account status or key detail is modified.
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS ACCOUNT_AUDIT (
    AuditID INT AUTO_INCREMENT PRIMARY KEY,
    AccountID INT NOT NULL,
    OldStatus VARCHAR(20) NULL,
    NewStatus VARCHAR(20) NULL,
    OldBalance DECIMAL(15, 2) NULL,
    NewBalance DECIMAL(15, 2) NULL,
    ChangedAt DATETIME DEFAULT CURRENT_TIMESTAMP,
    ActionType VARCHAR(50) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

DROP TRIGGER IF EXISTS trg_validate_transaction_before_insert;
DROP TRIGGER IF EXISTS trg_prevent_negative_balance_before_update;
DROP TRIGGER IF EXISTS trg_audit_account_update;
DROP TRIGGER IF EXISTS trg_prevent_loan_amount_mutation;

DELIMITER $$

-- ----------------------------------------------------------------------------
-- TRIGGER 1: trg_validate_transaction_before_insert
-- Timing: BEFORE INSERT ON BANK_TRANSACTION
-- Purpose: Enforces financial safety invariants at the database level.
-- Rejects transactions on non-active accounts or with non-positive amounts.
-- ----------------------------------------------------------------------------
CREATE TRIGGER trg_validate_transaction_before_insert
BEFORE INSERT ON BANK_TRANSACTION
FOR EACH ROW
BEGIN
    DECLARE v_acc_status ENUM('Active', 'Inactive', 'Closed');

    -- Validate positive amount
    IF NEW.Amount <= 0.00 THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Integrity Violation: Transaction amount must be strictly greater than zero.';
    END IF;

    -- Retrieve linked account status
    SELECT Status INTO v_acc_status
    FROM ACCOUNT
    WHERE AccountID = NEW.AccountID;

    IF v_acc_status IS NULL THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Integrity Violation: Referenced AccountID does not exist.';
    END IF;

    IF v_acc_status != 'Active' THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Integrity Violation: Cannot execute transactions against an Inactive or Closed account.';
    END IF;
END$$

-- ----------------------------------------------------------------------------
-- TRIGGER 2: trg_prevent_negative_balance_before_update
-- Timing: BEFORE UPDATE ON ACCOUNT
-- Purpose: Mathematical guard guaranteeing an account balance can never drop
-- below zero, even if an external application bug attempts it.
-- ----------------------------------------------------------------------------
CREATE TRIGGER trg_prevent_negative_balance_before_update
BEFORE UPDATE ON ACCOUNT
FOR EACH ROW
BEGIN
    IF NEW.Balance < 0.00 THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Integrity Violation: Account balance cannot become negative.';
    END IF;
END$$

-- ----------------------------------------------------------------------------
-- TRIGGER 3: trg_audit_account_update
-- Timing: AFTER UPDATE ON ACCOUNT
-- Purpose: Automatically logs status changes or balance modifications to an
-- immutable audit log table for regulatory compliance and audit trails.
-- ----------------------------------------------------------------------------
CREATE TRIGGER trg_audit_account_update
AFTER UPDATE ON ACCOUNT
FOR EACH ROW
BEGIN
    IF OLD.Status != NEW.Status OR OLD.Balance != NEW.Balance THEN
        INSERT INTO ACCOUNT_AUDIT (
            AccountID, OldStatus, NewStatus, OldBalance, NewBalance, ActionType
        ) VALUES (
            NEW.AccountID,
            OLD.Status,
            NEW.Status,
            OLD.Balance,
            NEW.Balance,
            CASE 
                WHEN OLD.Status != NEW.Status AND OLD.Balance != NEW.Balance THEN 'STATUS_AND_BALANCE_CHANGE'
                WHEN OLD.Status != NEW.Status THEN 'STATUS_CHANGE'
                ELSE 'BALANCE_UPDATE'
            END
        );
    END IF;
END$$

-- ----------------------------------------------------------------------------
-- TRIGGER 4: trg_prevent_loan_amount_mutation
-- Timing: BEFORE UPDATE ON LOAN
-- Purpose: Protects loan contracts from unauthorized principal modification
-- once sanctioned and active.
-- ----------------------------------------------------------------------------
CREATE TRIGGER trg_prevent_loan_amount_mutation
BEFORE UPDATE ON LOAN
FOR EACH ROW
BEGIN
    IF OLD.LoanStatus = 'Active' AND OLD.LoanAmount != NEW.LoanAmount THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Integrity Violation: Principal sanctioned LoanAmount of an active loan cannot be altered.';
    END IF;
END$$

DELIMITER ;
