# OutScope SDK

Python client library for the OutScope API.

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

## Features

- ✅ **Easy to use** - Simple, intuitive API
- ✅ **Pagination support** - Automatic and manual pagination
- ✅ **Error handling** - Detailed error information with retry capabilities
- ✅ **Usage monitoring** - Query limits and usage in real-time
- ✅ **Type hints** - Full type annotation support
- ✅ **Context manager** - Automatic resource cleanup

## Installation

```bash
pip install outscope-sdk
```

Or install from source:

```bash
cd api_client
pip install -e .
```

## Quick Start

```python
from outscope_sdk import Client

# Create a client
client = Client(api_key="your_api_key_here")

# Create a security check
check = client.checks.create(
    fqdn="example.com",
    paths=["/", "/api"],
    ports=[443]
)
print(f"Check created: {check.job_id}")

# Get check status
status = client.checks.get(check.job_id)
print(f"Status: {status['status']}")

# List all checks with automatic pagination
for check in client.checks.list_all():
    print(f"{check['job_id']}: {check['status']}")

# Check your usage
usage = client.usage.get()
print(f"Used: {usage['usage']['checks_used']}/{usage['usage']['checks_limit']}")

# Close the client
client.close()
```

## Authentication

The SDK requires an API key for authentication. You can generate one from your OutScope dashboard.

```python
from outscope_sdk import Client

# Option 1: Direct in code
client = Client(api_key="your_api_key_here")

# Option 2: From environment variable
import os
client = Client(api_key=os.getenv("OUTSCOPE_API_KEY"))
```

## Usage Guide

### Creating Checks

```python
# Basic check
check = client.checks.create(
    fqdn="example.com",
    paths=["/"],
    ports=[443]
)

# Advanced check with multiple paths and ports
check = client.checks.create(
    fqdn="api.example.com",
    paths=["/", "/api/v1", "/health"],
    ports=[80, 443, 8080],
    redirects=True
)

# Privacy-aware check with content sample
check = client.checks.create(
    fqdn="secure.example.com",
    paths=["/"],
    ports=[443],
    include_content_sample=True,           # Enable content sample capture
    content_sample_retention_days=7        # Retain for 7 days (default: 7, max: 30)
)

print(f"Check ID: {check.job_id}")
print(f"Status: {check.status}")
```

### Creating Multiple Checks (Batch)

The SDK includes built-in batch processing with automatic rate limit handling:

```python
# Simple batch creation
result = client.checks.create_batch(
    domains=["example.com", "example.org", "example.net"]
)

print(f"Created: {result['stats']['created']}")
print(f"Failed: {result['stats']['failed']}")
print(f"Duration: {result['duration']:.1f}s")

# Access results
for check in result['results']:
    print(f"{check['domain']}: {check['job_id']}")
```

#### Large Batch with Progress

```python
# Create 1000 checks with automatic handling of all limits
def show_progress(current, total, stats):
    if current % 50 == 0:  # Update every 50 checks
        print(f"Progress: {current}/{total} - Created: {stats['created']}, Failed: {stats['failed']}")

result = client.checks.create_batch(
    domains=[f"site{i}.com" for i in range(1000)],
    paths=["/", "/api"],
    ports=[443],
    include_content_sample=False,     # Don't capture content samples for privacy
    check_usage_first=True,           # Verify quota before starting
    wait_on_limits=True,              # Wait when hitting limits (recommended)
    max_retries=5,                    # Retry up to 5 times per check
    progress_callback=show_progress
)

# Results
print(f"\n✅ Successfully created {result['stats']['created']} checks")
print(f"⏱️  Total time: {result['duration']/60:.1f} minutes")
print(f"📊 Rate limited: {result['stats']['rate_limited']} times")
print(f"📊 Inflight limited: {result['stats']['inflight_limited']} times")
```

**What `create_batch()` does automatically:**
- ✅ Checks your quota before starting
- ✅ Waits when rate limit is hit (30-120 req/min depending on plan)
- ✅ Waits when inflight limit is hit (5-30 concurrent checks depending on plan)
- ✅ Retries automatically on temporary errors
- ✅ Stops if monthly quota is exceeded
- ✅ Provides detailed statistics

