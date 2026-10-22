import re
import datetime
from flask import Flask, render_template, request, redirect, url_for, flash
import mysql.connector
from config import Config
from db import (
    get_db_connection, test_connection, execute_query,
    open_account_transaction, deposit_transaction, withdrawal_transaction,
    transfer_transaction, record_loan_payment_transaction
)

app = Flask(__name__)
app.config.from_object(Config)

# ----------------------------------------------------------------------------
# CONTEXT PROCESSOR & TEMPLATE FILTERS
# ----------------------------------------------------------------------------
@app.context_processor
def inject_db_status():
    """Provides database connection status to all templates for the header badge."""
    is_connected, msg = test_connection()
    return {"db_connected": is_connected, "db_message": msg}

@app.template_filter("currency")
def currency_filter(value):
    try:
        val = float(value)
        return f"₹{val:,.2f}"
    except (ValueError, TypeError):
        return "₹0.00"

@app.template_filter("dateformat")
def dateformat_filter(value, fmt="%d %b %Y"):
    if not value:
        return ""
    if isinstance(value, str):
        try:
            value = datetime.datetime.fromisoformat(value)
        except ValueError:
            return value
    if isinstance(value, (datetime.datetime, datetime.date)):
        return value.strftime(fmt)
    return str(value)

# ----------------------------------------------------------------------------
# 1. DASHBOARD ROUTE
# ----------------------------------------------------------------------------
@app.route("/")
def index():
    is_connected, msg = test_connection()
    if not is_connected:
        return render_template(
            "index.html",
            db_error=msg,
            stats={"customers": 0, "accounts": 0, "active_accounts": 0, "branches": 0, "total_deposits": 0, "transactions": 0},
            recent_transactions=[]
        )

    try:
        cust_count = execute_query("SELECT COUNT(*) AS total FROM CUSTOMER", fetchone=True)["total"]
        acc_stats = execute_query("""
            SELECT 
                COUNT(*) AS total_accounts,
                COALESCE(SUM(CASE WHEN Status = 'Active' THEN 1 ELSE 0 END), 0) AS active_accounts,
                COALESCE(SUM(Balance), 0.00) AS total_deposits
            FROM ACCOUNT
        """, fetchone=True)
        branch_count = execute_query("SELECT COUNT(*) AS total FROM BRANCH", fetchone=True)["total"]
        tx_count = execute_query("SELECT COUNT(*) AS total FROM BANK_TRANSACTION", fetchone=True)["total"]

        recent_tx = execute_query("""
            SELECT 
                t.TransactionID,
                t.ReferenceNumber,
                t.TransactionType,
                t.Amount,
                t.TransactionDate,
                t.TransactionStatus,
                a.AccountNumber,
                c.FirstName,
                c.LastName
            FROM BANK_TRANSACTION t
            JOIN ACCOUNT a ON t.AccountID = a.AccountID
            LEFT JOIN ACCOUNT_HOLDER ah ON a.AccountID = ah.AccountID AND ah.HolderType = 'Primary'
            LEFT JOIN CUSTOMER c ON ah.CustomerID = c.CustomerID
            ORDER BY t.TransactionDate DESC, t.TransactionID DESC
            LIMIT 8
        """, fetchall=True)

        stats = {
            "customers": cust_count,
            "accounts": acc_stats["total_accounts"],
            "active_accounts": acc_stats["active_accounts"],
            "branches": branch_count,
            "total_deposits": acc_stats["total_deposits"],
            "transactions": tx_count
        }

        return render_template("index.html", stats=stats, recent_transactions=recent_tx, db_error=None)
    except mysql.connector.Error as e:
        return render_template("index.html", db_error=f"Database query error: {e.msg}", stats={}, recent_transactions=[])

# ----------------------------------------------------------------------------
# 2. CUSTOMER MANAGEMENT ROUTES
# ----------------------------------------------------------------------------
@app.route("/customers")
def customer_list():
    search = request.args.get("search", "").strip()
    is_connected, _ = test_connection()
    if not is_connected:
        flash("MySQL database is not connected. Displaying offline mode.", "warning")
        return render_template("customers.html", customers=[], search=search)

    try:
        query = """
            SELECT 
                c.CustomerID,
                c.FirstName,
                c.LastName,
                c.Email,
                c.Mobile,
                c.City,
                c.RegistrationDate,
                COUNT(ah.AccountID) AS AccountCount
            FROM CUSTOMER c
            LEFT JOIN ACCOUNT_HOLDER ah ON c.CustomerID = ah.CustomerID
        """
        params = []
        if search:
            query += " WHERE c.FirstName LIKE %s OR c.LastName LIKE %s OR c.Email LIKE %s OR c.Mobile LIKE %s OR c.City LIKE %s"
            wildcard = f"%{search}%"
            params.extend([wildcard, wildcard, wildcard, wildcard, wildcard])

        query += " GROUP BY c.CustomerID ORDER BY c.CustomerID DESC"
        customers = execute_query(query, params, fetchall=True)
        return render_template("customers.html", customers=customers, search=search)
    except mysql.connector.Error as e:
        flash(f"Database error: {e.msg}", "danger")
        return render_template("customers.html", customers=[], search=search)

