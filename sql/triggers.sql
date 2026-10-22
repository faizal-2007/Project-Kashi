-- Project Kashi - database triggers
USE project_kashi;

DROP TRIGGER IF EXISTS trg_account_status_before_update;
DROP TRIGGER IF EXISTS trg_account_holder_primary_before_insert;
DROP TRIGGER IF EXISTS trg_account_holder_primary_before_update;
DROP TRIGGER IF EXISTS trg_transaction_before_insert;
DROP TRIGGER IF EXISTS trg_transaction_prevent_update;
DROP TRIGGER IF EXISTS trg_transaction_prevent_delete;
DROP TRIGGER IF EXISTS trg_loan_payment_before_insert;
DROP TRIGGER IF EXISTS trg_loan_payment_after_insert;

DELIMITER $$

CREATE TRIGGER trg_account_status_before_update
BEFORE UPDATE ON ACCOUNT
FOR EACH ROW
BEGIN
    IF OLD.Status = 'Closed' AND NEW.Status <> 'Closed' THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'A closed account cannot be reopened.';
    END IF;

    IF NEW.Status = 'Closed' AND NEW.Balance <> 0 THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'An account can be closed only when its balance is zero.';
    END IF;
END$$

CREATE TRIGGER trg_account_holder_primary_before_insert
BEFORE INSERT ON ACCOUNT_HOLDER
FOR EACH ROW
BEGIN
    DECLARE v_primary_count INT;

    IF NEW.HolderType = 'Primary' THEN
        SELECT COUNT(*)
          INTO v_primary_count
          FROM ACCOUNT_HOLDER
         WHERE AccountID = NEW.AccountID
           AND HolderType = 'Primary';

        IF v_primary_count > 0 THEN
            SIGNAL SQLSTATE '45000'
                SET MESSAGE_TEXT = 'An account can have only one primary holder.';
        END IF;
    END IF;
END$$

CREATE TRIGGER trg_account_holder_primary_before_update
BEFORE UPDATE ON ACCOUNT_HOLDER
FOR EACH ROW
BEGIN
    DECLARE v_primary_count INT;

    IF NEW.HolderType = 'Primary' AND OLD.HolderType <> 'Primary' THEN
        SELECT COUNT(*)
          INTO v_primary_count
          FROM ACCOUNT_HOLDER
         WHERE AccountID = NEW.AccountID
           AND HolderType = 'Primary'
           AND NOT (CustomerID = OLD.CustomerID AND AccountID = OLD.AccountID);

        IF v_primary_count > 0 THEN
            SIGNAL SQLSTATE '45000'
                SET MESSAGE_TEXT = 'An account can have only one primary holder.';
        END IF;
    END IF;
END$$

CREATE TRIGGER trg_transaction_before_insert
BEFORE INSERT ON BANK_TRANSACTION
FOR EACH ROW
BEGIN
    DECLARE v_account_status VARCHAR(20);

    SELECT Status
      INTO v_account_status
      FROM ACCOUNT
     WHERE AccountID = NEW.AccountID;

    IF v_account_status <> 'Active' THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Transactions are allowed only on active accounts.';
    END IF;
END$$

CREATE TRIGGER trg_transaction_prevent_update
BEFORE UPDATE ON BANK_TRANSACTION
FOR EACH ROW
BEGIN
    SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Transaction history is immutable and cannot be updated.';
END$$

CREATE TRIGGER trg_transaction_prevent_delete
BEFORE DELETE ON BANK_TRANSACTION
FOR EACH ROW
BEGIN
    SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Transaction history is immutable and cannot be deleted.';
END$$

CREATE TRIGGER trg_loan_payment_before_insert
BEFORE INSERT ON LOAN_PAYMENT
FOR EACH ROW
BEGIN
    DECLARE v_status VARCHAR(20);
    DECLARE v_outstanding DECIMAL(15,2);

    SELECT LoanStatus
      INTO v_status
      FROM LOAN
     WHERE LoanID = NEW.LoanID;

    SELECT GREATEST(
               l.LoanAmount - COALESCE(
                   (SELECT SUM(lp.Amount) FROM LOAN_PAYMENT lp WHERE lp.LoanID = l.LoanID),
                   0
               ),
               0
           )
      INTO v_outstanding
      FROM LOAN l
     WHERE l.LoanID = NEW.LoanID;

    IF v_status <> 'Approved' THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Loan payments are allowed only for approved loans.';
    END IF;

    IF NEW.Amount > v_outstanding THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Loan payment exceeds the outstanding loan amount.';
    END IF;
END$$

CREATE TRIGGER trg_loan_payment_after_insert
AFTER INSERT ON LOAN_PAYMENT
FOR EACH ROW
BEGIN
    DECLARE v_loan_amount DECIMAL(15,2);
    DECLARE v_total_paid DECIMAL(15,2);

    SELECT LoanAmount
      INTO v_loan_amount
      FROM LOAN
     WHERE LoanID = NEW.LoanID;

    SELECT COALESCE(SUM(Amount), 0)
      INTO v_total_paid
      FROM LOAN_PAYMENT
     WHERE LoanID = NEW.LoanID;

    IF v_total_paid >= v_loan_amount THEN
        UPDATE LOAN
           SET LoanStatus = 'Closed'
         WHERE LoanID = NEW.LoanID
           AND LoanStatus = 'Approved';
    END IF;
END$$

DELIMITER ;
