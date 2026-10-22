from decimal import Decimal

import mysql.connector
import pytest


def add_customer(db, mobile="9888888888", email="second.customer@example.com"):
    cursor = db.cursor()
    cursor.execute(
        """
        INSERT INTO CUSTOMER (FirstName, LastName, DateOfBirth, Gender, Mobile, Email, Address, City)
        VALUES ('Second', 'Customer', '1992-02-02', 'Female', %s, %s, '2 Test Lane', 'Test City')
        """,
        (mobile, email),
    )
    customer_id = cursor.lastrowid
    db.commit()
    cursor.close()
    return customer_id


def add_account(db, number="900000000002", balance="500.00", status="Active", customer_id=None):
    cursor = db.cursor()
    cursor.execute(
        """
        INSERT INTO ACCOUNT (AccountNumber, AccountType, Balance, Status, BranchID)
        VALUES (%s, 'Current', %s, %s, 1)
        """,
        (number, balance, status),
    )
    account_id = cursor.lastrowid
    if customer_id:
        cursor.execute(
            "INSERT INTO ACCOUNT_HOLDER (CustomerID, AccountID, HolderType) VALUES (%s, %s, 'Primary')",
            (customer_id, account_id),
        )
    db.commit()
    cursor.close()
    return account_id


def fetch_one(db, sql, params=()):
    cursor = db.cursor(dictionary=True)
    cursor.execute(sql, params)
    row = cursor.fetchone()
    cursor.close()
    return row


def fetch_all(db, sql, params=()):
    cursor = db.cursor(dictionary=True)
    cursor.execute(sql, params)
    rows = cursor.fetchall()
    cursor.close()
    return rows


def test_application_startup_and_dashboard(client, db):
    response = client.get("/")
    assert response.status_code == 200
    assert b"Banking Dashboard" in response.data
    assert b"Total Customers" in response.data


def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.get_json()["status"] == "ok"


