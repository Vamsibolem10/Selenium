from selenium.webdriver.common.by import By
from .base_page import BasePage

class LoginPage(BasePage):
    USERNAME_INPUT = (By.ID, "user-name")
    PASSWORD_INPUT = (By.ID, "password")
    LOGIN_BUTTON = (By.ID, "login-button")
    ERROR_MESSAGE = (By.CSS_SELECTOR, "[data-test='error']")

    def login(self, username, password):
        self.enter_text(self.USERNAME_INPUT, username)
        self.enter_text(self.PASSWORD_INPUT, password)
        # Verify that clicking login takes us to the inventory list
        from .dashboard_page import DashboardPage
        self.click(self.LOGIN_BUTTON, verify_visible=DashboardPage.INVENTORY_LIST)

    def get_error_message(self):
        return self.get_text(self.ERROR_MESSAGE)
