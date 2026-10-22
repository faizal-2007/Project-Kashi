-- Project Kashi - demonstration data
-- Load this script after schema.sql, views.sql, functions.sql, procedures.sql and triggers.sql.
USE project_kashi;

INSERT INTO BRANCH (BranchID, BranchName, IFSCCode, Address, City, State, ContactNumber) VALUES
(1, 'Mumbai Central Branch', 'KASH0000001', '12 Marine Lines, Near Central Station', 'Mumbai', 'Maharashtra', '02245678901'),
(2, 'Pune Camp Branch', 'KASH0000002', '45 MG Road, Camp Area', 'Pune', 'Maharashtra', '02045678902'),
(3, 'Bengaluru MG Road Branch', 'KASH0000003', '88 MG Road, Trinity Circle', 'Bengaluru', 'Karnataka', '08045678903'),
(4, 'New Delhi Connaught Place Branch', 'KASH0000004', '21 Connaught Place, Block A', 'New Delhi', 'Delhi', '01145678904'),
(5, 'Hyderabad Banjara Hills Branch', 'KASH0000005', '7 Road No. 12, Banjara Hills', 'Hyderabad', 'Telangana', '04045678905');

INSERT INTO CUSTOMER
(CustomerID, FirstName, LastName, DateOfBirth, Gender, Mobile, Email, Address, City, RegistrationDate) VALUES
(1, 'Aarav', 'Sharma', '1990-05-14', 'Male', '9876543210', 'aarav.sharma@example.com', '14 Andheri East', 'Mumbai', '2025-01-05 10:15:00'),
(2, 'Diya', 'Patel', '1994-11-02', 'Female', '9876543211', 'diya.patel@example.com', '22 Bandra West', 'Mumbai', '2025-01-08 11:20:00'),
(3, 'Rohan', 'Mehta', '1988-02-25', 'Male', '9876543212', 'rohan.mehta@example.com', '9 Koregaon Park', 'Pune', '2025-01-20 09:40:00'),
(4, 'Ananya', 'Iyer', '1996-08-19', 'Female', '9876543213', 'ananya.iyer@example.com', '31 Indiranagar', 'Bengaluru', '2025-02-10 14:05:00'),
(5, 'Kabir', 'Singh', '1992-12-07', 'Male', '9876543214', 'kabir.singh@example.com', '5 Camp Road', 'Pune', '2025-02-14 16:30:00'),
(6, 'Meera', 'Nair', '1998-03-30', 'Female', '9876543215', 'meera.nair@example.com', '18 Koramangala', 'Bengaluru', '2025-03-01 12:00:00'),
(7, 'Arjun', 'Rao', '1985-07-11', 'Male', '9876543216', 'arjun.rao@example.com', '77 Rajouri Garden', 'New Delhi', '2025-03-12 10:45:00'),
(8, 'Isha', 'Gupta', '1999-09-23', 'Female', '9876543217', 'isha.gupta@example.com', '6 Lajpat Nagar', 'New Delhi', '2025-04-02 15:10:00'),
(9, 'Vivaan', 'Joshi', '1991-01-16', 'Male', '9876543218', 'vivaan.joshi@example.com', '10 Jubilee Hills', 'Hyderabad', '2025-04-18 11:35:00'),
(10, 'Saanvi', 'Desai', '1993-06-05', 'Female', '9876543219', 'saanvi.desai@example.com', '3 Banjara Hills Road No. 2', 'Hyderabad', '2025-05-06 13:25:00'),
(11, 'Nimisha', 'Kulkarni', '1997-04-12', 'Female', '9876543220', 'nimisha.kulkarni@example.com', '40 Aundh Road', 'Pune', '2025-06-09 10:00:00');

