import os
import sqlite3
import datetime
from flask import Flask, jsonify, request, send_from_directory, redirect, url_for
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10 MB
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Allowed image types
ALLOWED_EXT = {"png", "jpg", "jpeg", "gif"}

# Database init
def get_conn():
    conn = sqlite3.connect("potholes.db")
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_conn()
    conn.execute("""
    CREATE TABLE IF NOT EXISTS potholes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        description TEXT,
        lat REAL,
        lon REAL,
        photo_filename TEXT,
        reported_by TEXT,
        reported_at TEXT,
        severity TEXT
    )
    """)
    conn.execute("""
    CREATE TABLE IF NOT EXISTS admin (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT
    )
    """)
    conn.commit()
    conn.close()

init_db()

# Ensure one default admin exists
def create_admin():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM admin WHERE username=?", ("admin",))
    if not cur.fetchone():
        cur.execute("INSERT INTO admin (username, password) VALUES (?, ?)", ("admin", "admin123"))
    conn.commit()
    conn.close()

create_admin()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXT

@app.route('/')
def home():
    return redirect('/user')

@app.route('/user')
def user_page():
    return send_from_directory('static', 'user.html')

@app.route('/admin')
def admin_page():
    return send_from_directory('static', 'admin.html')

@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# ------------------ API: Report pothole ------------------
@app.route('/api/report', methods=['POST'])
def report_pothole():
    try:
        title = request.form.get('title')
        description = request.form.get('description')
        lat = request.form.get('lat')
        lon = request.form.get('lon')
        reported_by = request.form.get('reported_by', 'Anonymous')
        severity = request.form.get('severity')
        photo = request.files.get('photo')

        filename = None
        if photo and allowed_file(photo.filename):
            filename = secure_filename(photo.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            photo.save(filepath)

        conn = get_conn()
        conn.execute("""
            INSERT INTO potholes (title, description, lat, lon, photo_filename, reported_by, reported_at, severity)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (title, description, lat, lon, filename, reported_by, datetime.datetime.now().isoformat(), severity))
        conn.commit()
        conn.close()

        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

# ------------------ API: Admin login ------------------
@app.route('/api/admin/login', methods=['POST'])
def admin_login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    conn = get_conn()
    cur = conn.execute("SELECT * FROM admin WHERE username=? AND password=?", (username, password))
    user = cur.fetchone()
    conn.close()

    if user:
        return jsonify({"status": "ok"})
    else:
        return jsonify({"status": "error", "message": "Invalid credentials"})

# ------------------ API: Admin view potholes ------------------
@app.route('/api/admin/potholes')
def admin_potholes():
    conn = get_conn()
    potholes = conn.execute("SELECT * FROM potholes ORDER BY reported_at DESC").fetchall()
    conn.close()

    data = [dict(row) for row in potholes]
    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True)
