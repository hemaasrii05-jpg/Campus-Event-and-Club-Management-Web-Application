from flask import Blueprint, render_template, request, redirect, session, url_for
from models import db, User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(
            email=request.form['email'],
            password=request.form['password']
        ).first()

        if user:
            session['user_id'] = user.id
            session['username'] = user.username
            # Change this to look up the 'events' blueprint dashboard function
            return redirect(url_for('events.dashboard'))

    return render_template('login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return "Email already registered"

        new_user = User(username=username, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()

        session['user_id'] = new_user.id
        session['username'] = new_user.username
        # Change this to look up the 'events' blueprint dashboard function
        return redirect(url_for('events.dashboard'))

    return render_template('register.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))