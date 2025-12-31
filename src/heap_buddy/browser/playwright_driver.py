"""
Playwright browser driver - supports Firefox, Chrome, and WebKit
"""

import time
import asyncio
from typing import Optional, List, Dict, Any
from pathlib import Path

try:
    from playwright.sync_api import sync_playwright, Browser, Page, BrowserContext
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False

from .base import BaseBrowser


class PlaywrightBrowser(BaseBrowser):
    """Playwright-based browser implementation"""

    def __init__(self, config):
        super().__init__(config)
        self._playwright = None
        self._browser: Optional[Browser] = None
        self._context: Optional[BrowserContext] = None
        self._page: Optional[Page] = None
        self._browser_type = config.browser_type  # firefox, chrome, webkit

    def start(self) -> bool:
        """Start Playwright browser"""
        if not PLAYWRIGHT_AVAILABLE:
            print("Playwright is not installed. Run: pip install playwright && playwright install")
            return False

        try:
            self._playwright = sync_playwright().start()

            # Select browser type
            if self._browser_type == "firefox":
                browser_launcher = self._playwright.firefox
            elif self._browser_type in ["chrome", "chromium"]:
                browser_launcher = self._playwright.chromium
            elif self._browser_type == "webkit":
                browser_launcher = self._playwright.webkit
            else:
                browser_launcher = self._playwright.firefox  # Default to Firefox

            # Launch options
            launch_options = {
                "headless": self.config.headless,
            }

            # Use persistent context for profile support
            if self.config.profile_path or self.config.user_data_dir:
                user_data_dir = self.config.profile_path or self.config.user_data_dir
                self._context = browser_launcher.launch_persistent_context(
                    user_data_dir,
                    headless=self.config.headless,
                    viewport={"width": self.config.window_width, "height": self.config.window_height},
                )
                self._page = self._context.pages[0] if self._context.pages else self._context.new_page()
                print(f"Using persistent profile: {user_data_dir}")
            else:
                self._browser = browser_launcher.launch(**launch_options)
                self._context = self._browser.new_context(
                    viewport={"width": self.config.window_width, "height": self.config.window_height},
                )
                self._page = self._context.new_page()

            self._is_connected = True
            print(f"Playwright {self._browser_type} browser started successfully")
            return True

        except Exception as e:
            print(f"Failed to start Playwright browser: {e}")
            return False

    def stop(self):
        """Stop Playwright browser"""
        try:
            if self._page:
                self._page.close()
            if self._context:
                self._context.close()
            if self._browser:
                self._browser.close()
            if self._playwright:
                self._playwright.stop()
            print("Playwright browser stopped")
        except Exception as e:
            print(f"Error stopping Playwright: {e}")
        finally:
            self._page = None
            self._context = None
            self._browser = None
            self._playwright = None
            self._is_connected = False

    def navigate(self, url: str) -> bool:
        """Navigate to URL"""
        try:
            self._page.goto(url, wait_until="networkidle")
            return True
        except Exception as e:
            print(f"Navigation error: {e}")
            return False

    def get_current_url(self) -> str:
        """Get current URL"""
        return self._page.url if self._page else ""

    def get_page_source(self) -> str:
        """Get page source"""
        return self._page.content() if self._page else ""

    def find_element(self, selector: str, by: str = "css") -> Optional[Any]:
        """Find single element"""
        try:
            locator = self._get_locator(selector, by)
            if locator.count() > 0:
                return locator.first
            return None
        except Exception:
            return None

    def find_elements(self, selector: str, by: str = "css") -> List[Any]:
        """Find multiple elements"""
        try:
            locator = self._get_locator(selector, by)
            return locator.all()
        except Exception:
            return []

    def _get_locator(self, selector: str, by: str = "css"):
        """Get Playwright locator based on selector type"""
        if by == "xpath":
            return self._page.locator(f"xpath={selector}")
        elif by == "id":
            return self._page.locator(f"#{selector}")
        elif by == "class":
            return self._page.locator(f".{selector}")
        elif by == "text":
            return self._page.get_by_text(selector)
        elif by == "role":
            return self._page.get_by_role(selector)
        else:  # css
            return self._page.locator(selector)

    def click(self, selector: str, by: str = "css") -> bool:
        """Click element"""
        try:
            locator = self._get_locator(selector, by)
            locator.click()
            return True
        except Exception as e:
            print(f"Click error: {e}")
            return False

    def type_text(self, selector: str, text: str, by: str = "css") -> bool:
        """Type text into element"""
        try:
            locator = self._get_locator(selector, by)
            locator.fill(text)
            return True
        except Exception as e:
            print(f"Type error: {e}")
            return False

    def wait_for_element(self, selector: str, timeout: int = 10, by: str = "css") -> bool:
        """Wait for element to be present"""
        try:
            locator = self._get_locator(selector, by)
            locator.wait_for(timeout=timeout * 1000)
            return True
        except Exception:
            return False

    def wait_for_page_load(self, timeout: int = 30) -> bool:
        """Wait for page to load"""
        try:
            self._page.wait_for_load_state("networkidle", timeout=timeout * 1000)
            return True
        except Exception:
            return False

    def execute_script(self, script: str, *args) -> Any:
        """Execute JavaScript"""
        return self._page.evaluate(script, *args)

    def take_screenshot(self, filepath: str) -> bool:
        """Take screenshot"""
        try:
            self._page.screenshot(path=filepath, full_page=True)
            return True
        except Exception as e:
            print(f"Screenshot error: {e}")
            return False

    def get_cookies(self) -> List[Dict[str, Any]]:
        """Get all cookies"""
        return self._context.cookies() if self._context else []

    def add_cookie(self, cookie: Dict[str, Any]):
        """Add cookie"""
        if self._context:
            self._context.add_cookies([cookie])

    def get_text(self, selector: str, by: str = "css") -> Optional[str]:
        """Get element text"""
        try:
            locator = self._get_locator(selector, by)
            return locator.text_content()
        except Exception:
            return None

    def get_attribute(self, selector: str, attribute: str, by: str = "css") -> Optional[str]:
        """Get element attribute"""
        try:
            locator = self._get_locator(selector, by)
            return locator.get_attribute(attribute)
        except Exception:
            return None

    def is_element_visible(self, selector: str, by: str = "css") -> bool:
        """Check if element is visible"""
        try:
            locator = self._get_locator(selector, by)
            return locator.is_visible()
        except Exception:
            return False

    def scroll_to_element(self, selector: str, by: str = "css") -> bool:
        """Scroll to element"""
        try:
            locator = self._get_locator(selector, by)
            locator.scroll_into_view_if_needed()
            return True
        except Exception:
            return False

    def scroll_page(self, direction: str = "down", amount: int = 500):
        """Scroll page"""
        if direction == "down":
            self._page.evaluate(f"window.scrollBy(0, {amount})")
        elif direction == "up":
            self._page.evaluate(f"window.scrollBy(0, -{amount})")
        elif direction == "top":
            self._page.evaluate("window.scrollTo(0, 0)")
        elif direction == "bottom":
            self._page.evaluate("window.scrollTo(0, document.body.scrollHeight)")

    def wait_for_navigation(self, timeout: int = 30) -> bool:
        """Wait for navigation to complete"""
        try:
            self._page.wait_for_url("**/*", timeout=timeout * 1000)
            return True
        except Exception:
            return False

    def get_all_text(self) -> str:
        """Get all text content from the page"""
        return self._page.inner_text("body") if self._page else ""

    def screenshot_element(self, selector: str, filepath: str, by: str = "css") -> bool:
        """Take screenshot of specific element"""
        try:
            locator = self._get_locator(selector, by)
            locator.screenshot(path=filepath)
            return True
        except Exception as e:
            print(f"Element screenshot error: {e}")
            return False
