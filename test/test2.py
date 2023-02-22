import app
import unittest


class TestRegister(unittest.TestCase):

    def setUp(self):
        app.app.testing = True
        self.app = app.app.test_client()

    def test_register(self):
        result = self.app.get('/register')
        # Make your assertions