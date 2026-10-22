import re
import secrets
import uuid
from decimal import Decimal, InvalidOperation
from datetime import datetime, date

from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    current_app,
)
from flask_wtf.csrf import CSRFError, CSRFProtect

from config import Config
from db import (
    check_connection,
    query_all,
    query_one,
    execute,
    transaction,
)


app = Flask(__name__)
app.config.from_object(Config)
csrf = CSRFProtect(app)


@app.template_filter('currency')
def currency_filter(value):
    try:
        amount = Decimal(str(value if value is not None else 0)).quantize(Decimal("0.01"))
        return f"₹{amount:,.2f}"
    except Exception:
        return f"₹{value}"


@app.template_filter('datetime')
def datetime_filter(value):
    if value is None:
        return "-"
    if isinstance(value, str):
        return value
    try:
        return value.strftime("%Y-%m-%d %H:%M")
    except Exception:
        return str(value)


@app.context_processor
def inject_now():
    return {"current_year": datetime.now().year}


EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
MOBILE_PATTERN = re.compile(r"^[0-9]{10,15}$")
IFSC_PATTERN = re.compile(r"^[A-Z]{4}0[0-9]{6}$")
MONEY_LIMIT = Decimal("9999999999999.99")


def parse_money(raw_value, label="Amount", allow_zero=False):
    if raw_value is None or str(raw_value).strip() == "":
        raise ValueError(f"{label} is required.")
    try:
        value = Decimal(str(raw_value).strip())
    except (InvalidOperation, ValueError):
        raise ValueError(f"{label} must be a valid number.")
    if not value.is_finite():
        raise ValueError(f"{label} must be a finite number.")
    if value < 0 or (value == 0 and not allow_zero):
        raise ValueError(f"{label} must be greater than zero.")
    if value.as_tuple().exponent < -2:
        raise ValueError(f"{label} can have at most two decimal places.")
    if value > MONEY_LIMIT:
        raise ValueError(f"{label} is too large.")
    return value.quantize(Decimal("0.01"))


def parse_date_value(raw_value, label="Date", allow_future=False):
    if raw_value is None or str(raw_value).strip() == "":
        raise ValueError(f"{label} is required.")
    try:
        value = date.fromisoformat(str(raw_value).strip())
    except ValueError:
        raise ValueError(f"{label} must use the YYYY-MM-DD format.")
    if value < date(1900, 1, 1):
        raise ValueError(f"{label} is not valid.")
    if not allow_future and value > date.today():
        raise ValueError(f"{label} cannot be in the future.")
    return value


def parse_record_id(raw_value, label="Record"):
    if raw_value is None or not str(raw_value).strip().isdigit():
        raise ValueError(f"Please select a valid {label.lower()}.")
    return int(str(raw_value).strip())


@app.route("/")
def index():
    try:
        total_customers = query_one("SELECT COUNT(*) AS cnt FROM CUSTOMER")["cnt"]
        total_accounts = query_one("SELECT COUNT(*) AS cnt FROM ACCOUNT")["cnt"]
        total_branches = query_one("SELECT COUNT(*) AS cnt FROM BRANCH")["cnt"]
        active_accounts = query_one("SELECT COUNT(*) AS cnt FROM ACCOUNT WHERE Status = 'Active'")["cnt"]
        total_transactions = query_one("SELECT COUNT(*) AS cnt FROM BANK_TRANSACTION")["cnt"]
        total_loans = query_one("SELECT COUNT(*) AS cnt FROM LOAN")["cnt"]
        total_balance = query_one("SELECT COALESCE(SUM(Balance), 0) AS total FROM ACCOUNT WHERE Status = 'Active'")["total"]
        recent_transactions = query_all(
            """
            SELECT t.TransactionID, t.AccountID, a.AccountNumber, t.TransactionType, t.Amount, t.TransactionDate, t.ReferenceNumber, t.TransactionStatus
            FROM BANK_TRANSACTION t
            JOIN ACCOUNT a ON a.AccountID = t.AccountID
            ORDER BY t.TransactionDate DESC, t.TransactionID DESC
            LIMIT 10
            """
        )
        branch_summary = query_all("SELECT * FROM vw_branch_summary ORDER BY BranchID")
    except Exception:
        current_app.logger.exception("Dashboard database query failed")
        return render_template("error.html", error_message="The dashboard could not load data from MySQL. Check the database connection."), 500

    return render_template(
        "index.html",
        total_customers=total_customers,
        total_accounts=total_accounts,
        total_branches=total_branches,
        active_accounts=active_accounts,
        total_transactions=total_transactions,
        total_loans=total_loans,
        total_balance=total_balance,
        recent_transactions=recent_transactions,
        branch_summary=branch_summary,
    )


@app.route("/health")
def health():
    try:
        check_connection()
        return {"status": "ok", "database": app.config["DB_NAME"]}
    except Exception:
        current_app.logger.exception("Database health check failed")
        return {"status": "error", "message": "Database connection unavailable."}, 500


