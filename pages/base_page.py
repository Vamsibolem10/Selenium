from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from utils.logger import log
import os
import time

class BasePage:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 15)

    def wait_for_full_load(self, timeout=30):
        """Waits for the page to be fully loaded and stabilized."""
        log.info("Waiting for page to fully load and stabilize...")
        try:
            # 1. Wait for readyState complete
            self.wait.until(lambda d: d.execute_script("return document.readyState") == "complete")
            
            # 2. Wait for body to be visible
            self.wait.until(EC.visibility_of_element_located((By.TAG_NAME, "body")))
            
            # 3. Small sleep to allow for JS animations and dynamic content to settle
            time.sleep(3)
            log.success("Page loaded and stabilized.")
        except Exception as e:
            log.warning(f"Wait for full load timed out or failed: {e}")

    def find_element(self, locator, timeout=None):
        wait = WebDriverWait(self.driver, timeout) if timeout else self.wait
        try:
            log.debug(f"Finding element: {locator}")
            return wait.until(EC.presence_of_element_located(locator))
        except TimeoutException:
            self.take_screenshot(f"error_finding_{locator[1]}")
            log.error(f"Element not found within timeout: {locator}")
            raise

    def click(self, locator, verify_visible=None):
        try:
            element = self.find_element(locator)
            log.info(f"Clicking on element: {locator}")
            
            # Record current state for verification
            old_url = self.driver.current_url
            
            element.click()
            
            # 1. Automatic Verification: Check if URL changed or specific element appeared
            if verify_visible:
                if self.is_visible(verify_visible):
                    log.success(f"Verification Successful: {verify_visible} is visible.")
                else:
                    log.error(f"Verification Failed: {verify_visible} did not appear after click.")
            
            # 2. General Integrity Check: Look for error text on page
            body_text = self.driver.find_element(By.TAG_NAME, "body").text.lower()
            if "error" in body_text or "404" in body_text:
                log.warning(f"Potential issue detected on page after clicking {locator}")
                
        except Exception as e:
            log.error(f"Failed to click on {locator}: {e}")
            self.take_screenshot(f"fail_click_{locator[1]}")
            raise

    def enter_text(self, locator, text):
        try:
            element = self.find_element(locator)
            log.info(f"Entering text into {locator}: {text[:5]}...")
            element.clear()
            element.send_keys(text)
        except Exception as e:
            log.error(f"Failed to enter text into {locator}: {e}")
            raise

    def get_text(self, locator):
        text = self.find_element(locator).text
        log.debug(f"Text retrieved from {locator}: {text}")
        return text

    def is_visible(self, locator):
        try:
            visible = self.wait.until(EC.visibility_of_element_located(locator)).is_displayed()
            log.debug(f"Element {locator} visibility: {visible}")
            return visible
        except:
            return False

    def take_screenshot(self, name):
        os.makedirs("screenshots", exist_ok=True)
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        
        # Get domain for better screenshot organization
        try:
            url = self.driver.current_url
            domain = url.replace("https://", "").replace("http://", "").replace("www.", "").split("/")[0]
            domain = "".join(c if c.isalnum() or c in ("-", "_") else "_" for c in domain)
            prefix = f"{domain}_"
        except:
            prefix = ""
            
        filename = f"screenshots/{prefix}{name}_{timestamp}.png"
        self.driver.save_screenshot(filename)
        log.info(f"Screenshot saved: {filename}")

    def scroll_to_element(self, locator):
        element = self.find_element(locator)
        self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
        log.info(f"Scrolled to element: {locator}")
