import unittest

from app.services.redaction import redact_headers


class RedactionTests(unittest.TestCase):
    def test_redacts_sensitive_headers(self) -> None:
        headers = {
            'Authorization': 'Bearer secret-token',
            'X-Api-Key': 'top-secret',
            'Content-Type': 'application/json',
        }

        redacted = redact_headers(headers)

        self.assertEqual(redacted['Authorization'], '[REDACTED]')
        self.assertEqual(redacted['X-Api-Key'], '[REDACTED]')
        self.assertEqual(redacted['Content-Type'], 'application/json')


if __name__ == '__main__':
    unittest.main()
