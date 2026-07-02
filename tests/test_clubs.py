import unittest

from app import app, db
from models import User


class ClubDashboardTests(unittest.TestCase):
    def setUp(self):
        self.app = app
        self.app.config.update(
            TESTING=True,
            SQLALCHEMY_DATABASE_URI='sqlite:///:memory:'
        )
        self.client = self.app.test_client()
        with self.app.app_context():
            db.drop_all()
            db.create_all()
            user = User(username='clubuser', email='club@example.com', password='hashed')
            db.session.add(user)
            db.session.commit()
            self.user_id = user.id

    def test_user_can_create_and_view_registered_club(self):
        with self.client.session_transaction() as session:
            session['user_id'] = self.user_id
            session['username'] = 'clubuser'

        response = self.client.post('/create_club', data={
            'club_name': 'Robotics Club',
            'club_desc': 'Build robots and learn coding.'
        }, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Robotics Club', response.data)
        self.assertIn(b'Leave', response.data)


if __name__ == '__main__':
    unittest.main()
