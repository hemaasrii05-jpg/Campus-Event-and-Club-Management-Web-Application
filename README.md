# Campus-Event-and-Club-Management-Web-Application
Mini IT Project
campus-event-system/
│
├── app.py
├── database.db
├── requirements.txt
│
├── templates/
│   ├── index.html
│
├── static/
│   ├── style.css
│
├── models/
│   ├── db.py
│
└── routes/
    ├── auth.py
    ├── events.py

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
    return "Campus Event System is Running 🚀"

if __name__ == "__main__":
    app.run(debug=True)