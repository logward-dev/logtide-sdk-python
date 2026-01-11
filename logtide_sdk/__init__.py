"""LogTide SDK - Official Python SDK for LogTide."""

from .client import LogTideClient
from .enums import CircuitState, LogLevel
from .exceptions import BufferFullError, CircuitBreakerOpenError, LogTideError
from .models import (
    AggregatedStatsOptions,
    AggregatedStatsResponse,
    ClientMetrics,
    ClientOptions,
    LogEntry,
    LogsResponse,
    QueryOptions,
)

__version__ = "0.1.0"

__all__ = [
    # Client
    "LogTideClient",
    # Models
    "LogEntry",
    "ClientOptions",
    "QueryOptions",
    "AggregatedStatsOptions",
    "ClientMetrics",
    "LogsResponse",
    "AggregatedStatsResponse",
    # Enums
    "LogLevel",
    "CircuitState",
    # Exceptions
    "LogTideError",
    "CircuitBreakerOpenError",
    "BufferFullError",
]