@app.route("/customers/register", methods=["GET", "POST"])
def customer_register():
    if request.method == "POST":
        first_name = request.form.get("first_name", "").strip()
        last_name = request.form.get("last_name", "").strip()
        dob = request.form.get("dob", "").strip()
        gender = request.form.get("gender", "").strip()
        mobile = request.form.get("mobile", "").strip()
        email = request.form.get("email", "").strip()
        address = request.form.get("address", "").strip()
        city = request.form.get("city", "").strip()

        errors = []
        if not first_name or not last_name:
            errors.append("First name and Last name are mandatory.")
        if not dob:
            errors.append("Date of Birth is required.")
        if gender not in ["Male", "Female", "Other"]:
            errors.append("Please select a valid Gender.")
        if not re.match(r"^[0-9]{10}$", mobile):
            errors.append("Mobile number must be exactly 10 digits.")
        if not re.match(r"^[^@]+@[^@]+\.[^@]+$", email):
            errors.append("Please provide a valid email address.")
        if not address or not city:
            errors.append("Address and City are required.")

        if errors:
            for err in errors:
                flash(err, "danger")
            return render_template("customer_form.html", form_data=request.form)

        is_connected, _ = test_connection()
        if not is_connected:
            flash("Cannot register customer: MySQL database is currently disconnected.", "danger")
            return render_template("customer_form.html", form_data=request.form)

        try:
            existing = execute_query(
                "SELECT CustomerID FROM CUSTOMER WHERE Email = %s OR Mobile = %s",
                (email, mobile), fetchone=True
            )
            if existing:
                flash("A customer with this email or mobile number is already registered.", "warning")
                return render_template("customer_form.html", form_data=request.form)

            sql = """
                INSERT INTO CUSTOMER (FirstName, LastName, DateOfBirth, Gender, Mobile, Email, Address, City)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            res = execute_query(sql, (first_name, last_name, dob, gender, mobile, email, address, city), commit=True)
            cust_id = res["lastrowid"]
            flash(f"Customer {first_name} {last_name} registered successfully with ID #{cust_id}!", "success")
            return redirect(url_for("customer_detail", customer_id=cust_id))
        except mysql.connector.Error as e:
            flash(f"Database error during registration: {e.msg}", "danger")
            return render_template("customer_form.html", form_data=request.form)

    return render_template("customer_form.html", form_data={})

@app.route("/customers/<int:customer_id>")
def customer_detail(customer_id):
    is_connected, _ = test_connection()
    if not is_connected:
        flash("MySQL database is not connected.", "warning")
        return redirect(url_for("customer_list"))

    try:
        customer = execute_query("SELECT * FROM CUSTOMER WHERE CustomerID = %s", (customer_id,), fetchone=True)
        if not customer:
            flash("Customer not found.", "warning")
            return redirect(url_for("customer_list"))

        accounts = execute_query("""
            SELECT 
                a.AccountID,
                a.AccountNumber,
                a.AccountType,
                a.Balance,
                a.Status,
                a.OpeningDate,
                ah.HolderType,
                b.BranchName,
                b.IFSCCode
            FROM ACCOUNT a
            JOIN ACCOUNT_HOLDER ah ON a.AccountID = ah.AccountID
            JOIN BRANCH b ON a.BranchID = b.BranchID
            WHERE ah.CustomerID = %s
        """, (customer_id,), fetchall=True)

        loans = execute_query("""
            SELECT l.*, b.BranchName
            FROM LOAN l
            JOIN BRANCH b ON l.BranchID = b.BranchID
            WHERE l.CustomerID = %s
        """, (customer_id,), fetchall=True)

        return render_template("customer_detail.html", customer=customer, accounts=accounts, loans=loans)
    except mysql.connector.Error as e:
        flash(f"Database error: {e.msg}", "danger")
        return redirect(url_for("customer_list"))

# ----------------------------------------------------------------------------
# 3. ACCOUNT MANAGEMENT ROUTES
# ----------------------------------------------------------------------------
@app.route("/accounts")
def account_list():
    search = request.args.get("search", "").strip()
    status_filter = request.args.get("status", "").strip()
    type_filter = request.args.get("type", "").strip()

    is_connected, _ = test_connection()
    if not is_connected:
        flash("MySQL database is not connected. Displaying offline mode.", "warning")
        return render_template("accounts.html", accounts=[], search=search, status_filter=status_filter, type_filter=type_filter)

    try:
        query = """
            SELECT 
                a.AccountID,
                a.AccountNumber,
                a.AccountType,
                a.Balance,
                a.Status,
                a.OpeningDate,
                b.BranchName,
                b.IFSCCode,
                GROUP_CONCAT(CONCAT(c.FirstName, ' ', c.LastName, ' (', ah.HolderType, ')') SEPARATOR ', ') AS Holders
            FROM ACCOUNT a
            JOIN BRANCH b ON a.BranchID = b.BranchID
            LEFT JOIN ACCOUNT_HOLDER ah ON a.AccountID = ah.AccountID
            LEFT JOIN CUSTOMER c ON ah.CustomerID = c.CustomerID
            WHERE 1=1
        """
        params = []
        if search:
            query += " AND (a.AccountNumber LIKE %s OR c.FirstName LIKE %s OR c.LastName LIKE %s OR b.BranchName LIKE %s)"
            wildcard = f"%{search}%"
            params.extend([wildcard, wildcard, wildcard, wildcard])
        if status_filter:
            query += " AND a.Status = %s"
            params.append(status_filter)
        if type_filter:
            query += " AND a.AccountType = %s"
            params.append(type_filter)

        query += " GROUP BY a.AccountID ORDER BY a.AccountID DESC"
        accounts = execute_query(query, params, fetchall=True)
        return render_template("accounts.html", accounts=accounts, search=search, status_filter=status_filter, type_filter=type_filter)
    except mysql.connector.Error as e:
        flash(f"Database error: {e.msg}", "danger")
        return render_template("accounts.html", accounts=[], search=search, status_filter=status_filter, type_filter=type_filter)

@app.route("/accounts/open", methods=["GET", "POST"])
def account_open():
    is_connected, _ = test_connection()
    customers = []
    branches = []
    if is_connected:
        try:
            customers = execute_query("SELECT CustomerID, FirstName, LastName, Mobile FROM CUSTOMER ORDER BY FirstName", fetchall=True) or []
            branches = execute_query("SELECT BranchID, BranchName, IFSCCode, City FROM BRANCH ORDER BY BranchName", fetchall=True) or []
        except mysql.connector.Error:
            pass

    preselected_customer = request.args.get("customer_id", type=int)

    if request.method == "POST":
        customer_id = request.form.get("customer_id", type=int)
        branch_id = request.form.get("branch_id", type=int)
        account_type = request.form.get("account_type", "").strip()
        opening_balance = request.form.get("opening_balance", type=float, default=0.0)
        holder_type = request.form.get("holder_type", "Primary").strip()

        errors = []
        if not customer_id:
            errors.append("Please select a valid customer.")
        if not branch_id:
            errors.append("Please select a branch.")
        if account_type not in ["Saving", "Current", "Salary"]:
            errors.append("Invalid account type selected.")
        if opening_balance < 0:
            errors.append("Opening balance cannot be negative.")

        if errors:
            for err in errors:
                flash(err, "danger")
            return render_template("account_form.html", customers=customers, branches=branches, preselected_customer=customer_id)

        result = open_account_transaction(customer_id, branch_id, account_type, opening_balance, holder_type)
        if result["success"]:
            flash(result["message"], "success")
            return redirect(url_for("account_detail", account_id=result["account_id"]))
        else:
            flash(result["message"], "danger")
            return render_template("account_form.html", customers=customers, branches=branches, preselected_customer=customer_id)

    return render_template("account_form.html", customers=customers, branches=branches, preselected_customer=preselected_customer)

@app.route("/accounts/<int:account_id>")
def account_detail(account_id):
    is_connected, _ = test_connection()
    if not is_connected:
        flash("MySQL database is not connected.", "warning")
        return redirect(url_for("account_list"))

    try:
        account = execute_query("""
            SELECT a.*, b.BranchName, b.IFSCCode, b.City, b.Address AS BranchAddress
            FROM ACCOUNT a
            JOIN BRANCH b ON a.BranchID = b.BranchID
            WHERE a.AccountID = %s
        """, (account_id,), fetchone=True)

        if not account:
            flash("Account not found.", "warning")
            return redirect(url_for("account_list"))

        holders = execute_query("""
            SELECT c.*, ah.HolderType, ah.HolderSince
            FROM CUSTOMER c
            JOIN ACCOUNT_HOLDER ah ON c.CustomerID = ah.CustomerID
            WHERE ah.AccountID = %s
        """, (account_id,), fetchall=True)

        transactions = execute_query("""
            SELECT * FROM BANK_TRANSACTION 
            WHERE AccountID = %s 
            ORDER BY TransactionDate DESC, TransactionID DESC
        """, (account_id,), fetchall=True)

        return render_template("account_detail.html", account=account, holders=holders, transactions=transactions)
    except mysql.connector.Error as e:
        flash(f"Database error: {e.msg}", "danger")
        return redirect(url_for("account_list"))

# ----------------------------------------------------------------------------
# 4. DEPOSIT, WITHDRAWAL, & TRANSFER ROUTES
# ----------------------------------------------------------------------------
@app.route("/deposit", methods=["GET", "POST"])
def deposit():
    preselected_acc = request.args.get("account_id", type=int)
    accounts = []
    is_connected, _ = test_connection()
    if is_connected:
        try:
            accounts = execute_query("""
                SELECT a.AccountID, a.AccountNumber, a.AccountType, a.Balance, b.BranchName,
                       CONCAT(c.FirstName, ' ', c.LastName) AS PrimaryHolder
                FROM ACCOUNT a
                JOIN BRANCH b ON a.BranchID = b.BranchID
                LEFT JOIN ACCOUNT_HOLDER ah ON a.AccountID = ah.AccountID AND ah.HolderType = 'Primary'
                LEFT JOIN CUSTOMER c ON ah.CustomerID = c.CustomerID
                WHERE a.Status = 'Active'
                ORDER BY a.AccountNumber
            """, fetchall=True) or []
        except mysql.connector.Error:
            pass

    if request.method == "POST":
        account_id = request.form.get("account_id", type=int)
        amount = request.form.get("amount", type=float, default=0.0)
        description = request.form.get("description", "").strip()

        if not account_id or amount <= 0:
            flash("Please choose an account and enter a valid positive deposit amount.", "danger")
            return render_template("deposit.html", accounts=accounts, preselected_acc=account_id)

        result = deposit_transaction(account_id, amount, description)
        if result["success"]:
            flash(result["message"], "success")
            return redirect(url_for("account_detail", account_id=account_id))
        else:
            flash(result["message"], "danger")

    return render_template("deposit.html", accounts=accounts, preselected_acc=preselected_acc)

@app.route("/withdrawal", methods=["GET", "POST"])
def withdrawal():
    preselected_acc = request.args.get("account_id", type=int)
    accounts = []
    is_connected, _ = test_connection()
    if is_connected:
        try:
            accounts = execute_query("""
                SELECT a.AccountID, a.AccountNumber, a.AccountType, a.Balance, b.BranchName,
                       CONCAT(c.FirstName, ' ', c.LastName) AS PrimaryHolder
                FROM ACCOUNT a
                JOIN BRANCH b ON a.BranchID = b.BranchID
                LEFT JOIN ACCOUNT_HOLDER ah ON a.AccountID = ah.AccountID AND ah.HolderType = 'Primary'
                LEFT JOIN CUSTOMER c ON ah.CustomerID = c.CustomerID
                WHERE a.Status = 'Active'
                ORDER BY a.AccountNumber
            """, fetchall=True) or []
        except mysql.connector.Error:
            pass

    if request.method == "POST":
        account_id = request.form.get("account_id", type=int)
        amount = request.form.get("amount", type=float, default=0.0)
        description = request.form.get("description", "").strip()

        if not account_id or amount <= 0:
            flash("Please choose an account and enter a positive withdrawal amount.", "danger")
            return render_template("withdrawal.html", accounts=accounts, preselected_acc=account_id)

        result = withdrawal_transaction(account_id, amount, description)
        if result["success"]:
            flash(result["message"], "success")
            return redirect(url_for("account_detail", account_id=account_id))
        else:
            flash(result["message"], "danger")

    return render_template("withdrawal.html", accounts=accounts, preselected_acc=preselected_acc)

@app.route("/transfer", methods=["GET", "POST"])
def transfer():
    preselected_src = request.args.get("src_id", type=int)
    accounts = []
    is_connected, _ = test_connection()
    if is_connected:
        try:
            accounts = execute_query("""
                SELECT a.AccountID, a.AccountNumber, a.AccountType, a.Balance, b.BranchName,
                       CONCAT(c.FirstName, ' ', c.LastName) AS PrimaryHolder
                FROM ACCOUNT a
                JOIN BRANCH b ON a.BranchID = b.BranchID
                LEFT JOIN ACCOUNT_HOLDER ah ON a.AccountID = ah.AccountID AND ah.HolderType = 'Primary'
                LEFT JOIN CUSTOMER c ON ah.CustomerID = c.CustomerID
                WHERE a.Status = 'Active'
                ORDER BY a.AccountNumber
            """, fetchall=True) or []
        except mysql.connector.Error:
            pass

    if request.method == "POST":
        src_id = request.form.get("src_account_id", type=int)
        dest_id = request.form.get("dest_account_id", type=int)
        amount = request.form.get("amount", type=float, default=0.0)
        description = request.form.get("description", "").strip()

        if not src_id or not dest_id:
            flash("Please select both source and destination accounts.", "danger")
            return render_template("transfer.html", accounts=accounts, preselected_src=src_id)

        if src_id == dest_id:
            flash("Source and destination accounts must be different.", "warning")
            return render_template("transfer.html", accounts=accounts, preselected_src=src_id)

        if amount <= 0:
            flash("Transfer amount must be strictly greater than zero.", "danger")
            return render_template("transfer.html", accounts=accounts, preselected_src=src_id)

        result = transfer_transaction(src_id, dest_id, amount, description)
        if result["success"]:
            flash(result["message"], "success")
            return redirect(url_for("transactions"))
        else:
            flash(result["message"], "danger")

    return render_template("transfer.html", accounts=accounts, preselected_src=preselected_src)

# ----------------------------------------------------------------------------
# 5. TRANSACTION HISTORY ROUTE
# ----------------------------------------------------------------------------
@app.route("/transactions")
def transactions():
    tx_type = request.args.get("type", "").strip()
    status = request.args.get("status", "").strip()
    search = request.args.get("search", "").strip()

    is_connected, _ = test_connection()
    if not is_connected:
        flash("MySQL database is not connected. Displaying offline mode.", "warning")
        return render_template("transactions.html", transactions=[], tx_type=tx_type, status=status, search=search)

    try:
        query = """
            SELECT 
                t.TransactionID,
                t.ReferenceNumber,
                t.TransactionType,
                t.Amount,
                t.TransactionDate,
                t.TransactionStatus,
                t.Description,
                a.AccountNumber,
                a.AccountType,
                b.BranchName
            FROM BANK_TRANSACTION t
            JOIN ACCOUNT a ON t.AccountID = a.AccountID
            JOIN BRANCH b ON a.BranchID = b.BranchID
            WHERE 1=1
        """
        params = []
        if tx_type:
            query += " AND t.TransactionType = %s"
            params.append(tx_type)
        if status:
            query += " AND t.TransactionStatus = %s"
            params.append(status)
        if search:
            query += " AND (t.ReferenceNumber LIKE %s OR a.AccountNumber LIKE %s OR t.Description LIKE %s)"
            wildcard = f"%{search}%"
            params.extend([wildcard, wildcard, wildcard])

        query += " ORDER BY t.TransactionDate DESC, t.TransactionID DESC LIMIT 100"
        tx_list = execute_query(query, params, fetchall=True)
        return render_template("transactions.html", transactions=tx_list, tx_type=tx_type, status=status, search=search)
    except mysql.connector.Error as e:
        flash(f"Database error: {e.msg}", "danger")
        return render_template("transactions.html", transactions=[], tx_type=tx_type, status=status, search=search)

# ----------------------------------------------------------------------------
# 6. BRANCH MANAGEMENT ROUTES
# ----------------------------------------------------------------------------
@app.route("/branches")
def branch_list():
    is_connected, _ = test_connection()
    if not is_connected:
        flash("MySQL database is not connected. Displaying offline mode.", "warning")
        return render_template("branches.html", branches=[])

    try:
        branches = execute_query("""
            SELECT 
                b.*,
                COUNT(DISTINCT a.AccountID) AS TotalAccounts,
                COALESCE(SUM(a.Balance), 0.00) AS TotalDeposits,
                COUNT(DISTINCT e.EmployeeID) AS TotalEmployees
            FROM BRANCH b
            LEFT JOIN ACCOUNT a ON b.BranchID = a.BranchID AND a.Status = 'Active'
            LEFT JOIN EMPLOYEE e ON b.BranchID = e.BranchID
            GROUP BY b.BranchID
            ORDER BY b.BranchID
        """, fetchall=True)
        return render_template("branches.html", branches=branches)
    except mysql.connector.Error as e:
        flash(f"Database error: {e.msg}", "danger")
        return render_template("branches.html", branches=[])

@app.route("/branches/create", methods=["GET", "POST"])
def branch_create():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        ifsc = request.form.get("ifsc", "").strip().upper()
        address = request.form.get("address", "").strip()
        city = request.form.get("city", "").strip()
        state = request.form.get("state", "").strip()
        contact = request.form.get("contact", "").strip()

        errors = []
        if not name or not ifsc or not address or not city or not state or not contact:
            errors.append("All branch fields are required.")
        if len(ifsc) < 8:
            errors.append("IFSC code must be at least 8 characters long.")

        if errors:
            for err in errors:
                flash(err, "danger")
            return render_template("branch_form.html", form_data=request.form)

        is_connected, _ = test_connection()
        if not is_connected:
            flash("Cannot create branch: MySQL database is disconnected.", "danger")
            return render_template("branch_form.html", form_data=request.form)

        try:
            existing = execute_query("SELECT BranchID FROM BRANCH WHERE IFSCCode = %s", (ifsc,), fetchone=True)
            if existing:
                flash(f"A branch with IFSC code {ifsc} already exists.", "warning")
                return render_template("branch_form.html", form_data=request.form)

            sql = """
                INSERT INTO BRANCH (BranchName, IFSCCode, Address, City, State, ContactNumber)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            res = execute_query(sql, (name, ifsc, address, city, state, contact), commit=True)
            flash(f"Branch '{name}' created successfully with ID #{res['lastrowid']}!", "success")
            return redirect(url_for("branch_list"))
        except mysql.connector.Error as e:
            flash(f"Database error creating branch: {e.msg}", "danger")

    return render_template("branch_form.html", form_data={})

