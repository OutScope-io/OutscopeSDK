#!/usr/bin/env python3
"""
Example usage of the OutScope SDK with all new features
"""

from outscope_sdk import Client

def main():
    # Initialize client
    client = Client(api_key="your_api_key_here")
    
    print("=== OutScope SDK - Advanced Features Demo ===\n")
    
    # 1. List available worker pools
    print("1. Available Worker Pools:")
    pools_data = client.pools.list()
    for pool in pools_data["pools"]:
        status = "✅ Available" if pool.available else "❌ Unavailable"
        print(f"  - {pool.display_name} ({pool.queue_name}) [{pool.type}] {status}")
    print(f"  Default pool: {pools_data['default']}\n")
    
    # 2. List companies
    print("2. Companies:")
    companies = client.companies.list(active_only=True)
    for company in companies:
        print(f"  - {company.name} (ID: {company.id})")
    print()
    
    # 3. Create a check with advanced options
    print("3. Creating advanced check...")
    check = client.checks.create(
        fqdn="example.com",
        paths=["/", "/api"],
        ports=[443],
        max_redirects=1,
        collect_content_sample=False,
        pool_id="general",
        company_id=companies[0].id if companies else None
    )
    print(f"  ✅ Check created: {check.job_id} (status: {check.status})\n")
    
    # 4. Get check details
    print("4. Getting check details...")
    details = client.checks.get(check.job_id)
    print(f"  Job ID: {details['job_id']}")
    print(f"  Status: {details['status']}")
    print(f"  FQDN: {details.get('fqdn_normalized', 'N/A')}\n")
    
    # 5. List checks with filters
    print("5. Listing checks with filters...")
    if companies:
        filtered_checks = client.checks.list(
            page=1,
            limit=10,
            company_id=companies[0].id,
            analyzability="all"
        )
        print(f"  Found {filtered_checks['total']} checks\n")
    
    # 6. Create batch
    print("6. Creating batch with advanced options...")
    batch_result = client.checks.create_batch(
        domains=["test1.example.com", "test2.example.com"],
        paths=["/"],
        ports=[443],
        pool_id="general",
        company_id=companies[0].id if companies else None,
        collect_content_sample=False,
        check_usage_first=True,
        wait_on_limits=True,
        max_retries=3
    )
    print(f"  ✅ Created: {batch_result['stats']['created']}")
    print(f"  ❌ Failed: {batch_result['stats']['failed']}")
    print(f"  ⏱️  Duration: {batch_result['duration']:.2f}s\n")
    
    # 7. Check usage
    print("7. Usage and Limits:")
    usage = client.usage.get()
    print(f"  Tenant: {usage['tenant']['name']}")
    print(f"  Checks: {usage['usage']['checks_used']}/{usage['usage']['checks_limit']}")
    print(f"  In progress: {usage['usage']['inflight']}/{usage['limits']['max_inflight']}\n")
    
    print("=== Demo Complete ===")
    client.close()

if __name__ == "__main__":
    main()
