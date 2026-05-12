#!/usr/bin/env python3
"""
OutScope SDK Demo - Complete Workflow
Creates checks for domains and generates a report
"""

from outscope_sdk import Client
from example_creds import OUTSCOPE_API_KEY
import time
import sys

def main():
    print("=" * 70)
    print("🚀 OutScope SDK v0.3.0 - Complete Workflow Demo")
    print("=" * 70)
    print()
    
    # Initialize client
    client = Client(api_key=OUTSCOPE_API_KEY)
    
    # Domains to analyze
    domains = [
        "api.outscope.es",
        "www.outscope.es",
        "outscope.es"
    ]
    
    print("📋 Step 1: Creating checks for domains")
    print("-" * 70)
    
    # Create checks
    checks = []
    for domain in domains:
        try:
            print(f"  Creating check for {domain}...", end=" ")
            check = client.checks.create(
                fqdn=domain,
                paths=["/"],
                ports=[443],
                max_redirects=1
            )
            checks.append({
                'domain': domain,
                'job_id': check.job_id,
                'status': check.status
            })
            print(f"✅ {check.job_id}")
        except Exception as e:
            print(f"❌ Error: {e}")
            continue
    
    if not checks:
        print("\n❌ No checks were created. Exiting.")
        sys.exit(1)
    
    print(f"\n✅ Created {len(checks)} checks successfully")
    print()
    
    # Wait for checks to complete
    print("📋 Step 2: Waiting for checks to complete")
    print("-" * 70)
    
    max_wait = 60  # 1 minute max
    start_time = time.time()
    completed_checks = []
    
    while time.time() - start_time < max_wait:
        all_done = True
        
        for check in checks:
            if check.get('completed'):
                continue
                
            try:
                result = client.checks.get(check['job_id'])
                status = result.get('status', 'unknown')
                
                if status in ['completed', 'done', 'failed', 'error']:
                    check['completed'] = True
                    check['final_status'] = status
                    check['result'] = result
                    completed_checks.append(check)
                    print(f"  ✅ {check['domain']}: {status}")
                else:
                    all_done = False
            except Exception as e:
                print(f"  ⚠️  Error checking {check['domain']}: {e}")
                all_done = False
        
        if all_done:
            break
        
        if time.time() - start_time < max_wait:
            time.sleep(3)
    
    print(f"\n✅ {len(completed_checks)}/{len(checks)} checks completed")
    print()
    
    # List available report templates
    print("📋 Step 3: Finding report template 'test'")
    print("-" * 70)
    
    try:
        templates = client.reports.list_templates(page=1, per_page=50)
        print(f"  Found {templates['total']} templates total")
        
        test_template = None
        for template in templates['templates']:
            template_id = template.get('_id') or template.get('id')
            print(f"  - {template['name']} (ID: {template_id})")
            if template['name'].lower() == 'test':
                test_template = template
        
        if not test_template:
            print(f"\n  ⚠️  Template 'test' not found. Using first available template...")
            test_template = templates['templates'][0] if templates['templates'] else None
        
        if not test_template:
            print("\n❌ No templates found. Cannot generate report.")
            sys.exit(1)
        
        template_id = test_template.get('_id') or test_template.get('id')
        print(f"\n✅ Using template: {test_template['name']} (ID: {template_id})")
        
    except Exception as e:
        print(f"❌ Error listing templates: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    print()
    
    # Generate report
    print("📋 Step 4: Generating report")
    print("-" * 70)
    
    try:
        report = client.reports.generate(
            template_id=template_id,
            title=f"OutScope Domains Analysis - {time.strftime('%Y-%m-%d %H:%M')}",
            description=f"Security assessment for: {', '.join(domains)}"
        )
        
        report_id = report['report_id']
        print(f"  ✅ Report generation started: {report_id}")
        print(f"  Status: {report['status']}")
        
    except Exception as e:
        print(f"❌ Error generating report: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    print()
    
    # Wait for report completion
    print("📋 Step 5: Waiting for report to complete")
    print("-" * 70)
    
    max_wait_report = 180  # 3 minutes max
    start_time = time.time()
    
    while time.time() - start_time < max_wait_report:
        try:
            report_status = client.reports.get(report_id)
            status = report_status['report']['status']
            
            elapsed = int(time.time() - start_time)
            print(f"  ⏳ Report status: {status} ({elapsed}s elapsed)", end="\r")
            
            if status == 'completed':
                print(f"\n\n  ✅ Report completed successfully!")
                
                # Get download URL
                download_url = client.reports.get_download_url(report_id)
                print(f"  📎 Download URL: {download_url}")
                
                # Try to download
                try:
                    output_file = f"outscope_report_{report_id}.pdf"
                    client.reports.download(report_id, output_file)
                    print(f"  ✅ Report downloaded: {output_file}")
                except Exception as e:
                    print(f"  ⚠️  Could not download file: {e}")
                    print(f"  You can download manually from: {download_url}")
                
                break
            
            elif status == 'failed':
                error_msg = report_status['report'].get('error_message', 'Unknown error')
                print(f"\n\n  ❌ Report generation failed: {error_msg}")
                break
            
            time.sleep(5)
            
        except Exception as e:
            print(f"\n  ⚠️  Error checking report: {e}")
            time.sleep(5)
    else:
        print(f"\n\n  ⏱️  Report still generating after {max_wait_report}s")
        print(f"  You can check status later with report ID: {report_id}")
    
    print()
    
    # Summary
    print("=" * 70)
    print("📊 Summary")
    print("=" * 70)
    print(f"  Checks created: {len(checks)}")
    print(f"  Checks completed: {len(completed_checks)}")
    print(f"  Report ID: {report_id}")
    print(f"  Template used: {test_template['name']}")
    print()
    print("✅ Demo completed successfully!")
    print("=" * 70)
    
    client.close()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Demo interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
