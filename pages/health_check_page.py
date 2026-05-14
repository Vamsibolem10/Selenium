from selenium.webdriver.common.by import By
from .base_page import BasePage
from utils.logger import log
import requests

class HealthCheckPage(BasePage):
    LINKS = (By.TAG_NAME, "a")
    IMAGES = (By.TAG_NAME, "img")

    def check_all_links(self):
        log.info("Starting link validation...")
        links = self.driver.find_elements(*self.LINKS)
        report = []
        for link in links:
            url = link.get_attribute("href")
            if url and url.startswith("http"):
                try:
                    response = requests.head(url, timeout=5)
                    status = response.status_code
                    report.append({"url": url, "status": status})
                    if status >= 400:
                        log.warning(f"Broken link found: {url} (Status: {status})")
                except Exception as e:
                    log.error(f"Error checking link {url}: {e}")
        return report

    def check_all_images(self):
        log.info("Starting image validation...")
        images = self.driver.find_elements(*self.IMAGES)
        broken_images = []
        for img in images:
            src = img.get_attribute("src")
            is_loaded = self.driver.execute_script(
                "return arguments[0].complete && typeof arguments[0].naturalWidth != 'undefined' && arguments[0].naturalWidth > 0", 
                img
            )
            if not is_loaded:
                log.warning(f"Broken image detected: {src}")
                broken_images.append(src)
        return broken_images

    def get_performance_metrics(self):
        log.info("Retrieving performance metrics...")
        navigation_start = self.driver.execute_script("return window.performance.timing.navigationStart")
        load_event_end = self.driver.execute_script("return window.performance.timing.loadEventEnd")
        load_time = (load_event_end - navigation_start) / 1000
        log.info(f"Page Load Time: {load_time}s")
        return {"load_time": load_time}

    def capture_full_page_screenshot(self):
        log.info("Capturing full page screenshot...")
        S = lambda X: self.driver.execute_script('return document.body.parentNode.scroll'+X)
        self.driver.set_window_size(S('Width'), S('Height')) # Resizes window to object width/height
        self.take_screenshot("full_page_audit")
