# OutScope SDK

Python client library for the OutScope API - Complete security monitoring and assessment automation.

[![Python Version](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-0.3.0-brightgreen.svg)](CHANGELOG.md)

## Features

- ✅ **Complete API Coverage** - 6 resources, 38 methods, 61% API coverage
- ✅ **Asset Inventory** - Full lifecycle management of monitored services
- ✅ **Automated Scheduling** - Recurring checks (hourly, daily, weekly)
- ✅ **Multi-Tenant** - Company-based organization
- ✅ **Report Generation** - Customizable security reports
- ✅ **Worker Pools** - Select execution environment
- ✅ **Batch Operations** - Automatic rate limit handling
- ✅ **Type Hints** - Full type annotation support
- ✅ **Error Handling** - Detailed error information with retry capabilities

## Installation

```bash
pip install outscope-sdk
```

Or install from source:

```bash
cd sdk
pip install -e .
```

## Quick Start

```python
from outscope_sdk import Client

# Create a client
client = Client(api_key="your_api_key_here")

# Create an asset in inventory
asset = client.assets.create(
    target="api.example.com",
    name="Production API",
    tags=["production", "critical"]
)

# Set up automated daily checks
client.assets.set_schedule(asset['asset_id'], schedule="daily")

# Or trigger a manual check
check = client.checks.create(
    fqdn="example.com",
    paths=["/", "/api"],
    ports=[443]
)

# Check usage
usage = client.usage.get()
print(f"Used: {usage['usage']['checks_used']}/{usage['usage']['checks_limit']}")

client.close()
```

## Table of Contents

