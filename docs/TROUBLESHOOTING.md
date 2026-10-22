# Troubleshooting & FAQs — Project Kashi

Comprehensive guide to resolving common local development, database connectivity, and environment issues on Windows.

---

## 1. MySQL Connectivity Issues

### Error 1045 (28000): Access denied for user 'root'@'localhost'
* **Cause**: The password supplied in `.env` does not match the actual root password configured on your local MySQL Server 8.0 instance.
* **Fix**:
  1. Open your `.env` file in VS Code or Notepad.
  2. Locate the line `DB_PASSWORD=`.
  3. Enter your correct MySQL root password. (If you installed MySQL with an empty password, leave it blank: `DB_PASSWORD=`).
  4. Save the file and restart Flask (`python app.py`).

### Error 2003 (HY000): Can't connect to MySQL server on 'localhost:3306'
* **Cause**: The local MySQL Windows Service is stopped or not running.
* **Fix**:
  1. Press `Win + R`, type `services.msc`, and press Enter.
  2. Scroll down to find **MySQL80** or **MySQL**.
  3. Right-click and choose **Start** or **Restart**.
  4. Alternatively, open Command Prompt as Administrator and run:
     ```cmd
     net start MySQL80
     ```

### Error: Unknown database 'project_kashi'
* **Cause**: The database schema has not been imported yet.
* **Fix**:
  Open Command Prompt and run:
  ```cmd
  mysql -u root -p < sql/schema.sql
  mysql -u root -p < sql/sample_data.sql
  mysql -u root -p < sql/views.sql
  mysql -u root -p < sql/functions.sql
  mysql -u root -p < sql/procedures.sql
  mysql -u root -p < sql/triggers.sql
  ```
  Or open MySQL Workbench, open the SQL scripts from the `sql/` folder, and execute them.

---

## 2. Python & Virtual Environment Issues

### PowerShell Execution Policy Error: Script Execution is Disabled
* **Symptom**: Running `.venv\Scripts\activate` fails with `File cannot be loaded because running scripts is disabled on this system.`
* **Fix**: Run this in PowerShell before activating:
  ```powershell
  Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
  ```
  Or use the standard Command Prompt (`cmd.exe`) where activation is unrestricted:
  ```cmd
  .venv\Scripts\activate.bat
  ```

### Port 5000 Already in Use
* **Symptom**: `OSError: [Errno 10048] error while attempting to bind on address ('127.0.0.1', 5000)`.
* **Fix**:
  Either terminate the process using port 5000:
  ```cmd
  netstat -ano | findstr :5000
  taskkill /PID <PID_NUMBER> /F
  ```
  Or modify the port in `app.py` at the bottom:
  ```python
  app.run(host="127.0.0.1", port=5050, debug=True)
  ```

---

## 3. Automated Test Execution

### Running pytest
To run the automated test suite locally:
```cmd
.venv\Scripts\activate
pytest -v tests/test_app.py
```
All 25 unit and route validation tests will execute and output green status indicators.
