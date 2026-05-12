#!/usr/bin/env python3
"""
Example usage of Assets Resource in OutScope SDK
"""

from outscope_sdk import Client
import time

def main():
    client = Client(api_key="your_api_key_here")
    
    print("=== OutScope SDK - Assets Demo ===\n")
    
    # 1. Create company for organization
    print("1. Creating company...")
    company = client.companies.create(name="Production Services")
    print(f"  ✅ Company created: {company.name} (ID: {company.id})\n")
    
    # 2. Create assets
    print("2. Creating assets...")
    
    # Web server
    web_asset = client.assets.create(
        target="web.example.com",
        company_id=company.id,
        name="Production Web Server",
        description="Main production web application",
        tags=["production", "web", "critical"],
        metadata={
            "environment": "production",
            "owner": "platform-team",
            "sla": "99.9%"
        }
    )
    print(f"  ✅ Asset created: {web_asset['name']}")
    
    # API server
    api_asset = client.assets.create(
        target="api.example.com",
        company_id=company.id,
        name="Production API Server",
        description="REST API backend",
        tags=["production", "api", "critical"]
    )
    print(f"  ✅ Asset created: {api_asset['name']}\n")
    
    # 3. List assets
    print("3. Listing assets...")
    assets = client.assets.list(
        company_id=company.id,
        active_only=True,
        page=1,
        per_page=10
    )
    print(f"  Found {assets['total']} assets:")
    for asset in assets['assets']:
        print(f"    - {asset['name']} ({asset['target']})")
    print()
    
    # 4. Update asset
    print("4. Updating asset...")
    client.assets.update(
        asset_id=web_asset['asset_id'],
        description="Main production web app - Updated with new features",
        tags=["production", "web", "critical", "updated"]
    )
    print("  ✅ Asset updated\n")
    
    # 5. Set schedule for recurring checks
    print("5. Setting up recurring checks...")
    schedule_result = client.assets.set_schedule(
        asset_id=web_asset['asset_id'],
        schedule="daily"
    )
    print(f"  ✅ Schedule set: {schedule_result['schedule']}")
    print(f"  Asset: {schedule_result['target']}\n")
    
    # 6. Trigger manual check
    print("6. Triggering manual check...")
    check_result = client.assets.trigger_check(web_asset['asset_id'])
    print(f"  ✅ Check triggered: {check_result['job_id']}")
    print(f"  Status: {check_result['status']}")
    print(f"  Queue: {check_result['queue']}\n")
    
    # 7. Get asset statistics
    print("7. Getting asset statistics...")
    stats = client.assets.get_stats()
    print(f"  Total assets: {stats['total_assets']}")
    print(f"  Manual: {stats['manual_assets']}")
    print(f"  Auto-discovered: {stats['auto_discovered']}")
    print(f"  Recent checks (24h): {stats['recent_checks']}")
    if stats['top_tags']:
        print(f"  Top tags:")
        for tag in stats['top_tags'][:5]:
            print(f"    - {tag['tag']}: {tag['count']}")
    print()
    
    # 8. Get specific asset
    print("8. Getting asset details...")
    asset_detail = client.assets.get(web_asset['asset_id'])
    print(f"  Asset: {asset_detail['name']}")
    print(f"  Target: {asset_detail['target']}")
    print(f"  Status: {'Active' if asset_detail['active'] else 'Inactive'}")
    print(f"  Schedule: {asset_detail.get('schedule', 'none')}")
    print(f"  Check count: {asset_detail['check_count']}")
    print(f"  Tags: {', '.join(asset_detail.get('tags', []))}\n")
    
    # 9. Wait a bit for check to complete
    print("9. Waiting for check to complete...")
    time.sleep(5)
    
    # 10. Get check history for asset
    print("10. Getting check history...")
    check_history = client.assets.get_checks(
        asset_id=web_asset['asset_id'],
        page=1,
        limit=5
    )
    print(f"  Total checks: {check_history['total']}")
    if check_history['checks']:
        print(f"  Recent checks:")
        for check in check_history['checks'][:3]:
            print(f"    - {check.get('created_at')} : {check.get('status')}")
    print()
    
    # 11. Filter assets by tags
    print("11. Filtering assets by tags...")
    critical_assets = client.assets.list(
        tags="critical",
        active_only=True
    )
    print(f"  Critical assets: {critical_assets['total']}")
    for asset in critical_assets['assets']:
        print(f"    - {asset['name']}")
    print()
    
    # 12. Search assets
    print("12. Searching assets...")
    search_results = client.assets.list(
        search="api",
        active_only=True
    )
    print(f"  Found {search_results['total']} assets matching 'api'")
    for asset in search_results['assets']:
        print(f"    - {asset['name']} ({asset['target']})")
    print()
    
    # 13. Filter by analyzability
    print("13. Filtering by analyzability...")
    not_analyzable = client.assets.list(
        analyzability="not_analyzable",
        active_only=True
    )
    print(f"  Not analyzable assets: {not_analyzable['total']}")
    print()
    
    # 14. Deactivate asset (soft delete)
    print("14. Deactivating asset...")
    client.assets.delete(api_asset['asset_id'])
    print(f"  ✅ Asset deactivated: {api_asset['name']}\n")
    
    # 15. Verify deactivation
    print("15. Verifying deactivation...")
    active_only = client.assets.list(company_id=company.id, active_only=True)
    all_assets = client.assets.list(company_id=company.id, active_only=False)
    print(f"  Active assets: {active_only['total']}")
    print(f"  Total assets (including inactive): {all_assets['total']}\n")
    
    print("=== Assets Demo Complete ===")
    client.close()


if __name__ == "__main__":
    main()