**Estimated times for 1000 checks:**
- Starter plan (30/min): ~35 minutes
- Pro plan (60/min): ~18 minutes
- Team plan (120/min): ~9 minutes

### Getting Check Status

```python
# Get a specific check
check = client.checks.get("check_id_here")

print(f"Status: {check['status']}")
print(f"Created: {check['created_at']}")

if check['status'] == 'done':
    print(f"Results: {check['result']}")
```

### Listing Checks

#### Manual Pagination

```python
# Get first page (50 items)
response = client.checks.list(page=1, limit=50)

print(f"Total checks: {response['total']}")
print(f"Page {response['page']} of {response['total'] // response['per_page'] + 1}")

for check in response['items']:
    print(f"- {check['job_id']}: {check['status']}")

# Get next page
response = client.checks.list(page=2, limit=50)
```

#### Automatic Pagination (Recommended)

```python
# Iterate through ALL checks automatically
for check in client.checks.list_all(limit=100):
    print(f"{check['job_id']}: {check['status']}")
```

#### Filtering

```python
# Filter by FQDN
for check in client.checks.list_all(fqdn="example.com"):
    print(f"{check['job_id']}: {check['fqdn_normalized']}")
```

### Monitoring Usage and Limits

```python
# Get current usage
usage = client.usage.get()

# Tenant info
print(f"Tenant: {usage['tenant']['name']}")
print(f"Plan: {usage['tenant']['plan']}")

# Current usage
print(f"\nChecks used: {usage['usage']['checks_used']}/{usage['usage']['checks_limit']}")
print(f"In progress: {usage['usage']['inflight']}")

# Limits
print(f"\nRate limit: {usage['limits']['rate_per_minute']}/min")
print(f"Max inflight: {usage['limits']['max_inflight']}")
print(f"Retention: {usage['limits']['retention_days']} days")

# Check if approaching limits
checks_percent = (usage['usage']['checks_used'] / usage['usage']['checks_limit']) * 100
if checks_percent > 80:
    print("⚠️  Warning: You've used over 80% of your monthly quota!")
```

## Error Handling

The SDK provides detailed error information, especially for rate limiting scenarios.

### Basic Error Handling

```python
from outscope_sdk import Client
from outscope_sdk.exceptions import (
    RateLimitError,
    AuthenticationError,
    NotFoundError,
    ValidationError
)

client = Client(api_key="...")

try:
    check = client.checks.create(fqdn="example.com", paths=["/"], ports=[443])
    
except AuthenticationError as e:
    print(f"Authentication failed: {e.message}")
    
except NotFoundError as e:
    print(f"Resource not found: {e.message}")
    
except ValidationError as e:
    print(f"Validation error: {e.message}")
    print(f"Details: {e.details}")
    
except RateLimitError as e:
    print(f"Rate limit exceeded: {e.message}")
    # Detailed error handling below
```

### Rate Limit Error Handling

The `RateLimitError` provides detailed information about the rate limit:

```python
from outscope_sdk.exceptions import RateLimitError
import time

try:
    check = client.checks.create(...)
    
except RateLimitError as e:
    print(f"Error: {e.message}")
    
    # Check error type
    if e.code == "rate_limit_exceeded":
        # Too many requests per minute
        print(f"Rate limit: {e.limit}/min")
        print(f"Remaining: {e.remaining}")
        print(f"Retry after: {e.retry_after}s")
        print(f"Resets at: {time.ctime(e.reset_at)}")
        
        # Wait and retry
        time.sleep(e.retry_after)
        check = client.checks.create(...)
    
    elif e.code == "inflight_limit":
        # Too many concurrent checks
        print(f"In progress: {e.current}/{e.limit}")
        print(f"Wait for some checks to complete")
        print(f"Suggested retry: {e.retry_after}s")
    
    elif e.code == "checks_limit":
        # Monthly quota exceeded
        print(f"Monthly quota: {e.used}/{e.limit} for {e.period}")
        print(f"Wait until next month or upgrade your plan")
```

