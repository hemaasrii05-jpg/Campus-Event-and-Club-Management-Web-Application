from flask import Blueprint, render_template, request, redirect, session, flash, url_for
from sqlalchemy import func
from models import db, User, Event, Club, ClubMember
from werkzeug.security import generate_password_hash, check_password_hash

auth_bp = Blueprint('auth', __name__)


def normalize_email(email):
    return (email or '').strip().lower()


def verify_password(stored_password, provided_password):
    if not stored_password or not provided_password:
        return False

    if stored_password.startswith(('pbkdf2:', 'scrypt:', 'sha256$')):
        try:
            return check_password_hash(stored_password, provided_password)
        except ValueError:
            return False

    return stored_password == provided_password


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = normalize_email(request.form.get('email', ''))
        password = request.form.get('password', '')

        user = User.query.filter(func.lower(User.email) == email).first()
        if user and verify_password(user.password, password):
            session['user_id'] = user.id
            session['username'] = user.username
            return redirect(url_for('auth.dashboard'))

        flash('Invalid email or password. Please try again.')

    return render_template('login.html')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = normalize_email(request.form.get('email', ''))
        password = request.form.get('password', '')

        if not username or not email or not password:
            flash('Please fill in all required fields.')
            return render_template('register.html')

        existing_user = User.query.filter(func.lower(User.email) == email).first()
        if existing_user:
            flash('Email already registered. Please use a different email.')
            return render_template('register.html')

        new_user = User(
            username=username,
            email=email,
            password=generate_password_hash(password)
        )
        db.session.add(new_user)
        db.session.commit()

        session['user_id'] = new_user.id
        session['username'] = new_user.username
        return redirect(url_for('auth.dashboard'))

    return render_template('register.html')


@auth_bp.route('/dashboard')
def dashboard():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('auth.login'))

    user = User.query.get(user_id)
    if not user:
        session.clear()
        return redirect(url_for('auth.login'))

    events = Event.query.order_by(Event.start_datetime.asc()).all()
    clubs = [membership.club for membership in user.club_memberships]

    return render_template('dashboard.html', events=events, clubs=clubs)


@auth_bp.route('/create_club', methods=['GET', 'POST'])
def create_club():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        club_name = request.form.get('club_name', '').strip()
        club_desc = request.form.get('club_desc', '').strip()

        if not club_name:
            flash('Club name is required.')
            return render_template('create_club.html')

        club = Club(name=club_name, description=club_desc, created_by_id=user_id)
        db.session.add(club)
        db.session.flush()

        membership = ClubMember(user_id=user_id, club_id=club.id, role='owner')
        db.session.add(membership)
        db.session.commit()

        flash('Club created successfully.')
        return redirect(url_for('auth.dashboard'))

    return render_template('create_club.html')


@auth_bp.route('/clubs/<int:club_id>')
def club_detail(club_id):
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('auth.login'))

    membership = ClubMember.query.filter_by(user_id=user_id, club_id=club_id).first()
    if not membership:
        flash('You are not a member of that club.')
        return redirect(url_for('auth.dashboard'))

    club = Club.query.get_or_404(club_id)
    return render_template('club_detail.html', club=club, membership=membership)


@auth_bp.route('/clubs/<int:club_id>/leave', methods=['POST'])
def leave_club(club_id):
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('auth.login'))

    membership = ClubMember.query.filter_by(user_id=user_id, club_id=club_id).first()
    if not membership:
        flash('You are not a member of that club.')
        return redirect(url_for('auth.dashboard'))

    if membership.role == 'owner':
        remaining_members = ClubMember.query.filter(ClubMember.club_id == club_id, ClubMember.user_id != user_id).first()
        if remaining_members:
            remaining_members.role = 'owner'
        else:
            club = Club.query.get(club_id)
            if club:
                db.session.delete(club)
                db.session.commit()
                flash('Club deleted because you were the only member.')
                return redirect(url_for('auth.dashboard'))

    db.session.delete(membership)
    db.session.commit()
    flash('You left the club.')
    return redirect(url_for('auth.dashboard'))


@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = normalize_email(request.form.get('email', ''))
        new_password = request.form.get('new_password', '')
        confirm_password = request.form.get('confirm_password', '')

        if not email or not new_password or not confirm_password:
            flash('Please fill in all fields.')
            return render_template('forgot_password.html')

        if len(new_password) < 4:
            flash('Password should be at least 4 characters long.')
            return render_template('forgot_password.html')

        if new_password != confirm_password:
            flash('Passwords do not match.')
            return render_template('forgot_password.html')

        user = User.query.filter(func.lower(User.email) == email).first()
        if not user:
            flash('No account found with that email address.')
            return render_template('forgot_password.html')

        user.password = generate_password_hash(new_password)
        db.session.commit()

        flash('Password reset successfully. You can now log in.')
        return redirect(url_for('auth.login'))

    return render_template('forgot_password.html')


@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect('/')
