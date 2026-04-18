============================================================
  Smart Food Ordering & Queue Management System (SFOQS)
  Advanced Software Development — UFCF8S-30-2
  Academic Year 2025/26
============================================================

------------------------------------------------------------
HOW TO RUN THE SYSTEM
------------------------------------------------------------

1. Make sure Python 3.8 or higher is installed on your machine.
   To check: open a terminal and type:
       python --version
   or
       python3 --version

2. Install the required Python packages (see Dependencies below).

3. Place all project files in the same folder:
       main.py
       auth.py
       database.py
       customer.py
       staff.py
       admin.py
       sfoqs.db   (or leave it out — it will be created automatically)

4. Run the application by executing:
       python main.py
   or on some systems:
       python3 main.py

5. The login screen will appear. Use the sample credentials below.


------------------------------------------------------------
REQUIRED PYTHON PACKAGES / DEPENDENCIES
------------------------------------------------------------

The following packages are required to run the system:

  - Python 3.8+          (mandatory — core language)
  - tkinter              (mandatory — GUI framework, included with standard Python)
  - sqlite3              (mandatory — database, included with standard Python)
  - hashlib              (mandatory — password hashing, included with standard Python)

No external packages need to be installed via pip.
All dependencies are part of the Python standard library.

If tkinter is missing (common on some Linux distributions), install it with:
  Ubuntu/Debian:   sudo apt-get install python3-tk
  Fedora:          sudo dnf install python3-tkinter


------------------------------------------------------------
SAMPLE USERNAMES AND PASSWORDS
------------------------------------------------------------

  Role        Username       Password
  --------    -----------    -----------
  Admin       admin          admin123
  Staff       staff1         staff123
  Customer    customer1      customer123
  Customer    customer2      cust456

NOTE: Each role opens a different interface:
  - Customer  -> Menu browsing, cart, order tracking
  - Staff     -> Active orders queue, status updates
  - Admin     -> Menu management, reports and analytics


------------------------------------------------------------
DATABASE
------------------------------------------------------------

  File: sfoqs.db (SQLite database)

  The database is created and seeded automatically on first run.
  It contains the following tables:
    - users        : registered user accounts and roles
    - menu_items   : food menu with prices and availability
    - orders       : customer orders with status and queue position
    - order_items  : individual items within each order

  Do NOT delete sfoqs.db during normal use as it contains all
  order and user data. To reset to a clean state, delete the
  file and rerun main.py — it will be recreated automatically.


------------------------------------------------------------
PROJECT STRUCTURE
------------------------------------------------------------

  main.py        -> Application entry point and login screen
  auth.py        -> Authentication logic and session management
  database.py    -> Database connection, table creation, seed data
  customer.py    -> Customer panel (menu, cart, order history)
  staff.py       -> Staff panel (order queue, status updates)
  admin.py       -> Admin panel (menu management, reports)
  sfoqs.db       -> SQLite database file
  README.txt     -> This file


------------------------------------------------------------
TESTING EVIDENCE
------------------------------------------------------------

  See the file: test_cases.pdf (or test_cases section in the Portfolio)
  for the full list of test cases, expected results, and outcomes.


------------------------------------------------------------
VERSION CONTROL
------------------------------------------------------------

  GitHub Repository: [INSERT YOUR GITHUB LINK HERE]

  The repository contains:
    - Full commit history showing individual contributions
    - Issue tracking and task allocation per sprint
    - All source code files


------------------------------------------------------------
NOTES FOR MARKERS
------------------------------------------------------------

  - The system runs on Windows and Linux with Python 3.8+
  - No internet connection is required to run the system
  - All passwords in the seeded database are stored as
    SHA-256 hashed values (not plain text)
  - The GUI is built entirely with Tkinter (no external UI libs)


============================================================
  Group Portfolio — UFCF8S-30-2 | Submission: 7 May 2026
============================================================