### Automatic Retry

Implement automatic retry with exponential backoff:

```python
def create_check_with_retry(client, fqdn, max_retries=3):
    """Create a check with automatic retry on rate limit"""
    for attempt in range(max_retries):
        try:
            return client.checks.create(fqdn=fqdn, paths=["/"], ports=[443])
            
        except RateLimitError as e:
            if attempt == max_retries - 1:
                raise  # Last attempt, re-raise the error
            
            retry_after = e.retry_after or 60
            print(f"Rate limited. Retrying in {retry_after}s... (attempt {attempt+1}/{max_retries})")
            time.sleep(retry_after)

# Use it
check = create_check_with_retry(client, "example.com")
```

### Proactive Limit Checking

Check limits before making requests to avoid errors:

```python
# Check usage before creating checks
usage = client.usage.get()

# Check monthly quota
if usage['usage']['checks_used'] >= usage['usage']['checks_limit']:
    print("❌ Monthly quota exceeded")
    print("   Upgrade your plan or wait until next month")
    exit(1)

# Check concurrent limit
if usage['usage']['inflight'] >= usage['limits']['max_inflight']:
    print(f"❌ Too many checks in progress ({usage['usage']['inflight']}/{usage['limits']['max_inflight']})")
    print("   Wait for some checks to complete")
    exit(1)

# Calculate available quota
remaining = usage['usage']['checks_limit'] - usage['usage']['checks_used']
print(f"✅ You can create {remaining} more checks this month")

# Now create the check
check = client.checks.create(...)
```

## Advanced Usage

### Using Context Manager

The recommended way to use the client is with a context manager for automatic cleanup:

```python
from outscope_sdk import Client

with Client(api_key="...") as client:
    # Your code here
    check = client.checks.create(...)
    usage = client.usage.get()
    
# Client is automatically closed here
```

### Custom Timeout

```python
# Increase timeout for long-running operations
client = Client(
    api_key="...",
    timeout=120.0  # 2 minutes
)
```

### Batch Operations

```python
# Check multiple domains
domains = ["example.com", "example.org", "example.net"]

for domain in domains:
    try:
        check = client.checks.create(fqdn=domain, paths=["/"], ports=[443])
        print(f"✅ {domain}: {check.job_id}")
    except RateLimitError as e:
        print(f"⚠️ {domain}: Rate limited, waiting {e.retry_after}s...")
        time.sleep(e.retry_after)
        check = client.checks.create(fqdn=domain, paths=["/"], ports=[443])
        print(f"✅ {domain}: {check.job_id} (retried)")
```

## API Reference

### Client

```python
Client(api_key: str, base_url: Optional[str] = None, timeout: float = 30.0)
```

#### Attributes

- `checks`: ChecksResource - Manage security checks
- `usage`: UsageResource - Query usage and limits

#### Methods

- `close()`: Close the HTTP client
- `__enter__()`: Context manager entry
- `__exit__()`: Context manager exit

### ChecksResource

#### Methods

##### `create()`

```python
create(
    fqdn: str,
    paths: Optional[List[str]] = None,
    ports: Optional[List[int]] = None,
    redirects: Optional[bool] = None,
    include_content_sample: Optional[bool] = None,
    content_sample_retention_days: Optional[int] = None
) -> Check
```

Create a new security check.

**Parameters:**
- `fqdn`: Fully qualified domain name to check
- `paths`: Paths to check (default: `["/"]`)
- `ports`: Ports to check (default: `[443]`)
- `redirects`: Follow redirects (optional)
- `include_content_sample`: Capture HTTP response content sample (default: `False`)
- `content_sample_retention_days`: Days to retain content sample (default: `7`, max: `30`)

**Returns:** Check object with `job_id` and `status`

**Note:** Content samples may contain sensitive data. Only enable when necessary and use appropriate retention periods.

##### `create_batch()`

