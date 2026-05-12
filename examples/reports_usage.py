#!/usr/bin/env python3
"""
Example usage of Reports Resource in OutScope SDK
"""

from outscope_sdk import Client

def main():
    client = Client(api_key="your_api_key_here")
    
    print("=== OutScope SDK - Reports Demo ===\n")
    
    # 1. Create a report template
    print("1. Creating report template...")
    template = client.reports.create_template(
        name="Security Assessment Report",
        description="Comprehensive security assessment report",
        branding={
            "company_name": "ACME Security",
            "logo_url": None,  # We'll upload logo later
            "primary_color": "#0066cc",
            "secondary_color": "#00cc66"
        },
        sections=[
            {
                "type": "executive_summary",
                "title": "Executive Summary",
                "enabled": True
            },
            {
                "type": "analyzability_overview",
                "title": "Service Analyzability",
                "enabled": True
            },
            {
                "type": "security_findings",
                "title": "Security Findings",
                "enabled": True
            },
            {
                "type": "recommendations",
                "title": "Recommendations",
                "enabled": True
            }
        ],
        default_filters={
            "analyzability": "all",
            "date_range": "last_30_days"
        },
        output_format="pdf",
        is_default=True
    )
    print(f"  ✅ Template created: {template['template']['id']}\n")
    
    # 2. Upload logo (optional)
    print("2. Uploading company logo...")
    try:
        logo_result = client.reports.upload_logo("path/to/logo.png")
        print(f"  ✅ Logo uploaded: {logo_result['logo_url']}\n")
        
        # Update template with logo
        client.reports.update_template(
            template_id=template['template']['id'],
            branding={
                "company_name": "ACME Security",
                "logo_url": logo_result['logo_url'],
                "primary_color": "#0066cc",
                "secondary_color": "#00cc66"
            }
        )
    except Exception as e:
        print(f"  ⚠️  Logo upload skipped: {e}\n")
    
    # 3. List templates
    print("3. Listing templates...")
    templates = client.reports.list_templates(page=1, per_page=10)
    print(f"  Found {templates['total']} templates")
    for t in templates['templates']:
        print(f"    - {t['name']} ({'Default' if t.get('is_default') else 'Custom'})")
    print()
    
    # 4. Generate a report
    print("4. Generating report...")
    report = client.reports.generate(
        template_id=template['template']['id'],
        title="Monthly Security Assessment - January 2026",
        description="Security assessment for all services",
        filters={
            "analyzability": "not_analyzable",
            "date_range": "last_30_days",
            "category": "Security Blocks"
        }
    )
    print(f"  ✅ Report generation started: {report['report_id']}")
    print(f"  Status: {report['status']}\n")
    
    # 5. Wait for report completion (polling)
    import time
    print("5. Waiting for report to complete...")
    report_id = report['report_id']
    max_attempts = 30
    
    for attempt in range(max_attempts):
        report_status = client.reports.get(report_id)
        status = report_status['report']['status']
        
        print(f"  Attempt {attempt + 1}/{max_attempts}: {status}", end="\r")
        
        if status == "completed":
            print(f"\n  ✅ Report completed!\n")
            break
        elif status == "failed":
            print(f"\n  ❌ Report generation failed")
            print(f"  Error: {report_status['report'].get('error_message')}\n")
            break
        
        time.sleep(2)
    else:
        print(f"\n  ⏱️  Report still generating after {max_attempts * 2}s\n")
    
    # 6. List all reports
    print("6. Listing all reports...")
    reports = client.reports.list(
        status="completed",
        page=1,
        per_page=10
    )
    print(f"  Found {reports['total']} completed reports")
    for r in reports['reports']:
        print(f"    - {r['title']} ({r['created_at']})")
    print()
    
    # 7. Download report (if completed)
    if status == "completed":
        print("7. Downloading report...")
        output_file = "security_assessment_report.pdf"
        client.reports.download(report_id, output_file)
        print(f"  ✅ Report downloaded: {output_file}\n")
        
        # Alternative: Get download URL
        download_url = client.reports.get_download_url(report_id)
        print(f"  📎 Download URL: {download_url}\n")
    
    # 8. Update template
    print("8. Updating template...")
    client.reports.update_template(
        template_id=template['template']['id'],
        description="Updated: Comprehensive security assessment with enhanced metrics"
    )
    print("  ✅ Template updated\n")
    
    # 9. Get specific template
    print("9. Getting template details...")
    template_detail = client.reports.get_template(template['template']['id'])
    print(f"  Template: {template_detail['template']['name']}")
    print(f"  Sections: {len(template_detail['template']['sections'])}")
    print(f"  Format: {template_detail['template']['output_format']}\n")
    
    print("=== Reports Demo Complete ===")
    client.close()


if __name__ == "__main__":
    main()
