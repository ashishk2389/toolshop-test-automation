from pages.base_page import BasePage
from playwright.sync_api import expect


class LoginPage(BasePage):

    # Locators
    EMAIL_INPUT = "Your email"
    PASSWORD_INPUT = "Your password"
    LOGIN_BUTTON = "Login"
    def __init__(self, page):
        super().__init__(page)

    # Actions

    def enter_email(self, email):
        self.page.get_by_placeholder(self.EMAIL_INPUT).fill(email)
        
    def enter_password(self, password):
        self.page.get_by_placeholder(self.PASSWORD_INPUT).fill(password)


    def click_login(self):
        self.page.get_by_role("button", name=self.LOGIN_BUTTON).click()


    def login(self, user_details: dict):

        self.enter_email(user_details.get("email"))
        self.enter_password(user_details.get("password"))
        self.click_login()

    def navigateToLoginPage(self):
        self.navigate("https://practicesoftwaretesting.com/auth/login")

    def getErrorMessage(self):
        #todo
        pass

    # Validations

    def verify_login_page_displayed(self):

        expect(
            self.page.locator("h3")
        ).to_have_text("Login")


    def verify_email_field_visible(self):
        self.page.get_by_placeholder(self.EMAIL_INPUT).is_visible()

