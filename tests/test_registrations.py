import json
from datetime import datetime

import pytest

from app import app, db
from models import User, Event, Registration


@pytest.fixture
def client():
    with app.test_client() as client:
        yield client


def create_user_and_regs():
    # create a test user and several events/registrations
    user = User(username='test_user_x', email='test_user_x@example.com', password='pwd')
    db.session.add(user)
    db.session.flush()

    for i in range(12):
        e = Event(title=f'Test Event {i}', description='desc', start_datetime=datetime.utcnow(), host_id=user.id)
        db.session.add(e)
        db.session.flush()
        reg = Registration(user_id=user.id, event_id=e.id)
        db.session.add(reg)

    db.session.commit()
    return user


def test_api_my_registrations_requires_auth(client):
    res = client.get('/api/my-registrations')
    assert res.status_code == 401


def test_api_my_registrations_pagination(client):
    with app.app_context():
        user = create_user_and_regs()

    with client.session_transaction() as sess:
        sess['user_id'] = user.id

    res = client.get('/api/my-registrations?page=1&per_page=5')
    assert res.status_code == 200
    data = res.get_json()
    assert data['page'] == 1
    assert data['per_page'] == 5
    assert data['total'] >= 12
    assert len(data['registrations']) == 5
