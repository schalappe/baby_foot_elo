# -*- coding: utf-8 -*-
"""
Unit tests for retry logic.
"""

from unittest import TestCase, main
from unittest.mock import MagicMock, call, patch

from app.db.retry import with_retry


class TestWithRetryDecorator(TestCase):
    """Tests for the with_retry decorator."""

    @patch("app.db.retry.sleep", return_value=None)
    def test_retry_success_first_try(self, mock_sleep):
        """Test that the function succeeds on the first attempt."""
        mock_func = MagicMock(return_value="Success")

        @with_retry(max_retries=3, retry_delay=0.1)
        def decorated_func():
            return mock_func()

        result = decorated_func()

        self.assertEqual(result, "Success")
        mock_func.assert_called_once()
        mock_sleep.assert_not_called()

    @patch("app.db.retry.sleep", return_value=None)
    def test_retry_success_after_failure(self, mock_sleep):
        """Test that the function succeeds after a few retries."""
        mock_func = MagicMock()
        mock_func.side_effect = [
            ValueError("Temporary Error"),
            ValueError("Another Error"),
            "Success",
        ]

        @with_retry(max_retries=4, retry_delay=0.2)
        def decorated_func(arg1, kwarg1="default"):
            return mock_func(arg1, kwarg1=kwarg1)

        result = decorated_func("test_arg", kwarg1="test_kwarg")

        self.assertEqual(result, "Success")
        self.assertEqual(mock_func.call_count, 3)
        expected_calls = [
            call("test_arg", kwarg1="test_kwarg"),
            call("test_arg", kwarg1="test_kwarg"),
            call("test_arg", kwarg1="test_kwarg"),
        ]
        mock_func.assert_has_calls(expected_calls)

        # ##: Check that sleep was called twice with the correct delay.
        expected_sleep_calls = [call(0.2), call(0.2)]
        mock_sleep.assert_has_calls(expected_sleep_calls)
        self.assertEqual(mock_sleep.call_count, 2)

    @patch("app.db.retry.sleep", return_value=None)
    def test_retry_all_attempts_fail(self, mock_sleep):
        """Test that the function raises the last exception after all retries fail."""
        mock_func = MagicMock()
        final_exception = ConnectionError("Persistent Error")
        mock_func.side_effect = [ValueError("Error 1"), TimeoutError("Error 2"), final_exception]

        @with_retry(max_retries=3, retry_delay=0.05)
        def decorated_func():
            return mock_func()

        with self.assertRaises(ConnectionError) as cm:
            decorated_func()

        self.assertEqual(cm.exception, final_exception)
        self.assertEqual(mock_func.call_count, 3)

        # ##: Check sleep was called twice (between 3 attempts).
        expected_sleep_calls = [call(0.05), call(0.05)]
        mock_sleep.assert_has_calls(expected_sleep_calls)
        self.assertEqual(mock_sleep.call_count, 2)

    @patch("app.db.retry.sleep", return_value=None)
    def test_retry_with_zero_retries(self, mock_sleep):
        """Test behavior when max_retries is 1 (no actual retries)."""
        mock_func = MagicMock(side_effect=RuntimeError("Fail"))

        @with_retry(max_retries=1, retry_delay=0.1)
        def decorated_func():
            return mock_func()

        with self.assertRaises(RuntimeError):
            decorated_func()

        mock_func.assert_called_once()
        mock_sleep.assert_not_called()


if __name__ == "__main__":
    main()
