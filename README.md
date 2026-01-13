<p align="center">
  <img src="https://raw.githubusercontent.com/logtide-dev/logtide/main/docs/images/logo.png" alt="LogTide Logo" width="400">
</p>

<h1 align="center">LogTide Python SDK</h1>

<p align="center">
  <a href="https://pypi.org/project/logtide-sdk/"><img src="https://img.shields.io/pypi/v/logtide-sdk?color=blue" alt="PyPI"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-blue.svg" alt="License"></a>
  <a href="https://www.python.org/"><img src="https://img.shields.io/badge/Python-3.8+-blue.svg" alt="Python"></a>
  <a href="https://github.com/logtide-dev/logtide-sdk-python/releases"><img src="https://img.shields.io/github/v/release/logtide-dev/logtide-sdk-python" alt="Release"></a>
</p>

<p align="center">
  Official Python SDK for <a href="https://logtide.dev">LogTide</a> with automatic batching, retry logic, circuit breaker, query API, live streaming, and middleware support.
</p>

---

## Features

- **Automatic batching** with configurable size and interval
- **Retry logic** with exponential backoff
- **Circuit breaker** pattern for fault tolerance
- **Max buffer size** with drop policy to prevent memory leaks
- **Query API** for searching and filtering logs
- **Live tail** with Server-Sent Events (SSE)
- **Trace ID context** for distributed tracing
- **Global metadata** added to all logs
- **Structured error serialization**
- **Internal metrics** (logs sent, errors, latency, etc.)
- **Flask, Django & FastAPI middleware** for auto-logging HTTP requests
- **Full Python 3.8+ support** with type hints

## Requirements

- Python 3.8 or higher
- pip or poetry

## Installation

```bash
pip install logtide-sdk
```

### Optional Dependencies

```bash
# For async support
pip install logtide-sdk[async]

# For Flask middleware
pip install logtide-sdk[flask]

# For Django middleware
pip install logtide-sdk[django]

# For FastAPI middleware
pip install logtide-sdk[fastapi]

# Install all extras
pip install logtide-sdk[async,flask,django,fastapi]
```

## Quick Start

```python
from logtide_sdk import LogTideClient, ClientOptions

client = LogTideClient(
    ClientOptions(
        api_url='http://localhost:8080',
        api_key='lp_your_api_key_here',
    )
)

# Send logs
client.info('api-gateway', 'Server started', {'port': 3000})
client.error('database', 'Connection failed', Exception('Timeout'))

# Graceful shutdown (automatic via atexit, but can be called manually)
client.close()
```

---

## Configuration Options

### Basic Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `api_url` | `str` | **required** | Base URL of your LogTide instance |
| `api_key` | `str` | **required** | Project API key (starts with `lp_`) |
| `batch_size` | `int` | `100` | Number of logs to batch before sending |
| `flush_interval` | `int` | `5000` | Interval in ms to auto-flush logs |

### Advanced Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `max_buffer_size` | `int` | `10000` | Max logs in buffer (prevents memory leak) |
| `max_retries` | `int` | `3` | Max retry attempts on failure |
| `retry_delay_ms` | `int` | `1000` | Initial retry delay (exponential backoff) |
| `circuit_breaker_threshold` | `int` | `5` | Failures before opening circuit |
| `circuit_breaker_reset_ms` | `int` | `30000` | Time before retrying after circuit opens |
| `enable_metrics` | `bool` | `True` | Track internal metrics |
| `debug` | `bool` | `False` | Enable debug logging to console |
| `global_metadata` | `dict` | `{}` | Metadata added to all logs |
| `auto_trace_id` | `bool` | `False` | Auto-generate trace IDs for logs |

### Example: Full Configuration

