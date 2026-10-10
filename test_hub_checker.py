import unittest
import tempfile
from pathlib import Path
from unittest.mock import Mock
import requests
from hub_checker import read_config, check_authentication

class HubCheckerTests(unittest.TestCase):
    def setUp(self):
        self.config = {
            "base_url": "http://localhost:5000",
            "basic_username": "sensor_admin",
            "basic_password": "homehub_pass",
            "bearer_token": "smart-home-demo-token",
            "timeout": 3,
        }

    def test_read_config(self):
        content = (
            "base_url=http://localhost:5000\n"
            "basic_username=user\nbasic_password=pass\n"
            "bearer_token=token\ntimeout=5\n"
        )
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "config.txt"
            path.write_text(content, encoding="utf-8")
            self.assertEqual(read_config(path)["timeout"], 5.0)

    def test_both_auth_methods_pass(self):
        session = Mock()
        session.get.side_effect = [Mock(status_code=200), Mock(status_code=200)]
        result = check_authentication(self.config, session)
        self.assertTrue(result["valid"])
        self.assertEqual(session.get.call_args_list[0].kwargs["auth"],
                         ("sensor_admin", "homehub_pass"))
        self.assertEqual(
            session.get.call_args_list[1].kwargs["headers"]["Authorization"],
            "Bearer smart-home-demo-token",
        )

    def test_basic_failure(self):
        session = Mock()
        session.get.side_effect = [Mock(status_code=401), Mock(status_code=200)]
        result = check_authentication(self.config, session)
        self.assertFalse(result["valid"])

    def test_bearer_failure(self):
        session = Mock()
        session.get.side_effect = [Mock(status_code=200), Mock(status_code=401)]
        result = check_authentication(self.config, session)
        self.assertFalse(result["valid"])

    def test_network_error(self):
        session = Mock()
        session.get.side_effect = [
            requests.ConnectionError("offline"), Mock(status_code=200)
        ]
        result = check_authentication(self.config, session)
        self.assertFalse(result["basic"])
        self.assertFalse(result["valid"])

if __name__ == "__main__":
    unittest.main()
