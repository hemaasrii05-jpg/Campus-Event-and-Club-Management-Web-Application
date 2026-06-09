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
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        
        # Validate form fields
        if not username or not email or not password:
            return render_template('register.html', error='All fields are required')
        
        # Check if user already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return render_template('register.html', error='Email already registered')
        
        # Create a new User object from the form data
        user = User(
            username=username,
            email=email,
            password=password  # In production, this should be hashed!
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
            email=request.form.get('email', ''),
            password=request.form.get('password', '')
        ).first()

        if user:
            # Store user ID in session to keep them logged in
            session['user_id'] = user.id
            return redirect('/dashboard')
        else:
            return render_template('login.html', error='Invalid email or password')

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
    
    title = request.form.get('title', '').strip()
    description = request.form.get('description', '').strip()
    date = request.form.get('date', '').strip()
    
    if not title or not description or not date:
        return redirect('/dashboard')  # Return to dashboard if missing fields
        
    event = Event(
        title=title,
        description=description,
        date=date,
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