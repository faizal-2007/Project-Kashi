import pytest
import datetime
from app import app, currency_filter, dateformat_filter
from db import (
    deposit_transaction, withdrawal_transaction, transfer_transaction,
    open_account_transaction, record_loan_payment_transaction
)

@pytest.fixture
def client():
    app.config["TESTING"] = True
    app.config["SECRET_KEY"] = "test-secret-key"
    with app.test_client() as client:
        yield client

# ----------------------------------------------------------------------------
# 1. APPLICATION STARTUP & ROUTE AVAILABILITY TESTS
# ----------------------------------------------------------------------------
def test_dashboard_route_loads(client):
    """Verifies that the dashboard loads gracefully even if DB is disconnected."""
    response = client.get("/")
    assert response.status_code == 200
    assert b"Project Kashi" in response.data
    assert b"Dashboard" in response.data

def test_customers_route_loads(client):
    response = client.get("/customers")
    assert response.status_code == 200
    assert b"Customer Directory" in response.data

def test_customer_register_get_form(client):
    response = client.get("/customers/register")
    assert response.status_code == 200
    assert b"New Customer Registration Form" in response.data

def test_accounts_route_loads(client):
    response = client.get("/accounts")
    assert response.status_code == 200
    assert b"Accounts Central Register" in response.data

def test_account_open_get_form(client):
    response = client.get("/accounts/open")
    assert response.status_code == 200
    assert b"Account Opening Application" in response.data

def test_deposit_get_form(client):
    response = client.get("/deposit")
    assert response.status_code == 200
    assert b"Deposit Funds Entry Form" in response.data

def test_withdrawal_get_form(client):
    response = client.get("/withdrawal")
    assert response.status_code == 200
    assert b"Withdrawal Application Form" in response.data

def test_transfer_get_form(client):
    response = client.get("/transfer")
    assert response.status_code == 200
    assert b"Electronic Fund Transfer" in response.data

def test_transactions_route_loads(client):
    response = client.get("/transactions")
    assert response.status_code == 200
    assert b"Bank Transaction Ledger" in response.data

def test_branches_route_loads(client):
    response = client.get("/branches")
    assert response.status_code == 200
    assert b"Bank Branches" in response.data

def test_employees_route_loads(client):
    response = client.get("/employees")
    assert response.status_code == 200
    assert b"Employee Roster" in response.data

def test_loans_route_loads(client):
    response = client.get("/loans")
    assert response.status_code == 200
    assert b"Credit &amp; Loan Facilities" in response.data or b"Credit & Loan Facilities" in response.data


def test_404_handling(client):
    response = client.get("/page-that-definitely-does-not-exist")
    assert response.status_code == 404
    assert b"404" in response.data

# ----------------------------------------------------------------------------
# 2. VALIDATION & BUSINESS LOGIC INTEGRITY TESTS
# ----------------------------------------------------------------------------
def test_zero_amount_deposit_rejected():
    res = deposit_transaction(account_id=1, amount=0)
    assert res["success"] is False
    assert "greater than zero" in res["message"]

def test_negative_amount_deposit_rejected():
    res = deposit_transaction(account_id=1, amount=-500)
    assert res["success"] is False
    assert "greater than zero" in res["message"]

def test_zero_amount_withdrawal_rejected():
    res = withdrawal_transaction(account_id=1, amount=0)
    assert res["success"] is False
    assert "greater than zero" in res["message"]

def test_negative_amount_withdrawal_rejected():
    res = withdrawal_transaction(account_id=1, amount=-200)
    assert res["success"] is False
    assert "greater than zero" in res["message"]

def test_identical_source_dest_transfer_rejected():
    res = transfer_transaction(src_account_id=5, dest_account_id=5, amount=1000)
    assert res["success"] is False
    assert "cannot be identical" in res["message"]

def test_zero_amount_transfer_rejected():
    res = transfer_transaction(src_account_id=1, dest_account_id=2, amount=0)
    assert res["success"] is False
    assert "greater than zero" in res["message"]

def test_negative_amount_transfer_rejected():
    res = transfer_transaction(src_account_id=1, dest_account_id=2, amount=-100)
    assert res["success"] is False
    assert "greater than zero" in res["message"]

def test_loan_payment_zero_amount_rejected():
    res = record_loan_payment_transaction(loan_id=1, amount=0, payment_mode="Online")
    assert res["success"] is False
    assert "strictly positive" in res["message"]

def test_customer_registration_validation(client):
    """Submitting missing mandatory fields should re-render form with error message."""
    response = client.post("/customers/register", data={
        "first_name": "",
        "last_name": "Test",
        "dob": "1995-01-01",
        "gender": "Male",
        "mobile": "invalid",
        "email": "not-an-email",
        "address": "Street",
        "city": "City"
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"mandatory" in response.data or b"Mobile number must be exactly 10 digits" in response.data

# ----------------------------------------------------------------------------
# 3. TEMPLATE FILTER FORMATTING TESTS
# ----------------------------------------------------------------------------
def test_currency_filter():
    assert currency_filter(1500) == "₹1,500.00"
    assert currency_filter(2500000.5) == "₹2,500,000.50"
    assert currency_filter(0) == "₹0.00"
    assert currency_filter(None) == "₹0.00"
    assert currency_filter("invalid") == "₹0.00"

def test_dateformat_filter():
    dt = datetime.date(2023, 1, 15)
    assert dateformat_filter(dt, "%d %b %Y") == "15 Jan 2023"
    assert dateformat_filter(None) == ""
