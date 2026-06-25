from datetime import datetime
from flask import Flask, render_template
from werkzeug.security import generate_password_hash
from models import db, User, Event
from routes.events import events_bp
from routes.auth import auth_bp

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = 'supersecretkey123'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Link the database instance (from models.py) to this Flask app
db.init_app(app)

app.register_blueprint(events_bp)
app.register_blueprint(auth_bp)

@app.template_filter('format_datetime')
def format_datetime(value, fmt='%b %d, %Y %I:%M %p'):
    if value is None:
        return ''
    return value.strftime(fmt)

@app.template_filter('datetime_local')
def datetime_local(value):
    if value is None:
        return ''
    return value.strftime('%Y-%m-%dT%H:%M')

with app.app_context():
    db.create_all()

    if not User.query.first():
        demo_user = User(
            username='demo_user',
            email='demo@example.com',
            password=generate_password_hash('demo123')
        )
        db.session.add(demo_user)
        db.session.commit()
    else:
        demo_user = User.query.first()

    if not Event.query.first():
        sample_events = [
            Event(
                title='Campus Orientation',
                description='Join us for a welcome orientation and campus tour.',
                start_datetime=datetime(2026, 7, 1, 10, 0),
                end_datetime=datetime(2026, 7, 1, 12, 0),
                location='Main Hall',
                capacity=200,
                host_id=demo_user.id
            ),
            Event(
                title='Coding Workshop',
                description='Hands-on Python and Flask workshop for students.',
                start_datetime=datetime(2026, 7, 3, 14, 0),
                end_datetime=datetime(2026, 7, 3, 17, 0),
                location='Computer Lab',
                capacity=50,
                host_id=demo_user.id
            ),
            Event(
                title='Club Fair',
                description='Visit club booths and register for your favorite campus clubs.',
                start_datetime=datetime(2026, 7, 8, 11, 0),
                end_datetime=datetime(2026, 7, 8, 15, 0),
                location='Student Plaza',
                capacity=300,
                host_id=demo_user.id
            )
        ]
        db.session.bulk_save_objects(sample_events)
        db.session.commit()


@app.route('/')
def home():
    return render_template('home.html')


if __name__ == '__main__':
    app.run(debug=True)