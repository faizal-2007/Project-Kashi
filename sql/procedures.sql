-- Project Kashi - stored procedures
USE project_kashi;

DROP PROCEDURE IF EXISTS sp_customer_accounts;
DROP PROCEDURE IF EXISTS sp_account_statement;
DROP PROCEDURE IF EXISTS sp_branch_summary;
DROP PROCEDURE IF EXISTS sp_approve_loan;

DELIMITER $$

CREATE PROCEDURE sp_customer_accounts(IN p_customer_id INT)
BEGIN
    SELECT
        a.AccountID,
        a.AccountNumber,
        a.AccountType,
        a.OpeningDate,
        a.Balance,
        a.Status,
        b.BranchName,
        ah.HolderType,
        ah.HolderSince
    FROM ACCOUNT_HOLDER ah
    JOIN ACCOUNT a ON a.AccountID = ah.AccountID
    JOIN BRANCH b ON b.BranchID = a.BranchID
    WHERE ah.CustomerID = p_customer_id
    ORDER BY a.OpeningDate DESC;
END$$

CREATE PROCEDURE sp_account_statement(
    IN p_account_id INT,
    IN p_from_date DATE,
    IN p_to_date DATE
)
BEGIN
    SET p_from_date = COALESCE(p_from_date, '1900-01-01');
    SET p_to_date = COALESCE(p_to_date, '2100-12-31');

    SELECT
        t.TransactionID,
        a.AccountNumber,
        t.TransactionType,
        t.Amount,
        t.TransactionDate,
        t.Description,
        t.ReferenceNumber,
        t.TransferGroupReference,
        t.TransactionStatus
    FROM BANK_TRANSACTION t
    JOIN ACCOUNT a ON a.AccountID = t.AccountID
    WHERE t.AccountID = p_account_id
      AND DATE(t.TransactionDate) BETWEEN p_from_date AND p_to_date
    ORDER BY t.TransactionDate DESC, t.TransactionID DESC;
END$$

CREATE PROCEDURE sp_branch_summary()
BEGIN
    SELECT
        BranchID,
        BranchName,
        IFSCCode,
        City,
        State,
        EmployeeCount,
        AccountCount,
        ActiveAccountCount,
        TotalBalance
    FROM vw_branch_summary
    ORDER BY BranchID;
END$$

CREATE PROCEDURE sp_approve_loan(
    IN p_loan_id INT,
    OUT p_result VARCHAR(100)
)
BEGIN
    DECLARE v_status VARCHAR(20);

    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        RESIGNAL;
    END;

    START TRANSACTION;

    SELECT LoanStatus
      INTO v_status
      FROM LOAN
     WHERE LoanID = p_loan_id
     FOR UPDATE;

    IF v_status IS NULL THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Loan record was not found.';
    END IF;

    IF v_status <> 'Pending' THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Only a pending loan can be approved.';
    END IF;

    UPDATE LOAN
       SET LoanStatus = 'Approved'
     WHERE LoanID = p_loan_id;

    COMMIT;
    SET p_result = 'Loan approved successfully.';
END$$

DELIMITER ;