```python
import os

client = LogTideClient(
    ClientOptions(
        api_url='http://localhost:8080',
        api_key='lp_your_api_key_here',

        # Batching
        batch_size=100,
        flush_interval=5000,

        # Buffer management
        max_buffer_size=10000,

        # Retry with exponential backoff (1s -> 2s -> 4s)
        max_retries=3,
        retry_delay_ms=1000,

        # Circuit breaker
        circuit_breaker_threshold=5,
        circuit_breaker_reset_ms=30000,

        # Metrics & debugging
        enable_metrics=True,
        debug=True,

        # Global context
        global_metadata={
            'env': os.getenv('APP_ENV'),
            'version': '1.0.0',
            'hostname': os.uname().nodename,
        },

        # Auto trace IDs
        auto_trace_id=False,
    )
)
```

---

## Logging Methods

### Basic Logging

```python
from logtide_sdk import LogLevel

client.debug('service-name', 'Debug message')
client.info('service-name', 'Info message', {'userId': 123})
client.warn('service-name', 'Warning message')
client.error('service-name', 'Error message', {'custom': 'data'})
client.critical('service-name', 'Critical message')
```

### Error Logging with Auto-Serialization

The SDK automatically serializes `Exception` objects:

```python
try:
    raise RuntimeError('Database timeout')
except Exception as e:
    # Automatically serializes error with stack trace
    client.error('database', 'Query failed', e)
```

Generated log metadata:
```json
{
  "error": {
    "name": "RuntimeError",
    "message": "Database timeout",
    "stack": "Traceback (most recent call last):\n  ..."
  }
}
```

---

## Trace ID Context

Track requests across services with trace IDs.

### Manual Trace ID

```python
client.set_trace_id('request-123')

client.info('api', 'Request received')
client.info('database', 'Querying users')
client.info('api', 'Response sent')

client.set_trace_id(None)  # Clear context
```

### Scoped Trace ID (Context Manager)

```python
with client.with_trace_id('request-456'):
    client.info('api', 'Processing in context')
    client.warn('cache', 'Cache miss')
# Trace ID automatically restored after context
```

### Auto-Generated Trace ID

```python
with client.with_new_trace_id():
    client.info('worker', 'Background job started')
    client.info('worker', 'Job completed')
```

---

## Query API

Search and retrieve logs programmatically.

### Basic Query

```python
from datetime import datetime, timedelta
from logtide_sdk import QueryOptions, LogLevel

result = client.query(
    QueryOptions(
        service='api-gateway',
        level=LogLevel.ERROR,
        from_time=datetime.now() - timedelta(hours=24),
        to_time=datetime.now(),
        limit=100,
        offset=0,
    )
)

print(f"Found {result.total} logs")
for log in result.logs:
    print(log)
```

### Full-Text Search

```python
result = client.query(QueryOptions(q='timeout', limit=50))
```

### Get Logs by Trace ID

```python
logs = client.get_by_trace_id('trace-123')
print(f"Trace has {len(logs)} logs")
```

### Aggregated Statistics

```python
from datetime import datetime, timedelta
from logtide_sdk import AggregatedStatsOptions

stats = client.get_aggregated_stats(
    AggregatedStatsOptions(
        from_time=datetime.now() - timedelta(days=7),
        to_time=datetime.now(),
        interval='1h',
    )
)

for service in stats.top_services:
    print(f"{service['service']}: {service['count']} logs")
```

---

## Live Streaming (SSE)

Stream logs in real-time using Server-Sent Events.

```python
def handle_log(log):
    print(f"[{log['time']}] {log['level']}: {log['message']}")

def handle_error(error):
    print(f"Stream error: {error}")

client.stream(
    on_log=handle_log,
    on_error=handle_error,
    filters={
        'service': 'api-gateway',
        'level': 'error',
    }
)

# Note: This blocks. Run in separate thread for production.
```

---

## Metrics

Track SDK performance and health.

