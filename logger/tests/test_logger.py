"""Tests for logger module."""

from my_logger import get_logger


class TestLogger:
    """Tests for logger functions."""

    def test_get_logger_returns_logger(self):
        """Test that get_logger returns a logger instance."""
        logger = get_logger(__name__)

        assert logger is not None
        assert hasattr(logger, "info")
        assert hasattr(logger, "debug")
        assert hasattr(logger, "error")

    def test_get_logger_with_different_names(self):
        """Test that get_logger can be called with different names."""
        logger1 = get_logger("test.module1")
        logger2 = get_logger("test.module2")

        assert logger1 is not None
        assert logger2 is not None

    def test_logger_can_log_message(self, capsys):
        """Test that logger can log a message without error."""
        logger = get_logger("test.logging")

        # Should not raise any exception
        logger.info("test message", extra_field="value")
