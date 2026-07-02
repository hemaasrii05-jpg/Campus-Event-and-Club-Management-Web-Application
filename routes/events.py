from functools import wraps

from flask import Blueprint, render_template, request, redirect, session, url_for, jsonify, flash
from models import db, Event, Registration, User
from datetime import datetime

events_bp = Blueprint('events', __name__)


def login_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to continue.')
            return redirect(url_for('auth.login'))
        return view(*args, **kwargs)
    return wrapped_view


def parse_event_data(form):
    title = form.get('title', '').strip()
    description = form.get('description', '').strip()
    start = form.get('start_datetime', '').strip()
    end = form.get('end_datetime', '').strip()
    location = form.get('location', '').strip()
    capacity = form.get('capacity', '').strip()

    errors = []
    if not title:
        errors.append('Event title is required.')
    if not start:
        errors.append('Start date/time is required.')

    start_dt = None
    end_dt = None

    if start:
        try:
            start_dt = datetime.fromisoformat(start)
        except Exception:
            errors.append('Start date/time is invalid. Use the picker or ISO datetime format.')

    if end:
        try:
            end_dt = datetime.fromisoformat(end)
        except Exception:
            errors.append('End date/time is invalid. Use the picker or ISO datetime format.')

    if start_dt and end_dt and end_dt <= start_dt:
        errors.append('End time must be after start time.')

    capacity_value = None
    if capacity:
        try:
            capacity_value = int(capacity)
            if capacity_value < 0:
                errors.append('Capacity cannot be negative.')
        except ValueError:
            errors.append('Capacity must be a number.')

    return {
        'title': title,
        'description': description,
        'start_datetime': start_dt,
        'end_datetime': end_dt,
        'location': location,
        'capacity': capacity_value,
        'errors': errors,
        'raw': {
            'title': title,
            'description': description,
            'start_datetime': start,
            'end_datetime': end,
            'location': location,
            'capacity': capacity
        }
    }


@events_bp.route('/events')
def events_list():
    events = Event.query.order_by(Event.start_datetime.asc()).all()
    user_events = []
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        if user:
            user_events = [registration.event for registration in user.registrations]
    return render_template('events.html', events=events, user_events=user_events)


@events_bp.route('/my-events')
@login_required
def my_events():
    user = User.query.get(session.get('user_id'))
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 8, type=int)

    if not user:
        return redirect(url_for('auth.login'))

    # Query registrations and paginate
    regs_q = Registration.query.filter_by(user_id=user.id).order_by(Registration.created_at.desc())
    total = regs_q.count()
    regs = regs_q.offset((page - 1) * per_page).limit(per_page).all()
    user_events = [r.event for r in regs]

    pagination = {
        'page': page,
        'per_page': per_page,
        'total': total,
        'pages': (total + per_page - 1) // per_page
    }

    return render_template('my_events.html', user_events=user_events, pagination=pagination)



@events_bp.route('/api/my-registrations')
def api_my_registrations():
    if 'user_id' not in session:
        return jsonify({'error': 'authentication required'}), 401

    user_id = session['user_id']
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    regs_q = Registration.query.filter_by(user_id=user_id).order_by(Registration.created_at.desc())
    total = regs_q.count()
    regs = regs_q.offset((page - 1) * per_page).limit(per_page).all()

    out = []
    for r in regs:
        e = r.event
        out.append({
            'registration_id': r.id,
            'status': r.status,
            'registered_at': r.created_at.isoformat() if r.created_at else None,
            'event': {
                'id': e.id,
                'title': e.title,
                'description': e.description,
                'start': e.start_datetime.isoformat() if e.start_datetime else None,
                'end': e.end_datetime.isoformat() if e.end_datetime else None,
                'location': e.location,
            }
        })

    return jsonify({
        'page': page,
        'per_page': per_page,
        'total': total,
        'pages': (total + per_page - 1) // per_page,
        'registrations': out
    })


@events_bp.route('/events/<int:event_id>')
def event_detail(event_id):
    event = Event.query.get_or_404(event_id)
    return render_template('event_detail.html', event=event)


@events_bp.route('/events/create', methods=['GET', 'POST'])
@login_required
def create_event():
    if request.method == 'POST':
        payload = parse_event_data(request.form)
        if payload['errors']:
            for error in payload['errors']:
                flash(error)
            return render_template('create_event.html', form=payload['raw'])

        event = Event(
            title=payload['title'],
            description=payload['description'],
            start_datetime=payload['start_datetime'],
            end_datetime=payload['end_datetime'],
            location=payload['location'],
            capacity=payload['capacity'],
            host_id=session['user_id']
        )
        db.session.add(event)
        db.session.commit()
        flash('Event created successfully.')
        return redirect(url_for('events.event_detail', event_id=event.id))

    return render_template('create_event.html', form={})


@events_bp.route('/events/<int:event_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_event(event_id):
    event = Event.query.get_or_404(event_id)
    if event.host_id != session['user_id']:
        flash('Only the event host can edit this event.')
        return redirect(url_for('events.event_detail', event_id=event.id))

    if request.method == 'POST':
        payload = parse_event_data(request.form)
        if payload['errors']:
            for error in payload['errors']:
                flash(error)
            return render_template('edit_event.html', event=event, form=payload['raw'])

        event.title = payload['title']
        event.description = payload['description']
        event.start_datetime = payload['start_datetime']
        event.end_datetime = payload['end_datetime']
        event.location = payload['location']
        event.capacity = payload['capacity']
        db.session.commit()
        flash('Event updated successfully.')
        return redirect(url_for('events.event_detail', event_id=event.id))

    return render_template('edit_event.html', event=event, form={})


@events_bp.route('/events/<int:event_id>/delete', methods=['POST'])
@login_required
def delete_event(event_id):
    event = Event.query.get_or_404(event_id)
    if event.host_id != session['user_id']:
        flash('Only the event host can delete this event.')
        return redirect(url_for('events.event_detail', event_id=event.id))

    db.session.delete(event)
    db.session.commit()
    flash('Event deleted successfully.')
    return redirect(url_for('events.events_list'))


@events_bp.route('/events/<int:event_id>/rsvp', methods=['POST'])
def rsvp(event_id):
    if 'user_id' not in session:
        return jsonify({'error': 'authentication required'}), 401

    user_id = session['user_id']
    event = Event.query.get_or_404(event_id)

    existing = Registration.query.filter_by(user_id=user_id, event_id=event.id).first()
    if existing:
        return jsonify({'status': 'already_registered'})

    if event.capacity is not None:
        current_count = Registration.query.filter_by(event_id=event.id).count()
        if current_count >= event.capacity:
            return jsonify({'error': 'This event is full.'}), 400

    reg = Registration(user_id=user_id, event_id=event.id)
    db.session.add(reg)
    db.session.commit()
    return jsonify({'status': 'registered'})


@events_bp.route('/events/<int:event_id>/cancel', methods=['POST'])
def cancel_registration(event_id):
    if 'user_id' not in session:
        return jsonify({'error': 'authentication required'}), 401

    registration = Registration.query.filter_by(user_id=session['user_id'], event_id=event_id).first()
    if not registration:
        return jsonify({'error': 'not_registered'}), 404

    db.session.delete(registration)
    db.session.commit()
    return jsonify({'status': 'cancelled'})


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