def test_customer_creation_stores_record(client, db):
    response = client.post(
        "/customers/new",
        data={
            "FirstName": "Asha",
            "LastName": "Rao",
            "DateOfBirth": "1995-05-10",
            "Gender": "Female",
            "Mobile": "9777777777",
            "Email": "asha.rao@example.com",
            "Address": "10 Test Road",
            "City": "Test City",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"registered successfully" in response.data
    row = fetch_one(db, "SELECT * FROM CUSTOMER WHERE Mobile = %s", ("9777777777",))
    assert row is not None
    assert row["Email"] == "asha.rao@example.com"


def test_duplicate_customer_is_rejected(client, db, baseline):
    response = client.post(
        "/customers/new",
        data={
            "FirstName": "Copy",
            "LastName": "Customer",
            "DateOfBirth": "1990-01-01",
            "Gender": "Male",
            "Mobile": "9999999999",
            "Email": "different@example.com",
            "Address": "Elsewhere",
            "City": "Test City",
        },
    )
    assert response.status_code == 200
    assert b"already exists" in response.data
    count = fetch_one(db, "SELECT COUNT(*) AS cnt FROM CUSTOMER")["cnt"]
    assert count == 1


def test_invalid_customer_form_is_rejected(client, db):
    response = client.post(
        "/customers/new",
        data={
            "FirstName": "Bad",
            "LastName": "Date",
            "DateOfBirth": "2099-01-01",
            "Gender": "Male",
            "Mobile": "123",
            "Email": "bad-email",
            "Address": "Nowhere",
            "City": "Test City",
        },
    )
    assert response.status_code == 200
    assert b"Mobile" in response.data or b"Email" in response.data or b"future" in response.data
    assert fetch_one(db, "SELECT COUNT(*) AS cnt FROM CUSTOMER")["cnt"] == 0


def test_account_opening_creates_account_holder_and_initial_transaction(client, db, baseline):
    response = client.post(
        "/accounts/open",
        data={
            "CustomerID": str(baseline["customer_id"]),
            "AccountType": "Saving",
            "BranchID": "1",
            "HolderType": "Primary",
            "InitialDeposit": "500.00",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    account = fetch_one(db, "SELECT * FROM ACCOUNT WHERE Balance = 500.00")
    assert account is not None
    assert len(account["AccountNumber"]) == 12
    holder = fetch_one(db, "SELECT * FROM ACCOUNT_HOLDER WHERE AccountID = %s", (account["AccountID"],))
    assert holder["CustomerID"] == baseline["customer_id"]
    transaction = fetch_one(db, "SELECT * FROM BANK_TRANSACTION WHERE AccountID = %s", (account["AccountID"],))
    assert transaction["TransactionType"] == "DEPOSIT"
    assert transaction["Amount"] == Decimal("500.00")


def test_deposit_updates_balance_and_records_transaction(client, db, baseline):
    response = client.post(
        "/deposit",
        data={"AccountID": str(baseline["account_id"]), "Amount": "250.50", "Description": "Test deposit"},
        follow_redirects=True,
    )
    assert response.status_code == 200
    account = fetch_one(db, "SELECT Balance FROM ACCOUNT WHERE AccountID = %s", (baseline["account_id"],))
    assert account["Balance"] == Decimal("1250.50")
    transaction = fetch_one(db, "SELECT * FROM BANK_TRANSACTION WHERE AccountID = %s", (baseline["account_id"],))
    assert transaction["TransactionType"] == "DEPOSIT"
    assert transaction["Amount"] == Decimal("250.50")


def test_withdrawal_success(client, db, baseline):
    response = client.post(
        "/withdraw",
        data={"AccountID": str(baseline["account_id"]), "Amount": "300.00", "Description": "Test withdrawal"},
        follow_redirects=True,
    )
    assert response.status_code == 200
    account = fetch_one(db, "SELECT Balance FROM ACCOUNT WHERE AccountID = %s", (baseline["account_id"],))
    assert account["Balance"] == Decimal("700.00")
    transaction = fetch_one(db, "SELECT * FROM BANK_TRANSACTION WHERE AccountID = %s", (baseline["account_id"],))
    assert transaction["TransactionType"] == "WITHDRAWAL"


def test_insufficient_balance_is_rejected_without_changes(client, db, baseline):
    response = client.post(
        "/withdraw",
        data={"AccountID": str(baseline["account_id"]), "Amount": "9999.00", "Description": "Too much"},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Insufficient balance" in response.data
    account = fetch_one(db, "SELECT Balance FROM ACCOUNT WHERE AccountID = %s", (baseline["account_id"],))
    assert account["Balance"] == Decimal("1000.00")
    count = fetch_one(db, "SELECT COUNT(*) AS cnt FROM BANK_TRANSACTION")["cnt"]
    assert count == 0


def test_invalid_amount_is_rejected(client, db, baseline):
    response = client.post(
        "/deposit",
        data={"AccountID": str(baseline["account_id"]), "Amount": "0"},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"greater than zero" in response.data
    assert fetch_one(db, "SELECT COUNT(*) AS cnt FROM BANK_TRANSACTION")["cnt"] == 0


def test_transfer_success_creates_two_linked_entries(client, db, baseline):
    destination_id = add_account(db, customer_id=baseline["customer_id"])
    response = client.post(
        "/transfer",
        data={
            "FromAccountID": str(baseline["account_id"]),
            "ToAccountID": str(destination_id),
            "Amount": "400.00",
            "Description": "Test transfer",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    source = fetch_one(db, "SELECT Balance FROM ACCOUNT WHERE AccountID = %s", (baseline["account_id"],))
    destination = fetch_one(db, "SELECT Balance FROM ACCOUNT WHERE AccountID = %s", (destination_id,))
    assert source["Balance"] == Decimal("600.00")
    assert destination["Balance"] == Decimal("900.00")
    rows = fetch_all(db, "SELECT * FROM BANK_TRANSACTION ORDER BY TransactionID")
    assert len(rows) == 2
    assert rows[0]["TransactionType"] == "TRANSFER_OUT"
    assert rows[1]["TransactionType"] == "TRANSFER_IN"
    assert rows[0]["TransferGroupReference"] == rows[1]["TransferGroupReference"]


def test_transfer_failure_rolls_back_everything(client, db, baseline):
    destination_id = add_account(db, customer_id=baseline["customer_id"])
    response = client.post(
        "/transfer",
        data={
            "FromAccountID": str(baseline["account_id"]),
            "ToAccountID": str(destination_id),
            "Amount": "5000.00",
            "Description": "Should fail",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"rolled back" in response.data
    source = fetch_one(db, "SELECT Balance FROM ACCOUNT WHERE AccountID = %s", (baseline["account_id"],))
    destination = fetch_one(db, "SELECT Balance FROM ACCOUNT WHERE AccountID = %s", (destination_id,))
    assert source["Balance"] == Decimal("1000.00")
    assert destination["Balance"] == Decimal("500.00")
    assert fetch_one(db, "SELECT COUNT(*) AS cnt FROM BANK_TRANSACTION")["cnt"] == 0


def test_transfer_to_same_account_is_rejected(client, db, baseline):
    response = client.post(
        "/transfer",
        data={
            "FromAccountID": str(baseline["account_id"]),
            "ToAccountID": str(baseline["account_id"]),
            "Amount": "10.00",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"cannot be the same" in response.data
    assert fetch_one(db, "SELECT COUNT(*) AS cnt FROM BANK_TRANSACTION")["cnt"] == 0


def test_transaction_history_and_filters(client, db, baseline):
    client.post(
        "/deposit",
        data={"AccountID": str(baseline["account_id"]), "Amount": "25.00"},
    )
    response = client.get(f"/transactions?account_id={baseline['account_id']}&type=DEPOSIT")
    assert response.status_code == 200
    assert b"DEPOSIT" in response.data
    assert b"Transaction History" in response.data


def test_branch_and_employee_creation(client, db):
    response = client.post(
        "/branches/new",
        data={
            "BranchName": "Second Branch",
            "IFSCCode": "TEST0000002",
            "Address": "2 Test Road",
            "City": "Test City",
            "State": "Test State",
            "ContactNumber": "9000000002",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert fetch_one(db, "SELECT COUNT(*) AS cnt FROM BRANCH")["cnt"] == 2
    response = client.post(
        "/employees/new",
        data={
            "EmployeeName": "Test Employee",
            "Mobile": "9000000009",
            "Email": "employee@example.com",
            "Designation": "Clerk",
            "Salary": "30000",
            "JoiningDate": "2025-01-01",
            "BranchID": "1",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    employee = fetch_one(db, "SELECT * FROM EMPLOYEE WHERE Email = %s", ("employee@example.com",))
    assert employee is not None
    assert employee["Salary"] == Decimal("30000.00")


def test_loan_workflow_and_payment_trigger(client, db, baseline):
    response = client.post(
        "/loans/new",
        data={
            "CustomerID": str(baseline["customer_id"]),
            "BranchID": "1",
            "LoanType": "Personal Loan",
            "LoanAmount": "100000.00",
            "InterestRate": "9.50",
            "StartDate": "2025-01-01",
            "TenureMonths": "24",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    loan = fetch_one(db, "SELECT * FROM LOAN")
    assert loan["LoanStatus"] == "Pending"

    client.post(f"/loans/{loan['LoanID']}/decision/approve", follow_redirects=True)
    assert fetch_one(db, "SELECT LoanStatus FROM LOAN WHERE LoanID = %s", (loan["LoanID"],))["LoanStatus"] == "Approved"

    client.post(
        f"/loans/{loan['LoanID']}/pay",
        data={"Amount": "40000.00", "PaymentMode": "UPI"},
        follow_redirects=True,
    )
    outstanding = fetch_one(db, "SELECT fn_loan_outstanding(%s) AS amount", (loan["LoanID"],))["amount"]
    assert outstanding == Decimal("60000.00")

    client.post(
        f"/loans/{loan['LoanID']}/pay",
        data={"Amount": "60000.00", "PaymentMode": "NEFT"},
        follow_redirects=True,
    )
    status = fetch_one(db, "SELECT LoanStatus FROM LOAN WHERE LoanID = %s", (loan["LoanID"],))["LoanStatus"]
    assert status == "Closed"


def test_account_status_rules(client, db, baseline):
    response = client.post(
        f"/accounts/{baseline['account_id']}/status",
        data={"Status": "Closed"},
        follow_redirects=True,
    )
    assert b"zero" in response.data
    assert fetch_one(db, "SELECT Status FROM ACCOUNT WHERE AccountID = %s", (baseline["account_id"],))["Status"] == "Active"

    cursor = db.cursor()
    cursor.execute("UPDATE ACCOUNT SET Balance = 0 WHERE AccountID = %s", (baseline["account_id"],))
    db.commit()
    cursor.close()
    client.post(
        f"/accounts/{baseline['account_id']}/status",
        data={"Status": "Closed"},
        follow_redirects=True,
    )
    assert fetch_one(db, "SELECT Status FROM ACCOUNT WHERE AccountID = %s", (baseline["account_id"],))["Status"] == "Closed"


def test_missing_records_return_404(client):
    assert client.get("/customers/99999").status_code == 404
    assert client.get("/accounts/99999").status_code == 404
    assert client.get("/loans/99999").status_code == 404


def test_views_functions_and_procedures(db, baseline):
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM vw_account_details WHERE AccountID = %s", (baseline["account_id"],))
    assert cursor.fetchone() is not None

    cursor.execute("SELECT fn_customer_age(%s) AS age", (baseline["customer_id"],))
    assert cursor.fetchone()["age"] >= 0

    cursor.execute("SELECT fn_account_tenure_months(%s) AS months", (baseline["account_id"],))
    assert cursor.fetchone()["months"] >= 0

    cursor.execute("SELECT fn_branch_total_balance(1) AS total")
    assert cursor.fetchone()["total"] == Decimal("1000.00")

    cursor.callproc("sp_customer_accounts", (baseline["customer_id"],))
    results = list(cursor.stored_results())
    assert results and results[0].fetchone() is not None

    cursor.callproc("sp_account_statement", (baseline["account_id"], "2025-01-01", "2030-01-01"))
    assert list(cursor.stored_results())
    cursor.close()

    cursor = db.cursor(dictionary=True)
    cursor.callproc("sp_branch_summary")
    branch_results = list(cursor.stored_results())
    assert branch_results and branch_results[0].fetchone()["BranchID"] == 1
    cursor.close()

    loan_cursor = db.cursor()
    loan_cursor.execute(
        """
        INSERT INTO LOAN (CustomerID, BranchID, LoanType, LoanAmount, InterestRate, StartDate, TenureMonths, LoanStatus)
        VALUES (%s, 1, 'Personal Loan', 50000.00, 9.00, '2025-01-01', 12, 'Pending')
        """,
        (baseline["customer_id"],),
    )
    loan_id = loan_cursor.lastrowid
    db.commit()
    loan_cursor.close()

    cursor = db.cursor(dictionary=True)
    cursor.callproc("sp_approve_loan", (loan_id, "placeholder"))
    list(cursor.stored_results())
    cursor.close()
    status = fetch_one(db, "SELECT LoanStatus FROM LOAN WHERE LoanID = %s", (loan_id,))["LoanStatus"]
    assert status == "Approved"


def test_primary_holder_and_status_triggers(db, baseline):
    customer_id = add_customer(db)
    cursor = db.cursor()
    with pytest.raises(mysql.connector.Error):
        cursor.execute(
            "INSERT INTO ACCOUNT_HOLDER (CustomerID, AccountID, HolderType) VALUES (%s, %s, 'Primary')",
            (customer_id, baseline["account_id"]),
        )
    db.rollback()

    cursor.execute(
        "INSERT INTO ACCOUNT_HOLDER (CustomerID, AccountID, HolderType) VALUES (%s, %s, 'Joint')",
        (customer_id, baseline["account_id"]),
    )
    db.commit()
    with pytest.raises(mysql.connector.Error):
        cursor.execute(
            "UPDATE ACCOUNT_HOLDER SET HolderType = 'Primary' WHERE CustomerID = %s AND AccountID = %s",
            (customer_id, baseline["account_id"]),
        )
    db.rollback()

    with pytest.raises(mysql.connector.Error):
        cursor.execute("UPDATE ACCOUNT SET Status = 'Closed' WHERE AccountID = %s", (baseline["account_id"],))
    db.rollback()
    cursor.close()


def test_loan_payment_trigger_prevents_overpayment(db, baseline):
    cursor = db.cursor()
    cursor.execute(
        """
        INSERT INTO LOAN (CustomerID, BranchID, LoanType, LoanAmount, InterestRate, StartDate, TenureMonths, LoanStatus)
        VALUES (%s, 1, 'Education Loan', 10000.00, 7.00, '2025-01-01', 12, 'Approved')
        """,
        (baseline["customer_id"],),
    )
    loan_id = cursor.lastrowid
    db.commit()
    with pytest.raises(mysql.connector.Error):
        cursor.execute(
            "INSERT INTO LOAN_PAYMENT (LoanID, Amount, PaymentMode, ReferenceNumber) VALUES (%s, 10001.00, 'Cash', 'OVERPAY-1')",
            (loan_id,),
        )
    db.rollback()
    cursor.close()


def test_transaction_history_is_immutable(db, baseline):
    cursor = db.cursor()
    cursor.execute(
        """
        INSERT INTO BANK_TRANSACTION (AccountID, TransactionType, Amount, ReferenceNumber, TransactionStatus)
        VALUES (%s, 'DEPOSIT', 10.00, 'IMMUTABLE-TEST-1', 'SUCCESS')
        """,
        (baseline["account_id"],),
    )
    db.commit()
    with pytest.raises(mysql.connector.Error):
        cursor.execute("UPDATE BANK_TRANSACTION SET Amount = 99 WHERE ReferenceNumber = 'IMMUTABLE-TEST-1'")
    db.rollback()
    with pytest.raises(mysql.connector.Error):
        cursor.execute("DELETE FROM BANK_TRANSACTION WHERE ReferenceNumber = 'IMMUTABLE-TEST-1'")
    db.rollback()
    cursor.close()


def test_transactions_are_blocked_on_inactive_accounts(db, baseline):
    inactive_id = add_account(db, number="900000000003", balance="50.00", status="Inactive")
    cursor = db.cursor()
    with pytest.raises(mysql.connector.Error):
        cursor.execute(
            """
            INSERT INTO BANK_TRANSACTION (AccountID, TransactionType, Amount, ReferenceNumber, TransactionStatus)
            VALUES (%s, 'DEPOSIT', 10.00, 'INACTIVE-TEST-1', 'SUCCESS')
            """,
            (inactive_id,),
        )
    db.rollback()
    cursor.close()
