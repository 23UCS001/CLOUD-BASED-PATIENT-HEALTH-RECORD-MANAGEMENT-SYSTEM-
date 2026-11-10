from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import sqlite3
import os
import hashlib
import secrets
from datetime import datetime
from functools import wraps

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "health_records.db")
app = Flask(__name__)
app.secret_key = os.environ.get("APP_SECRET_KEY", secrets.token_hex(32))

# Demo credentials for a local student project only.
DEMO_USERNAME = "admin"
DEMO_PASSWORD = "Health@123"

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def password_hash(password):
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

def log_action(username, action, detail=""):
    conn = get_db()
    conn.execute(
        "INSERT INTO audit_logs (username, action, detail, created_at) VALUES (?, ?, ?, ?)",
        (username, action, detail[:250], datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    )
    conn.commit()
    conn.close()

def init_db():
    conn = get_db()
    conn.execute("""CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL DEFAULT 'staff'
    )""")
    conn.execute("""CREATE TABLE IF NOT EXISTS patients (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_code TEXT UNIQUE NOT NULL,
        full_name TEXT NOT NULL,
        age INTEGER NOT NULL,
        gender TEXT NOT NULL,
        phone TEXT,
        condition_name TEXT NOT NULL,
        notes TEXT,
        created_at TEXT NOT NULL
    )""")
    conn.execute("""CREATE TABLE IF NOT EXISTS audit_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        action TEXT NOT NULL,
        detail TEXT,
        created_at TEXT NOT NULL
    )""")
    existing = conn.execute("SELECT id FROM users WHERE username = ?", (DEMO_USERNAME,)).fetchone()
    if not existing:
        conn.execute(
            "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
            (DEMO_USERNAME, password_hash(DEMO_PASSWORD), "admin")
        )
    count = conn.execute("SELECT COUNT(*) AS n FROM patients").fetchone()["n"]
    if count == 0:
        samples = [
            ("P1001", "Ananya Kumar", 28, "Female", "9000000001", "Asthma", "Routine follow-up requested."),
            ("P1002", "Rahul Das", 54, "Male", "9000000002", "Diabetes", "Needs regular glucose monitoring."),
            ("P1003", "Meera Joseph", 46, "Female", "9000000003", "Hypertension", "Review blood pressure readings."),
        ]
        for code, name, age, gender, phone, condition, notes in samples:
            conn.execute(
                """INSERT OR IGNORE INTO patients
                (patient_code, full_name, age, gender, phone, condition_name, notes, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (code, name, age, gender, phone, condition, notes, datetime.now().strftime("%Y-%m-%d %H:%M"))
            )
    conn.commit()
    conn.close()

def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "username" not in session:
            return redirect(url_for("login"))
        return view(*args, **kwargs)
    return wrapped

@app.route("/", methods=["GET"])
def home():
    if "username" not in session:
        return redirect(url_for("login"))
    return redirect(url_for("dashboard"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        conn = get_db()
        user = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        conn.close()
        if user and secrets.compare_digest(user["password_hash"], password_hash(password)):
            session.clear()
            session["username"] = user["username"]
            session["role"] = user["role"]
            log_action(username, "LOGIN", "Successful login")
            return redirect(url_for("dashboard"))
        flash("That username and password did not match. Please try again.", "error")
    return render_template("login.html")

@app.route("/logout")
def logout():
    username = session.get("username", "unknown")
    if "username" in session:
        log_action(username, "LOGOUT", "User signed out")
    session.clear()
    return redirect(url_for("login"))

@app.route("/dashboard")
@login_required
def dashboard():
    q = request.args.get("q", "").strip()
    conn = get_db()
    if q:
        like = f"%{q}%"
        patients = conn.execute(
            """SELECT * FROM patients WHERE full_name LIKE ? OR patient_code LIKE ?
            OR condition_name LIKE ? ORDER BY id DESC""", (like, like, like)
        ).fetchall()
    else:
        patients = conn.execute("SELECT * FROM patients ORDER BY id DESC").fetchall()
    total = conn.execute("SELECT COUNT(*) AS n FROM patients").fetchone()["n"]
    condition_rows = conn.execute(
        "SELECT condition_name, COUNT(*) AS count FROM patients GROUP BY condition_name ORDER BY count DESC"
    ).fetchall()
    logs = conn.execute("SELECT * FROM audit_logs ORDER BY id DESC LIMIT 6").fetchall()
    conn.close()

    # Simple, explainable rule-based insight for demonstration—not a medical diagnosis.
    older_count = sum(1 for p in patients if int(p["age"]) >= 60)
    common_condition = condition_rows[0]["condition_name"] if condition_rows else "No records yet"
    insight = f"{common_condition} is the most common recorded condition in this dataset."
    if older_count:
        insight += f" {older_count} displayed patient record(s) are age 60 or above and may need routine follow-up review."
    else:
        insight += " No displayed records are age 60 or above."
    return render_template(
        "dashboard.html", patients=patients, total=total, conditions=condition_rows,
        logs=logs, q=q, insight=insight, username=session["username"], role=session.get("role", "staff")
    )

@app.route("/patients/add", methods=["POST"])
@login_required
def add_patient():
    code = request.form.get("patient_code", "").strip().upper()
    name = request.form.get("full_name", "").strip()
    age_raw = request.form.get("age", "").strip()
    gender = request.form.get("gender", "").strip()
    phone = request.form.get("phone", "").strip()
    condition = request.form.get("condition_name", "").strip()
    notes = request.form.get("notes", "").strip()

    if not all([code, name, age_raw, gender, condition]):
        flash("Please fill in all required fields.", "error")
        return redirect(url_for("dashboard"))
    try:
        age = int(age_raw)
        if age < 0 or age > 120:
            raise ValueError()
    except ValueError:
        flash("Please enter a valid age between 0 and 120.", "error")
        return redirect(url_for("dashboard"))

    conn = get_db()
    try:
        conn.execute(
            """INSERT INTO patients
            (patient_code, full_name, age, gender, phone, condition_name, notes, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (code, name, age, gender, phone, condition, notes, datetime.now().strftime("%Y-%m-%d %H:%M"))
        )
        conn.commit()
        log_action(session["username"], "CREATE_PATIENT", f"Added patient record {code}")
        flash(f"Patient record for {name} was added.", "success")
    except sqlite3.IntegrityError:
        flash("That patient ID already exists. Please use a different ID.", "error")
    finally:
        conn.close()
    return redirect(url_for("dashboard"))

@app.route("/patients/<int:patient_id>/delete", methods=["POST"])
@login_required
def delete_patient(patient_id):
    if session.get("role") != "admin":
        flash("Only an administrator can delete records.", "error")
        return redirect(url_for("dashboard"))
    conn = get_db()
    patient = conn.execute("SELECT patient_code, full_name FROM patients WHERE id = ?", (patient_id,)).fetchone()
    if patient:
        conn.execute("DELETE FROM patients WHERE id = ?", (patient_id,))
        conn.commit()
        log_action(session["username"], "DELETE_PATIENT", f"Deleted {patient['patient_code']}")
        flash(f"Record for {patient['full_name']} was deleted.", "success")
    conn.close()
    return redirect(url_for("dashboard"))

# Module 3: a small local knowledge-base assistant (retrieval + response).
# This is an offline RAG-style demo, not a medical advice service.
FAQS = [
    ("What is a patient health record?", "A patient health record stores basic details, health conditions, notes, and relevant care history in one place."),
    ("How do I add a patient?", "Open the dashboard, complete the Add a patient form, and select Save patient. Patient ID must be unique."),
    ("How is patient information protected?", "This demo requires sign-in, uses parameterized database queries, limits deletion to the admin role, and records key actions in an audit log."),
    ("Can this system diagnose a disease?", "No. This educational demo stores records and shows simple dataset summaries. It does not diagnose, prescribe treatment, or replace a qualified healthcare professional."),
    ("What does the data insight mean?", "The insight summarizes the records currently stored, such as the most common recorded condition. It is descriptive only and is not a clinical risk prediction."),
    ("How do I search records?", "Use the search box to look up a patient by name, patient ID, or recorded condition."),
]

@app.route("/assistant", methods=["POST"])
@login_required
def assistant():
    question = request.form.get("question", "").strip()
    if not question:
        return jsonify({"answer": "Please enter a question so I can look for a relevant help note."})
    words = set(question.lower().replace("?", "").replace(".", "").split())
    best_score, best_answer = 0, None
    for title, answer in FAQS:
        combined = set((title + " " + answer).lower().replace(",", "").replace(".", "").split())
        score = len(words & combined)
        if score > best_score:
            best_score, best_answer = score, answer
    if best_score == 0:
        best_answer = "I couldn't find a close match in the local help notes. Try asking about adding a patient, searching records, security, or data insights."
    log_action(session["username"], "ASK_ASSISTANT", question[:100])
    return jsonify({"answer": best_answer})

@app.route("/health")
def health():
    return jsonify({"status": "ok", "service": "Cloud Health Records demo"})

init_db()

if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)
