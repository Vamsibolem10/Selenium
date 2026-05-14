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
        links_report, broken_links_details = audit_page.check_all_links()
        audit_results["links_total"] = len(links_report)
        audit_results["links_broken"] = len(broken_links_details)
        audit_results["broken_links_list"] = broken_links_details
        audit_results["images_broken"] = len(audit_page.check_all_images())

        # 3. Button Interaction (New requirement)
        log.info("--- Initiating Button Interaction Analysis ---")
        clicked_buttons = audit_page.interact_with_all_buttons()
        audit_results["buttons_found"] = len(clicked_buttons)
        audit_results["clicked_buttons_list"] = clicked_buttons

        # 4. Deep Analysis (Optional)
        if deep_crawl:
            log.info("--- Initiating Deep Analysis / Site Mapping ---")
            spider = SiteSpider(driver, max_depth=1)
            spider.crawl(url)
            summary = spider.get_summary()
            audit_results["pages_crawled"] = summary["pages_visited"]
            # Merge spider results if needed, but we already have button interactions from the main page
        
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
    """Generates a premium, modern HTML report with rich aesthetics."""
    import platform
    import sys
    from datetime import datetime
    
    timestamp = res.get('timestamp', datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    python_version = sys.version.split()[0]
    plat = platform.platform()
    
    passed = res['status'] == 'Success'
    
    # Pre-process lists for HTML
    broken_links_html = "".join([
        f"<li class='list-item broken'><span class='tag error'>{l['status']}</span> <span class='url'>{l['url']}</span></li>" 
        for l in res.get('broken_links_list', [])
    ]) or "<li class='list-item empty'>No broken links detected.</li>"
    
    buttons_html = "".join([
        f"<li class='list-item button-act'><span class='tag {'success' if 'Success' in b['status'] else 'error'}'>{b['status']}</span> <span class='btn-text'>{b['text']}</span></li>" 
        for b in res.get('clicked_buttons_list', [])
    ]) or "<li class='list-item empty'>No buttons found or interacted with.</li>"
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Premium Audit Report - {res['url']}</title>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
        <style>
            :root {{
                --bg-primary: #0f172a;
                --bg-secondary: #1e293b;
                --text-primary: #f1f5f9;
                --text-secondary: #94a3b8;
                --accent-primary: #38bdf8;
                --accent-success: #22c55e;
                --accent-error: #ef4444;
                --accent-warning: #f59e0b;
                --border-color: #334155;
            }}
            
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            
            body {{
                font-family: 'Inter', sans-serif;
                background-color: var(--bg-primary);
                color: var(--text-primary);
                line-height: 1.6;
                padding: 40px 20px;
            }}
            
            .container {{
                max-width: 1100px;
                margin: 0 auto;
            }}
            
            header {{
                margin-bottom: 40px;
                border-bottom: 1px solid var(--border-color);
                padding-bottom: 20px;
                display: flex;
                justify-content: space-between;
                align-items: flex-end;
            }}
            
            h1 {{ font-size: 2.5rem; font-weight: 700; letter-spacing: -0.025em; color: var(--accent-primary); }}
            .gen-info {{ color: var(--text-secondary); font-size: 0.875rem; }}
            
            .grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 20px;
                margin-bottom: 40px;
            }}
            
            .card {{
                background: var(--bg-secondary);
                border: 1px solid var(--border-color);
                border-radius: 12px;
                padding: 24px;
                box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1);
                transition: transform 0.2s;
            }}
            
            .card:hover {{ transform: translateY(-2px); }}
            
            h2 {{ font-size: 1.25rem; margin-bottom: 16px; font-weight: 600; display: flex; align-items: center; gap: 8px; }}
            
            .stat-value {{ font-size: 2rem; font-weight: 700; color: var(--accent-primary); }}
            .stat-label {{ color: var(--text-secondary); font-size: 0.875rem; text-transform: uppercase; letter-spacing: 0.05em; }}
            
            .table-container {{ overflow-x: auto; margin-top: 20px; }}
            table {{ width: 100%; border-collapse: collapse; }}
            th {{ text-align: left; padding: 12px; color: var(--text-secondary); border-bottom: 1px solid var(--border-color); font-size: 0.75rem; text-transform: uppercase; }}
            td {{ padding: 16px 12px; border-bottom: 1px solid var(--border-color); vertical-align: top; }}
            
            .tag {{
                padding: 4px 8px;
                border-radius: 4px;
                font-size: 0.75rem;
                font-weight: 600;
                display: inline-block;
            }}
            .tag.success {{ background: rgba(34, 197, 94, 0.2); color: #4ade80; }}
            .tag.error {{ background: rgba(239, 68, 68, 0.2); color: #f87171; }}
            .tag.warning {{ background: rgba(245, 158, 11, 0.2); color: #fbbf24; }}
            
            .details-log {{
                background: #000;
                color: #10b981;
                padding: 16px;
                border-radius: 8px;
                font-family: 'JetBrains Mono', monospace;
                font-size: 0.8125rem;
                white-space: pre-wrap;
                margin-top: 10px;
                border: 1px solid #064e3b;
            }}
            
            .list-container {{ list-style: none; }}
            .list-item {{
                padding: 10px;
                border-bottom: 1px solid var(--border-color);
                display: flex;
                align-items: center;
                gap: 12px;
                font-size: 0.875rem;
            }}
            .list-item:last-child {{ border-bottom: none; }}
            .list-item .url {{ color: var(--accent-primary); text-decoration: none; word-break: break-all; }}
            .list-item.empty {{ color: var(--text-secondary); font-style: italic; }}
            
            footer {{
                margin-top: 60px;
                text-align: center;
                color: var(--text-secondary);
                font-size: 0.75rem;
            }}
            
            .highlight-box {{
                background: rgba(56, 189, 248, 0.05);
                border-left: 4px solid var(--accent-primary);
                padding: 16px;
                margin-top: 20px;
                border-radius: 0 8px 8px 0;
            }}
            
            ::-webkit-scrollbar {{ width: 8px; }}
            ::-webkit-scrollbar-track {{ background: var(--bg-primary); }}
            ::-webkit-scrollbar-thumb {{ background: var(--border-color); border-radius: 4px; }}
            ::-webkit-scrollbar-thumb:hover {{ background: var(--text-secondary); }}
        </style>
    </head>
    <body>
        <div class="container">
            <header>
                <div>
                    <h1>Audit Report</h1>
                    <div class="gen-info">Target: {res['url']} &bull; {timestamp}</div>
                </div>
                <div class="tag {'success' if passed else 'error'}" style="font-size: 1rem; padding: 8px 16px;">
                    {res['status']}
                </div>
            </header>

            <div class="grid">
                <div class="card">
                    <div class="stat-label">Load Time</div>
                    <div class="stat-value">{res['performance']}</div>
                </div>
                <div class="card">
                    <div class="stat-label">Broken Links</div>
                    <div class="stat-value" style="color: {'#ef4444' if res['links_broken'] > 0 else '#22c55e'}">
                        {res['links_broken']}
                    </div>
                </div>
                <div class="card">
                    <div class="stat-label">Buttons Clicked</div>
                    <div class="stat-value">{res['buttons_found']}</div>
                </div>
            </div>

            <div class="grid">
                <div class="card" style="grid-column: span 1;">
                    <h2>Broken Links Discovery</h2>
                    <ul class="list-container">
                        {broken_links_html}
                    </ul>
                </div>
                <div class="card" style="grid-column: span 1;">
                    <h2>Button Interaction Log</h2>
                    <ul class="list-container">
                        {buttons_html}
                    </ul>
                </div>
            </div>

            <div class="card">
                <h2>Execution Environment</h2>
                <div class="grid" style="grid-template-columns: repeat(2, 1fr); gap: 10px; margin-top: 10px;">
                    <div class="gen-info"><strong>Python:</strong> {python_version}</div>
                    <div class="gen-info"><strong>OS:</strong> {plat}</div>
                    <div class="gen-info"><strong>Framework:</strong> Industrial Selenium v2.0</div>
                    <div class="gen-info"><strong>Browser:</strong> Chrome (Headless)</div>
                </div>
                
                <h2 style="margin-top: 30px;">Raw Audit Output</h2>
                <div class="details-log">
URL: {res['url']}
Load Time: {res['performance']}
Links Total: {res['links_total']}
Links Broken: {res['links_broken']}
Images Broken: {res['images_broken']}
Buttons Interacted: {res['buttons_found']}
Pages Crawled: {res['pages_crawled']}
Status: {res['status']}
Timestamp: {timestamp}
                </div>
            </div>

            <footer>
                &copy; 2026 Industrial Selenium Automation &bull; All Rights Reserved
            </footer>
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
