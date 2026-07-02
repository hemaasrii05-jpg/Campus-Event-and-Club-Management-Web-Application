from flask import Blueprint, render_template, request, redirect, session, url_for, jsonify, flash
from models import db, Event, User, Registration, Club
from datetime import datetime
from sqlalchemy.exc import IntegrityError

events_bp = Blueprint('events', __name__)


@events_bp.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
        
    # Dynamically fetch real active clubs and campus events from your SQLite tables
    clubs = Club.query.order_by(Club.created_at.desc()).all()
    events = Event.query.order_by(Event.start_datetime.asc()).all()
    
    return render_template('dashboard.html', clubs=clubs, events=events)


@events_bp.route('/create_club', methods=['GET', 'POST'])
def create_club():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
        
    if request.method == 'POST':
        # Capture form inputs matching HTML 'name' elements exactly
        title = request.form.get('club_name')
        desc = request.form.get('club_desc')
        
        if not title or not desc:
            flash("Both club name and description are required!", "danger")
            return render_template('create_club.html')
            
        try:
            # Create object instance and commit to your central SQLite db file
            new_club = Club(name=title, description=desc)
            db.session.add(new_club)
            db.session.commit()
            
            flash("Club created successfully!", "success")
            # Redirect right back to dashboard layout structure
            return redirect(url_for('events.dashboard'))
            
        except IntegrityError:
            db.session.rollback()  # Undo the failed transaction safely
            flash("A club with this name already exists! Please choose a unique name.", "danger")
            return render_template('create_club.html')
        
    return render_template('create_club.html')


@events_bp.route('/events')
def events_list():
    events = Event.query.order_by(Event.start_datetime.asc()).all()
    return render_template('events.html', events=events)


@events_bp.route('/events/<int:event_id>')
def event_detail(event_id):
    event = Event.query.get_or_404(event_id)
    return render_template('event_detail.html', event=event)


@events_bp.route('/events/create', methods=['GET', 'POST'])
def create_event():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        start = request.form.get('start_datetime')
        end = request.form.get('end_datetime')
        location = request.form.get('location')
        capacity = request.form.get('capacity')

        try:
            start_dt = datetime.fromisoformat(start)
        except Exception:
            start_dt = datetime.utcnow()

        end_dt = None
        if end:
            try:
                end_dt = datetime.fromisoformat(end)
            except Exception:
                end_dt = None

        host_id = session.get('user_id') or 1

        event = Event(
            title=title,
            description=description,
            start_datetime=start_dt,
            end_datetime=end_dt,
            location=location,
            capacity=int(capacity) if capacity else None,
            host_id=host_id
        )
        db.session.add(event)
        db.session.commit()
        return redirect(url_for('events.dashboard'))

    return render_template('create_event.html')


@events_bp.route('/events/<int:event_id>/rsvp', methods=['POST'])
def rsvp(event_id):
    if 'user_id' not in session:
        return jsonify({'error': 'authentication required'}), 401

    user_id = session['user_id']
    event = Event.query.get_or_404(event_id)

    existing = Registration.query.filter_by(user_id=user_id, event_id=event.id).first()
    if existing:
        return jsonify({'status': 'already_registered'})

    reg = Registration(user_id=user_id, event_id=event.id)
    db.session.add(reg)
    db.session.commit()
    return jsonify({'status': 'registered'})


@events_bp.route('/api/events')
def api_events():
    events = Event.query.order_by(Event.start_datetime.asc()).all()
    out = []
    for e in events:
        out.append({
            'id': e.id,
            'title': e.title,
            'description': e.description,
            'start': e.start_datetime.isoformat() if e.start_datetime else None,
            'end': e.end_datetime.isoformat() if e.end_datetime else None,
            'location': e.location,
            'capacity': e.capacity,
            'host_id': e.host_id
        })
    return jsonify(out)