CARENEST - CLOUD-BASED PATIENT HEALTH RECORD MANAGEMENT SYSTEM
==============================================================

A simple student project demonstrating all four Wipro COE - WE CPPE modules.
Built with Python, Flask, SQLite, HTML, CSS and JavaScript.

HOW TO RUN (WINDOWS)
--------------------
1. Extract the ZIP file to a normal folder (for example, Desktop).
2. Install Python 3.10 or newer from https://www.python.org/downloads/ if needed.
   During setup, select "Add Python to PATH".
3. Double-click run.bat.
4. The first run installs Flask; internet is required for this installation.
5. The website opens at http://127.0.0.1:5000.
6. Sign in with:
      Username: admin
      Password: Health@123
7. Keep the black command window open while using the website.
8. To stop, click the command window and press Ctrl+C.

FEATURES
--------
- Login page and demo admin account
- Patient record dashboard
- Add and search patient records
- Delete patient records as admin
- SQLite database created automatically
- Simple data summaries and visual condition counts
- Local help assistant that retrieves answers from a small FAQ knowledge base
- Activity audit log
- Service health endpoint at http://127.0.0.1:5000/health
- Responsive interface for desktop and mobile

THE FOUR TRAINING MODULES
-------------------------
MODULE 1: Cloud Product & Platform Engineering
- Flask routes act as small API/web service endpoints.
- /health is a health-check endpoint.
- SQLite is used locally so the project runs easily.
- AWS Lambda, API Gateway, Step Functions and CI/CD are documented as future cloud deployment extensions.
- This downloaded project does NOT create AWS resources automatically.

MODULE 2: Data Engineering, Big Data & ML Insights
- Records are stored in a structured database.
- Dashboard queries group patient records by condition.
- A simple descriptive insight summarizes the current dataset.
- ETL/Spark/Glue/Redshift and a trained ML model can be future extensions.
- Current insights are descriptive only, not clinical predictions.

MODULE 3: Generative AI, Foundation Models & RAG
- The help assistant searches a local FAQ knowledge base and returns the closest matching note.
- This demonstrates the basic retrieval idea without API keys, paid services or internet access.
- It is an RAG-style learning demo, not a full LLM or production RAG pipeline.
- A real LLM, embeddings and AI agent can be added later.

MODULE 4: Cloud Security, Cryptography & Governance
- Sign-in is required for the dashboard.
- Demo password is stored as a hash.
- Database queries use parameters.
- Only the admin role can delete records.
- Important actions are written to an audit log.
- AWS IAM, VPC, KMS encryption, CloudTrail, CloudWatch and threat detection are future cloud extensions.

PROJECT STRUCTURE
-----------------
app.py                 Flask application and database logic
templates/login.html   Login page
templates/dashboard.html Main dashboard
static/style.css       Website styling
requirements.txt       Python package list
run.bat                One-click Windows launcher
health_records.db      Created automatically on first run

IMPORTANT SAFETY NOTES
----------------------
- This is an educational prototype, not a production healthcare system.
- Use only fictional/demo patient data. Do not enter real patient information.
- Do not deploy this demo publicly or use it for actual clinical decisions.
- The built-in login is for local demonstration only. Production deployment needs stronger
  authentication, CSRF protection, secure secret management, encryption at rest/in transit,
  backups, monitoring, and privacy/legal review.
- The assistant and data insights do not diagnose disease or provide medical advice.
- The CSS loads Google Fonts when internet is available; the site still works if fonts cannot load.

TROUBLESHOOTING
---------------
- If 'Python was not found': install Python and tick 'Add Python to PATH', then reopen the folder.
- If Flask installation fails: connect to the internet and run run.bat again.
- If port 5000 is already in use: close the other local Flask app, then try again.
- If the page does not open automatically: manually visit http://127.0.0.1:5000.
