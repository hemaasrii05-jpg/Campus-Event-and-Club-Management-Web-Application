from flask import Blueprint, render_template, request, redirect, session
from models import db

events_bp = Blueprint('events', __name__)

@events_bp.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect('/login')
        
    # We pass empty lists for clubs and events so your template variables don't crash
    return render_template('dashboard.html', clubs=[], events=[])

@events_bp.route('/create_club')
def create_club():
    if 'user_id' not in session:
        return redirect('/login')
    return render_template('create_club.html')

@events_bp.route('/create_event')
def create_event():
    if 'user_id' not in session:
        return redirect('/login')
    return render_template('create_event.html')
