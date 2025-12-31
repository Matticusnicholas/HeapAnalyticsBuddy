"""
Base browser interface for browser automation
"""

from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
from dataclasses import dataclass


@dataclass
class PageElement:
    """Represents a page element"""
    selector: str
    text: str
    attributes: Dict[str, str]
    tag_name: str


class BaseBrowser(ABC):
    """Abstract base class for browser automation"""

    def __init__(self, config):
        self.config = config
        self._driver = None
        self._is_connected = False

    @abstractmethod
    def start(self) -> bool:
        """Start the browser instance"""
        pass

    @abstractmethod
    def stop(self):
        """Stop the browser and clean up"""
        pass

    @abstractmethod
    def navigate(self, url: str) -> bool:
        """Navigate to a URL"""
        pass

    @abstractmethod
    def get_current_url(self) -> str:
        """Get the current page URL"""
        pass

    @abstractmethod
    def get_page_source(self) -> str:
        """Get the current page HTML source"""
        pass

    @abstractmethod
    def find_element(self, selector: str, by: str = "css") -> Optional[Any]:
        """Find a single element"""
        pass

    @abstractmethod
    def find_elements(self, selector: str, by: str = "css") -> List[Any]:
        """Find multiple elements"""
        pass

    @abstractmethod
    def click(self, selector: str, by: str = "css") -> bool:
        """Click an element"""
        pass

    @abstractmethod
    def type_text(self, selector: str, text: str, by: str = "css") -> bool:
        """Type text into an element"""
        pass

    @abstractmethod
    def wait_for_element(self, selector: str, timeout: int = 10, by: str = "css") -> bool:
        """Wait for an element to be present"""
        pass

    @abstractmethod
    def wait_for_page_load(self, timeout: int = 30) -> bool:
        """Wait for page to fully load"""
        pass

    @abstractmethod
    def execute_script(self, script: str, *args) -> Any:
        """Execute JavaScript in the browser"""
        pass

    @abstractmethod
    def take_screenshot(self, filepath: str) -> bool:
        """Take a screenshot of the current page"""
        pass

    @abstractmethod
    def get_cookies(self) -> List[Dict[str, Any]]:
        """Get all cookies"""
        pass

    @abstractmethod
    def add_cookie(self, cookie: Dict[str, Any]):
        """Add a cookie"""
        pass

    @abstractmethod
    def get_text(self, selector: str, by: str = "css") -> Optional[str]:
        """Get text content of an element"""
        pass

    @abstractmethod
    def get_attribute(self, selector: str, attribute: str, by: str = "css") -> Optional[str]:
        """Get an attribute of an element"""
        pass

    @abstractmethod
    def is_element_visible(self, selector: str, by: str = "css") -> bool:
        """Check if an element is visible"""
        pass

    @abstractmethod
    def scroll_to_element(self, selector: str, by: str = "css") -> bool:
        """Scroll to an element"""
        pass

    @abstractmethod
    def scroll_page(self, direction: str = "down", amount: int = 500):
        """Scroll the page"""
        pass

    def is_connected(self) -> bool:
        """Check if browser is connected"""
        return self._is_connected

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()
