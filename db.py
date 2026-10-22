import uuid
import datetime
import mysql.connector
from mysql.connector import Error
from config import Config

def get_db_connection(use_database=True):
    """
    Establishes and returns a fresh MySQL connection using settings from Config.
    """
    params = {
        "host": Config.DB_HOST,
        "port": Config.DB_PORT,
        "user": Config.DB_USER,
        "password": Config.DB_PASSWORD,
        "autocommit": False
    }
    if use_database:
        params["database"] = Config.DB_NAME

    return mysql.connector.connect(**params)

def test_connection():
    """
    Tests database connectivity and returns a tuple (is_connected, message).
    """
    try:
        conn = get_db_connection(use_database=False)
        cursor = conn.cursor()
        cursor.execute("SELECT VERSION()")
        version = cursor.fetchone()
        cursor.close()
        conn.close()
        return True, f"Successfully connected to MySQL Server version {version[0]}"
    except Error as e:
        return False, f"MySQL connection error: {e.msg} (Code: {e.errno})"
    except Exception as ex:
        return False, f"Unexpected error: {str(ex)}"

def execute_query(query, params=None, fetchone=False, fetchall=False, commit=False):
    """
    Executes a parameterized SQL query safely with automatic resource cleanup.
    Returns:
      - For fetchone: single dictionary or None
      - For fetchall: list of dictionaries
      - For insert/update (commit=True): lastrowid or rowcount
    """
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(query, params or ())

        if commit:
            conn.commit()
            last_id = cursor.lastrowid
            row_count = cursor.rowcount
            return {"lastrowid": last_id, "rowcount": row_count}

        if fetchone:
            return cursor.fetchone()
        if fetchall:
            return cursor.fetchall()

        return None
    except Error as e:
        if conn:
            conn.rollback()
        raise e
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# ----------------------------------------------------------------------------
# CORE BANKING ATOMIC TRANSACTION WORKFLOWS (ACID)
# ----------------------------------------------------------------------------

