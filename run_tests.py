import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from pages.login_page import LoginPage
from pages.dashboard_page import DashboardPage
from utils.logger import log
import config

def run_selenium_check():
    log.info(f"Initializing Chrome Driver (Headless={config.HEADLESS})...")
    options = webdriver.ChromeOptions()
    if config.HEADLESS:
        options.add_argument("--headless=new")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    if not config.HEADLESS:
        driver.maximize_window()
    
    try:
        print(f"Navigating to {config.BASE_URL}...")
        driver.get(config.BASE_URL)
        
        login_page = LoginPage(driver)
        dashboard_page = DashboardPage(driver)

        print("Performing Login...")
        login_page.login(config.USERNAME, config.PASSWORD)

        if dashboard_page.is_inventory_displayed():
            print("Login Successful! Dashboard is visible.")
            print(f"Page Title: {dashboard_page.get_title()}")
        else:
            print("Login Failed or Dashboard not visible.")
            return

        print("Checking webpage content...")
        time.sleep(2)
        print("Performing Logout...")
        dashboard_page.logout()
        print("Logout Successful!")
        
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        print("Closing the browser...")
        driver.quit()

if __name__ == "__main__":
    run_selenium_check()
