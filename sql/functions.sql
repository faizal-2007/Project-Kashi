-- Project Kashi - stored functions
USE project_kashi;

DROP FUNCTION IF EXISTS fn_customer_age;
DROP FUNCTION IF EXISTS fn_account_tenure_months;
DROP FUNCTION IF EXISTS fn_loan_outstanding;
DROP FUNCTION IF EXISTS fn_branch_total_balance;

DELIMITER $$

CREATE FUNCTION fn_customer_age(p_customer_id INT)
RETURNS INT
READS SQL DATA
BEGIN
    DECLARE v_dob DATE;

    SELECT DateOfBirth
      INTO v_dob
      FROM CUSTOMER
     WHERE CustomerID = p_customer_id;

    IF v_dob IS NULL THEN
        RETURN NULL;
    END IF;

    RETURN TIMESTAMPDIFF(YEAR, v_dob, CURDATE());
END$$

CREATE FUNCTION fn_account_tenure_months(p_account_id INT)
RETURNS INT
READS SQL DATA
BEGIN
    DECLARE v_opening_date DATETIME;

    SELECT OpeningDate
      INTO v_opening_date
      FROM ACCOUNT
     WHERE AccountID = p_account_id;

    IF v_opening_date IS NULL THEN
        RETURN NULL;
    END IF;

    RETURN TIMESTAMPDIFF(MONTH, v_opening_date, NOW());
END$$

CREATE FUNCTION fn_loan_outstanding(p_loan_id INT)
RETURNS DECIMAL(15,2)
READS SQL DATA
BEGIN
    DECLARE v_loan_amount DECIMAL(15,2);
    DECLARE v_paid DECIMAL(15,2);

    SELECT LoanAmount
      INTO v_loan_amount
      FROM LOAN
     WHERE LoanID = p_loan_id;

    IF v_loan_amount IS NULL THEN
        RETURN NULL;
    END IF;

    SELECT COALESCE(SUM(Amount), 0)
      INTO v_paid
      FROM LOAN_PAYMENT
     WHERE LoanID = p_loan_id;

    RETURN GREATEST(v_loan_amount - v_paid, 0);
END$$

CREATE FUNCTION fn_branch_total_balance(p_branch_id INT)
RETURNS DECIMAL(15,2)
READS SQL DATA
BEGIN
    DECLARE v_total DECIMAL(15,2);

    SELECT COALESCE(SUM(Balance), 0)
      INTO v_total
      FROM ACCOUNT
     WHERE BranchID = p_branch_id
       AND Status = 'Active';

    RETURN v_total;
END$$

DELIMITER ;