# ----------------------------------------------------------------------------
# 7. EMPLOYEE MANAGEMENT ROUTES
# ----------------------------------------------------------------------------
@app.route("/employees")
def employee_list():
    is_connected, _ = test_connection()
    if not is_connected:
        flash("MySQL database is not connected. Displaying offline mode.", "warning")
        return render_template("employees.html", employees=[])

    try:
        employees = execute_query("""
            SELECT e.*, b.BranchName, b.City AS BranchCity
            FROM EMPLOYEE e
            JOIN BRANCH b ON e.BranchID = b.BranchID
            ORDER BY e.EmployeeID DESC
        """, fetchall=True)
        return render_template("employees.html", employees=employees)
    except mysql.connector.Error as e:
        flash(f"Database error: {e.msg}", "danger")
        return render_template("employees.html", employees=[])

@app.route("/employees/create", methods=["GET", "POST"])
def employee_create():
    branches = []
    is_connected, _ = test_connection()
    if is_connected:
        try:
            branches = execute_query("SELECT BranchID, BranchName, City FROM BRANCH ORDER BY BranchName", fetchall=True) or []
        except mysql.connector.Error:
            pass

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        mobile = request.form.get("mobile", "").strip()
        email = request.form.get("email", "").strip()
        designation = request.form.get("designation", "").strip()
        salary = request.form.get("salary", type=float, default=0.0)
        joining_date = request.form.get("joining_date", "").strip()
        branch_id = request.form.get("branch_id", type=int)

        errors = []
        if not name or not designation or not joining_date or not branch_id:
            errors.append("Please complete all required fields.")
        if salary <= 0:
            errors.append("Salary must be greater than zero.")
        if not re.match(r"^[0-9]{10}$", mobile):
            errors.append("Mobile number must be 10 digits.")

        if errors:
            for err in errors:
                flash(err, "danger")
            return render_template("employee_form.html", branches=branches, form_data=request.form)

        if not is_connected:
            flash("Cannot register employee: MySQL database is disconnected.", "danger")
            return render_template("employee_form.html", branches=branches, form_data=request.form)

        try:
            sql = """
                INSERT INTO EMPLOYEE (EmployeeName, Mobile, Email, Designation, Salary, JoiningDate, BranchID)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            res = execute_query(sql, (name, mobile, email, designation, salary, joining_date, branch_id), commit=True)
            flash(f"Employee {name} registered successfully with ID #{res['lastrowid']}!", "success")
            return redirect(url_for("employee_list"))
        except mysql.connector.Error as e:
            flash(f"Database error registering employee: {e.msg}", "danger")

    return render_template("employee_form.html", branches=branches, form_data={})

# ----------------------------------------------------------------------------
# 8. LOAN & LOAN PAYMENT MANAGEMENT
# ----------------------------------------------------------------------------
@app.route("/loans")
def loan_list():
    is_connected, _ = test_connection()
    if not is_connected:
        flash("MySQL database is not connected. Displaying offline mode.", "warning")
        return render_template("loans.html", loans=[])

    try:
        loans = execute_query("""
            SELECT 
                l.*,
                CONCAT(c.FirstName, ' ', c.LastName) AS BorrowerName,
                c.Mobile AS BorrowerMobile,
                b.BranchName,
                COALESCE(SUM(lp.Amount), 0.00) AS TotalPaid,
                (l.LoanAmount - COALESCE(SUM(lp.Amount), 0.00)) AS OutstandingBalance
            FROM LOAN l
            JOIN CUSTOMER c ON l.CustomerID = c.CustomerID
            JOIN BRANCH b ON l.BranchID = b.BranchID
            LEFT JOIN LOAN_PAYMENT lp ON l.LoanID = lp.LoanID
            GROUP BY l.LoanID
            ORDER BY l.LoanID DESC
        """, fetchall=True)
        return render_template("loans.html", loans=loans)
    except mysql.connector.Error as e:
        flash(f"Database error: {e.msg}", "danger")
        return render_template("loans.html", loans=[])

@app.route("/loans/create", methods=["GET", "POST"])
def loan_create():
    customers = []
    branches = []
    is_connected, _ = test_connection()
    if is_connected:
        try:
            customers = execute_query("SELECT CustomerID, FirstName, LastName, Mobile FROM CUSTOMER ORDER BY FirstName", fetchall=True) or []
            branches = execute_query("SELECT BranchID, BranchName FROM BRANCH ORDER BY BranchName", fetchall=True) or []
        except mysql.connector.Error:
            pass

    if request.method == "POST":
        customer_id = request.form.get("customer_id", type=int)
        branch_id = request.form.get("branch_id", type=int)
        loan_type = request.form.get("loan_type", "").strip()
        amount = request.form.get("amount", type=float, default=0.0)
        rate = request.form.get("rate", type=float, default=0.0)
        start_date = request.form.get("start_date", "").strip()
        tenure = request.form.get("tenure", type=int, default=0)

        errors = []
        if not customer_id or not branch_id:
            errors.append("Customer and Branch are required.")
        if loan_type not in ["Home Loan", "Education Loan", "Personal Loan", "Vehicle Loan"]:
            errors.append("Invalid loan type.")
        if amount <= 0:
            errors.append("Loan amount must be strictly positive.")
        if rate < 0:
            errors.append("Interest rate cannot be negative.")
        if tenure <= 0:
            errors.append("Tenure must be at least 1 month.")

        if errors:
            for err in errors:
                flash(err, "danger")
            return render_template("loan_form.html", customers=customers, branches=branches, form_data=request.form)

        if not is_connected:
            flash("Cannot sanction loan: MySQL database is disconnected.", "danger")
            return render_template("loan_form.html", customers=customers, branches=branches, form_data=request.form)

        try:
            sql = """
                INSERT INTO LOAN (CustomerID, BranchID, LoanType, LoanAmount, InterestRate, StartDate, TenureMonths, LoanStatus)
                VALUES (%s, %s, %s, %s, %s, %s, %s, 'Active')
            """
            res = execute_query(sql, (customer_id, branch_id, loan_type, amount, rate, start_date, tenure), commit=True)
            flash(f"Loan #{res['lastrowid']} sanctioned and activated successfully!", "success")
            return redirect(url_for("loan_list"))
        except mysql.connector.Error as e:
            flash(f"Database error creating loan: {e.msg}", "danger")

    return render_template("loan_form.html", customers=customers, branches=branches, form_data={})

@app.route("/loans/<int:loan_id>/payments", methods=["GET", "POST"])
def loan_payments(loan_id):
    is_connected, _ = test_connection()
    if not is_connected:
        flash("MySQL database is not connected.", "warning")
        return redirect(url_for("loan_list"))

    try:
        loan = execute_query("""
            SELECT l.*, CONCAT(c.FirstName, ' ', c.LastName) AS BorrowerName, b.BranchName
            FROM LOAN l
            JOIN CUSTOMER c ON l.CustomerID = c.CustomerID
            JOIN BRANCH b ON l.BranchID = b.BranchID
            WHERE l.LoanID = %s
        """, (loan_id,), fetchone=True)

        if not loan:
            flash("Loan not found.", "warning")
            return redirect(url_for("loan_list"))

        if request.method == "POST":
            amount = request.form.get("amount", type=float, default=0.0)
            mode = request.form.get("payment_mode", "Online").strip()

            if amount <= 0:
                flash("Repayment amount must be positive.", "danger")
            else:
                result = record_loan_payment_transaction(loan_id, amount, mode)
                if result["success"]:
                    flash(result["message"], "success")
                else:
                    flash(result["message"], "danger")
                return redirect(url_for("loan_payments", loan_id=loan_id))

        payments = execute_query("SELECT * FROM LOAN_PAYMENT WHERE LoanID = %s ORDER BY PaymentDate DESC", (loan_id,), fetchall=True)
        total_paid = sum(float(p["Amount"]) for p in payments)
        outstanding = max(0.0, float(loan["LoanAmount"]) - total_paid)

        return render_template("loan_payments.html", loan=loan, payments=payments, total_paid=total_paid, outstanding=outstanding)
    except mysql.connector.Error as e:
        flash(f"Database error: {e.msg}", "danger")
        return redirect(url_for("loan_list"))

# ----------------------------------------------------------------------------
# 9. LIVE SQL BUSINESS QUERIES RUNNER
# ----------------------------------------------------------------------------
BUSINESS_QUERIES = [
    {
        "id": 1,
        "title": "All Customers with Linked Bank Accounts",
        "description": "Customer 360-degree overview showing customer contact details, accounts, types, balances, and branch names.",
        "concepts": "Multi-table INNER JOIN, String Concatenation, Aliasing",
        "sql": """SELECT 
    c.CustomerID,
    CONCAT(c.FirstName, ' ', c.LastName) AS FullName,
    c.Email,
    a.AccountNumber,
    a.AccountType,
    a.Balance,
    b.BranchName
