from flask import Flask, render_template, request, redirect, session
from models import db, User, Event, Registration

# ==========================================
# 1. INITIALIZATION & CONFIGURATION
# ==========================================

app = Flask(__name__)

# Configure the local SQLite database file
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = 'secret123'

# Link the database instance (from models.py) to this Flask app
db.init_app(app)

# Automatically create the database tables if they don't exist yet
with app.app_context():
    db.create_all()


# ==========================================
# 2. MAHA'S USER ACCOUNT ROUTES (CORE TASKS)
# ==========================================

@app.route('/')
def home():
    """Simple homepage to test if the server is running properly."""
    return "Flask is working!"


@app.route('/register', methods=['GET', 'POST'])
def register():
    """Handles new user sign-ups."""
    if request.method == 'POST':
        # Create a new User object from the form data
        user = User(
            username=request.form['username'],
            email=request.form['email'],
            password=request.form['password']  # In production, this should be hashed!
        )
        # Save to the database
        db.session.add(user)
        db.session.commit()
        return redirect('/login')

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Handles user authentication and starting a session."""
    if request.method == 'POST':
        # Check if a user exists with matching email and password
        user = User.query.filter_by(
            email=request.form['email'],
            password=request.form['password']
        ).first()

        if user:
            # Store user ID in session to keep them logged in
            session['user_id'] = user.id
            return redirect('/dashboard')

    return render_template('login.html')


@app.route('/dashboard')
def dashboard():
    """Displays the user dashboard (Requires being logged in)."""
    if 'user_id' not in session:
        return redirect('/login')

    # Fetch all events to show on the dashboard
    events = Event.query.all()
    return render_template('dashboard.html', events=events)


# ==========================================
# 3. CLUB / EVENT MANAGEMENT ROUTES
# ==========================================

@app.route('/create_event', methods=['POST'])
def create_event():
    """Handles event creation (linked to Event/Club features)."""
    if 'user_id' not in session:
        return redirect('/login')
        
    event = Event(
        title=request.form['title'],
        description=request.form['description'],
        date=request.form['date'],
        created_by=session['user_id']
    )
    db.session.add(event)
    db.session.commit()
    return redirect('/dashboard')


# ==========================================
# 4. RUN THE APPLICATION
# ==========================================
# This must ALWAYS stay at the very bottom of the file!
if __name__ == "__main__":
    app.run(debug=True)