# Customer management
@app.route("/customers")
def customers():
    search = request.args.get("q", "").strip()
    if search:
        rows = query_all(
            """
            SELECT c.*, 
                   (SELECT COUNT(*) FROM ACCOUNT_HOLDER ah WHERE ah.CustomerID = c.CustomerID) AS account_count,
                   (SELECT COUNT(*) FROM LOAN l WHERE l.CustomerID = c.CustomerID) AS loan_count
            FROM CUSTOMER c
            WHERE c.FirstName LIKE %s OR c.LastName LIKE %s OR c.Mobile LIKE %s OR c.Email LIKE %s
            ORDER BY c.CustomerID
            """,
            (f"%{search}%", f"%{search}%", f"%{search}%", f"%{search}%"),
        )
    else:
        rows = query_all(
            """
            SELECT c.*, 
                   (SELECT COUNT(*) FROM ACCOUNT_HOLDER ah WHERE ah.CustomerID = c.CustomerID) AS account_count,
                   (SELECT COUNT(*) FROM LOAN l WHERE l.CustomerID = c.CustomerID) AS loan_count
            FROM CUSTOMER c
            ORDER BY c.CustomerID
            """
        )
    return render_template("customers.html", customers=rows, search=search)


@app.route("/customers/new", methods=["GET", "POST"])
def customer_new():
    if request.method == "POST":
        first_name = request.form.get("FirstName", "").strip()
        last_name = request.form.get("LastName", "").strip()
        dob = request.form.get("DateOfBirth", "").strip()
        gender = request.form.get("Gender", "").strip()
        mobile = request.form.get("Mobile", "").strip()
        email = request.form.get("Email", "").strip().lower()
        address = request.form.get("Address", "").strip()
        city = request.form.get("City", "").strip()

        try:
            if not all([first_name, last_name, dob, gender, mobile, email, address, city]):
                raise ValueError("All fields are required.")
            if len(first_name) > 60 or len(last_name) > 60:
                raise ValueError("First name and last name must be 60 characters or fewer.")
            if gender not in ("Male", "Female", "Other"):
                raise ValueError("Select a valid gender.")
            if not MOBILE_PATTERN.fullmatch(mobile):
                raise ValueError("Mobile must contain 10 to 15 digits.")
            if not EMAIL_PATTERN.fullmatch(email) or len(email) > 120:
                raise ValueError("Enter a valid email address.")
            parse_date_value(dob, "Date of birth")
            if len(address) > 255 or len(city) > 80:
                raise ValueError("Address or city is too long.")
            execute(
                """
                INSERT INTO CUSTOMER (FirstName, LastName, DateOfBirth, Gender, Mobile, Email, Address, City)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (first_name, last_name, dob, gender, mobile, email, address, city),
            )
            flash("Customer registered successfully.", "success")
            return redirect(url_for("customers"))
        except ValueError as exc:
            flash(str(exc), "danger")
            return render_template("customer_form.html")
        except Exception as exc:
            if "uq_customer_mobile" in str(exc):
                flash("Mobile number already exists.", "danger")
            elif "uq_customer_email" in str(exc):
                flash("Email address already exists.", "danger")
            elif "CHECK" in str(exc).upper():
                flash("Validation error: check the entered values.", "danger")
            else:
                current_app.logger.exception("Customer registration failed")
                flash("Could not register customer. Ensure values are valid.", "danger")
            return render_template("customer_form.html")

    return render_template("customer_form.html")


@app.route("/customers/<int:customer_id>")
def customer_detail(customer_id):
    customer = query_one("SELECT * FROM CUSTOMER WHERE CustomerID = %s", (customer_id,))
    if not customer:
        return render_template("404.html", message="Customer not found"), 404
    accounts = query_all(
        """
        SELECT a.*, ah.HolderType, ah.HolderSince, b.BranchName
        FROM ACCOUNT_HOLDER ah
        JOIN ACCOUNT a ON a.AccountID = ah.AccountID
        JOIN BRANCH b ON b.BranchID = a.BranchID
        WHERE ah.CustomerID = %s
        ORDER BY a.AccountID
        """,
        (customer_id,),
    )
    loans = query_all("SELECT * FROM LOAN WHERE CustomerID = %s ORDER BY LoanID", (customer_id,))
    transactions = query_all(
        """
        SELECT t.*, a.AccountNumber
        FROM BANK_TRANSACTION t
        JOIN ACCOUNT a ON a.AccountID = t.AccountID
        JOIN ACCOUNT_HOLDER ah ON ah.AccountID = a.AccountID
        WHERE ah.CustomerID = %s
        ORDER BY t.TransactionDate DESC, t.TransactionID DESC
        LIMIT 50
        """,
        (customer_id,),
    )
    return render_template("customer_detail.html", customer=customer, accounts=accounts, loans=loans, transactions=transactions)


# Account management
@app.route("/accounts")
def accounts():
    search = request.args.get("q", "").strip()
    if search:
        rows = query_all(
            """
            SELECT a.*, b.BranchName, b.IFSCCode,
                   (SELECT GROUP_CONCAT(CONCAT(c.FirstName, ' ', c.LastName) SEPARATOR ', ')
                      FROM ACCOUNT_HOLDER ah JOIN CUSTOMER c ON c.CustomerID = ah.CustomerID
                     WHERE ah.AccountID = a.AccountID) AS Holders
            FROM ACCOUNT a
            JOIN BRANCH b ON b.BranchID = a.BranchID
            WHERE a.AccountNumber LIKE %s OR b.BranchName LIKE %s
            ORDER BY a.AccountID
            """,
            (f"%{search}%", f"%{search}%"),
        )
    else:
        rows = query_all(
            """
            SELECT a.*, b.BranchName, b.IFSCCode,
                   (SELECT GROUP_CONCAT(CONCAT(c.FirstName, ' ', c.LastName) SEPARATOR ', ')
                      FROM ACCOUNT_HOLDER ah JOIN CUSTOMER c ON c.CustomerID = ah.CustomerID
                     WHERE ah.AccountID = a.AccountID) AS Holders
            FROM ACCOUNT a
            JOIN BRANCH b ON b.BranchID = a.BranchID
            ORDER BY a.AccountID
            """
        )
    return render_template("accounts.html", accounts=rows, search=search)


@app.route("/accounts/open", methods=["GET", "POST"])
def account_open():
    if request.method == "POST":
        customer_id = request.form.get("CustomerID")
        account_type = request.form.get("AccountType")
        branch_id = request.form.get("BranchID")
        initial_deposit = request.form.get("InitialDeposit", "0").strip()
        holder_type = request.form.get("HolderType", "Primary")

        try:
            customer_id = parse_record_id(customer_id, "Customer")
            branch_id = parse_record_id(branch_id, "Branch")
            if account_type not in ("Saving", "Current", "Salary"):
                raise ValueError("Select a valid account type.")
            if holder_type not in ("Primary", "Joint"):
                raise ValueError("Select a valid holder type.")
            initial_deposit_decimal = parse_money(initial_deposit or "0", "Initial deposit", allow_zero=True)
        except ValueError as exc:
            flash(str(exc), "danger")
            return redirect(url_for("account_open"))

        account_number = str(secrets.randbelow(900_000_000_000) + 100_000_000_000)

        try:
            with transaction() as (conn, cur):
                cur.execute(
                    """
                    INSERT INTO ACCOUNT (AccountNumber, AccountType, Balance, Status, BranchID)
                    VALUES (%s, %s, %s, 'Active', %s)
                    """,
                    (account_number, account_type, str(initial_deposit_decimal), branch_id),
                )
                account_id = cur.lastrowid

                cur.execute(
                    """
                    INSERT INTO ACCOUNT_HOLDER (CustomerID, AccountID, HolderType)
                    VALUES (%s, %s, %s)
                    """,
                    (customer_id, account_id, holder_type),
                )

                if initial_deposit_decimal > 0:
                    ref = f"OPEN-{account_number}-{uuid.uuid4().hex[:10].upper()}"
                    cur.execute(
                        """
                        INSERT INTO BANK_TRANSACTION (AccountID, TransactionType, Amount, Description, ReferenceNumber, TransactionStatus)
                        VALUES (%s, 'DEPOSIT', %s, 'Initial deposit at account opening', %s, 'SUCCESS')
                        """,
                        (account_id, str(initial_deposit_decimal), ref),
                    )
            flash(f"Account opened successfully. Account Number: {account_number}", "success")
            return redirect(url_for("accounts"))
        except Exception as exc:
            if "uq_account_number" in str(exc):
                flash("Account number generation conflict. Please try again.", "danger")
            elif "FOREIGN KEY" in str(exc):
                flash("Invalid customer or branch selection.", "danger")
            elif "CHK" in str(exc).upper():
                flash("Constraint validation failed while opening the account.", "danger")
            else:
                flash("Could not open account. All operations were rolled back.", "danger")
            return redirect(url_for("account_open"))

    customers = query_all("SELECT CustomerID, FirstName, LastName, Mobile FROM CUSTOMER ORDER BY CustomerID")
    branches = query_all("SELECT BranchID, BranchName, City FROM BRANCH ORDER BY BranchID")
    return render_template("account_form.html", customers=customers, branches=branches)


@app.route("/accounts/<int:account_id>")
def account_detail(account_id):
    account = query_one(
        """
        SELECT a.*, b.BranchName, b.IFSCCode, b.City, b.State
        FROM ACCOUNT a
        JOIN BRANCH b ON b.BranchID = a.BranchID
        WHERE a.AccountID = %s
        """,
        (account_id,),
    )
    if not account:
        return render_template("404.html", message="Account not found"), 404
    holders = query_all(
        """
        SELECT c.*, ah.HolderType, ah.HolderSince
        FROM ACCOUNT_HOLDER ah
        JOIN CUSTOMER c ON c.CustomerID = ah.CustomerID
        WHERE ah.AccountID = %s
        ORDER BY ah.HolderType DESC, c.CustomerID
        """,
        (account_id,),
    )
    transactions = query_all(
        """
        SELECT * FROM BANK_TRANSACTION
        WHERE AccountID = %s
        ORDER BY TransactionDate DESC, TransactionID DESC
        LIMIT 100
        """,
        (account_id,),
    )
    return render_template("account_detail.html", account=account, holders=holders, transactions=transactions)


@app.route("/accounts/<int:account_id>/status", methods=["POST"])
def account_status(account_id):
    new_status = request.form.get("Status", "").strip()
    if new_status not in ("Active", "Inactive", "Closed"):
        flash("Select a valid account status.", "danger")
        return redirect(url_for("account_detail", account_id=account_id))
    try:
        with transaction() as (conn, cur):
            cur.execute("SELECT Status, Balance FROM ACCOUNT WHERE AccountID = %s FOR UPDATE", (account_id,))
            account = cur.fetchone()
            if not account:
                raise ValueError("Account not found.")
            if account["Status"] == "Closed" and new_status != "Closed":
                raise ValueError("A closed account cannot be reopened.")
            if new_status == "Closed" and account["Balance"] != 0:
                raise ValueError("An account can be closed only when its balance is zero.")
            cur.execute("UPDATE ACCOUNT SET Status = %s WHERE AccountID = %s", (new_status, account_id))
        flash("Account status updated successfully.", "success")
    except ValueError as exc:
        flash(str(exc), "danger")
    except Exception:
        current_app.logger.exception("Account status update failed")
        flash("Account status could not be updated because of a database error.", "danger")
    return redirect(url_for("account_detail", account_id=account_id))


# Transactions
@app.route("/deposit", methods=["GET", "POST"])
def deposit():
    if request.method == "POST":
        account_id = request.form.get("AccountID")
        amount = request.form.get("Amount", "").strip()
        description = request.form.get("Description", "Cash deposit").strip() or "Cash deposit"

        try:
            account_id = parse_record_id(account_id, "Account")
            amount_decimal = parse_money(amount, "Deposit amount")
            if len(description) > 255:
                raise ValueError("Description must be 255 characters or fewer.")
        except ValueError as exc:
            flash(str(exc), "danger")
            return redirect(url_for("deposit"))

        try:
            with transaction() as (conn, cur):
                cur.execute("SELECT Balance, Status FROM ACCOUNT WHERE AccountID = %s FOR UPDATE", (account_id,))
                account = cur.fetchone()
                if not account:
                    raise ValueError("Account not found")
                if account["Status"] != "Active":
                    raise ValueError("Cannot deposit into a non-active account")
                new_balance = account["Balance"] + amount_decimal
                cur.execute("UPDATE ACCOUNT SET Balance = %s WHERE AccountID = %s", (str(new_balance), account_id))
                ref = f"DEP-{uuid.uuid4().hex[:12].upper()}"
                cur.execute(
                    """
                    INSERT INTO BANK_TRANSACTION (AccountID, TransactionType, Amount, Description, ReferenceNumber, TransactionStatus)
                    VALUES (%s, 'DEPOSIT', %s, %s, %s, 'SUCCESS')
                    """,
                    (account_id, str(amount_decimal), description, ref),
                )
            flash("Deposit completed successfully.", "success")
            return redirect(url_for("account_detail", account_id=account_id))
        except ValueError as exc:
            flash(f"Deposit failed and was rolled back: {exc}", "danger")
            return redirect(url_for("deposit"))
        except Exception:
            current_app.logger.exception("Deposit failed")
            flash("Deposit failed because of a database error. All changes were rolled back.", "danger")
            return redirect(url_for("deposit"))

    accounts = query_all("SELECT AccountID, AccountNumber, Status FROM ACCOUNT ORDER BY AccountID")
    return render_template("deposit.html", accounts=accounts)


@app.route("/withdraw", methods=["GET", "POST"])
def withdraw():
    if request.method == "POST":
        account_id = request.form.get("AccountID")
        amount = request.form.get("Amount", "").strip()
        description = request.form.get("Description", "Cash withdrawal").strip() or "Cash withdrawal"

        try:
            account_id = parse_record_id(account_id, "Account")
            amount_decimal = parse_money(amount, "Withdrawal amount")
            if len(description) > 255:
                raise ValueError("Description must be 255 characters or fewer.")
        except ValueError as exc:
            flash(str(exc), "danger")
            return redirect(url_for("withdraw"))

        try:
            with transaction() as (conn, cur):
                cur.execute("SELECT Balance, Status FROM ACCOUNT WHERE AccountID = %s FOR UPDATE", (account_id,))
                account = cur.fetchone()
                if not account:
                    raise ValueError("Account not found")
                if account["Status"] != "Active":
                    raise ValueError("Cannot withdraw from a non-active account")
                if account["Balance"] < amount_decimal:
                    raise ValueError("Insufficient balance")
                new_balance = account["Balance"] - amount_decimal
                if new_balance < 0:
                    raise ValueError("Withdrawal would create a negative balance")
                cur.execute("UPDATE ACCOUNT SET Balance = %s WHERE AccountID = %s", (str(new_balance), account_id))
                ref = f"WDR-{uuid.uuid4().hex[:12].upper()}"
                cur.execute(
                    """
                    INSERT INTO BANK_TRANSACTION (AccountID, TransactionType, Amount, Description, ReferenceNumber, TransactionStatus)
                    VALUES (%s, 'WITHDRAWAL', %s, %s, %s, 'SUCCESS')
                    """,
                    (account_id, str(amount_decimal), description, ref),
                )
            flash("Withdrawal completed successfully.", "success")
            return redirect(url_for("account_detail", account_id=account_id))
        except ValueError as exc:
            flash(f"Withdrawal failed and was rolled back: {exc}", "danger")
            return redirect(url_for("withdraw"))
        except Exception:
            current_app.logger.exception("Withdrawal failed")
            flash("Withdrawal failed because of a database error. All changes were rolled back.", "danger")
            return redirect(url_for("withdraw"))

    accounts = query_all("SELECT AccountID, AccountNumber, Status FROM ACCOUNT ORDER BY AccountID")
    return render_template("withdrawal.html", accounts=accounts)


@app.route("/transfer", methods=["GET", "POST"])
def transfer():
    if request.method == "POST":
        from_account_id = request.form.get("FromAccountID")
        to_account_id = request.form.get("ToAccountID")
        amount = request.form.get("Amount", "").strip()
        description = request.form.get("Description", "Fund transfer").strip() or "Fund transfer"

        try:
            from_account_id = parse_record_id(from_account_id, "Source account")
            to_account_id = parse_record_id(to_account_id, "Destination account")
            if from_account_id == to_account_id:
                raise ValueError("Source and destination accounts cannot be the same.")
            amount_decimal = parse_money(amount, "Transfer amount")
            if len(description) > 200:
                raise ValueError("Description must be 200 characters or fewer.")
        except ValueError as exc:
            flash(str(exc), "danger")
            return redirect(url_for("transfer"))

        try:
            with transaction() as (conn, cur):
                ids = sorted([from_account_id, to_account_id])
                cur.execute("SELECT AccountID, Balance, Status FROM ACCOUNT WHERE AccountID IN (%s, %s) FOR UPDATE", (ids[0], ids[1]))
                accounts = {row["AccountID"]: row for row in cur.fetchall()}
                from_acc = accounts.get(from_account_id)
                to_acc = accounts.get(to_account_id)
                if not from_acc or not to_acc:
                    raise ValueError("Invalid source or destination account")
                if from_acc["Status"] != "Active" or to_acc["Status"] != "Active":
                    raise ValueError("Both accounts must be active")
                if from_acc["Balance"] < amount_decimal:
                    raise ValueError("Insufficient balance in source account")
                cur.execute("UPDATE ACCOUNT SET Balance = %s WHERE AccountID = %s", (str(from_acc["Balance"] - amount_decimal), from_account_id))
                cur.execute("UPDATE ACCOUNT SET Balance = %s WHERE AccountID = %s", (str(to_acc["Balance"] + amount_decimal), to_account_id))
                group_ref = f"TRF-{uuid.uuid4().hex[:14].upper()}"
                out_ref = f"{group_ref}-OUT"
                in_ref = f"{group_ref}-IN"
                cur.execute(
                    """
                    INSERT INTO BANK_TRANSACTION (AccountID, TransactionType, Amount, Description, ReferenceNumber, TransferGroupReference, TransactionStatus)
                    VALUES (%s, 'TRANSFER_OUT', %s, %s, %s, %s, 'SUCCESS')
                    """,
                    (from_account_id, str(amount_decimal), f"Transfer to account ID {to_account_id} - {description}", out_ref, group_ref),
                )
                cur.execute(
                    """
                    INSERT INTO BANK_TRANSACTION (AccountID, TransactionType, Amount, Description, ReferenceNumber, TransferGroupReference, TransactionStatus)
                    VALUES (%s, 'TRANSFER_IN', %s, %s, %s, %s, 'SUCCESS')
                    """,
                    (to_account_id, str(amount_decimal), f"Transfer from account ID {from_account_id} - {description}", in_ref, group_ref),
                )
            flash("Transfer completed successfully with both entries recorded.", "success")
            return redirect(url_for("transactions"))
        except ValueError as exc:
            flash(f"Transfer failed and was rolled back: {exc}", "danger")
            return redirect(url_for("transfer"))
        except Exception:
            current_app.logger.exception("Transfer failed")
            flash("Transfer failed because of a database error. All changes were rolled back.", "danger")
            return redirect(url_for("transfer"))

    accounts = query_all("SELECT AccountID, AccountNumber, Status FROM ACCOUNT ORDER BY AccountID")
    return render_template("transfer.html", accounts=accounts)


@app.route("/transactions")
def transactions():
    account_filter = request.args.get("account_id", "").strip()
    type_filter = request.args.get("type", "").strip()
    if account_filter and not account_filter.isdigit():
        account_filter = ""
    if type_filter not in ("DEPOSIT", "WITHDRAWAL", "TRANSFER_IN", "TRANSFER_OUT"):
        type_filter = ""
    sql = """
        SELECT t.*, a.AccountNumber, b.BranchName
        FROM BANK_TRANSACTION t
        JOIN ACCOUNT a ON a.AccountID = t.AccountID
        JOIN BRANCH b ON b.BranchID = a.BranchID
        WHERE 1=1
    """
    params = []
    if account_filter:
        sql += " AND t.AccountID = %s"
        params.append(account_filter)
    if type_filter:
        sql += " AND t.TransactionType = %s"
        params.append(type_filter)
    sql += " ORDER BY t.TransactionDate DESC, t.TransactionID DESC LIMIT 200"
    rows = query_all(sql, tuple(params))
    accounts = query_all("SELECT AccountID, AccountNumber FROM ACCOUNT ORDER BY AccountID")
    return render_template("transactions.html", transactions=rows, accounts=accounts, account_filter=account_filter, type_filter=type_filter)


# Branch and employee
@app.route("/branches")
def branches():
    rows = query_all("SELECT * FROM vw_branch_summary ORDER BY BranchID")
    return render_template("branches.html", branches=rows)


@app.route("/branches/new", methods=["GET", "POST"])
def branch_new():
    if request.method == "POST":
        branch_name = request.form.get("BranchName", "").strip()
        ifsc = request.form.get("IFSCCode", "").strip().upper()
        address = request.form.get("Address", "").strip()
        city = request.form.get("City", "").strip()
        state = request.form.get("State", "").strip()
        contact = request.form.get("ContactNumber", "").strip()
        if not all([branch_name, ifsc, address, city, state, contact]):
            flash("All fields are required.", "danger")
            return render_template("branch_form.html")
        if not IFSC_PATTERN.fullmatch(ifsc):
            flash("IFSC must use the format ABCD0123456.", "danger")
            return render_template("branch_form.html")
        if not MOBILE_PATTERN.fullmatch(contact):
            flash("Contact number must contain 10 to 15 digits.", "danger")
            return render_template("branch_form.html")
        if len(branch_name) > 100 or len(address) > 255 or len(city) > 80 or len(state) > 80:
            flash("One or more branch fields are too long.", "danger")
            return render_template("branch_form.html")
        try:
            execute(
                "INSERT INTO BRANCH (BranchName, IFSCCode, Address, City, State, ContactNumber) VALUES (%s, %s, %s, %s, %s, %s)",
                (branch_name, ifsc, address, city, state, contact),
            )
            flash("Branch created successfully.", "success")
            return redirect(url_for("branches"))
        except Exception as exc:
            if "uq_branch_ifsc" in str(exc):
                flash("IFSC code already exists.", "danger")
            elif "CHECK" in str(exc).upper():
                flash("Validation error: check IFSC/contact format.", "danger")
            else:
                flash("Could not create branch.", "danger")
            return render_template("branch_form.html")
    return render_template("branch_form.html")


@app.route("/employees")
def employees():
    rows = query_all(
        """
        SELECT e.*, b.BranchName, b.City
        FROM EMPLOYEE e
        JOIN BRANCH b ON b.BranchID = e.BranchID
        ORDER BY e.EmployeeID
        """
    )
    return render_template("employees.html", employees=rows)


@app.route("/employees/new", methods=["GET", "POST"])
def employee_new():
    if request.method == "POST":
        employee_name = request.form.get("EmployeeName", "").strip()
        mobile = request.form.get("Mobile", "").strip()
        email = request.form.get("Email", "").strip().lower()
        designation = request.form.get("Designation", "").strip()
        salary = request.form.get("Salary", "").strip()
        joining_date = request.form.get("JoiningDate", "").strip()
        branch_id = request.form.get("BranchID")
        try:
            if not all([employee_name, mobile, email, designation, salary, joining_date, branch_id]):
                raise ValueError("All fields are required.")
            if not MOBILE_PATTERN.fullmatch(mobile):
                raise ValueError("Mobile must contain 10 to 15 digits.")
            if not EMAIL_PATTERN.fullmatch(email):
                raise ValueError("Enter a valid email address.")
            salary_decimal = parse_money(salary, "Salary")
            parse_date_value(joining_date, "Joining date")
            branch_id = parse_record_id(branch_id, "Branch")
            if len(employee_name) > 100 or len(designation) > 60:
                raise ValueError("Employee name or designation is too long.")
        except ValueError as exc:
            flash(str(exc), "danger")
            return redirect(url_for("employee_new"))
        try:
            execute(
                """
                INSERT INTO EMPLOYEE (EmployeeName, Mobile, Email, Designation, Salary, JoiningDate, BranchID)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                (employee_name, mobile, email, designation, str(salary_decimal), joining_date, branch_id),
            )
            flash("Employee added successfully.", "success")
            return redirect(url_for("employees"))
        except Exception as exc:
            if "uq_employee_mobile" in str(exc):
                flash("Employee mobile already exists.", "danger")
            elif "uq_employee_email" in str(exc):
                flash("Employee email already exists.", "danger")
            elif "CHECK" in str(exc).upper():
                flash("Validation error: check values.", "danger")
            else:
                flash("Could not add employee.", "danger")
            return redirect(url_for("employee_new"))
    branches = query_all("SELECT BranchID, BranchName FROM BRANCH ORDER BY BranchID")
    return render_template("employee_form.html", branches=branches)


