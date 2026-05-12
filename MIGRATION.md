# Migration Guide: SDK v0.1.x → v0.2.0

## Overview

Version 0.2.0 brings the SDK to full alignment with the OutScope API, adding support for worker pools, companies, and advanced check operations. This guide will help you upgrade your code.

## Breaking Changes

### 1. Parameter Rename: `include_content_sample` → `collect_content_sample`

**Reason:** Align with API naming convention

**Before (0.1.x):**
```python
check = client.checks.create(
    fqdn="example.com",
    include_content_sample=True,
    content_sample_retention_days=7
)
```

**After (0.2.0):**
```python
check = client.checks.create(
    fqdn="example.com",
    collect_content_sample=True,  # Renamed parameter
    content_sample_retention_days=7
)
```

**Action Required:** 
- Search for `include_content_sample` in your codebase
- Replace with `collect_content_sample`

---

## New Features (Non-Breaking)

### 2. Worker Pool Selection

You can now specify which worker pool executes your checks:

```python
# List available pools
pools = client.pools.list()
print(f"Default pool: {pools['default']}")

for pool in pools['pools']:
    print(f"- {pool.display_name} ({pool.type}): {'Available' if pool.available else 'Unavailable'}")

# Create check with specific pool
check = client.checks.create(
    fqdn="example.com",
    pool_id="premium-pool"  # NEW parameter
)

# Batch with pool
result = client.checks.create_batch(
    domains=["site1.com", "site2.com"],
    pool_id="premium-pool"  # NEW parameter
)
```

### 3. Company Management

Associate checks with organizational units:

```python
# List companies
companies = client.companies.list(active_only=True)

# Create new company
company = client.companies.create(name="ACME Corp")

# Create check associated with company
check = client.checks.create(
    fqdn="example.com",
    company_id=company.id  # NEW parameter
)

# Filter checks by company
checks = client.checks.list(
    company_id=company.id,  # NEW filter
    page=1,
    limit=50
)
```

### 4. Advanced Check Filtering

New filter options for listing checks:

```python
# Filter by analyzability
not_analyzable = client.checks.list(
    analyzability="not_analyzable",  # NEW: all, analyzable, not_analyzable
    reasons="blocked_by_security,no_http_response",  # NEW: filter by reasons
    category="Security Blocks"  # NEW: filter by category
)

# Combined filtering
enterprise_blocked = client.checks.list(
    company_id="company_123",
    analyzability="not_analyzable",
    category="Security Blocks",
    page=1,
    limit=50
)

# Also works with list_all()
for check in client.checks.list_all(
    company_id="company_123",
    analyzability="analyzable"
):
    print(f"Analyzable check: {check['job_id']}")
```

### 5. Advanced Check Operations

New methods for check lifecycle management:

```python
# Get latest check for a domain
try:
    latest = client.checks.latest(fqdn="example.com")
    print(f"Latest: {latest['job_id']} - {latest['status']}")
except NotFoundError:
    print("No completed checks found")

# Cancel a running check
client.checks.cancel(check_id="abc123")

# Request review for incorrect classification
client.checks.send_review(
    check_id="abc123",
    reason="false_positive",
    comments="This endpoint should be marked as analyzable"
)

# Check review status
review_status = client.checks.get_review_status(check_id="abc123")
if review_status['has_pending_review']:
    print(f"Review requested at: {review_status['review']['created_at']}")

# Debug: Get queue status (MongoDB + Celery)
queue_status = client.checks.get_queue_status(check_id="abc123")
print(f"MongoDB: {queue_status['mongodb']['status']}")
print(f"Celery: {queue_status['celery']['status']}")
```

---

## Updated Examples

### Before (0.1.x): Basic Usage

```python
from outscope_sdk import Client

client = Client(api_key="...")

# Create check
check = client.checks.create(
    fqdn="example.com",
    paths=["/"],
    ports=[443]
)

# List checks
checks = client.checks.list(page=1, limit=50)

# Check usage
usage = client.usage.get()
```

### After (0.2.0): Advanced Usage

```python
from outscope_sdk import Client

client = Client(api_key="...")

# Get companies and pools
companies = client.companies.list()
pools = client.pools.list()

# Create advanced check
check = client.checks.create(
    fqdn="example.com",
    paths=["/", "/api"],
    ports=[443],
    max_redirects=1,
    collect_content_sample=False,
    pool_id=pools['default'],
    company_id=companies[0].id if companies else None
)

# List with advanced filters
checks = client.checks.list(
    company_id=companies[0].id,
    analyzability="not_analyzable",
    category="Security Blocks",
    page=1,
    limit=50
)

# Advanced operations
latest = client.checks.latest(fqdn="example.com")
client.checks.send_review(check_id=check.job_id, reason="review_needed", comments="Please verify")

# Check usage
usage = client.usage.get()
```

---

## Step-by-Step Migration

### Step 1: Update Package

```bash
pip install --upgrade outscope-sdk
```

### Step 2: Fix Breaking Changes

```bash
# Search for the old parameter
grep -r "include_content_sample" .

# Replace with new parameter
# include_content_sample → collect_content_sample
```

### Step 3: Test Your Code

```python
# Quick test script
from outscope_sdk import Client

client = Client(api_key="your_key")

# Verify basic functionality
usage = client.usage.get()
print(f"✅ Basic check: {usage['tenant']['name']}")

# Verify new features
pools = client.pools.list()
print(f"✅ Pools: {len(pools['pools'])} available")

companies = client.companies.list()
print(f"✅ Companies: {len(companies)} found")

print("✅ Migration successful!")
```

### Step 4: Adopt New Features (Optional)

Consider enhancing your workflows with:
- Worker pool selection for performance
- Company organization for multi-tenant scenarios
- Advanced filtering for analytics
- Review workflows for false positives

---

## Compatibility Matrix

| SDK Version | API Version | Python Version |
|-------------|-------------|----------------|
| 0.2.0       | v1 (current)| 3.9+          |
| 0.1.x       | v1          | 3.8+          |

---

## Getting Help

- **Documentation:** See `examples/advanced_usage.py`
- **Issues:** GitHub Issues
- **Support:** support@outscope.es
- **Changelog:** See CHANGELOG.md

---

## Future Deprecations

None planned. All 0.1.x features remain supported except `include_content_sample` parameter.
