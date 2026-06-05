from flask import Flask, render_template, request, redirect, session
from models import db, User, Event, Registration

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = 'secret123'

db.init_app(app)

with app.app_context():
    db.create_all()

@app.route('/')
def home():
    return "Flask is working!"

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        user = User(
            username=request.form['username'],
            email=request.form['email'],
            password=request.form['password']
        )
        db.session.add(user)
        db.session.commit()
        return redirect('/login')

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(
            email=request.form['email'],
            password=request.form['password']
        ).first()

        if user:
            session['user_id'] = user.id
            return redirect('/dashboard')

    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect('/login')

    events = Event.query.all()
    return render_template('dashboard.html', events=events)

@app.route('/create_event', methods=['POST'])
def create_event():
    event = Event(
        title=request.form['title'],
        description=request.form['description'],
        date=request.form['date'],
        created_by=session['user_id']
    )
    db.session.add(event)
    db.session.commit()
    return redirect('/dashboard')

if __name__ == '__main__':
    app.run(debug=True)