# Loans
def record_loan_payment(loan_id, amount_decimal, payment_mode):
    with transaction() as (conn, cur):
        cur.execute("SELECT LoanAmount, LoanStatus FROM LOAN WHERE LoanID = %s FOR UPDATE", (loan_id,))
        loan = cur.fetchone()
        if not loan:
            raise ValueError("Loan not found.")
        if loan["LoanStatus"] != "Approved":
            raise ValueError("Payments are allowed only for approved loans.")
        cur.execute("SELECT COALESCE(SUM(Amount), 0) AS paid FROM LOAN_PAYMENT WHERE LoanID = %s", (loan_id,))
        paid = cur.fetchone()["paid"]
        outstanding = loan["LoanAmount"] - paid
        if amount_decimal > outstanding:
            raise ValueError(f"Payment exceeds the outstanding amount of ₹{outstanding:,.2f}.")
        reference = f"LPAY-{uuid.uuid4().hex[:12].upper()}"
        cur.execute(
            """
            INSERT INTO LOAN_PAYMENT (LoanID, Amount, PaymentMode, ReferenceNumber)
            VALUES (%s, %s, %s, %s)
            """,
            (loan_id, str(amount_decimal), payment_mode, reference),
        )


@app.route("/loans")
def loans():
    rows = query_all("SELECT * FROM vw_loan_payment_summary ORDER BY LoanID")
    return render_template("loans.html", loans=rows)


