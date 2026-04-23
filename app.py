from flask import Flask
from models.db import init_db

app = Flask(__name__)

# Initialize database
init_db()

# Import routes
from routes.auth import auth_bp
from routes.events import events_bp

# Register Blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(events_bp)

@app.route("/")
def home():
    return "Campus Event System is Running "

if __name__ == "__main__":
    app.run(debug=True)



    import sqlite3

DB = "database.db"

def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()

    # USERS TABLE
    c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT,
        password TEXT
    )
    """)

    # EVENTS TABLE
    c.execute("""
    CREATE TABLE IF NOT EXISTS events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        description TEXT,
        date TEXT,
        time TEXT,
        venue TEXT,
        category TEXT
    )
    """)

    conn.commit()
    conn.close()



    from flask import Blueprint, request
import sqlite3

auth_bp = Blueprint("auth", __name__)
DB = "database.db"

# TEST ROUTE
@auth_bp.route("/test-auth")
def test_auth():
    return "Auth working "

# REGISTER
@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.form

    conn = sqlite3.connect(DB)
    c = conn.cursor()

    c.execute("INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
              (data["name"], data["email"], data["password"]))

    conn.commit()
    conn.close()

    return "User Registered "

# LOGIN
@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.form

    conn = sqlite3.connect(DB)
    c = conn.cursor()

    c.execute("SELECT * FROM users WHERE email=? AND password=?",
              (data["email"], data["password"]))

    user = c.fetchone()
    conn.close()

    if user:
        return "Login Success "
    else:
        return "Invalid Credentials "