from flask import Flask, render_template, request, redirect, session
from models import db
from routes.events import events_bp

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = 'supersecretkey123'

db.init_app(app)

app.register_blueprint(events_bp)

with app.app_context():
    db.create_all()


@app.route('/')
def home():
    return render_template('home.html')


if __name__ == '__main__':
    app.run(debug=True)
