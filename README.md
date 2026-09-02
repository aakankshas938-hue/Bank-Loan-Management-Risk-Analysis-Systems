**🏦 Bank Loan Management & Risk Analysis System**


An end-to-end Data Engineering and Analytics project that automates the loan approval lifecycle for financial institutions. This system ingests raw banking application data, applies business logic to calculate risk scores and EMIs, stores it in a normalized MySQL database, and generates interactive Excel reports and a web dashboard.

📌 Project Overview
In the banking sector, manually verifying loan applications is time-consuming and prone to errors. To solve this, I developed a pipeline that takes real-world banking data and transforms it into actionable insights, automated decisions, and interactive visual reports.

🛠️ Tech Stack
Language: Python 3
Database: MySQL 8.0
Data Processing: Pandas, NumPy
Excel Automation: openpyxl
Web Dashboard: Streamlit, Plotly
✨ Key Features
ETL Pipeline: Ingests and cleans 4,200+ loan records from a raw Kaggle CSV using Pandas, handling missing values and data transformation.
Risk Scoring Engine: Custom Python logic to approve, reject, or flag loans based on CIBIL score, annual income, and loan-to-income ratio.
MySQL Database: Designed 4 normalized tables (Customer, Loan, CreditProfile, LoanDecision) enforcing referential integrity via Foreign Keys.
Excel Automation: Auto-generates Bank_Loan_Final_Report.xlsx with embedded Pie and Bar charts using openpyxl.
Interactive Dashboard: A Streamlit web app allowing managers to filter data dynamically and visualize KPIs, CIBIL distributions, and approval rates.
