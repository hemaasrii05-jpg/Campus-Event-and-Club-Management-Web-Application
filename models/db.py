from pathlib import Path

from flask_sqlalchemy import SQLAlchemy

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / 'instance' / 'database.db'

# Shared SQLAlchemy instance used by the application models.
db = SQLAlchemy()


def get_database_uri(database_path=None):
    if database_path is None:
        database_path = DB_PATH
    return f"sqlite:///{database_path}"


def init_db(app, database_uri=None):
    if database_uri is None:
        database_uri = get_database_uri()

    app.config.setdefault('SQLALCHEMY_DATABASE_URI', database_uri)
    app.config.setdefault('SQLALCHEMY_TRACK_MODIFICATIONS', False)
    db.init_app(app)
    return db


def create_tables(app):
    with app.app_context():
        db.create_all()