```python
metrics = client.get_metrics()

print(f"Logs sent: {metrics.logs_sent}")
print(f"Logs dropped: {metrics.logs_dropped}")
print(f"Errors: {metrics.errors}")
print(f"Retries: {metrics.retries}")
print(f"Avg latency: {metrics.avg_latency_ms}ms")
print(f"Circuit breaker trips: {metrics.circuit_breaker_trips}")

# Get circuit breaker state
print(client.get_circuit_breaker_state())  # CLOSED|OPEN|HALF_OPEN

# Reset metrics
client.reset_metrics()
```

---

## Middleware Integration

LogTide provides ready-to-use middleware for popular frameworks.

### Flask Middleware

Auto-log all HTTP requests and responses.

```python
from flask import Flask
from logtide_sdk import LogTideClient, ClientOptions
from logtide_sdk.middleware import LogTideFlaskMiddleware

app = Flask(__name__)

client = LogTideClient(
    ClientOptions(
        api_url='http://localhost:8080',
        api_key='lp_your_api_key_here',
    )
)

LogTideFlaskMiddleware(
    app,
    client=client,
    service_name='flask-api',
    log_requests=True,
    log_responses=True,
    skip_paths=['/metrics'],
)
```

**Logged automatically:**
- Request: `GET /api/users`
- Response: `GET /api/users 200 (45ms)`
- Errors: `Request error: Internal Server Error`

### Django Middleware

```python
# settings.py
MIDDLEWARE = [
    'logtide_sdk.middleware.LogTideDjangoMiddleware',
]

from logtide_sdk import LogTideClient, ClientOptions

LOGTIDE_CLIENT = LogTideClient(
    ClientOptions(
        api_url='http://localhost:8080',
        api_key='lp_your_api_key_here',
    )
)
LOGTIDE_SERVICE_NAME = 'django-api'
```

### FastAPI Middleware

```python
from fastapi import FastAPI
from logtide_sdk import LogTideClient, ClientOptions
from logtide_sdk.middleware import LogTideFastAPIMiddleware

app = FastAPI()

client = LogTideClient(
    ClientOptions(
        api_url='http://localhost:8080',
        api_key='lp_your_api_key_here',
    )
)

app.add_middleware(
    LogTideFastAPIMiddleware,
    client=client,
    service_name='fastapi-api',
)
```

---

## Examples

See the [examples/](./examples) directory for complete working examples:

- **[basic.py](./examples/basic.py)** - Simple usage
- **[advanced.py](./examples/advanced.py)** - All advanced features
- **[flask_example.py](./examples/flask_example.py)** - Flask integration
- **[fastapi_example.py](./examples/fastapi_example.py)** - FastAPI integration

---

## Best Practices

### 1. Always Close on Shutdown

```python
import atexit

# Automatic cleanup (already registered by client)
# Or manually:
atexit.register(client.close)
```

### 2. Use Global Metadata

```python
client = LogTideClient(
    ClientOptions(
        api_url='http://localhost:8080',
        api_key='lp_your_api_key_here',
        global_metadata={
            'env': os.getenv('ENV'),
            'version': '1.0.0',
            'region': 'us-east-1',
        },
    )
)
```

### 3. Enable Debug Mode in Development

```python
client = LogTideClient(
    ClientOptions(
        api_url='http://localhost:8080',
        api_key='lp_your_api_key_here',
        debug=os.getenv('ENV') == 'development',
    )
)
```

### 4. Monitor Metrics in Production

```python
import time
import threading

def monitor_metrics():
    while True:
        metrics = client.get_metrics()

        if metrics.logs_dropped > 0:
            print(f"Warning: Logs dropped: {metrics.logs_dropped}")

        if metrics.circuit_breaker_trips > 0:
            print("Error: Circuit breaker is OPEN!")

        time.sleep(60)

# Run in background thread
monitor_thread = threading.Thread(target=monitor_metrics, daemon=True)
monitor_thread.start()
```

---

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

MIT License - see [LICENSE](LICENSE) for details.

## Links

- [LogTide Website](https://logtide.dev)
- [Documentation](https://logtide.dev/docs/sdks/python/)
- [GitHub Issues](https://github.com/logtide-dev/logtide-sdk-python/issues)
