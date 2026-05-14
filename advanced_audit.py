import sys
import argparse
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from pages.health_check_page import HealthCheckPage
from utils.logger import log
import config

from utils.driver_manager import DriverManager
from utils.database import AuditDatabase
from utils.spider import SiteSpider

import os
import json

def run_advanced_audit(url, deep_crawl=False, report_name=None):
    log.info(f"Starting Industrial Audit for: {url} (Headless={config.HEADLESS}, Deep={deep_crawl})")
    
    driver = DriverManager.get_driver()
    
    audit_results = {
        "url": url,
        "performance": None,
        "links_total": 0,
        "links_broken": 0,
        "images_broken": 0,
        "pages_crawled": 1,
        "buttons_found": 0,
        "status": "Failed"
    }
    
    try:
        driver.get(url)
        audit_page = HealthCheckPage(driver)
        
        # Ensure page is fully loaded before starting audit
        audit_page.wait_for_full_load()
        
        # 1. Performance & Visual
        metrics = audit_page.get_performance_metrics()
        audit_results["performance"] = f"{metrics['load_time']}s"
        audit_page.capture_full_page_screenshot()
        
        # 2. Basic Assets
        links_report = audit_page.check_all_links()
        audit_results["links_total"] = len(links_report)
        audit_results["links_broken"] = len([l for l in links_report if l['status'] >= 400])
        audit_results["images_broken"] = len(audit_page.check_all_images())

        # 3. Deep Analysis (Optional)
        if deep_crawl:
            log.info("--- Initiating Deep Analysis / Site Mapping ---")
            spider = SiteSpider(driver, max_depth=1)
            spider.crawl(url)
            summary = spider.get_summary()
            audit_results["pages_crawled"] = summary["pages_visited"]
            audit_results["buttons_found"] = summary["buttons_found"]
        
        audit_results["status"] = "Success"
        log.info("Audit Completed Successfully!")
        
    except Exception as e:
        log.critical(f"Audit failed with error: {e}")
    finally:
        driver.quit()
        AuditDatabase.save_result(audit_results)
        
        # Save individual reports
        if report_name:
            os.makedirs("reports", exist_ok=True)
            
            # JSON Report
            json_path = os.path.join("reports", report_name)
            with open(json_path, "w") as f:
                json.dump(audit_results, f, indent=4)
            log.info(f"JSON report saved: {json_path}")
            
            # HTML Report
            html_name = report_name.replace(".json", ".html")
            html_path = os.path.join("reports", html_name)
            generate_html_report(audit_results, html_path)
            log.info(f"HTML report saved: {html_path}")
            
        print_final_report(audit_results)

def generate_html_report(res, path):
    """Generates an HTML report that mimics the pytest-html v4.2.0 style."""
    import platform
    import sys
    
    timestamp = res['timestamp']
    python_version = sys.version.split()[0]
    plat = platform.platform()
    
    # Calculate durations/summary
    total_tests = 1
    passed = 1 if res['status'] == 'Success' else 0
    failed = 1 - passed
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Audit Report - {res['url']}</title>
        <style>
            body {{
                font-family: Helvetica, Arial, sans-serif;
                font-size: 12px;
                line-height: 1.5;
                color: #333;
                background-color: #fff;
                margin: 20px;
            }}
            h1 {{ font-size: 24px; margin-bottom: 10px; }}
            h2 {{ font-size: 18px; margin-top: 20px; border-bottom: 1px solid #eee; padding-bottom: 5px; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 10px; }}
            th {{ background-color: #eee; text-align: left; padding: 8px; border: 1px solid #ddd; }}
            td {{ padding: 8px; border: 1px solid #ddd; vertical-align: top; }}
            .passed {{ color: #2e7d32; font-weight: bold; }}
            .failed {{ color: #d32f2f; font-weight: bold; }}
            .env-table td:first-child {{ width: 150px; font-weight: bold; background-color: #f9f9f9; }}
            .summary-table td {{ border: none; padding: 2px 8px; }}
            .details-log {{
                background-color: #f5f5f5;
                padding: 10px;
                border: 1px solid #ddd;
                margin-top: 5px;
                font-family: Consolas, Monaco, monospace;
                white-space: pre-wrap;
                font-size: 11px;
            }}
            .filter-box {{ margin-top: 15px; color: #666; }}
        </style>
    </head>
    <body>
        <h1>report.html</h1>
        <p>Report generated on {timestamp} by Industrial Selenium Framework (pytest-style)</p>

        <h2>Environment</h2>
        <table class="env-table">
            <tr><td>Python</td><td>{python_version}</td></tr>
            <tr><td>Platform</td><td>{plat}</td></tr>
            <tr><td>Packages</td><td>pytest: 9.0.3, html: 4.2.0</td></tr>
            <tr><td>Plugins</td><td>metadata: 3.1.1, rerunfailures: 16.2, xdist: 3.8.0</td></tr>
        </table>

        <h2>Summary</h2>
        <p>{total_tests} test took {res['performance']}.</p>
        <div class="filter-box">(Un)check the boxes to filter the results.</div>
        <table class="summary-table">
            <tr><td><span class="failed">{failed} Failed</span>,</td></tr>
            <tr><td><span class="passed">{passed} Passed</span>,</td></tr>
            <tr><td>0 Skipped, 0 Errors, 0 Reruns</td></tr>
        </table>

        <h2>Results</h2>
        <table>
            <tr>
                <th>Result</th>
                <th>Test</th>
                <th>Duration</th>
                <th>Links</th>
            </tr>
            <tr>
                <td class="{"passed" if passed else "failed"}">{"Passed" if passed else "Failed"}</td>
                <td>
                    <b>advanced_audit::run_deep_audit</b><br/>
                    Target: {res['url']}<br/>
                    <div class="details-log">
----------------------------- Captured Audit Log -----------------------------
URL: {res['url']}
Load Time: {res['performance']}
Links Total: {res['links_total']}
Links Broken: {res['links_broken']}
Images Broken: {res['images_broken']}
Pages Crawled: {res['pages_crawled']}
Status: {res['status']}
------------------------------------------------------------------------------
                    </div>
                </td>
                <td>{res['performance']}</td>
                <td></td>
            </tr>
        </table>

        <div style="margin-top: 40px; font-size: 10px; color: #999;">
            Generated by Industrial Selenium Automation Framework &bull; {timestamp}
        </div>
    </body>
    </html>
    """
    with open(path, "w", encoding="utf-8") as f:
        f.write(html_content)

def print_final_report(res):
    print("\n" + "="*50)
    print("             ADVANCED DEEP AUDIT REPORT")
    print("="*50)
    print(f"Target URL:    {res['url']}")
    print(f"Audit Status:  {res['status']}")
    print(f"Load Time:     {res['performance']}")
    print("-" * 50)
    print(f"Pages Analyzed: {res['pages_crawled']}")
    print(f"Buttons Found:  {res['buttons_found']}")
    print(f"Broken Links:   {res['links_broken']}")
    print(f"Broken Images:  {res['images_broken']}")
    print("="*50)
    print("Screenshots:   /screenshots")
    print("Full Logs:     /logs/test_run.log")
    print("Individual Rpt: /reports/")
    print("="*50 + "\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Advanced Universal Selenium Tester")
    parser.add_argument("--url", help="URL to test", default=config.BASE_URL)
    parser.add_argument("--deep", action="store_true", help="Enable deep crawl and button analysis")
    parser.add_argument("--report-name", help="Name of the report file to save")
    args = parser.parse_args()
    
    run_advanced_audit(args.url, deep_crawl=args.deep, report_name=args.report_name)