def open_account_transaction(customer_id, branch_id, account_type, opening_balance, holder_type="Primary"):
    """
    Atomic transaction to:
    1. Generate a unique account number
    2. Insert row into ACCOUNT
    3. Insert relationship into ACCOUNT_HOLDER
    4. Record initial deposit in BANK_TRANSACTION if opening_balance > 0
    All steps commit together or rollback on any error.
    """
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # 1. Generate unique 10-digit account number based on BranchID and timestamp/UUID
        timestamp_part = datetime.datetime.now().strftime("%y%m%d")
        rand_part = str(uuid.uuid4().int)[:4]
        account_number = f"{branch_id:02d}{timestamp_part}{rand_part}"

        # 2. Insert into ACCOUNT
        insert_acc_sql = """
            INSERT INTO ACCOUNT (AccountNumber, AccountType, Balance, Status, BranchID)
            VALUES (%s, %s, %s, 'Active', %s)
        """
        cursor.execute(insert_acc_sql, (account_number, account_type, opening_balance, branch_id))
        account_id = cursor.lastrowid

        # 3. Insert into ACCOUNT_HOLDER
        insert_holder_sql = """
            INSERT INTO ACCOUNT_HOLDER (CustomerID, AccountID, HolderType)
            VALUES (%s, %s, %s)
        """
        cursor.execute(insert_holder_sql, (customer_id, account_id, holder_type))

        # 4. If initial balance > 0, record initial deposit transaction
        if opening_balance > 0:
            ref_num = f"DEP{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}{account_id}"
            insert_tx_sql = """
                INSERT INTO BANK_TRANSACTION (
                    AccountID, TransactionType, Amount, Description, ReferenceNumber, TransactionStatus
                ) VALUES (%s, 'DEPOSIT', %s, 'Initial Account Opening Deposit', %s, 'SUCCESS')
            """
            cursor.execute(insert_tx_sql, (account_id, opening_balance, ref_num))

        conn.commit()
        return {
            "success": True,
            "account_id": account_id,
            "account_number": account_number,
            "message": f"Account {account_number} created successfully with balance ₹{opening_balance:,.2f}"
        }
    except Error as e:
        if conn:
            conn.rollback()
        return {"success": False, "message": f"Database error during account opening: {e.msg}"}
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def deposit_transaction(account_id, amount, description=None):
    """
    Atomic Deposit Transaction:
    1. Lock Account row FOR UPDATE
    2. Validate Active status
    3. Update Account balance
    4. Insert record into BANK_TRANSACTION
    5. Commit transaction
    """
    conn = None
    cursor = None
    try:
        if amount <= 0:
            return {"success": False, "message": "Deposit amount must be strictly greater than zero."}

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # 1. Lock Account
        cursor.execute("SELECT Balance, Status FROM ACCOUNT WHERE AccountID = %s FOR UPDATE", (account_id,))
        acc = cursor.fetchone()
        if not acc:
            conn.rollback()
            return {"success": False, "message": "Target account not found."}

        if acc["Status"] != "Active":
            conn.rollback()
            return {"success": False, "message": f"Account is {acc['Status']}. Deposits only permitted on Active accounts."}

        # 2. Update Balance
        new_balance = float(acc["Balance"]) + float(amount)
        cursor.execute("UPDATE ACCOUNT SET Balance = %s WHERE AccountID = %s", (new_balance, account_id))

        # 3. Insert Transaction
        ref_num = f"DEP{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}{account_id}"
        cursor.execute("""
            INSERT INTO BANK_TRANSACTION (
                AccountID, TransactionType, Amount, Description, ReferenceNumber, TransactionStatus
            ) VALUES (%s, 'DEPOSIT', %s, %s, %s, 'SUCCESS')
        """, (account_id, amount, description or "Branch Counter Deposit", ref_num))

        conn.commit()
        return {
            "success": True,
            "new_balance": new_balance,
            "reference_number": ref_num,
            "message": f"₹{amount:,.2f} deposited successfully. New balance: ₹{new_balance:,.2f}"
        }
    except Error as e:
        if conn:
            conn.rollback()
        return {"success": False, "message": f"Database error during deposit: {e.msg}"}
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def withdrawal_transaction(account_id, amount, description=None):
    """
    Atomic Withdrawal Transaction:
    1. Lock Account row FOR UPDATE
    2. Check Active status and sufficient funds
    3. Deduct balance
    4. Insert record into BANK_TRANSACTION
    5. Commit transaction
    """
    conn = None
    cursor = None
    try:
        if amount <= 0:
            return {"success": False, "message": "Withdrawal amount must be strictly greater than zero."}

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # 1. Lock Account
        cursor.execute("SELECT Balance, Status FROM ACCOUNT WHERE AccountID = %s FOR UPDATE", (account_id,))
        acc = cursor.fetchone()
        if not acc:
            conn.rollback()
            return {"success": False, "message": "Target account not found."}

        if acc["Status"] != "Active":
            conn.rollback()
            return {"success": False, "message": f"Account is {acc['Status']}. Withdrawals only permitted on Active accounts."}

        current_balance = float(acc["Balance"])
        if current_balance < float(amount):
            conn.rollback()
            return {
                "success": False, 
                "message": f"Insufficient funds. Available balance: ₹{current_balance:,.2f}, Requested: ₹{amount:,.2f}"
            }

        # 2. Update Balance
        new_balance = current_balance - float(amount)
        cursor.execute("UPDATE ACCOUNT SET Balance = %s WHERE AccountID = %s", (new_balance, account_id))

        # 3. Insert Transaction
        ref_num = f"WTH{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}{account_id}"
        cursor.execute("""
            INSERT INTO BANK_TRANSACTION (
                AccountID, TransactionType, Amount, Description, ReferenceNumber, TransactionStatus
            ) VALUES (%s, 'WITHDRAWAL', %s, %s, %s, 'SUCCESS')
        """, (account_id, amount, description or "ATM/Counter Withdrawal", ref_num))

        conn.commit()
        return {
            "success": True,
            "new_balance": new_balance,
            "reference_number": ref_num,
            "message": f"₹{amount:,.2f} withdrawn successfully. New balance: ₹{new_balance:,.2f}"
        }
    except Error as e:
        if conn:
            conn.rollback()
        return {"success": False, "message": f"Database error during withdrawal: {e.msg}"}
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def transfer_transaction(src_account_id, dest_account_id, amount, description=None):
    """
    Atomic Inter-Account Transfer Transaction:
    1. Prevent same-account transfer
    2. Lock accounts in ordered sequence (lowest ID first) to avoid deadlock
    3. Validate both accounts are Active
    4. Check sufficient balance in source account
    5. Deduct from source and credit destination
    6. Insert paired TRANSFER_OUT and TRANSFER_IN transactions with common ReferenceNumber
    7. Commit transaction; rollback everything on failure
    """
    conn = None
    cursor = None
    try:
        if src_account_id == dest_account_id:
            return {"success": False, "message": "Source and destination accounts cannot be identical."}

        if amount <= 0:
            return {"success": False, "message": "Transfer amount must be strictly greater than zero."}

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Order locks by ID to prevent deadlocks
        first_id = min(src_account_id, dest_account_id)
        second_id = max(src_account_id, dest_account_id)

        cursor.execute("SELECT AccountID, AccountNumber, Balance, Status FROM ACCOUNT WHERE AccountID = %s FOR UPDATE", (first_id,))
        acc1 = cursor.fetchone()

        cursor.execute("SELECT AccountID, AccountNumber, Balance, Status FROM ACCOUNT WHERE AccountID = %s FOR UPDATE", (second_id,))
        acc2 = cursor.fetchone()

        if not acc1 or not acc2:
            conn.rollback()
            return {"success": False, "message": "One or both specified accounts do not exist."}

        src_acc = acc1 if acc1["AccountID"] == src_account_id else acc2
        dest_acc = acc2 if acc2["AccountID"] == dest_account_id else acc1

        if src_acc["Status"] != "Active" or dest_acc["Status"] != "Active":
            conn.rollback()
            return {"success": False, "message": "Both source and destination accounts must be in 'Active' status."}

        src_balance = float(src_acc["Balance"])
        if src_balance < float(amount):
            conn.rollback()
            return {
                "success": False, 
                "message": f"Insufficient funds in source account. Available: ₹{src_balance:,.2f}"
            }

        # Deduct source and credit destination
        new_src_bal = src_balance - float(amount)
        new_dest_bal = float(dest_acc["Balance"]) + float(amount)

        cursor.execute("UPDATE ACCOUNT SET Balance = %s WHERE AccountID = %s", (new_src_bal, src_account_id))
        cursor.execute("UPDATE ACCOUNT SET Balance = %s WHERE AccountID = %s", (new_dest_bal, dest_account_id))

        # Generate common reference number
        ref_num = f"TRF{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}{src_account_id}X{dest_account_id}"

        # Insert TRANSFER_OUT
        cursor.execute("""
            INSERT INTO BANK_TRANSACTION (
                AccountID, TransactionType, Amount, Description, ReferenceNumber, TransactionStatus
            ) VALUES (%s, 'TRANSFER_OUT', %s, %s, %s, 'SUCCESS')
        """, (
            src_account_id, 
            amount, 
            description or f"Transfer to Account {dest_acc['AccountNumber']}", 
            ref_num
        ))

        # Insert TRANSFER_IN
        cursor.execute("""
            INSERT INTO BANK_TRANSACTION (
                AccountID, TransactionType, Amount, Description, ReferenceNumber, TransactionStatus
            ) VALUES (%s, 'TRANSFER_IN', %s, %s, %s, 'SUCCESS')
        """, (
            dest_account_id, 
            amount, 
            description or f"Transfer from Account {src_acc['AccountNumber']}", 
            ref_num
        ))

        conn.commit()
        return {
            "success": True,
            "reference_number": ref_num,
            "new_source_balance": new_src_bal,
            "message": f"Successfully transferred ₹{amount:,.2f} from Acc {src_acc['AccountNumber']} to Acc {dest_acc['AccountNumber']} (Ref: {ref_num})"
        }
    except Error as e:
        if conn:
            conn.rollback()
        return {"success": False, "message": f"Database error during transfer: {e.msg}"}
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def record_loan_payment_transaction(loan_id, amount, payment_mode, reference_number=None):
    """
    Atomic Loan Repayment Transaction:
    1. Lock LOAN row
    2. Check status is Active
    3. Insert LOAN_PAYMENT record
    4. Compute total repaid; if total >= loan amount, mark LOAN as 'Closed'
    5. Commit transaction
    """
    conn = None
    cursor = None
    try:
        if amount <= 0:
            return {"success": False, "message": "Payment amount must be strictly positive."}

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT LoanID, LoanAmount, LoanStatus FROM LOAN WHERE LoanID = %s FOR UPDATE", (loan_id,))
        loan = cursor.fetchone()
        if not loan:
            conn.rollback()
            return {"success": False, "message": "Loan not found."}

        if loan["LoanStatus"] != "Active":
            conn.rollback()
            return {"success": False, "message": f"Cannot make payment against a loan with status '{loan['LoanStatus']}'."}

        ref_no = reference_number or f"LPAY{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}{loan_id}"

        cursor.execute("""
            INSERT INTO LOAN_PAYMENT (LoanID, Amount, PaymentMode, ReferenceNumber)
            VALUES (%s, %s, %s, %s)
        """, (loan_id, amount, payment_mode, ref_no))

        cursor.execute("SELECT COALESCE(SUM(Amount), 0.00) AS TotalPaid FROM LOAN_PAYMENT WHERE LoanID = %s", (loan_id,))
        sum_row = cursor.fetchone()
        total_paid = float(sum_row["TotalPaid"])
        sanctioned = float(loan["LoanAmount"])

        if total_paid >= sanctioned:
            cursor.execute("UPDATE LOAN SET LoanStatus = 'Closed' WHERE LoanID = %s", (loan_id,))
            msg = f"Repayment of ₹{amount:,.2f} recorded. Loan #{loan_id} is now FULLY REPAID and CLOSED!"
        else:
            remaining = sanctioned - total_paid
            msg = f"Repayment of ₹{amount:,.2f} recorded. Remaining principal: ₹{remaining:,.2f} (Ref: {ref_no})"

        conn.commit()
        return {"success": True, "reference_number": ref_no, "message": msg}
    except Error as e:
        if conn:
            conn.rollback()
        return {"success": False, "message": f"Database error during loan repayment: {e.msg}"}
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
