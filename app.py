from flask import Flask, render_template, request, redirect, session, url_for
from models import db, User, Club, Event, Registration
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = 'supersecretkey123'

db.init_app(app)

# This creates the database file automatically
with app.app_context():
    db.create_all()

@app.route('/')
def home():
    return render_template('home.html')

# MAHA'S PART: Authentication
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        new_user = User(username=request.form['username'], email=request.form['email'], password=request.form['password'])
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(email=request.form['email'], password=request.form['password']).first()
        if user:
            session['user_id'] = user.id
            session['username'] = user.username
            return redirect(url_for('dashboard'))
    return render_template('login.html')

# HEMA'S PART: Club Management
@app.route('/create_club', methods=['GET', 'POST'])
def create_club():
    if 'user_id' not in session: return redirect(url_for('login'))
    if request.method == 'POST':
        new_club = Club(name=request.form['club_name'], description=request.form['club_desc'], owner_id=session['user_id'])
        db.session.add(new_club)
        db.session.commit()
        return redirect(url_for('dashboard'))
    return render_template('create_club.html')

# GEEJEN'S PART: Event Management
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session: return redirect(url_for('login'))
    
    # NEW: Fetch clubs owned by the logged-in user
    my_clubs = Club.query.filter_by(owner_id=session['user_id']).all()
    
    search_query = request.args.get('search')
    if search_query:
        events = Event.query.filter(Event.title.contains(search_query)).all()
    else:
        events = Event.query.all()

    # Updated to send 'clubs' to the HTML
    return render_template('dashboard.html', events=events, clubs=my_clubs)
@app.route('/create_event', methods=['GET', 'POST'])
def create_event():
    if 'user_id' not in session: return redirect(url_for('login'))
    if request.method == 'POST':
        club = Club.query.filter_by(owner_id=session['user_id']).first()
        if not club: return "Error: You must create a club first!"
        new_event = Event(title=request.form['title'], description=request.form['description'], date=request.form['date'], club_id=club.id)
        db.session.add(new_event)
        db.session.commit()
        return redirect(url_for('dashboard'))
    return render_template('create_event.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

if __name__ == "__main__":
    app.run(debug=True)