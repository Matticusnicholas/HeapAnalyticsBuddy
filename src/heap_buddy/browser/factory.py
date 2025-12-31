"""
Browser factory - creates the appropriate browser instance
"""

from typing import Optional
from .base import BaseBrowser
from .firefox_driver import FirefoxBrowser
from .chrome_driver import ChromeBrowser
from .playwright_driver import PlaywrightBrowser


def create_browser(config) -> Optional[BaseBrowser]:
    """
    Factory function to create the appropriate browser based on configuration

    Args:
        config: BrowserConfig object with browser settings

    Returns:
        BaseBrowser instance or None if browser type is invalid
    """
    browser_type = config.browser_type.lower()

    # Mapping of browser types to classes
    browser_map = {
        "firefox": FirefoxBrowser,
        "chrome": ChromeBrowser,
        "chromium": ChromeBrowser,
        "playwright": PlaywrightBrowser,
        "playwright-firefox": PlaywrightBrowser,
        "playwright-chrome": PlaywrightBrowser,
        "playwright-webkit": PlaywrightBrowser,
    }

    browser_class = browser_map.get(browser_type)

    if browser_class is None:
        print(f"Unknown browser type: {browser_type}")
        print(f"Available browsers: {', '.join(browser_map.keys())}")
        return None

    # For playwright variants, set the actual browser type
    if browser_type.startswith("playwright-"):
        actual_browser = browser_type.replace("playwright-", "")
        config.browser_type = actual_browser

    return browser_class(config)


def list_available_browsers():
    """List all available browser options"""
    return [
        {
            "name": "firefox",
            "description": "Firefox via Selenium (preferred)",
            "requires": "geckodriver",
        },
        {
            "name": "chrome",
            "description": "Chrome via Selenium",
            "requires": "chromedriver",
        },
        {
            "name": "playwright",
            "description": "Playwright with auto-detection",
            "requires": "playwright browsers",
        },
        {
            "name": "playwright-firefox",
            "description": "Firefox via Playwright",
            "requires": "playwright browsers",
        },
        {
            "name": "playwright-chrome",
            "description": "Chromium via Playwright",
            "requires": "playwright browsers",
        },
        {
            "name": "playwright-webkit",
            "description": "WebKit via Playwright",
            "requires": "playwright browsers",
        },
    ]