```python
create_batch(
    domains: List[str],
    paths: Optional[List[str]] = None,
    ports: Optional[List[int]] = None,
    redirects: Optional[bool] = None,
    include_content_sample: Optional[bool] = None,
    content_sample_retention_days: Optional[int] = None,
    check_usage_first: bool = True,
    wait_on_limits: bool = True,
    max_retries: int = 5,
    progress_callback: Optional[Callable[[int, int, Dict], None]] = None
) -> Dict[str, Any]
```

Create multiple checks in batch with automatic rate limit handling.

**Parameters:**
- `domains`: List of FQDNs to check
- `paths`: Paths to check (default: `["/"]`)
- `ports`: Ports to check (default: `[443]`)
- `redirects`: Follow redirects (optional)
- `include_content_sample`: Capture content samples (default: `False`)
- `content_sample_retention_days`: Days to retain content samples (default: `7`, max: `30`)
- `check_usage_first`: Verify quota before starting (default: `True`)
- `wait_on_limits`: Wait when hitting limits (default: `True`)
- `max_retries`: Max retries per check (default: `5`)
- `progress_callback`: Optional callback for progress updates

**Returns:** Dict with:
- `results`: List of created checks
- `stats`: Statistics dict (created, failed, rate_limited, etc.)
- `duration`: Total time in seconds

##### `get()`

```python
get(check_id: str) -> Dict[str, Any]
```

Get details of a specific check.

**Returns:** Dict with check details

##### `list()`

```python
list(
    page: int = 1,
    limit: int = 50,
    fqdn: Optional[str] = None
) -> Dict[str, Any]
```

List checks with pagination.

**Returns:** Dict with `items`, `total`, `page`, `per_page`

##### `list_all()`

```python
list_all(
    limit: int = 50,
    fqdn: Optional[str] = None
) -> Iterator[Dict[str, Any]]
```

Iterate through all checks automatically.

**Yields:** Individual check items

### UsageResource

#### Methods

##### `get()`

```python
get() -> Dict[str, Any]
```

Get current usage and limits.

**Returns:** Dict with `tenant`, `period`, `usage`, `limits`, `plan`

## Exceptions

### ApiError

Base exception for all API errors.

**Attributes:**
- `message`: Error message
- `status_code`: HTTP status code
- `details`: Additional error details

### RateLimitError

Raised when rate limit is exceeded.

**Attributes:**
- `code`: Error code (`rate_limit_exceeded`, `inflight_limit`, `checks_limit`)
- `message`: Descriptive error message
- `retry_after`: Seconds to wait before retrying
- `limit`: The limit that was exceeded
- `remaining`: Remaining requests (for rate_limit_exceeded)
- `reset_at`: Unix timestamp when rate limit resets (for rate_limit_exceeded)
- `current`: Current value (for inflight_limit)
- `used`: Used quota (for checks_limit)
- `period`: Period for the quota (for checks_limit)

### AuthenticationError

Raised when authentication fails (401).

### NotFoundError

Raised when resource is not found (404).

### ValidationError

Raised when request validation fails (400).

### ServerError

Raised when server error occurs (500+).

## Examples

See the [examples_usage.py](examples_usage.py) file for complete working examples:

1. Basic usage with error handling
2. Automatic retry on rate limit
3. Pagination (manual and automatic)
4. Usage monitoring
5. Proactive limit checking
6. Context manager usage
7. All error scenarios

## Changelog

### v0.1.0

- Privacy controls for content samples
- Configurable retention periods
- Enhanced batch operations
- Improved documentation
- Pagination support
- Automatic iteration with `list_all()`
- Enhanced error handling with detailed rate limit info
- Usage monitoring
- Batch operations with automatic rate limit handling
- Basic CRUD operations
- API key authentication
- Initial release

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License - see LICENSE file for details.

## Support

- Documentation: [https://docs.outscope.es](https://docs.outscope.es)
- Issues: [GitHub Issues](https://github.com/OutScope-io/OutscopeSDK/issues)
- Email: support@outscope.es

