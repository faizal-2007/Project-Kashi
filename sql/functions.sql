-- ============================================================================
-- PROJECT KASHI — BANKING MANAGEMENT SYSTEM
-- Script: functions.sql
-- Purpose: User-Defined Stored Functions for Calculations and Business Logic
-- Database: project_kashi
-- ============================================================================

USE project_kashi;

DROP FUNCTION IF EXISTS fn_calculate_customer_age;
DROP FUNCTION IF EXISTS fn_get_account_balance;
DROP FUNCTION IF EXISTS fn_calculate_monthly_emi;
DROP FUNCTION IF EXISTS fn_get_total_customer_balance;

DELIMITER $$

-- ----------------------------------------------------------------------------
-- FUNCTION 1: fn_calculate_customer_age
-- Purpose: Calculates current age in completed years from Date of Birth.
-- ----------------------------------------------------------------------------
CREATE FUNCTION fn_calculate_customer_age(p_dob DATE)
RETURNS INT
DETERMINISTIC
READS SQL DATA
BEGIN
    DECLARE v_age INT;
    IF p_dob IS NULL THEN
        RETURN 0;
    END IF;
    SET v_age = TIMESTAMPDIFF(YEAR, p_dob, CURDATE());
    RETURN v_age;
END$$

-- ----------------------------------------------------------------------------
-- FUNCTION 2: fn_get_account_balance
-- Purpose: Returns current real-time balance for an account ID.
-- ----------------------------------------------------------------------------
CREATE FUNCTION fn_get_account_balance(p_account_id INT)
RETURNS DECIMAL(15, 2)
DETERMINISTIC
READS SQL DATA
BEGIN
    DECLARE v_balance DECIMAL(15, 2);
    SELECT Balance INTO v_balance 
    FROM ACCOUNT 
    WHERE AccountID = p_account_id;
    
    RETURN COALESCE(v_balance, 0.00);
END$$

-- ----------------------------------------------------------------------------
-- FUNCTION 3: fn_calculate_monthly_emi
-- Purpose: Computes estimated monthly installment (EMI) using the reducing
-- balance formula: [P * r * (1 + r)^n] / [(1 + r)^n - 1]
-- ----------------------------------------------------------------------------
CREATE FUNCTION fn_calculate_monthly_emi(
    p_principal DECIMAL(15, 2),
    p_annual_rate DECIMAL(5, 2),
    p_tenure_months INT
)
RETURNS DECIMAL(15, 2)
DETERMINISTIC
NO SQL
BEGIN
    DECLARE v_monthly_rate DOUBLE;
    DECLARE v_pow DOUBLE;
    DECLARE v_emi DOUBLE;
    
    IF p_principal <= 0 OR p_tenure_months <= 0 THEN
        RETURN 0.00;
    END IF;
    
    IF p_annual_rate = 0 THEN
        RETURN ROUND(p_principal / p_tenure_months, 2);
    END IF;
    
    -- Convert annual interest percentage to monthly fractional rate
    SET v_monthly_rate = (p_annual_rate / 12.0) / 100.0;
    SET v_pow = POW(1.0 + v_monthly_rate, p_tenure_months);
    SET v_emi = (p_principal * v_monthly_rate * v_pow) / (v_pow - 1.0);
    
    RETURN ROUND(v_emi, 2);
END$$

-- ----------------------------------------------------------------------------
-- FUNCTION 4: fn_get_total_customer_balance
-- Purpose: Returns consolidated portfolio balance across all accounts held
-- by a given customer ID.
-- ----------------------------------------------------------------------------
CREATE FUNCTION fn_get_total_customer_balance(p_customer_id INT)
RETURNS DECIMAL(15, 2)
DETERMINISTIC
READS SQL DATA
BEGIN
    DECLARE v_total DECIMAL(15, 2);
    
    SELECT COALESCE(SUM(a.Balance), 0.00) INTO v_total
    FROM ACCOUNT a
    JOIN ACCOUNT_HOLDER ah ON a.AccountID = ah.AccountID
    WHERE ah.CustomerID = p_customer_id
      AND a.Status = 'Active';
      
    RETURN v_total;
END$$

DELIMITER ;
