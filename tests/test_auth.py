import unittest

from app import app, db
from models import User


class AuthPasswordResetTests(unittest.TestCase):
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
            user = User(username='tester', email='Demo@Example.com', password='hashed')
            db.session.add(user)
            db.session.commit()

    def test_forgot_password_accepts_case_insensitive_email(self):
        response = self.client.post('/forgot-password', data={
            'email': 'demo@example.com',
            'new_password': 'newpass123',
            'confirm_password': 'newpass123'
        }, follow_redirects=True)

        self.assertIn(b'Password reset successfully', response.data)

    def test_login_accepts_plain_text_passwords(self):
        with self.app.app_context():
            user = User(username='legacy', email='legacy@example.com', password='legacy123')
            db.session.add(user)
            db.session.commit()

        response = self.client.post('/login', data={
            'email': 'legacy@example.com',
            'password': 'legacy123'
        }, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Student Dashboard', response.data)


if __name__ == '__main__':
    unittest.main()