FROM CUSTOMER c
JOIN ACCOUNT_HOLDER ah ON c.CustomerID = ah.CustomerID
JOIN ACCOUNT a ON ah.AccountID = a.AccountID
JOIN BRANCH b ON a.BranchID = b.BranchID
ORDER BY c.CustomerID, a.AccountNumber;"""
    },
    {
        "id": 2,
        "title": "Customers Holding Multiple Accounts",
        "description": "Identifies high-engagement customers who own more than one bank account.",
        "concepts": "GROUP BY, HAVING COUNT(*) > 1, Aggregation",
        "sql": """SELECT 
    c.CustomerID,
    CONCAT(c.FirstName, ' ', c.LastName) AS FullName,
    c.Mobile,
    COUNT(ah.AccountID) AS TotalAccountsOwned
FROM CUSTOMER c
JOIN ACCOUNT_HOLDER ah ON c.CustomerID = ah.CustomerID
GROUP BY c.CustomerID, c.FirstName, c.LastName, c.Mobile
HAVING COUNT(ah.AccountID) > 1
ORDER BY TotalAccountsOwned DESC;"""
    },
    {
        "id": 3,
        "title": "Accounts with Branch Details & Branch Managers",
        "description": "Lists all bank accounts along with branch details and designated branch managers.",
        "concepts": "Multi-table JOIN, Conditional Left Join on Designation",
        "sql": """SELECT 
    a.AccountNumber,
    a.AccountType,
    a.Balance,
    a.Status,
    b.BranchName,
    b.City AS BranchCity,
    e.EmployeeName AS BranchManager
