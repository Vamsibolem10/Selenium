from selenium.webdriver.common.by import By
from utils.logger import log
import time

class SiteSpider:
    def __init__(self, driver, max_depth=2):
        self.driver = driver
        self.max_depth = max_depth
        self.visited_urls = set()
        self.discovered_buttons = []

    def crawl(self, url, current_depth=0):
        if current_depth > self.max_depth or url in self.visited_urls:
            return
        
        log.info(f"Spider crawling: {url} (Depth: {current_depth})")
        self.visited_urls.add(url)
        
        try:
            self.driver.get(url)
            time.sleep(2) # Allow page to settle
            
            # 1. Analyze Buttons
            buttons = self.driver.find_elements(By.TAG_NAME, "button")
            log.info(f"Found {len(buttons)} buttons on {url}")
            for btn in buttons:
                try:
                    text = btn.text or btn.get_attribute("aria-label") or "Unnamed Button"
                    self.discovered_buttons.append({"page": url, "button": text})
                except:
                    continue

            # 2. Find Links for deeper crawling
            links = self.driver.find_elements(By.TAG_NAME, "a")
            urls_to_visit = []
            for link in links:
                try:
                    href = link.get_attribute("href")
                    if href and href.startswith(self.driver.current_url) and href not in self.visited_urls:
                        urls_to_visit.append(href)
                except:
                    continue

            # 3. Recursively visit (limited)
            for next_url in urls_to_visit[:5]: # Limit branching factor for safety
                self.crawl(next_url, current_depth + 1)

        except Exception as e:
            log.error(f"Spider failed on {url}: {e}")

    def get_summary(self):
        return {
            "pages_visited": len(self.visited_urls),
            "buttons_found": len(self.discovered_buttons),
            "site_map": list(self.visited_urls)
        }
