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
        broken_links = []
        for link in links:
            try:
                url = link.get_attribute("href")
                if url and url.startswith("http"):
                    try:
                        response = requests.head(url, timeout=5)
                        status = response.status_code
                        link_info = {"url": url, "status": status}
                        report.append(link_info)
                        if status >= 400:
                            log.warning(f"Broken link found: {url} (Status: {status})")
                            broken_links.append(link_info)
                    except Exception as e:
                        log.error(f"Error checking link {url}: {e}")
                        broken_links.append({"url": url, "status": "Error", "error": str(e)})
            except:
                continue
        return report, broken_links

    def interact_with_all_buttons(self):
        log.info("Starting button interaction (view and click)...")
        buttons = self.driver.find_elements(By.TAG_NAME, "button")
        clicked_buttons = []
        
        # Also find elements that look like buttons but are <a> or <div> with btn class
        other_btns = self.driver.find_elements(By.CSS_SELECTOR, ".btn, .button, [role='button']")
        all_potential_buttons = buttons + other_btns
        
        log.info(f"Found {len(all_potential_buttons)} potential buttons to interact with.")
        
        original_url = self.driver.current_url
        
        for i, btn in enumerate(all_potential_buttons):
            try:
                # 1. View: Scroll into view
                self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", btn)
                self.driver.execute_script("arguments[0].style.border='3px solid red';", btn) # Highlight it
                
                text = btn.text.strip() or btn.get_attribute("aria-label") or btn.get_attribute("value") or f"Button {i+1}"
                log.info(f"Viewing and clicking button: {text}")
                
                # 2. Click
                try:
                    # Try normal click first
                    btn.click()
                    clicked_buttons.append({"text": text, "status": "Success (Native)"})
                except Exception:
                    try:
                        # Fallback to JS click
                        self.driver.execute_script("arguments[0].click();", btn)
                        clicked_buttons.append({"text": text, "status": "Success (JS)"})
                    except Exception as click_err:
                        log.warning(f"Failed to click button {text}: {click_err}")
                        clicked_buttons.append({"text": text, "status": f"Failed: {str(click_err)[:50]}"})
                
                # If we navigated away, go back
                if self.driver.current_url != original_url:
                    self.driver.back()
                    self.wait_for_full_load()
                
                # Remove highlight
                try:
                    self.driver.execute_script("arguments[0].style.border='';", btn)
                except:
                    pass
                    
            except Exception as e:
                log.error(f"Error interacting with element: {e}")
                
        return clicked_buttons

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
