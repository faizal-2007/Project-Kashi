# Automated Testing Suite — Project Kashi

This directory contains automated unit and integration tests for **Project Kashi — Banking Management System**.

---

## 1. Test Overview

* **`test_app.py`**:
  * **Route Availability & Rendering**: Ensures all 12 core routes (`/`, `/customers`, `/accounts`, `/deposit`, `/withdrawal`, `/transfer`, `/transactions`, `/branches`, `/employees`, `/loans`, etc.) load without crashing and render valid HTML templates even if MySQL is initializing or disconnected.
  * **HTTP 404 Handler**: Confirms that non-existent routes return HTTP 404 with friendly user messaging rather than a server stacktrace.
  * **Financial Validation**: Asserts that deposits, withdrawals, and transfers reject negative or zero values.
  * **Transfer Anti-Loop Guard**: Asserts that inter-account transfers reject identical source and destination accounts.
  * **Form Input Validation**: Verifies server-side form error reporting on malformed email or mobile numbers.

---

## 2. Running Automated Tests Locally

Activate your virtual environment and execute pytest:

```cmd
.venv\Scripts\activate
pytest -v tests/test_app.py
```

### Expected Output:
```text
tests/test_app.py::test_dashboard_route_loads PASSED
tests/test_app.py::test_customers_route_loads PASSED
tests/test_app.py::test_customer_register_get_form PASSED
tests/test_app.py::test_accounts_route_loads PASSED
tests/test_app.py::test_account_open_get_form PASSED
tests/test_app.py::test_deposit_get_form PASSED
tests/test_app.py::test_withdrawal_get_form PASSED
tests/test_app.py::test_transfer_get_form PASSED
tests/test_app.py::test_transactions_route_loads PASSED
tests/test_app.py::test_branches_route_loads PASSED
tests/test_app.py::test_employees_route_loads PASSED
tests/test_app.py::test_loans_route_loads PASSED
tests/test_app.py::test_404_handling PASSED
tests/test_app.py::test_zero_amount_deposit_rejected PASSED
tests/test_app.py::test_negative_amount_deposit_rejected PASSED
tests/test_app.py::test_zero_amount_withdrawal_rejected PASSED
tests/test_app.py::test_negative_amount_withdrawal_rejected PASSED
tests/test_app.py::test_identical_source_dest_transfer_rejected PASSED
tests/test_app.py::test_zero_amount_transfer_rejected PASSED
tests/test_app.py::test_customer_registration_validation PASSED
```
