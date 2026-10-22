# Test Cases & Quality Assurance — Project Kashi

Documentation of all unit, functional, validation, and database transaction test cases designed for **Project Kashi — Banking Management System**.

---

## Test Cases Summary Table

| Test ID | Module / Feature | Test Objective | Test Steps | Expected Result | Status |
| :---: | :--- | :--- | :--- | :--- | :---: |
| **TC-01** | System Initialization | Verify application boot and template rendering | Launch Flask app; request `GET /` | Returns HTTP 200; loads dashboard without server exceptions | **PASS** |
| **TC-02** | Customer Registration | Register a new customer with valid inputs | Submit `POST /customers/register` with valid names, DOB, 10-digit mobile, unique email | Customer record created in MySQL; redirects to profile | **PASS** |
| **TC-03** | Customer Validation | Reject registration with missing names or malformed mobile | Submit `POST /customers/register` with empty first name and non-10-digit phone | Returns HTTP 200; flashes validation errors; rejects insertion | **PASS** |
| **TC-04** | Duplicate Customer Guard | Prevent duplicate registration on existing email/mobile | Submit customer form using an email already registered | Rejects insertion; displays duplicate record warning | **PASS** |
| **TC-05** | Account Opening | Open an account with initial deposit | Submit `POST /accounts/open` with valid customer, branch, type, and opening deposit | Creates `ACCOUNT` row, `ACCOUNT_HOLDER` link, and `BANK_TRANSACTION` initial deposit atomically | **PASS** |
| **TC-06** | Deposit Validation | Reject zero and negative deposits | Invoke `deposit_transaction()` with `amount <= 0` | Returns `success: False`; error message "must be strictly greater than zero" | **PASS** |
| **TC-07** | Deposit Execution | Credit funds and record transaction | Submit valid positive deposit on active account | Updates account balance by deposit amount; inserts `DEPOSIT` record | **PASS** |
| **TC-08** | Withdrawal Validation | Reject zero and negative withdrawals | Invoke `withdrawal_transaction()` with `amount <= 0` | Returns `success: False`; prevents debit | **PASS** |
| **TC-09** | Balance Sufficiency Guard | Reject withdrawal exceeding available balance | Request withdrawal of ₹50,000 from account with balance ₹5,000 | Rejects withdrawal; flashes insufficient funds alert; balance unaltered | **PASS** |
| **TC-10** | Withdrawal Execution | Debit funds and preserve non-negative balance | Request valid withdrawal within available balance | Balance deducted; `WITHDRAWAL` transaction inserted in ledger | **PASS** |
| **TC-11** | Transfer Loop Guard | Prevent inter-account transfer to the same account | Submit transfer with identical source and destination account IDs | Rejects transfer; alerts that source and destination cannot be identical | **PASS** |
| **TC-12** | Transfer Execution | Atomic dual-balance update with paired ledger rows | Transfer ₹5,000 from Account A to Account B | Account A debited ₹5,000; Account B credited ₹5,000; paired `TRANSFER_OUT` & `TRANSFER_IN` logged with identical Ref # | **PASS** |
| **TC-13** | Inactive Account Guard | Prevent transactions against Inactive or Closed accounts | Attempt deposit/withdrawal on closed account | Trigger `trg_validate_transaction_before_insert` fires or backend rejects; operation aborts | **PASS** |
| **TC-14** | Loan Repayment | Record installment and auto-close loan on full repayment | Submit repayment equal to remaining loan debt | Payment logged; loan status automatically toggles from `'Active'` to `'Closed'` | **PASS** |
| **TC-15** | Error Routing (404) | Handle non-existent URLs gracefully | Request `GET /nonexistent-url` | Returns HTTP 404 with styled error page; no stack trace exposure | **PASS** |