FROM ACCOUNT a
JOIN BRANCH b ON a.BranchID = b.BranchID
LEFT JOIN EMPLOYEE e ON b.BranchID = e.BranchID AND e.Designation = 'Branch Manager'
ORDER BY b.BranchName, a.AccountNumber;"""
    },
    {
        "id": 4,
        "title": "Total Deposits & Average Balance Per Branch",
        "description": "Evaluates branch financial health, customer balance distribution, and active accounts count.",
        "concepts": "GROUP BY, Aggregate Functions (SUM, AVG, COUNT), COALESCE",
        "sql": """SELECT 
    b.BranchID,
    b.BranchName,
    COUNT(a.AccountID) AS ActiveAccountsCount,
    COALESCE(SUM(a.Balance), 0.00) AS TotalDeposits,
    COALESCE(ROUND(AVG(a.Balance), 2), 0.00) AS AverageBalance
FROM BRANCH b
LEFT JOIN ACCOUNT a ON b.BranchID = a.BranchID AND a.Status = 'Active'
GROUP BY b.BranchID, b.BranchName
ORDER BY TotalDeposits DESC;"""
    },
    {
        "id": 5,
        "title": "High-Net-Worth Accounts (Above Bank Average)",
        "description": "Filters accounts having a balance strictly greater than the overall system average balance.",
        "concepts": "Scalar Subquery, Comparison against Nested Aggregation",
        "sql": """SELECT 
    a.AccountNumber,
    a.AccountType,
    a.Balance,
    a.Status,
    b.BranchName
