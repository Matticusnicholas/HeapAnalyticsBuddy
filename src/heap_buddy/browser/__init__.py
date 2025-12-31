"""
Browser automation module for Heap Analytics Buddy
Supports Firefox, Chrome via Selenium, and Playwright
"""

from .base import BaseBrowser
from .firefox_driver import FirefoxBrowser
from .chrome_driver import ChromeBrowser
from .playwright_driver import PlaywrightBrowser
from .factory import create_browser

__all__ = [
    'BaseBrowser',
    'FirefoxBrowser',
    'ChromeBrowser',
    'PlaywrightBrowser',
    'create_browser'
]
