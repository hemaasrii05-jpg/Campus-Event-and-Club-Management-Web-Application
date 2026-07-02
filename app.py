from datetime import datetime
from flask import Flask, render_template
from models import db, User, Club, Event
from routes.events import events_bp
from routes.auth import auth_bp

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = 'supersecretkey123'

# Link the database instance (from models.py) to this Flask app
db.init_app(app)

# Register both blueprint components with Flask
app.register_blueprint(events_bp)
app.register_blueprint(auth_bp)

with app.app_context():
    db.create_all()

    admin = User.query.filter_by(email='admin@example.com').first()
    if not admin:
        admin = User(username='admin', email='admin@example.com', password='admin123')
        db.session.add(admin)
        db.session.commit()

    if not Club.query.first():
        db.session.add_all([
            Club(name='Robotics Club', description='Students learn robotics, coding, electronics, and smart technology projects.'),
            Club(name='Coding Club', description='Students learn programming, websites, applications, and software development.'),
            Club(name='Debate Club', description='Students improve public speaking, confidence, and critical thinking skills.')
        ])

    if not Event.query.first():
        db.session.add(Event(
            title='Campus Orientation',
            description='Welcome event for students to learn about clubs and campus life.',
            start_datetime=datetime.utcnow(),
            location='Main Auditorium',
            capacity=100,
            host_id=admin.id
        ))

    db.session.commit()


@app.route('/')
def home():
    return render_template('home.html')


if __name__ == '__main__':
    app.run(debug=True)