# Project Kashi — Complete Banking Management System

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0%2B-black.svg)](https://palletsprojects.com/p/flask/)
[![MySQL](https://img.shields.io/badge/MySQL-8.0%2B-orange.svg)](https://www.mysql.com/)
[![Tests](https://img.shields.io/badge/Tests-24%20Passed-brightgreen.svg)]()
[![License](https://img.shields.io/badge/License-Academic-lightgrey.svg)]()

> **Academic DBMS Project for B.Tech Computer Science and Engineering**  
> **Submission Date:** 28 October 2026  
> **Repository:** `Project Kashi`

---

## 1. Project Overview

**Project Kashi** is a full-stack academic banking management system built to demonstrate the foundational concepts of Database Management Systems (DBMS). It combines a normalized MySQL 8.0 relational database with a Python Flask web application and a responsive raw HTML5/CSS frontend.

### Key Highlights
* **8 Relational Tables in 3NF**: `CUSTOMER`, `BRANCH`, `EMPLOYEE`, `ACCOUNT`, `ACCOUNT_HOLDER`, `BANK_TRANSACTION`, `LOAN`, and `LOAN_PAYMENT`.
* **Many-to-Many Modeling**: Connects customers and accounts using the `ACCOUNT_HOLDER` associative bridge table, allowing single and joint account structures.
* **ACID Transactions**: Atomic deposits, withdrawals, and inter-account transfers with pessimistic row locking (`SELECT ... FOR UPDATE`) and deadlock-free ordered locking.
* **Database Automation**: User-defined stored functions, stored procedures, audit triggers, and database views.
* **100% Parameterized SQL**: Zero string concatenation; fully resilient against SQL Injection.
* **Graceful Degradation**: Clear offline warnings when database is disconnected; no raw 500 error stacktraces.

---

## 2. Directory Structure

```text
Project Kashi/
│
├── app.py                      # Flask backend & routing application
├── db.py                       # Database connection pool & ACID transactions
├── config.py                   # Environment configuration loader
├── conftest.py                 # Pytest configuration helper
├── requirements.txt            # Python package dependencies
├── .env.example                # Template for database credentials
├── .gitignore                  # Git exclusion rules
├── README.md                   # Setup and execution guide (this file)
│
├── sql/                        # Relational Database Scripts (MySQL 8.0+)
│   ├── schema.sql              # Core DDL: 8 tables, PKs, FKs, CHECK constraints, indexes
│   ├── sample_data.sql         # Rich demonstration data across all 8 tables
│   ├── views.sql               # Database views for reporting and statements
│   ├── functions.sql           # Stored functions (Age, Balance, EMI, Customer Balance)
│   ├── procedures.sql          # ACID Stored procedures for deposits, withdrawals, transfers
│   └── triggers.sql            # Audit triggers, balance validation, state guards
│
├── templates/                  # Frontend HTML5 (Jinja2 Templates)
│   ├── base.html               # Master layout with navigation & DB status pill
│   ├── index.html              # Executive banking KPI dashboard
│   ├── customers.html          # Customer directory with live search
│   ├── customer_form.html      # Customer registration form with validation
│   ├── customer_detail.html    # Customer portfolio, accounts, and loan facilities
│   ├── accounts.html           # Central account register with multi-factor filters
│   ├── account_form.html       # Atomic account opening application
│   ├── account_detail.html     # Account details, holders, and complete statement
│   ├── deposit.html            # Cash/counter deposit form
│   ├── withdrawal.html         # Cash/ATM withdrawal form
│   ├── transfer.html           # Inter-account EFT fund transfer form
│   ├── transactions.html       # Comprehensive bank transaction ledger
│   ├── branches.html           # Branch network performance list
│   ├── branch_form.html        # Branch creation form
│   ├── employees.html          # Employee staff roster
│   ├── employee_form.html      # Employee onboarding form
│   ├── loans.html              # Credit & loan portfolio register
│   ├── loan_form.html          # Loan sanction application
│   ├── loan_payments.html      # Loan repayment form & installment history
│   ├── error.html              # Friendly error notification page
│   └── 404.html                # Not Found error page
│
├── static/
│   ├── css/
│   │   └── style.css           # Counter-ledger stylesheet (bottle green, stone, marigold)
│   └── js/
│       └── main.js             # Client-side transaction confirmations & alerts
│
├── docs/                       # Technical Documentation & Viva Prep
│   ├── PROJECT_REPORT.md       # Complete 39-section academic project report
│   ├── ER_DIAGRAM.md           # ER diagram with Mermaid diagram & M:N explanation
│   ├── ER_DIAGRAM.mmd          # Standalone Mermaid ER diagram source file
│   ├── RELATIONAL_SCHEMA.md    # Formal relational schema notation & referential rules
│   ├── DATA_DICTIONARY.md      # Field-level dictionary for all 8 database tables
│   ├── NORMALIZATION.md        # UNF to 3NF normalization derivation & dependencies
│   ├── RELATIONSHIPS_AND_CARDINALITY.md # Detailed 7-relationship cardinality analysis
│   ├── APPLICATION_WORKFLOW.md # Three-tier architecture & data lifecycle documentation
│   ├── DBMS_CONCEPTS.md        # Comprehensive DBMS theory, ACID, views, and security
│   ├── TEST_CASES.md           # Functional & transaction test cases (TC-01 to TC-15)
│   ├── TROUBLESHOOTING.md      # Troubleshooting guide for Windows & MySQL setup
│   └── SCREENSHOTS.md          # Guide for 12 essential evaluation screenshots
│
├── tests/
│   ├── test_app.py             # 24 automated pytest tests
│   └── README.md               # Testing documentation and instructions
│
└── screenshots/
    └── README.md               # Folder for captured UI evaluation screenshots
```

---

## 3. Prerequisites & Environment Setup (Windows)

Ensure the following software is installed on your Windows machine:
1. **Python 3.10 or higher**: Verify via `python --version`.
2. **MySQL Server 8.0+**: Verify via `mysql --version`.
3. **Git**: Verify via `git --version`.

---

## 4. Step-by-Step Installation & Execution Guide

### Step 1: Open Command Prompt
Open standard Command Prompt (`cmd.exe`) and navigate to the project directory:
```cmd
cd "c:\Projects\Project Kashi"
```

### Step 2: Create and Activate Virtual Environment
```cmd
python -m venv .venv
.venv\Scripts\activate.bat
```
*(You will see `(.venv)` appear in front of your command prompt).*

### Step 3: Install Required Dependencies
```cmd
python -m pip install -r requirements.txt
```

### Step 4: Configure Database Credentials
Copy `.env.example` to create `.env`:
```cmd
copy .env.example .env
```
Open `.env` in Notepad or VS Code and configure your local MySQL credentials:
```ini
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_actual_mysql_password_here
DB_NAME=project_kashi
```
*(If your local MySQL root user has no password, leave it empty: `DB_PASSWORD=`).*

### Step 5: Initialize MySQL Database & Load Data
Execute the SQL scripts in order using the MySQL command-line client:

```cmd
mysql -u root -p < sql\schema.sql
mysql -u root -p < sql\sample_data.sql
mysql -u root -p < sql\views.sql
mysql -u root -p < sql\functions.sql
mysql -u root -p < sql\procedures.sql
mysql -u root -p < sql\triggers.sql
```
*(Enter your MySQL root password when prompted for each command).*

> **Tip**: You can also open and run these `.sql` files directly inside **MySQL Workbench**.

### Step 6: Run Automated Tests
Verify system integrity by running the test suite:
```cmd
pytest -v tests/test_app.py
```
*(All 24 tests should pass).*

### Step 7: Start the Web Application
```cmd
python app.py
```

### Step 8: Open in Browser
Open your web browser and navigate to:
```text
http://127.0.0.1:5000
```
You will be greeted by the **Project Kashi Executive Banking Dashboard** with live data!

---

## 5. Pushing to GitHub

To push this repository to your personal GitHub account:

```cmd
git init
git add .
git commit -m "feat: complete Project Kashi banking management system with MySQL 8.0 & Flask"
git branch -M main
```

If you use the GitHub CLI (`gh`):
```cmd
gh repo create "Project Kashi" --public --source=. --push
```

Or using standard Git remote commands:
```cmd
git remote add origin https://github.com/YOUR_GITHUB_USERNAME/Project-Kashi.git
git push -u origin main
```

---

## 6. Submission Checklist for 28 October 2026

* [x] All 8 relational tables implemented and normalized to 3NF.
* [x] Many-to-Many customer-account bridge entity (`ACCOUNT_HOLDER`) functional.
* [x] ACID deposit, withdrawal, and transfer workflows with rollback protection.
* [x] Stored procedures, functions, triggers, and views created and documented.
* [x] 24 automated unit and validation tests passing.
* [x] Complete 39-section academic project report (`docs/PROJECT_REPORT.md`).
* [x] Windows CMD setup guide and `.gitignore` protecting credentials.

---

**Developed for Academic Evaluation — B.Tech Computer Science and Engineering (CSE)**
