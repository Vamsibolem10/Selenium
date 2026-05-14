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
    """Generates a premium, responsive HTML report for the audit."""
    status_color = "#2ecc71" if res["status"] == "Success" else "#e74c3c"
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Audit Report - {res['url']}</title>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&display=swap" rel="stylesheet">
        <style>
            :root {{
                --primary: #6366f1;
                --bg: #0f172a;
                --card: #1e293b;
                --text: #f8fafc;
                --text-muted: #94a3b8;
                --success: #22c55e;
                --error: #ef4444;
            }}
            body {{
                font-family: 'Inter', sans-serif;
                background: var(--bg);
                color: var(--text);
                margin: 0;
                padding: 40px 20px;
                display: flex;
                justify-content: center;
            }}
            .container {{
                max-width: 900px;
                width: 100%;
            }}
            header {{
                margin-bottom: 40px;
                border-left: 4px solid var(--primary);
                padding-left: 20px;
            }}
            h1 {{ margin: 0; font-size: 2.5rem; }}
            .url {{ color: var(--text-muted); word-break: break-all; }}
            .grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 20px;
                margin-bottom: 40px;
            }}
            .card {{
                background: var(--card);
                padding: 24px;
                border-radius: 12px;
                border: 1px solid #334155;
                transition: transform 0.2s;
            }}
            .card:hover {{ transform: translateY(-5px); }}
            .card-label {{ color: var(--text-muted); font-size: 0.875rem; text-transform: uppercase; letter-spacing: 0.05em; }}
            .card-value {{ font-size: 1.5rem; font-weight: 600; margin-top: 8px; }}
            .status-tag {{
                display: inline-block;
                padding: 4px 12px;
                border-radius: 20px;
                font-size: 0.875rem;
                font-weight: 600;
                background: {status_color}22;
                color: {status_color};
                border: 1px solid {status_color}44;
            }}
            .metric-bar {{
                height: 8px;
                background: #334155;
                border-radius: 4px;
                margin-top: 12px;
                overflow: hidden;
            }}
            .metric-fill {{
                height: 100%;
                background: var(--primary);
            }}
            .footer {{
                margin-top: 60px;
                text-align: center;
                color: var(--text-muted);
                font-size: 0.875rem;
            }}
            .highlight-error {{ color: var(--error); }}
        </style>
    </head>
    <body>
        <div class="container">
            <header>
                <div class="status-tag">{res['status']}</div>
                <h1>Deep Audit Report</h1>
                <div class="url">{res['url']}</div>
            </header>

            <div class="grid">
                <div class="card">
                    <div class="card-label">Performance</div>
                    <div class="card-value">{res['performance']}</div>
                    <div class="metric-bar"><div class="metric-fill" style="width: 80%"></div></div>
                </div>
                <div class="card">
                    <div class="card-label">Links Checked</div>
                    <div class="card-value">{res['links_total']}</div>
                    <div class="card-label" style="margin-top:10px">Broken: <span class="{'highlight-error' if res['links_broken'] > 0 else ''}">{res['links_broken']}</span></div>
                </div>
                <div class="card">
                    <div class="card-label">Images Analyzed</div>
                    <div class="card-value">{res['links_total'] + res['images_broken']}</div>
                    <div class="card-label" style="margin-top:10px">Broken: <span class="{'highlight-error' if res['images_broken'] > 0 else ''}">{res['images_broken']}</span></div>
                </div>
                <div class="card">
                    <div class="card-label">Pages Crawled</div>
                    <div class="card-value">{res['pages_crawled']}</div>
                </div>
            </div>

            <div class="card" style="margin-bottom: 20px;">
                <h3 style="margin-top: 0;">Audit Summary</h3>
                <p>The automated audit for <strong>{res['url']}</strong> was completed on {res['timestamp']}. 
                { "Multiple issues were detected that require attention." if (res['links_broken'] > 0 or res['images_broken'] > 0) else "The site appears to be in good health." }</p>
            </div>

            <div class="footer">
                Generated by Industrial Selenium Automation Framework &bull; {res['timestamp']}
            </div>
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
