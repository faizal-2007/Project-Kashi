# Screenshot Capture & Documentation Guide — Project Kashi

This guide documents the 12 essential screenshots required for your academic project evaluation, lab submission, and project report.

---

## Required Screenshot Checklist

| # | Screenshot Filename | View / Page | Key Visual Elements to Include |
| :---: | :--- | :--- | :--- |
| **01** | `01_dashboard.png` | Executive Dashboard (`/`) | Ledger plate with total deposits, the four position facts, counter operations, and recent ledger activity. |
| **02** | `02_customer_registration.png` | Customer Form (`/customers/register`) | Input fields (Name, DOB, Mobile, Email, Address, City) and validation elements. |
| **03** | `03_customer_directory.png` | Customer List (`/customers`) | Customer records table with search input and "+ Register Customer" action button. |
| **04** | `04_customer_portfolio.png` | Customer Detail (`/customers/1`) | Demographics card, linked bank accounts with holder roles, and active loans. |
| **05** | `05_account_opening.png` | Open Account Form (`/accounts/open`) | Customer dropdown, branch dropdown, account type, and initial deposit amount. |
| **06** | `06_accounts_register.png` | Accounts List (`/accounts`) | Multi-account table with status pills (Active, Inactive) and multi-factor filter bar. |
| **07** | `07_deposit_operation.png` | Deposit Screen (`/deposit`) | Target account selector, deposit amount, description, and success flash message. |
| **08** | `08_withdrawal_operation.png` | Withdrawal Screen (`/withdrawal`) | Debit account selection, amount validation, and post-withdrawal balance alert. |
| **09** | `09_transfer_operation.png` | EFT Transfer (`/transfer`) | Source and destination selectors, transfer amount, and confirmation dialog prompt. |
| **10** | `10_transactions_ledger.png` | Transactions Ledger (`/transactions`) | Comprehensive ledger showing `DEPOSIT`, `WITHDRAWAL`, `TRANSFER_IN`, and `TRANSFER_OUT` rows. |
| **11** | `11_loan_management.png` | Loan Portfolio (`/loans`) | Loan facilities table displaying sanctioned principal, repayments, and outstanding debt. |
| **12** | `12_mysql_cli_tables.png` | MySQL CLI or Workbench | Output of `SHOW TABLES;` and `DESCRIBE ACCOUNT;` in MySQL Command Line Client. |

---

## Instructions for Capturing Screenshots on Windows

1. Ensure MySQL Server is running and sample data is loaded.
2. Activate your virtual environment and start the application:
   ```cmd
   .venv\Scripts\activate
   python app.py
   ```
3. Open your browser to `http://127.0.0.1:5000/`.
4. Use Windows Snipping Tool (`Win + Shift + S`) or browser full-page screenshot (`Ctrl + Shift + I` $\rightarrow$ `Ctrl + Shift + P` $\rightarrow$ "Capture full size screenshot").
5. Save captured PNG files directly into the `screenshots/` directory following the naming convention above.