INSERT INTO EMPLOYEE
(EmployeeID, EmployeeName, Mobile, Email, Designation, Salary, JoiningDate, BranchID) VALUES
(1, 'Rajesh Kumar', '9123456701', 'rajesh.kumar@kashibank.example', 'Branch Manager', 85000.00, '2018-04-16', 1),
(2, 'Priya Sharma', '9123456702', 'priya.sharma@kashibank.example', 'Cashier', 42000.00, '2020-07-01', 1),
(3, 'Amit Verma', '9123456703', 'amit.verma@kashibank.example', 'Loan Officer', 55000.00, '2019-10-21', 2),
(4, 'Neha Kapoor', '9123456704', 'neha.kapoor@kashibank.example', 'Branch Manager', 78000.00, '2021-01-11', 3),
(5, 'Suresh Rao', '9123456705', 'suresh.rao@kashibank.example', 'Clerk', 38000.00, '2022-06-15', 4),
(6, 'Farah Khan', '9123456706', 'farah.khan@kashibank.example', 'Relationship Manager', 61000.00, '2020-11-03', 5);

INSERT INTO ACCOUNT
(AccountID, AccountNumber, AccountType, OpeningDate, Balance, Status, BranchID) VALUES
(1, '100000000001', 'Saving', '2025-01-05 10:30:00', 125500.00, 'Active', 1),
(2, '100000000002', 'Current', '2025-02-01 09:15:00', 425000.00, 'Active', 1),
(3, '100000000003', 'Salary', '2025-02-12 11:00:00', 107000.00, 'Active', 2),
(4, '100000000004', 'Saving', '2025-03-03 14:20:00', 15000.00, 'Active', 2),
(5, '100000000005', 'Current', '2025-03-20 10:10:00', 300000.00, 'Active', 3),
(6, '100000000006', 'Saving', '2025-04-10 12:45:00', 5000.00, 'Active', 3),
(7, '100000000007', 'Salary', '2025-04-25 09:05:00', 65000.00, 'Active', 4),
(8, '100000000008', 'Saving', '2025-05-18 15:35:00', 0.00, 'Active', 4),
(9, '100000000009', 'Current', '2025-05-20 11:25:00', 175000.00, 'Active', 5),
(10, '100000000010', 'Saving', '2025-06-02 13:55:00', 80000.00, 'Active', 5),
(11, '100000000011', 'Saving', '2025-06-20 10:20:00', 12000.00, 'Inactive', 1),
(12, '100000000012', 'Saving', '2025-07-01 09:30:00', 0.00, 'Closed', 4);

INSERT INTO ACCOUNT_HOLDER (CustomerID, AccountID, HolderSince, HolderType) VALUES
(1, 1, '2025-01-05 10:30:00', 'Primary'),
(2, 1, '2025-01-05 10:30:00', 'Joint'),
(3, 2, '2025-02-01 09:15:00', 'Primary'),
(4, 3, '2025-02-12 11:00:00', 'Primary'),
(5, 4, '2025-03-03 14:20:00', 'Primary'),
(6, 5, '2025-03-20 10:10:00', 'Primary'),
(7, 6, '2025-04-10 12:45:00', 'Primary'),
(8, 7, '2025-04-25 09:05:00', 'Primary'),
(9, 8, '2025-05-18 15:35:00', 'Primary'),
(10, 9, '2025-05-20 11:25:00', 'Primary'),
(1, 10, '2025-06-02 13:55:00', 'Primary'),
(3, 11, '2025-06-20 10:20:00', 'Primary'),
(2, 12, '2025-07-01 09:30:00', 'Primary');

