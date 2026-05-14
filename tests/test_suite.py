import pytest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from pages.login_page import LoginPage
from pages.dashboard_page import DashboardPage
from pages.health_check_page import HealthCheckPage
from utils.logger import log
import config

@pytest.fixture
def driver():
    log.info(f"Setting up WebDriver (Headless={config.HEADLESS})...")
    options = webdriver.ChromeOptions()
    if config.HEADLESS:
        options.add_argument("--headless=new")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    if not config.HEADLESS:
        driver.maximize_window()
    yield driver
    log.info("Tearing down WebDriver...")
    driver.quit()

def test_valid_login(driver):
    log.info("Running: test_valid_login")
    driver.get(config.BASE_URL)
    login_page = LoginPage(driver)
    login_page.wait_for_full_load()
    
    dashboard_page = DashboardPage(driver)
    
    login_page.login(config.USERNAME, config.PASSWORD)
    assert dashboard_page.is_inventory_displayed()
    log.success("Login assertion passed")

def test_site_health_audit(driver):
    log.info(f"Running: test_site_health_audit on {config.BASE_URL}")
    driver.get(config.BASE_URL)
    health_page = HealthCheckPage(driver)
    health_page.wait_for_full_load()
    
    # Perform a broad audit
    broken_images = health_page.check_all_images()
    health_page.capture_full_page_screenshot()
    
    assert len(broken_images) == 0, f"Found {len(broken_images)} broken images!"
    log.success("Health audit passed")