FROM ACCOUNT a
JOIN BRANCH b ON a.BranchID = b.BranchID
WHERE a.Balance > (
    SELECT AVG(Balance) FROM ACCOUNT WHERE Status = 'Active'
)
ORDER BY a.Balance DESC;"""
    },
    {
        "id": 6,
        "title": "Cash Flow Summary by Account (Inflows vs Outflows)",
        "description": "Profiles transaction volume per account: total money deposited/transferred-in vs withdrawn/transferred-out.",
        "concepts": "Conditional Aggregation (SUM CASE), LEFT JOIN, GROUP BY",
        "sql": """SELECT 
    a.AccountNumber,
    a.AccountType,
    COALESCE(SUM(CASE WHEN t.TransactionType IN ('DEPOSIT', 'TRANSFER_IN') THEN t.Amount ELSE 0 END), 0.00) AS TotalInflow,
    COALESCE(SUM(CASE WHEN t.TransactionType IN ('WITHDRAWAL', 'TRANSFER_OUT') THEN t.Amount ELSE 0 END), 0.00) AS TotalOutflow,
    COALESCE(SUM(CASE WHEN t.TransactionType IN ('DEPOSIT', 'TRANSFER_IN') THEN t.Amount ELSE -t.Amount END), 0.00) AS NetTransactionVolume