@app.route("/loans/<int:loan_id>")
def loan_detail(loan_id):
    loan = query_one("SELECT * FROM vw_loan_payment_summary WHERE LoanID = %s", (loan_id,))
    if not loan:
        return render_template("404.html", message="Loan not found"), 404
    payments = query_all("SELECT * FROM LOAN_PAYMENT WHERE LoanID = %s ORDER BY PaymentDate DESC", (loan_id,))
    return render_template("loan_detail.html", loan=loan, payments=payments)


@app.route("/loans/<int:loan_id>/decision/<decision>", methods=["POST"])
def loan_decision(loan_id, decision):
    if decision not in ("approve", "reject"):
        flash("Invalid loan decision.", "danger")
        return redirect(url_for("loans"))
    new_status = "Approved" if decision == "approve" else "Rejected"
    try:
        with transaction() as (conn, cur):
            cur.execute("SELECT LoanStatus FROM LOAN WHERE LoanID = %s FOR UPDATE", (loan_id,))
            loan = cur.fetchone()
            if not loan:
                raise ValueError("Loan not found.")
            if loan["LoanStatus"] != "Pending":
                raise ValueError("Only a pending loan can be approved or rejected.")
            cur.execute("UPDATE LOAN SET LoanStatus = %s WHERE LoanID = %s", (new_status, loan_id))
        flash(f"Loan {new_status.lower()} successfully.", "success")
    except ValueError as exc:
        flash(str(exc), "danger")
    except Exception:
        current_app.logger.exception("Loan decision failed")
        flash("The loan decision could not be saved.", "danger")
    return redirect(url_for("loans"))


