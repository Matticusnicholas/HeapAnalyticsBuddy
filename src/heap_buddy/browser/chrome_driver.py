"""
Chrome browser driver using Selenium
"""

import os
import time
from typing import Optional, List, Dict, Any

from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    WebDriverException,
    ElementNotInteractableException
)
from webdriver_manager.chrome import ChromeDriverManager

from .base import BaseBrowser


class ChromeBrowser(BaseBrowser):
    """Chrome browser implementation using Selenium"""

    SELECTOR_MAP = {
        "css": By.CSS_SELECTOR,
        "xpath": By.XPATH,
        "id": By.ID,
        "name": By.NAME,
        "class": By.CLASS_NAME,
        "tag": By.TAG_NAME,
        "link_text": By.LINK_TEXT,
        "partial_link_text": By.PARTIAL_LINK_TEXT,
    }

    def __init__(self, config):
        super().__init__(config)
        self._wait = None

    def start(self) -> bool:
        """Start Chrome browser"""
        try:
            options = ChromeOptions()

            # Headless mode
            if self.config.headless:
                options.add_argument("--headless=new")

            # Window size
            options.add_argument(f"--window-size={self.config.window_width},{self.config.window_height}")

            # Use existing Chrome profile if specified
            if self.config.user_data_dir:
                options.add_argument(f"--user-data-dir={self.config.user_data_dir}")
                print(f"Using Chrome user data directory: {self.config.user_data_dir}")
            elif self.config.profile_path:
                options.add_argument(f"--user-data-dir={self.config.profile_path}")

            # Anti-detection options
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option("useAutomationExtension", False)

            # Additional stability options
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-gpu")
            options.add_argument("--disable-extensions")

            # Install chromedriver automatically
            service = ChromeService(ChromeDriverManager().install())

            self._driver = webdriver.Chrome(service=service, options=options)
            self._driver.implicitly_wait(self.config.implicit_wait)
            self._wait = WebDriverWait(self._driver, self.config.timeout)

            # Remove webdriver flag
            self._driver.execute_script(
                "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
            )

            self._is_connected = True
            print("Chrome browser started successfully")
            return True

        except WebDriverException as e:
            print(f"Failed to start Chrome: {e}")
            return False

    def stop(self):
        """Stop Chrome browser"""
        if self._driver:
            try:
                self._driver.quit()
                print("Chrome browser stopped")
            except Exception as e:
                print(f"Error stopping Chrome: {e}")
            finally:
                self._driver = None
                self._is_connected = False

    def navigate(self, url: str) -> bool:
        """Navigate to URL"""
        try:
            self._driver.get(url)
            return True
        except WebDriverException as e:
            print(f"Navigation error: {e}")
            return False

    def get_current_url(self) -> str:
        """Get current URL"""
        return self._driver.current_url if self._driver else ""

    def get_page_source(self) -> str:
        """Get page source"""
        return self._driver.page_source if self._driver else ""

    def _get_by(self, by: str) -> By:
        """Convert string selector type to Selenium By"""
        return self.SELECTOR_MAP.get(by, By.CSS_SELECTOR)

    def find_element(self, selector: str, by: str = "css") -> Optional[Any]:
        """Find single element"""
        try:
            return self._driver.find_element(self._get_by(by), selector)
        except NoSuchElementException:
            return None

    def find_elements(self, selector: str, by: str = "css") -> List[Any]:
        """Find multiple elements"""
        try:
            return self._driver.find_elements(self._get_by(by), selector)
        except NoSuchElementException:
            return []

    def click(self, selector: str, by: str = "css") -> bool:
        """Click element"""
        try:
            element = self.find_element(selector, by)
            if element:
                element.click()
                return True
            return False
        except (ElementNotInteractableException, WebDriverException) as e:
            print(f"Click error: {e}")
            return False

    def type_text(self, selector: str, text: str, by: str = "css") -> bool:
        """Type text into element"""
        try:
            element = self.find_element(selector, by)
            if element:
                element.clear()
                element.send_keys(text)
                return True
            return False
        except (ElementNotInteractableException, WebDriverException) as e:
            print(f"Type error: {e}")
            return False

    def wait_for_element(self, selector: str, timeout: int = 10, by: str = "css") -> bool:
        """Wait for element to be present"""
        try:
            wait = WebDriverWait(self._driver, timeout)
            wait.until(EC.presence_of_element_located((self._get_by(by), selector)))
            return True
        except TimeoutException:
            return False

    def wait_for_page_load(self, timeout: int = 30) -> bool:
        """Wait for page to load"""
        try:
            wait = WebDriverWait(self._driver, timeout)
            wait.until(lambda d: d.execute_script("return document.readyState") == "complete")
            time.sleep(1)  # Additional wait for dynamic content
            return True
        except TimeoutException:
            return False

    def execute_script(self, script: str, *args) -> Any:
        """Execute JavaScript"""
        return self._driver.execute_script(script, *args)

    def take_screenshot(self, filepath: str) -> bool:
        """Take screenshot"""
        try:
            self._driver.save_screenshot(filepath)
            return True
        except WebDriverException as e:
            print(f"Screenshot error: {e}")
            return False

    def get_cookies(self) -> List[Dict[str, Any]]:
        """Get all cookies"""
        return self._driver.get_cookies() if self._driver else []

    def add_cookie(self, cookie: Dict[str, Any]):
        """Add cookie"""
        if self._driver:
            self._driver.add_cookie(cookie)

    def get_text(self, selector: str, by: str = "css") -> Optional[str]:
        """Get element text"""
        element = self.find_element(selector, by)
        return element.text if element else None

    def get_attribute(self, selector: str, attribute: str, by: str = "css") -> Optional[str]:
        """Get element attribute"""
        element = self.find_element(selector, by)
        return element.get_attribute(attribute) if element else None

    def is_element_visible(self, selector: str, by: str = "css") -> bool:
        """Check if element is visible"""
        element = self.find_element(selector, by)
        return element.is_displayed() if element else False

    def scroll_to_element(self, selector: str, by: str = "css") -> bool:
        """Scroll to element"""
        try:
            element = self.find_element(selector, by)
            if element:
                self._driver.execute_script("arguments[0].scrollIntoView(true);", element)
                time.sleep(0.5)
                return True
            return False
        except WebDriverException:
            return False

    def scroll_page(self, direction: str = "down", amount: int = 500):
        """Scroll page"""
        if direction == "down":
            self._driver.execute_script(f"window.scrollBy(0, {amount});")
        elif direction == "up":
            self._driver.execute_script(f"window.scrollBy(0, -{amount});")
        elif direction == "top":
            self._driver.execute_script("window.scrollTo(0, 0);")
        elif direction == "bottom":
            self._driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")


def get_chrome_profile_path() -> Optional[str]:
    """Get default Chrome profile path"""
    if os.name == 'nt':  # Windows
        return os.path.join(os.environ['LOCALAPPDATA'], 'Google', 'Chrome', 'User Data')
    elif os.name == 'posix':
        if 'darwin' in os.sys.platform:  # macOS
            return os.path.expanduser('~/Library/Application Support/Google/Chrome')
        else:  # Linux
            return os.path.expanduser('~/.config/google-chrome')
    return None