FROM ACCOUNT a
LEFT JOIN BANK_TRANSACTION t ON a.AccountID = t.AccountID AND t.TransactionStatus = 'SUCCESS'
GROUP BY a.AccountID, a.AccountNumber, a.AccountType
ORDER BY NetTransactionVolume DESC;"""
    },
    {
        "id": 7,
        "title": "Customer Statement & Passbook Ledger (Customer #1)",
        "description": "Retrieves comprehensive chronological transactions across all accounts belonging to Customer #1.",
        "concepts": "4-Table JOIN (CUSTOMER -> ACCOUNT_HOLDER -> ACCOUNT -> BANK_TRANSACTION)",
        "sql": """SELECT 
    t.TransactionID,
    t.ReferenceNumber,
    t.TransactionDate,
    a.AccountNumber,
    t.TransactionType,
    t.Amount,
    t.Description
FROM BANK_TRANSACTION t
JOIN ACCOUNT a ON t.AccountID = a.AccountID
JOIN ACCOUNT_HOLDER ah ON a.AccountID = ah.AccountID
WHERE ah.CustomerID = 1
ORDER BY t.TransactionDate DESC;"""
    },
    {
        "id": 8,
        "title": "Customers Without Any Bank Accounts",
        "description": "Finds registered customers who have not opened any account yet (dormant lead identification).",
        "concepts": "LEFT JOIN with IS NULL Filter, Set Difference Emulation",
        "sql": """SELECT 
    c.CustomerID,
    CONCAT(c.FirstName, ' ', c.LastName) AS FullName,
    c.Email,
    c.Mobile,
    c.RegistrationDate
FROM CUSTOMER c
LEFT JOIN ACCOUNT_HOLDER ah ON c.CustomerID = ah.CustomerID
WHERE ah.AccountID IS NULL;"""
    },
    {
        "id": 9,
        "title": "Branch Staffing and Payroll Expenditure",
        "description": "Aggregates total staff head-count, total monthly salary expenditure, and average employee salary by branch.",
        "concepts": "GROUP BY, Aggregation (COUNT, SUM, AVG), Rounding",
        "sql": """SELECT 
    b.BranchName,
    b.City,
    COUNT(e.EmployeeID) AS EmployeeCount,
    COALESCE(SUM(e.Salary), 0.00) AS TotalPayrollCost,
    COALESCE(ROUND(AVG(e.Salary), 2), 0.00) AS AverageSalary
FROM BRANCH b
LEFT JOIN EMPLOYEE e ON b.BranchID = e.BranchID
GROUP BY b.BranchID, b.BranchName, b.City
ORDER BY TotalPayrollCost DESC;"""
    },
    {
        "id": 10,
        "title": "Top Account by Balance in Each Branch",
        "description": "Identifies the highest-balance account for each branch using a correlated subquery.",
        "concepts": "Correlated Subquery, Subquery in WHERE clause",
        "sql": """SELECT 
    b.BranchName,
    a.AccountNumber,
    a.AccountType,
    a.Balance