@app.route("/loans/<int:loan_id>/pay", methods=["POST"])
def loan_payment_create(loan_id):
    amount = request.form.get("Amount", "").strip()
    payment_mode = request.form.get("PaymentMode", "").strip()
    try:
        amount_decimal = parse_money(amount, "Payment amount")
        if payment_mode not in ("Cash", "Cheque", "NEFT", "UPI", "Card"):
            raise ValueError("Select a valid payment mode.")
        record_loan_payment(loan_id, amount_decimal, payment_mode)
        flash("Loan payment recorded successfully.", "success")
    except ValueError as exc:
        flash(str(exc), "danger")
    except Exception:
        current_app.logger.exception("Loan payment failed")
        flash("Loan payment failed because of a database error.", "danger")
    return redirect(url_for("loan_detail", loan_id=loan_id))


@app.route("/loans/new", methods=["GET", "POST"])
def loan_new():
    if request.method == "POST":
        customer_id = request.form.get("CustomerID")
        branch_id = request.form.get("BranchID")
        loan_type = request.form.get("LoanType")
        loan_amount = request.form.get("LoanAmount", "").strip()
        interest_rate = request.form.get("InterestRate", "").strip()
        start_date = request.form.get("StartDate", "").strip()
        tenure_months = request.form.get("TenureMonths", "").strip()
        try:
            if not all([customer_id, branch_id, loan_type, loan_amount, interest_rate, start_date, tenure_months]):
                raise ValueError("All fields are required.")
            customer_id = parse_record_id(customer_id, "Customer")
            branch_id = parse_record_id(branch_id, "Branch")
            if loan_type not in ("Home Loan", "Education Loan", "Personal Loan", "Vehicle Loan"):
                raise ValueError("Select a valid loan type.")
            loan_amount = parse_money(loan_amount, "Loan amount")
            try:
                interest_rate = Decimal(interest_rate)
            except InvalidOperation:
                raise ValueError("Interest rate must be a number.")
            if interest_rate < 0 or interest_rate > 50:
                raise ValueError("Interest rate must be between 0 and 50.")
            start_date = parse_date_value(start_date, "Start date")
            if not str(tenure_months).isdigit():
                raise ValueError("Tenure must be a whole number of months.")
            tenure_months = int(tenure_months)
            if tenure_months < 1 or tenure_months > 600:
                raise ValueError("Tenure must be between 1 and 600 months.")
        except ValueError as exc:
            flash(str(exc), "danger")
            return redirect(url_for("loan_new"))
        try:
            execute(
                """
                INSERT INTO LOAN (CustomerID, BranchID, LoanType, LoanAmount, InterestRate, StartDate, TenureMonths, LoanStatus)
                VALUES (%s, %s, %s, %s, %s, %s, %s, 'Pending')
                """,
                (customer_id, branch_id, loan_type, loan_amount, interest_rate, start_date, tenure_months),
            )
            flash("Loan application submitted with status Pending.", "success")
            return redirect(url_for("loans"))
        except Exception as exc:
            if "CHECK" in str(exc).upper():
                flash("Validation error: check loan amount, interest rate, or tenure.", "danger")
            elif "FOREIGN KEY" in str(exc):
                flash("Invalid customer or branch selection.", "danger")
            else:
                flash("Could not submit loan application.", "danger")
            return redirect(url_for("loan_new"))
    customers = query_all("SELECT CustomerID, FirstName, LastName FROM CUSTOMER ORDER BY CustomerID")
    branches = query_all("SELECT BranchID, BranchName FROM BRANCH ORDER BY BranchID")
    return render_template("loan_form.html", customers=customers, branches=branches)


