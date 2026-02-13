import unittest

from worker.retry import compute_backoff


class RetryPolicyTests(unittest.TestCase):
    def test_backoff_grows_exponentially(self) -> None:
        self.assertEqual(compute_backoff(1, 1.0, 30.0), 1.0)
        self.assertEqual(compute_backoff(2, 1.0, 30.0), 2.0)
        self.assertEqual(compute_backoff(3, 1.0, 30.0), 4.0)

    def test_backoff_is_capped(self) -> None:
        self.assertEqual(compute_backoff(10, 1.0, 5.0), 5.0)

    def test_invalid_attempt_raises(self) -> None:
        with self.assertRaises(ValueError):
            compute_backoff(0, 1.0, 30.0)


if __name__ == '__main__':
    unittest.main()
