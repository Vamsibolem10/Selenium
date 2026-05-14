import os
import sys
import subprocess
import argparse
import config

def install_requirements():
    print("--- Step 1: Checking and Installing Dependencies ---")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("Dependencies installed successfully.\n")
    except Exception as e:
        print(f"Error installing dependencies: {e}")
        sys.exit(1)

def get_report_name(url):
    """Sanitizes URL to create a safe filename."""
    if not url:
        url = config.BASE_URL
    
    clean_name = url.replace("https://", "").replace("http://", "").replace("www.", "").strip("/")
    clean_name = "".join(c if c.isalnum() or c in ("-", "_") else "_" for c in clean_name)
    return clean_name

def run_tests(url=None, deep=False):
    target_url = url or config.BASE_URL
    report_base = get_report_name(target_url)
    print(f"--- Step 2: Running Advanced Selenium Audit on {target_url} ---")
    
    try:
        cmd = [sys.executable, "advanced_audit.py"]
        if url:
            cmd.extend(["--url", url])
        if deep:
            cmd.append("--deep")
        
        # Pass the report name to advanced_audit
        cmd.extend(["--report-name", f"audit_{report_base}.json"])
        
        subprocess.check_call(cmd)
    except subprocess.CalledProcessError:
        print("\nAudit finished with some issues (check logs/test_run.log).")
    except Exception as e:
        print(f"Error running audit: {e}")

def run_pytest(url=None):
    target_url = url or config.BASE_URL
    report_base = get_report_name(target_url)
    report_file = f"report_{report_base}.html"
    
    print(f"--- Step 2: Running Industrial Test Suite (Parallel={config.PARALLEL_WORKERS}, Retries={config.RETRIES}) ---")
    if url:
        print(f"Targeting custom URL: {url}")
        os.environ["BASE_URL"] = url
        
    try:
        cmd = [
            sys.executable, "-m", "pytest", 
            "-n", str(config.PARALLEL_WORKERS),      # Parallel execution
            "--reruns", str(config.RETRIES),        # Automatic retries for flakiness
            f"--html=reports/{report_file}", 
            "--self-contained-html"
        ]
        os.makedirs("reports", exist_ok=True)
        subprocess.check_call(cmd)
        print(f"\nTest Suite Completed. Report saved as 'reports/{report_file}'.")
    except subprocess.CalledProcessError:
        print(f"\nSome tests failed. Check 'reports/{report_file}' for details.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Selenium One-Command Launcher")
    parser.add_argument("--mode", choices=["audit", "test"], default="audit", help="Run 'audit' or 'test' mode")
    parser.add_argument("--url", help="Target website URL (overrides default)")
    parser.add_argument("--deep", action="store_true", help="Enable deep audit")
    args = parser.parse_args()

    install_requirements()

    if args.mode == "test":
        run_pytest(url=args.url)
    else:
        run_tests(url=args.url, deep=args.deep)

    print("\n--- All Processes Completed ---")
    print("Logs: logs/test_run.log")
    print("Screenshots: screenshots/")
    print("Reports: reports/")
