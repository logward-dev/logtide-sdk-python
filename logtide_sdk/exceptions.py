"""Custom exceptions for LogTide SDK."""


class LogTideError(Exception):
    """Base exception for LogTide SDK errors."""

    pass


class CircuitBreakerOpenError(LogTideError):
    """Raised when circuit breaker is open."""

    pass


class BufferFullError(LogTideError):
    """Raised when buffer is full and cannot accept more logs."""

    pass
