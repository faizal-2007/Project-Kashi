# Viva Questions and Answers

### 1. What is Project Kashi?
An academic banking management system that demonstrates MySQL database design and Flask integration for customers, branches, employees, accounts, transactions, loans, and payments.

### 2. Why is this not a production banking system?
It has no authentication, authorization, HTTPS, audit login, regulatory controls, or real security hardening. It is a local DBMS demonstration with simulated data.

### 3. What is three-layer architecture?
Presentation (HTML/CSS/JS and Jinja), application (Flask routes and validation), and data (MySQL). Each layer has a separate responsibility.

### 4. How does an HTML form reach MySQL?
The browser sends a POST request; Flask validates it; `db.py` sends a parameterized SQL statement through mysql-connector-python; MySQL executes it; Flask redirects or renders a page from database rows.

### 5. Why use Flask?
It is small, readable, beginner-friendly, and lets the project focus on database design and SQL rather than framework complexity.

### 6. How does Flask connect to MySQL?
`db.py` reads host, port, user, password, and database from Flask configuration, which comes from `.env` through `config.py`.

### 7. Why are credentials stored in `.env`?
Secrets should not be committed to source control. `.env` is ignored by Git; `.env.example` contains placeholders only.

### 8. What is a primary key?
A column or combination that uniquely identifies each row. Example: `CustomerID` in CUSTOMER.

### 9. What is a foreign key?
A column that references a primary key in another table. Example: `ACCOUNT.BranchID` references `BRANCH.BranchID`.

### 10. What is a composite key?
A key made of multiple columns. `ACCOUNT_HOLDER(CustomerID, AccountID)` uniquely identifies a holder link.

### 11. Why does ACCOUNT_HOLDER exist?
CUSTOMER and ACCOUNT have a many-to-many relationship. A junction table stores each relationship as one row and can add HolderSince and HolderType.

### 12. What is a unique constraint?
It prevents duplicate non-key values. This project uses it for mobile, email, IFSC, account number, and transaction references.

### 13. What is a CHECK constraint?
A database rule that rejects invalid values. Example: `Balance >= 0` or `Amount > 0`.

### 14. What is referential integrity?
Guaranteeing that a foreign key points to an existing parent row and that parent deletion does not leave orphan children.

### 15. What does ON DELETE RESTRICT do?
It blocks deletion of a parent row while dependent child rows exist. This protects account and transaction history.

### 16. What is cardinality?
The number of related rows. Branch-to-employee is one-to-many; customer-to-account is many-to-many through ACCOUNT_HOLDER.

### 17. What is an ER diagram?
A conceptual model of entities, attributes, and relationships. It is not the same as the physical table schema.

### 18. What is normalization?
Organizing tables to reduce redundancy and update anomalies.

### 19. Explain 1NF.
Each column contains one atomic value and there are no repeating groups. Transactions and joint holders are separate rows.

### 20. Explain 2NF.
It is 1NF with no partial dependency on part of a composite key. In ACCOUNT_HOLDER, HolderType depends on the full customer-account pair.

### 21. Explain 3NF.
It is 2NF with no transitive dependency. Branch details are stored in BRANCH and referenced by BranchID, not copied into every account.

### 22. Give a functional dependency from the project.
`AccountID -> AccountNumber, AccountType, Balance, Status, BranchID`.

### 23. Why is customer data not repeated in every account?
It would waste space and cause update anomalies. The account links to the customer through ACCOUNT_HOLDER.

### 24. What is a JOIN?
A query operation that combines rows from related tables using a condition, such as `a.BranchID = b.BranchID`.

### 25. What is the difference between INNER JOIN and LEFT JOIN?
INNER JOIN returns only matches. LEFT JOIN keeps all left-table rows, using NULL when there is no match. Customers without accounts require LEFT JOIN.

### 26. What is GROUP BY?
It groups rows by values so aggregate functions can calculate per-group results, such as total balance per branch.

### 27. What is HAVING?
A filter applied after GROUP BY. `HAVING COUNT(...) > 1` finds customers with multiple accounts.

### 28. What is a subquery?
A query inside another query. Query 11 uses a correlated subquery to list account holders for the highest-balance account.

### 29. What is a view?
A stored SELECT statement used like a virtual table. `vw_branch_summary` combines branch, employee, and account information.

### 30. What is a stored function?
A routine that returns one value. `fn_loan_outstanding(loan_id)` calculates loan amount minus payments.

### 31. What is a stored procedure?
A named routine that can run multiple statements and return result sets. `sp_approve_loan` locks and approves a pending loan.

### 32. What is a trigger?
A routine that runs automatically on INSERT, UPDATE, or DELETE. This project uses triggers for transaction immutability and loan validation.

### 33. Why can transaction rows not be updated or deleted?
Financial history should be permanent. The triggers signal an error, so corrections must be new transactions rather than silent edits.

### 34. What does a transfer do in the database?
It locks both accounts, checks status and balance, updates both balances, and inserts TRANSFER_OUT and TRANSFER_IN rows sharing a transfer group reference.

### 35. Why do both transfer rows need a shared reference?
It allows a report or auditor to see that the two rows are two sides of one transfer.

### 36. Why is ReferenceNumber unique but transfer group shared?
Each transaction row needs its own unique reference. The group reference intentionally repeats once for the two sides of the transfer.

### 37. What is a database transaction?
A unit of work that commits completely or rolls back completely.

### 38. What is COMMIT?
It permanently saves the current transaction's changes.

### 39. What is ROLLBACK?
It undoes the current transaction's changes.

### 40. Explain ACID.
Atomicity: all or nothing. Consistency: constraints and business rules hold. Isolation: concurrent transactions do not corrupt each other. Durability: committed data survives failure.

### 41. Where is ACID demonstrated?
Account opening commits account + holder + initial deposit together. Deposit/withdrawal commit balance + transaction together. Transfer commits two balances + two rows together and rolls all back on error.

### 42. What is `SELECT ... FOR UPDATE`?
It locks selected rows until the transaction ends, preventing another transaction from changing the same balance concurrently.

### 43. Why lock accounts in a consistent order?
If two transfers lock the same pair of accounts in opposite orders, they can deadlock. Sorting by AccountID gives both transactions the same order.

### 44. What is SQL injection?
An attack where user input is interpreted as SQL. It can expose or destroy data.

### 45. How does Project Kashi prevent SQL injection?
All user values are passed as parameters (`%s`) instead of being concatenated into SQL. User output is auto-escaped by Jinja.

### 46. Why validate on the server if HTML already validates?
HTML validation can be bypassed. Server validation enforces correctness for every request, and database constraints provide the final guard.

### 47. What is CSRF?
Cross-Site Request Forgery tricks a logged-in browser into submitting a request. Flask-WTF CSRF tokens ensure the POST came from the project's form.

### 48. Why are financial operations POST, not GET?
GET should be safe and repeatable. A GET link must not change a balance. POST is used for state changes.

### 49. Why does the dashboard value come from SQL?
Hardcoded numbers would be fake. COUNT and SUM queries show the actual database state.

### 50. What are the project's main limitations?
No login/roles, no interest calculation schedule, no statements export, no production security, and no real banking integration.
