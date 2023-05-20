import unittest
import sys
import logging
from os import getcwd
from flask import session
from app.app import app

sys.path.append("./app/*")
print(sys.path)
print(getcwd)


class TestPages(unittest.TestCase):
    def setUp(self):
        app.testing = True
        self.client = app.test_client()

    def test_home(self):

        """homepage test"""
        result = self.client.get("/")

    def test_register(self):
        """Register page test"""
        result = self.client.get("/register")

    def test_login(self):
        """Login page test"""
        result = self.client.get("/login")

    def test_logout(self):
        """Logout page test"""
        result = self.client.get("/logout")

    def test_pwdchange(self):
        """password change page test"""
        result = self.client.get("/pwdchange")

    def test_dest(self):
        """Destinations page test"""
        with self.client.session_transaction() as session:
            session["user_id"] = "1"
        result = self.client.get("/dest")


if __name__ == "__main__":
    unittest.main()
