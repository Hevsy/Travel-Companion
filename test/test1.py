import app
import unittest


class TestPages(unittest.TestCase):
    def setUp(self):
        app.app.testing = True
        self.app = app.app.test_client()

    def test_home(self):
        """homepage test"""
        result = self.app.get("/")

    def test_register(self):
        """Register page test"""
        result = self.app.get("/register")

    def test_login(self):
        """Login page test"""
        result = self.app.get("/login")

    def test_logout(self):
        """Logout page test"""
        result = self.app.get("/logout")

    def test_pwdchange(self):
        """password change page test"""
        result = self.app.get("/pwdchange")