- [Authentication](#authentication)
- [Resources](#resources)
  - [Assets](#assets) - Inventory management
  - [Checks](#checks) - Security checks
  - [Companies](#companies) - Multi-tenant organization
  - [Reports](#reports) - Report generation
  - [Pools](#pools) - Worker pools
  - [Usage](#usage) - Limits and usage
- [Advanced Usage](#advanced-usage)
- [Error Handling](#error-handling)
- [API Reference](#api-reference)

---

## Authentication

Generate an API key from your OutScope dashboard.

```python
from outscope_sdk import Client
import os

# Option 1: Direct in code (not recommended for production)
client = Client(api_key="osk_...")

# Option 2: From environment variable (recommended)
client = Client(api_key=os.getenv("OUTSCOPE_API_KEY"))

# Option 3: Context manager (automatic cleanup)
with Client(api_key=os.getenv("OUTSCOPE_API_KEY")) as client:
    # Your code here
    pass
```

---

## Resources

### Assets

Manage your service inventory with full lifecycle tracking.

#### Create Asset

```python
# Create asset with full metadata
asset = client.assets.create(
    target="api.example.com",
    company_id="company_123",
    name="Production API Server",
    description="Main REST API backend",
    tags=["production", "api", "critical"],
    metadata={
        "environment": "production",
        "owner": "platform-team",
        "sla": "99.9%"
    }
)
```

#### List Assets

```python
# List with filters
assets = client.assets.list(
    company_id="company_123",
    tags="critical",
    search="api",
    analyzability="analyzable",
    active_only=True,
    page=1,
    per_page=50
)

for asset in assets['assets']:
    print(f"{asset['name']}: {asset['target']}")
```

#### Schedule Automated Checks

```python
# Set up recurring checks
client.assets.set_schedule(
    asset_id=asset['asset_id'],
    schedule="daily"  # Options: none, hourly, daily, weekly
)
```

#### Trigger Manual Check

```python
# Manually trigger a check for an asset
check = client.assets.trigger_check(asset['asset_id'])
print(f"Check started: {check['job_id']}")
```

#### Get Asset Statistics

```python
# Inventory overview
stats = client.assets.get_stats()
print(f"Total assets: {stats['total_assets']}")
print(f"Manual: {stats['manual_assets']}")
print(f"Auto-discovered: {stats['auto_discovered']}")
```

#### Get Check History

```python
# View all checks for an asset
history = client.assets.get_checks(
    asset_id=asset['asset_id'],
    page=1,
    limit=20
)

for check in history['checks']:
    print(f"{check['created_at']}: {check['status']}")
```

#### Update Asset

```python
# Update asset properties
client.assets.update(
    asset_id=asset['asset_id'],
    name="Updated API Name",
    tags=["production", "api", "critical", "updated"],
    metadata={"version": "2.0"}
)
```

#### Deactivate Asset

```python
# Soft delete (keeps history)
client.assets.delete(asset['asset_id'])
```

---

### Checks

Execute security checks and monitor results.

#### Create Check

```python
# Basic check
check = client.checks.create(
    fqdn="example.com",
    paths=["/"],
    ports=[443]
)

# Advanced check with all options
check = client.checks.create(
    fqdn="api.example.com",
    paths=["/", "/api/v1", "/health"],
    ports=[80, 443, 8080],
    max_redirects=1,
    collect_content_sample=True,
    content_sample_retention_days=7,
    pool_id="premium",
    company_id="company_123"
)
```

#### Batch Create

```python
# Create multiple checks with automatic rate limiting
result = client.checks.create_batch(
    domains=["site1.com", "site2.com", "site3.com"],
    paths=["/"],
    ports=[443],
    pool_id="general",
    company_id="company_123",
    check_usage_first=True,
    wait_on_limits=True,
    max_retries=5,
    progress_callback=lambda cur, tot, stats: print(f"{cur}/{tot}")
)

print(f"Created: {result['stats']['created']}")
print(f"Failed: {result['stats']['failed']}")
```

#### Get Check

```python
check = client.checks.get("check_id_here")
print(f"Status: {check['status']}")

if check['status'] == 'done':
    print(f"Analyzable: {check['result']['analysis']['analyzable']}")
```

#### List Checks

```python
# With advanced filters
checks = client.checks.list(
    company_id="company_123",
    analyzability="not_analyzable",
    category="Security Blocks",
    fqdn="example.com",
    page=1,
    limit=50
)

# Auto-pagination
for check in client.checks.list_all(analyzability="analyzable"):
    print(f"{check['fqdn_normalized']}: analyzable")
```

#### Latest Check

```python
# Get latest completed check for a domain
latest = client.checks.latest(fqdn="example.com")
```

#### Cancel Check

```python
# Cancel running or queued check
client.checks.cancel(check_id="check_123")
```

#### Request Review

```python
# Submit false positive review
client.checks.send_review(
    check_id="check_123",
    reason="false_positive",
    comments="This endpoint should be marked as analyzable"
)

# Check review status
status = client.checks.get_review_status(check_id="check_123")
if status['has_pending_review']:
    print("Review pending")
```

---

### Companies

Organize assets and checks by company (multi-tenant).

#### Create Company

```python
company = client.companies.create(name="ACME Corp")
```

#### List Companies

```python
companies = client.companies.list(active_only=True)
for company in companies:
    print(f"{company.name} (ID: {company.id})")
```

#### Get Company

```python
company = client.companies.get(company_id="company_123")
```

#### Update Company

```python
client.companies.update(
    company_id="company_123",
    name="ACME Corporation",
    active=True
)
```

#### Delete Company

```python
client.companies.delete(company_id="company_123")
```

---

### Reports

Generate customizable security assessment reports.

#### Create Template

```python
template = client.reports.create_template(
    name="Security Assessment Report",
    description="Comprehensive security report",
    branding={
        "company_name": "ACME Security",
        "primary_color": "#0066cc",
        "secondary_color": "#00cc66"
    },
    sections=[
        {"type": "executive_summary", "enabled": True},
        {"type": "security_findings", "enabled": True},
        {"type": "recommendations", "enabled": True}
    ],
    output_format="pdf",
    is_default=True
)
```

#### Upload Logo

```python
logo = client.reports.upload_logo("path/to/logo.png")
# Returns: {'logo_url': '/v1/reports/logos/...'}
```

#### Generate Report

```python
report = client.reports.generate(
    template_id=template['template']['id'],
    title="Monthly Security Assessment",
    description="Q1 2026 Report",
    filters={
        "analyzability": "not_analyzable",
        "date_range": "last_30_days"
    },
    company_id="company_123"
)

# Check status
status = client.reports.get(report['report_id'])
if status['report']['status'] == 'completed':
    # Download
    client.reports.download(
        report['report_id'],
        "security_report.pdf"
    )
```

#### List Reports

```python
reports = client.reports.list(
    company_id="company_123",
    status="completed",
    page=1,
    per_page=20
)
```

---

### Pools

Select worker pools for check execution.

```python
# List available pools
pools = client.pools.list()

for pool in pools['pools']:
    print(f"{pool.display_name} ({pool.type}): {'Available' if pool.available else 'Unavailable'}")

# Use pool in check
check = client.checks.create(
    fqdn="example.com",
    pool_id="premium-pool"
)
```

---

### Usage

Monitor limits and usage.

```python
usage = client.usage.get()

# Tenant info
print(f"Tenant: {usage['tenant']['name']}")
print(f"Plan: {usage['tenant']['plan']}")

# Current usage
print(f"Checks: {usage['usage']['checks_used']}/{usage['usage']['checks_limit']}")
print(f"In progress: {usage['usage']['inflight']}/{usage['limits']['max_inflight']}")

# Limits
print(f"Rate: {usage['limits']['rate_per_minute']}/min")
print(f"Retention: {usage['limits']['retention_days']} days")
```

---

## Advanced Usage

### Complete Workflow Example

```python
from outscope_sdk import Client

with Client(api_key=os.getenv("OUTSCOPE_API_KEY")) as client:
    # 1. Create company
    company = client.companies.create(name="Production Services")
    
    # 2. Create asset
    asset = client.assets.create(
        target="api.example.com",
        company_id=company.id,
        name="Production API",
        tags=["production", "critical"]
    )
    
    # 3. Set up daily checks
    client.assets.set_schedule(asset['asset_id'], schedule="daily")
    
    # 4. Trigger immediate check
    check = client.assets.trigger_check(asset['asset_id'])
    
    # 5. Generate report
    template = client.reports.create_template(
        name="Production Report",
        output_format="pdf"
    )
    
    report = client.reports.generate(
        template_id=template['template']['id'],
        title="Production Security Report",
        company_id=company.id
    )
    
    # 6. Monitor usage
    usage = client.usage.get()
    print(f"Remaining: {usage['usage']['checks_limit'] - usage['usage']['checks_used']}")
```

---

## Error Handling

```python
from outscope_sdk.exceptions import (
    RateLimitError,
    AuthenticationError,
    NotFoundError,
    ValidationError
)

try:
    check = client.checks.create(fqdn="example.com", ports=[443])
    
except RateLimitError as e:
    if e.code == "rate_limit_exceeded":
        print(f"Rate limited: {e.limit}/min, retry in {e.retry_after}s")
        time.sleep(e.retry_after)
    elif e.code == "inflight_limit":
        print(f"Too many checks in progress: {e.current}/{e.limit}")
    elif e.code == "checks_limit":
        print(f"Monthly quota exceeded: {e.used}/{e.limit}")
        
except AuthenticationError as e:
    print(f"Authentication failed: {e.message}")
    
except NotFoundError as e:
    print(f"Resource not found: {e.message}")
    
except ValidationError as e:
    print(f"Validation error: {e.message}")
```

---

## API Reference

See [CHANGELOG.md](CHANGELOG.md) for complete version history.

### Client

```python
Client(
    api_key: str,
    base_url: Optional[str] = None,
    timeout: float = 30.0
)
```

**Resources:**
- `client.assets` - AssetsResource (10 methods)
- `client.checks` - ChecksResource (10 methods)
- `client.companies` - CompaniesResource (5 methods)
- `client.reports` - ReportsResource (11 methods)
- `client.pools` - PoolsResource (1 method)
- `client.usage` - UsageResource (1 method)

**Total:** 38 methods across 6 resources

---

## Examples

See the `examples/` directory for complete working examples:

- `examples/advanced_usage.py` - All features demo
- `examples/assets_usage.py` - Asset inventory management
- `examples/reports_usage.py` - Report generation

---

## Changelog

See [CHANGELOG.md](CHANGELOG.md)

### Current Version: v0.3.0

- ✅ Assets resource (complete inventory management)
- ✅ Automated scheduling (hourly, daily, weekly)
- ✅ Reports resource (customizable reports)
- ✅ Companies resource (multi-tenant)
- ✅ Worker pools support
- ✅ Advanced filtering
- ✅ 61% API coverage

---

## Support

- **Documentation:** [https://docs.outscope.es](https://docs.outscope.es)
- **Issues:** [GitHub Issues](https://github.com/outscope-io/outscope-sdk/issues)
- **Email:** support@outscope.es

---

## License

MIT License - see [LICENSE](LICENSE) file for details.

---

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