INSERT INTO BANK_TRANSACTION
(AccountID, TransactionType, Amount, TransactionDate, Description, ReferenceNumber, TransferGroupReference, TransactionStatus) VALUES
(1, 'DEPOSIT', 100000.00, '2025-01-05 10:35:00', 'Initial deposit at account opening', 'OPEN-100000000001', NULL, 'SUCCESS'),
(1, 'DEPOSIT', 30000.00, '2025-03-15 11:10:00', 'Cash deposit at branch', 'DEP-SAMPLE-0001', NULL, 'SUCCESS'),
(1, 'WITHDRAWAL', 10000.00, '2025-06-20 16:05:00', 'ATM withdrawal', 'WDR-SAMPLE-0001', NULL, 'SUCCESS'),
(1, 'DEPOSIT', 5500.00, '2025-09-05 10:40:00', 'Cash deposit at branch', 'DEP-SAMPLE-0002', NULL, 'SUCCESS'),
(2, 'DEPOSIT', 500000.00, '2025-02-01 09:20:00', 'Initial deposit at account opening', 'OPEN-100000000002', NULL, 'SUCCESS'),
(2, 'WITHDRAWAL', 50000.00, '2025-06-10 14:30:00', 'Business expense withdrawal', 'WDR-SAMPLE-0002', NULL, 'SUCCESS'),
(2, 'TRANSFER_OUT', 25000.00, '2025-07-12 12:15:00', 'Transfer to account 100000000003', 'TRF-SAMPLE-001-OUT', 'TRF-SAMPLE-001', 'SUCCESS'),
(3, 'TRANSFER_IN', 25000.00, '2025-07-12 12:15:00', 'Transfer from account 100000000002', 'TRF-SAMPLE-001-IN', 'TRF-SAMPLE-001', 'SUCCESS'),
(3, 'DEPOSIT', 82000.00, '2025-02-12 11:05:00', 'Initial deposit at account opening', 'OPEN-100000000003', NULL, 'SUCCESS'),
(4, 'DEPOSIT', 20000.00, '2025-03-03 14:25:00', 'Initial deposit at account opening', 'OPEN-100000000004', NULL, 'SUCCESS'),
(4, 'WITHDRAWAL', 5000.00, '2025-08-19 10:50:00', 'Cash withdrawal', 'WDR-SAMPLE-0003', NULL, 'SUCCESS'),
(4, 'WITHDRAWAL', 999999.00, '2025-10-01 20:10:00', 'Failed ATM withdrawal - insufficient balance', 'WDR-SAMPLE-FAILED-0001', NULL, 'FAILED'),
(5, 'DEPOSIT', 300000.00, '2025-03-20 10:15:00', 'Initial deposit at account opening', 'OPEN-100000000005', NULL, 'SUCCESS'),
(6, 'DEPOSIT', 5000.00, '2025-04-10 12:50:00', 'Initial deposit at account opening', 'OPEN-100000000006', NULL, 'SUCCESS'),
(7, 'DEPOSIT', 65000.00, '2025-04-25 09:10:00', 'Initial deposit at account opening', 'OPEN-100000000007', NULL, 'SUCCESS'),
(9, 'DEPOSIT', 200000.00, '2025-05-20 11:30:00', 'Initial deposit at account opening', 'OPEN-100000000009', NULL, 'SUCCESS'),
(9, 'WITHDRAWAL', 25000.00, '2025-09-11 15:45:00', 'Cash withdrawal', 'WDR-SAMPLE-0004', NULL, 'SUCCESS'),
(10, 'DEPOSIT', 80000.00, '2025-06-02 14:00:00', 'Initial deposit at account opening', 'OPEN-100000000010', NULL, 'SUCCESS');

INSERT INTO LOAN
(LoanID, CustomerID, BranchID, LoanType, LoanAmount, InterestRate, StartDate, TenureMonths, LoanStatus) VALUES
(1, 1, 1, 'Home Loan', 2500000.00, 8.50, '2024-04-01', 240, 'Approved'),
(2, 5, 2, 'Education Loan', 500000.00, 7.25, '2025-06-01', 60, 'Approved'),
(3, 8, 4, 'Personal Loan', 200000.00, 11.50, '2026-07-01', 36, 'Pending'),
(4, 9, 4, 'Vehicle Loan', 800000.00, 9.20, '2025-01-15', 84, 'Rejected'),
(5, 10, 5, 'Personal Loan', 300000.00, 10.00, '2024-01-01', 24, 'Approved'),
(6, 3, 1, 'Home Loan', 1500000.00, 8.75, '2025-02-01', 180, 'Approved');

INSERT INTO LOAN_PAYMENT
(LoanID, PaymentDate, Amount, PaymentMode, ReferenceNumber) VALUES
(1, '2025-04-01 10:00:00', 25000.00, 'NEFT', 'LPAY-SAMPLE-0001'),
(1, '2025-05-01 10:30:00', 25000.00, 'UPI', 'LPAY-SAMPLE-0002'),
(2, '2025-07-01 11:15:00', 50000.00, 'UPI', 'LPAY-SAMPLE-0003'),
(5, '2026-08-01 09:45:00', 300000.00, 'NEFT', 'LPAY-SAMPLE-0004');
