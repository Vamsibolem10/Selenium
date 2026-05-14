from selenium.webdriver.common.by import By
from .base_page import BasePage

class DashboardPage(BasePage):
    TITLE = (By.CLASS_NAME, "title")
    INVENTORY_LIST = (By.CLASS_NAME, "inventory_list")
    BURGER_MENU = (By.ID, "react-burger-menu-btn")
    LOGOUT_LINK = (By.ID, "logout_sidebar_link")

    def get_title(self):
        return self.get_text(self.TITLE)

    def is_inventory_displayed(self):
        return self.is_visible(self.INVENTORY_LIST)

    def logout(self):
        self.click(self.BURGER_MENU)
        self.click(self.LOGOUT_LINK)