FROM ACCOUNT a
JOIN BRANCH b ON a.BranchID = b.BranchID
WHERE a.Balance = (
    SELECT MAX(sub_a.Balance)
    FROM ACCOUNT sub_a
    WHERE sub_a.BranchID = a.BranchID AND sub_a.Status = 'Active'
)
ORDER BY a.Balance DESC;"""
    },
    {
        "id": 11,
        "title": "Customers Holding Active Loans",
        "description": "Lists borrowers currently servicing an active bank loan, with sanction amount and tenure.",
        "concepts": "Multi-table JOIN with WHERE filter, ORDER BY",
        "sql": """SELECT 
    CONCAT(c.FirstName, ' ', c.LastName) AS CustomerName,
    c.Mobile,
    l.LoanType,
    l.LoanAmount,
    l.InterestRate,
    l.TenureMonths,
    b.BranchName
FROM LOAN l
JOIN CUSTOMER c ON l.CustomerID = c.CustomerID
JOIN BRANCH b ON l.BranchID = b.BranchID
WHERE l.LoanStatus = 'Active'
ORDER BY l.LoanAmount DESC;"""
    },
    {
        "id": 12,
        "title": "Loan Portfolio Breakdown by Category",
        "description": "Aggregates loan sanctions, exposure volume, and average interest rate across loan categories.",
        "concepts": "GROUP BY, Aggregate Functions (COUNT, SUM, AVG)",
        "sql": """SELECT 
    LoanType,
    COUNT(LoanID) AS TotalLoansCount,
    SUM(LoanAmount) AS TotalSanctionedAmount,
    ROUND(AVG(InterestRate), 2) AS AverageInterestRate
FROM LOAN
GROUP BY LoanType
ORDER BY TotalSanctionedAmount DESC;"""
    },
    {
        "id": 13,
        "title": "Loan Repayment Progress (Sanctioned vs Repaid vs Outstanding)",
        "description": "Tracks loan recovery, total principal repaid, and outstanding debt for credit monitoring.",
        "concepts": "LEFT JOIN Aggregation, Arithmetic Computation across Tables",
        "sql": """SELECT 
    l.LoanID,
    CONCAT(c.FirstName, ' ', c.LastName) AS BorrowerName,
    l.LoanType,
    l.LoanAmount AS SanctionedAmount,
    COALESCE(SUM(lp.Amount), 0.00) AS TotalRepaid,
    (l.LoanAmount - COALESCE(SUM(lp.Amount), 0.00)) AS OutstandingBalance
FROM LOAN l
JOIN CUSTOMER c ON l.CustomerID = c.CustomerID
LEFT JOIN LOAN_PAYMENT lp ON l.LoanID = lp.LoanID
GROUP BY l.LoanID, c.FirstName, c.LastName, l.LoanType, l.LoanAmount
ORDER BY OutstandingBalance DESC;"""
    },
    {
        "id": 14,
        "title": "Inactive and Zero-Balance Accounts Audit",
        "description": "Identifies accounts flagged as Inactive, Closed, or holding zero balance for compliance review.",
        "concepts": "Boolean Logic (OR, IN), Multi-condition Filter",
        "sql": """SELECT 
    a.AccountNumber,
    a.AccountType,
    a.Balance,
    a.Status,
    b.BranchName,
    a.OpeningDate
FROM ACCOUNT a
JOIN BRANCH b ON a.BranchID = b.BranchID
WHERE a.Status IN ('Inactive', 'Closed') OR a.Balance = 0.00
ORDER BY a.Balance ASC, a.OpeningDate DESC;"""
    },
    {
        "id": 15,
        "title": "Inter-Account Transfer Audit with Matching Counterparts",
        "description": "Reconciles fund transfers by pairing TRANSFER_OUT and TRANSFER_IN entries sharing the same ReferenceNumber.",
        "concepts": "Self-Join on Ledger Table, Paired Transaction Reconciliation",
        "sql": """SELECT 
    t_out.ReferenceNumber,
    t_out.TransactionDate AS TransferDate,
    acc_from.AccountNumber AS SenderAccount,
    acc_to.AccountNumber AS ReceiverAccount,
    t_out.Amount AS TransferredAmount
FROM BANK_TRANSACTION t_out
JOIN BANK_TRANSACTION t_in ON t_out.ReferenceNumber = t_in.ReferenceNumber
JOIN ACCOUNT acc_from ON t_out.AccountID = acc_from.AccountID
JOIN ACCOUNT acc_to ON t_in.AccountID = acc_to.AccountID
WHERE t_out.TransactionType = 'TRANSFER_OUT' 
  AND t_in.TransactionType = 'TRANSFER_IN'
ORDER BY t_out.TransactionDate DESC;"""
    }
]

@app.route("/business-queries")
def business_queries():
    query_id = request.args.get("query_id", type=int, default=1)
    selected_query = next((q for q in BUSINESS_QUERIES if q["id"] == query_id), BUSINESS_QUERIES[0])

    results = []
    columns = []
    error_msg = None

    is_connected, _ = test_connection()
    if is_connected:
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute(selected_query["sql"])
            results = cursor.fetchall()
            if results:
                columns = list(results[0].keys())
            cursor.close()
            conn.close()
        except mysql.connector.Error as e:
            error_msg = f"SQL Execution Error: {e.msg}"
    else:
        error_msg = "Database not currently connected. Please configure your MySQL credentials in .env to run live queries."

    return render_template(
        "business_queries.html",
        queries=BUSINESS_QUERIES,
        selected_query=selected_query,
        results=results,
        columns=columns,
        error_msg=error_msg
    )

# ----------------------------------------------------------------------------
# ERROR HANDLERS
# ----------------------------------------------------------------------------
@app.errorhandler(404)
def not_found_error(error):
    return render_template("404.html"), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template("error.html", error_message="Internal server error occurred. Please verify database connectivity."), 500

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