@app.route("/loans/payments", methods=["GET", "POST"])
def loan_payments():
    if request.method == "POST":
        loan_id = request.form.get("LoanID")
        amount = request.form.get("Amount", "").strip()
        payment_mode = request.form.get("PaymentMode")
        try:
            loan_id = parse_record_id(loan_id, "Loan")
            amount_decimal = parse_money(amount, "Payment amount")
            if payment_mode not in ("Cash", "Cheque", "NEFT", "UPI", "Card"):
                raise ValueError("Select a valid payment mode.")
            record_loan_payment(loan_id, amount_decimal, payment_mode)
            flash("Loan payment recorded successfully.", "success")
        except ValueError as exc:
            flash(str(exc), "danger")
        except Exception:
            current_app.logger.exception("Loan payment failed")
            flash("Loan payment failed because of a database error.", "danger")
        return redirect(url_for("loan_payments"))
    loans = query_all("SELECT LoanID, CustomerID, LoanType, LoanStatus FROM LOAN ORDER BY LoanID")
    payments = query_all(
        """
        SELECT lp.*, l.LoanType, CONCAT(c.FirstName, ' ', c.LastName) AS CustomerName
        FROM LOAN_PAYMENT lp
        JOIN LOAN l ON l.LoanID = lp.LoanID
        JOIN CUSTOMER c ON c.CustomerID = l.CustomerID
        ORDER BY lp.PaymentDate DESC
        """
    )
    return render_template("loan_payments.html", loans=loans, payments=payments)


@app.errorhandler(404)
def not_found(error):
    return render_template("404.html"), 404


@app.errorhandler(CSRFError)
def csrf_error(error):
    return render_template("error.html", error_message="The form security token expired or was invalid. Reload the page and try again."), 400


@app.errorhandler(500)
def server_error(error):
    current_app.logger.exception("Unhandled application error")
    return render_template("error.html", error_message="An internal error occurred. Check the application log."), 500


if __name__ == "__main__":
    try:
        check_connection()
    except Exception as exc:
        print(f"Database connection failed: {exc}")
        print("Configure .env with correct DB credentials and ensure project_kashi database exists.")
    app.run(debug=app.config["FLASK_DEBUG"], host="127.0.0.1", port=5000)
