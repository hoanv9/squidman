import unittest
from app.models.client import Client

class TestClientModel(unittest.TestCase):

    def setUp(self):
        self.client = Client(ip_address="192.168.1.1", allowed_domains=["http://example.com"], expiration_date="2023-12-31")

    def test_client_creation(self):
        self.assertEqual(self.client.ip_address, "192.168.1.1")
        self.assertEqual(self.client.allowed_domains, ["http://example.com"])
        self.assertEqual(self.client.expiration_date, "2023-12-31")

    def test_client_expiration(self):
        self.client.expiration_date = "2023-01-01"
        self.assertTrue(self.client.is_expired())

    def test_invalid_ip_address(self):
        with self.assertRaises(ValueError):
            Client(ip_address="invalid_ip", allowed_domains=["http://example.com"], expiration_date="2023-12-31")

    def test_invalid_domain(self):
        with self.assertRaises(ValueError):
            Client(ip_address="192.168.1.1", allowed_domains=["invalid_domain"], expiration_date="2023-12-31")

    def test_expiration_date_format(self):
        with self.assertRaises(ValueError):
            Client(ip_address="192.168.1.1", allowed_domains=["http://example.com"], expiration_date="12-31-2023")

if __name__ == '__main__':
    unittest.main()