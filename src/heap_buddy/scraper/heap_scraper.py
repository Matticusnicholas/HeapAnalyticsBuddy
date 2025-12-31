"""
Heap Analytics web scraper for data extraction
Uses click-based navigation to explore all available sections
"""

import time
import json
import os
from typing import Optional, Dict, List, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, field

from ..browser import create_browser, BaseBrowser
from ..config import AppConfig


@dataclass
class HeapSession:
    """Represents a user session in Heap"""
    session_id: str
    user_id: Optional[str]
    start_time: datetime
    end_time: Optional[datetime]
    duration_seconds: int
    page_views: int
    events: List[Dict[str, Any]] = field(default_factory=list)
    pages_visited: List[str] = field(default_factory=list)
    device_type: str = ""
    browser: str = ""
    country: str = ""
    city: str = ""


@dataclass
class HeapUser:
    """Represents a user in Heap"""
    user_id: str
    identity: Optional[str]
    first_seen: datetime
    last_seen: datetime
    total_sessions: int
    total_events: int
    properties: Dict[str, Any] = field(default_factory=dict)


@dataclass
class HeapEvent:
    """Represents an event in Heap"""
    event_name: str
    event_type: str  # pageview, click, custom, etc.
    count: int
    unique_users: int
    properties: Dict[str, Any] = field(default_factory=dict)


class HeapScraper:
    """
    Scrapes data from Heap Analytics dashboard using browser automation
    Uses click-based navigation to explore all sections dynamically
    """

    # Selectors for finding elements - multiple options for flexibility
    SELECTORS = {
        # Login page
        "email_input": "input[type='email'], input[name='email'], #email, input[placeholder*='mail']",
        "password_input": "input[type='password'], input[name='password'], #password",
        "login_button": "button[type='submit'], input[type='submit'], button:contains('Log'), button:contains('Sign')",

        # Sidebar navigation - broad selectors to catch various UI patterns
        "sidebar": "nav, aside, [role='navigation'], .sidebar, .nav-sidebar, .side-nav, #sidebar",
        "nav_links": "nav a, aside a, .sidebar a, .nav-link, .menu-item, [role='menuitem'], .side-nav a",

        # Main content area
        "main_content": "main, .main-content, .content, #content, [role='main'], .dashboard",

        # Clickable cards and metrics
        "metric_cards": ".metric, .card, .kpi, .stat, .widget, [class*='metric'], [class*='card'], [class*='stat']",
        "clickable_items": ".clickable, [role='button'], [onclick], [class*='click'], button:not([type='submit'])",

        # Data containers
        "data_table": "table, .table, [class*='table'], .data-grid, .grid",
        "chart_container": ".chart, [class*='chart'], .graph, [class*='graph'], svg, canvas",
        "list_items": "li, .list-item, .row, tr",

        # Numbers and values
        "numbers": ".number, .value, .count, .metric-value, [class*='number'], [class*='value']",

        # Loading indicators
        "loading": ".loading, .spinner, [class*='loading'], [class*='spinner'], .loader",

        # Date/time selectors
        "date_picker": ".date-picker, .date-range, [class*='date'], .calendar, input[type='date']",
        "dropdown": "select, .dropdown, [class*='dropdown'], .select",
    }

    def __init__(self, config: AppConfig):
        self.config = config
        self.browser: Optional[BaseBrowser] = None
        self._is_logged_in = False
        self._extracted_data: Dict[str, Any] = {}
        self._visited_urls: set = set()
        self._screenshot_count = 0

    def start_browser(self) -> bool:
        """Initialize and start the browser"""
        self.browser = create_browser(self.config.browser)
        if self.browser:
            return self.browser.start()
        return False

    def stop_browser(self):
        """Stop the browser"""
        if self.browser:
            self.browser.stop()
            self.browser = None

    def login(self, email: Optional[str] = None, password: Optional[str] = None) -> bool:
        """
        Login to Heap Analytics

        If email/password not provided, will try to use existing browser session
        """
        if not self.browser:
            print("Browser not started. Call start_browser() first.")
            return False

        # Use config credentials if not provided
        email = email or self.config.heap.email
        password = password or self.config.heap.password

        print("Navigating to Heap Analytics...")
        self.browser.navigate(self.config.heap.login_url)
        self.browser.wait_for_page_load()
        time.sleep(5)  # Extra wait for page to fully render

        # Check if already logged in (look for dashboard elements or URL patterns)
        current_url = self.browser.get_current_url()
        if self._check_if_logged_in(current_url):
            print("Already logged in!")
            self._is_logged_in = True
            return True

        # If no credentials provided, wait for manual login
        if not email or not password:
            print("\n" + "=" * 60)
            print("MANUAL LOGIN REQUIRED")
            print("=" * 60)
            print("Please log in to Heap Analytics in the browser window.")
            print("The tool will wait for you to complete the login.")
            print("=" * 60 + "\n")

            return self._wait_for_manual_login()

        # Automated login
        print("Attempting automated login...")
        try:
            # Enter email
            if not self.browser.wait_for_element(self.SELECTORS["email_input"], timeout=15):
                print("Could not find email input field")
                return self._wait_for_manual_login()

            self.browser.type_text(self.SELECTORS["email_input"], email)
            time.sleep(1)

            # Enter password
            self.browser.type_text(self.SELECTORS["password_input"], password)
            time.sleep(1)

            # Click login button
            self.browser.click(self.SELECTORS["login_button"])

            # Wait for redirect
            time.sleep(5)
            self.browser.wait_for_page_load()
            time.sleep(3)

            current_url = self.browser.get_current_url()
            if self._check_if_logged_in(current_url):
                print("Login successful!")
                self._is_logged_in = True
                return True
            else:
                print("Login may have failed. Waiting for manual login...")
                return self._wait_for_manual_login()

        except Exception as e:
            print(f"Login error: {e}")
            return self._wait_for_manual_login()

    def _check_if_logged_in(self, url: str) -> bool:
        """Check if the current page indicates logged in state"""
        # Check URL patterns
        logged_in_patterns = ['/app', '/dashboard', '/home', '/analyze', '/data', '/reports', '/insights']
        login_patterns = ['/login', '/signin', '/auth']

        url_lower = url.lower()

        # If we're on a login page, not logged in
        if any(pattern in url_lower for pattern in login_patterns):
            return False

        # If we're on an app page, logged in
        if any(pattern in url_lower for pattern in logged_in_patterns):
            return True

        # Check for sidebar/navigation elements that indicate logged-in state
        if self.browser.find_element(self.SELECTORS["sidebar"]):
            return True

        return False

    def _wait_for_manual_login(self, timeout: int = 300) -> bool:
        """Wait for user to complete manual login"""
        print(f"Waiting up to {timeout} seconds for login...")
        start_time = time.time()

        while time.time() - start_time < timeout:
            current_url = self.browser.get_current_url()
            if self._check_if_logged_in(current_url):
                print("Login detected!")
                self._is_logged_in = True
                time.sleep(3)  # Wait for page to stabilize
                return True
            time.sleep(2)

        print("Login timeout. Please try again.")
        return False

    def is_logged_in(self) -> bool:
        """Check if currently logged in"""
        return self._is_logged_in

    def _wait_for_loading(self, timeout: int = 30):
        """Wait for loading indicators to disappear and page to stabilize"""
        time.sleep(2)  # Initial wait
        start = time.time()
        while time.time() - start < timeout:
            if not self.browser.is_element_visible(self.SELECTORS["loading"]):
                time.sleep(2)  # Additional buffer for dynamic content
                return
            time.sleep(0.5)
        time.sleep(2)  # Final buffer

    def _take_screenshot(self, name: str) -> str:
        """Take a screenshot with a numbered prefix"""
        self._screenshot_count += 1
        os.makedirs("reports/screenshots", exist_ok=True)
        filename = f"reports/screenshots/{self._screenshot_count:02d}_{name}.png"
        self.browser.take_screenshot(filename)
        print(f"  Screenshot saved: {filename}")
        return filename

    def _extract_text_content(self) -> Dict[str, Any]:
        """Extract all text content from the current page"""
        content = {
            "url": self.browser.get_current_url(),
            "title": "",
            "numbers": [],
            "text_blocks": [],
            "tables": [],
            "lists": []
        }

        try:
            # Get page title
            title_elem = self.browser.find_element("h1, .title, .page-title, [class*='title']")
            if title_elem:
                content["title"] = title_elem.text if hasattr(title_elem, 'text') else ""

            # Extract all visible numbers/metrics
            number_elements = self.browser.find_elements(self.SELECTORS["numbers"])
            for elem in number_elements:
                try:
                    text = elem.text if hasattr(elem, 'text') else ""
                    if text and any(c.isdigit() for c in text):
                        content["numbers"].append(text.strip())
                except:
                    continue

            # Extract metric cards
            cards = self.browser.find_elements(self.SELECTORS["metric_cards"])
            for card in cards:
                try:
                    text = card.text if hasattr(card, 'text') else ""
                    if text:
                        content["text_blocks"].append(text.strip())
                except:
                    continue

            # Extract tables
            tables = self.browser.find_elements(self.SELECTORS["data_table"])
            for table in tables:
                try:
                    table_data = self._extract_table_data(table)
                    if table_data:
                        content["tables"].append(table_data)
                except:
                    continue

            # Extract list items
            lists = self.browser.find_elements(self.SELECTORS["list_items"])
            for item in lists[:50]:  # Limit to prevent too many items
                try:
                    text = item.text if hasattr(item, 'text') else ""
                    if text and len(text) < 500:  # Skip very long items
                        content["lists"].append(text.strip())
                except:
                    continue

        except Exception as e:
            print(f"  Error extracting content: {e}")

        return content

    def _extract_table_data(self, table) -> List[List[str]]:
        """Extract data from a table element"""
        data = []
        try:
            rows = table.find_elements("css", "tr")
            for row in rows[:100]:  # Limit rows
                cells = row.find_elements("css", "th, td")
                row_data = []
                for cell in cells:
                    text = cell.text if hasattr(cell, 'text') else ""
                    row_data.append(text.strip())
                if any(row_data):  # Skip empty rows
                    data.append(row_data)
        except:
            pass
        return data

    def _find_sidebar_links(self) -> List[Any]:
        """Find all navigation links in the sidebar"""
        links = []

        # Try multiple selector strategies
        selectors = [
            "nav a",
            "aside a",
            ".sidebar a",
            ".nav a",
            ".side-nav a",
            "[role='navigation'] a",
            ".menu a",
            ".nav-menu a",
            "[class*='sidebar'] a",
            "[class*='nav'] a:not([class*='navbar'])",
        ]

        for selector in selectors:
            try:
                found = self.browser.find_elements(selector)
                if found:
                    links.extend(found)
            except:
                continue

        # Remove duplicates based on href
        seen_hrefs = set()
        unique_links = []
        for link in links:
            try:
                href = link.get_attribute('href') if hasattr(link, 'get_attribute') else None
                if href and href not in seen_hrefs:
                    seen_hrefs.add(href)
                    unique_links.append(link)
            except:
                continue

        return unique_links

    def _find_clickable_elements(self) -> List[Any]:
        """Find clickable elements in the main content area"""
        elements = []

        selectors = [
            ".card",
            ".metric",
            ".widget",
            "[class*='clickable']",
            ".kpi",
            "[role='button']",
            ".panel-heading",
            ".chart-title",
            "[class*='expand']",
            "[class*='detail']",
        ]

        for selector in selectors:
            try:
                found = self.browser.find_elements(selector)
                elements.extend(found[:10])  # Limit per selector
            except:
                continue

        return elements[:20]  # Total limit

    def explore_sidebar(self) -> Dict[str, Any]:
        """Click through all sidebar items and extract data"""
        print("\n" + "=" * 60)
        print("EXPLORING SIDEBAR NAVIGATION")
        print("=" * 60)

        all_sections = {}

        # First, take a screenshot of the initial state
        self._take_screenshot("initial_dashboard")
        time.sleep(2)

        # Find all sidebar links
        sidebar_links = self._find_sidebar_links()
        print(f"\nFound {len(sidebar_links)} navigation links")

        # Get link info before clicking (as clicking may change the DOM)
        link_info = []
        for link in sidebar_links:
            try:
                text = link.text if hasattr(link, 'text') else ""
                href = link.get_attribute('href') if hasattr(link, 'get_attribute') else ""
                if text and href:
                    link_info.append({"text": text.strip(), "href": href, "element": link})
            except:
                continue

        print(f"Navigation items: {[l['text'] for l in link_info]}")

        # Click each link and extract data
        for i, info in enumerate(link_info):
            section_name = info['text']
            href = info['href']

            # Skip if already visited
            if href in self._visited_urls:
                continue

            print(f"\n[{i+1}/{len(link_info)}] Exploring: {section_name}")

            try:
                # Navigate to the link
                self.browser.navigate(href)
                self.browser.wait_for_page_load()
                self._wait_for_loading()

                self._visited_urls.add(href)

                # Take screenshot
                safe_name = "".join(c if c.isalnum() else "_" for c in section_name)
                self._take_screenshot(safe_name)

                # Extract content
                section_data = self._extract_text_content()
                section_data["section_name"] = section_name

                # Try to find and click sub-items for more detail
                sub_data = self._explore_section_details()
                if sub_data:
                    section_data["details"] = sub_data

                all_sections[section_name] = section_data
                print(f"  Extracted: {len(section_data.get('numbers', []))} numbers, "
                      f"{len(section_data.get('tables', []))} tables, "
                      f"{len(section_data.get('text_blocks', []))} text blocks")

            except Exception as e:
                print(f"  Error exploring {section_name}: {e}")
                continue

        return all_sections

    def _explore_section_details(self) -> List[Dict[str, Any]]:
        """Within a section, click on items to get more details"""
        details = []

        clickable = self._find_clickable_elements()

        for elem in clickable[:5]:  # Limit to prevent infinite loops
            try:
                # Get current URL to detect navigation
                before_url = self.browser.get_current_url()

                # Try to click
                elem.click()
                time.sleep(2)
                self._wait_for_loading()

                after_url = self.browser.get_current_url()

                # If we navigated somewhere new, extract that data
                if after_url != before_url and after_url not in self._visited_urls:
                    self._visited_urls.add(after_url)
                    detail_data = self._extract_text_content()
                    self._take_screenshot("detail_view")
                    details.append(detail_data)

                    # Go back
                    self.browser.navigate(before_url)
                    self.browser.wait_for_page_load()
                    self._wait_for_loading()

            except:
                continue

        return details

    def extract_all_data(self, date_range_days: int = 30) -> Dict[str, Any]:
        """Extract all available data from Heap Analytics by clicking through everything"""
        print(f"\nExtracting all Heap Analytics data for the last {date_range_days} days...")
        print("=" * 60)

        # Ensure screenshot directory exists
        os.makedirs("reports/screenshots", exist_ok=True)

        # Store initial URL to return to
        initial_url = self.browser.get_current_url()

        # Wait for dashboard to fully load
        time.sleep(3)
        self._wait_for_loading()

        # Extract data from current page first (dashboard)
        print("\nExtracting initial dashboard data...")
        dashboard_data = self._extract_text_content()
        self._take_screenshot("dashboard")

        # Explore all sidebar sections
        sections_data = self.explore_sidebar()

        # Compile all data
        all_data = {
            "extraction_date": datetime.now().isoformat(),
            "date_range_days": date_range_days,
            "initial_url": initial_url,
            "dashboard": dashboard_data,
            "sections": sections_data,
            "visited_urls": list(self._visited_urls),
            "screenshot_count": self._screenshot_count,
            # For backward compatibility with report generator
            "dashboard_metrics": self._compile_metrics(dashboard_data, sections_data),
            "page_analytics": self._compile_pages(sections_data),
            "events": self._compile_events(sections_data),
            "user_paths": [],
            "user_segments": [],
            "funnels": self._compile_funnels(sections_data),
            "retention": self._compile_retention(sections_data),
        }

        self._extracted_data = all_data

        print("\n" + "=" * 60)
        print("DATA EXTRACTION COMPLETE!")
        print(f"  Sections explored: {len(sections_data)}")
        print(f"  Screenshots taken: {self._screenshot_count}")
        print(f"  URLs visited: {len(self._visited_urls)}")
        print("=" * 60)

        return all_data

    def _compile_metrics(self, dashboard: Dict, sections: Dict) -> Dict[str, Any]:
        """Compile metrics from extracted data for backward compatibility"""
        metrics = {}

        # Extract from dashboard numbers
        for i, num in enumerate(dashboard.get("numbers", [])[:20]):
            metrics[f"metric_{i+1}"] = num

        # Extract from text blocks that look like metrics
        for block in dashboard.get("text_blocks", []):
            lines = block.split('\n')
            if len(lines) >= 2:
                # Assume format: label\nvalue
                label = lines[0].strip()
                value = lines[1].strip()
                if any(c.isdigit() for c in value):
                    metrics[label] = value

        return metrics

    def _compile_pages(self, sections: Dict) -> List[Dict[str, Any]]:
        """Compile page analytics from sections"""
        pages = []

        for section_name, section_data in sections.items():
            for table in section_data.get("tables", []):
                if len(table) > 1:  # Has header and data
                    headers = table[0] if table else []
                    for row in table[1:]:
                        if row and len(row) >= 2:
                            page_data = {
                                "page": row[0] if row else "",
                                "views": row[1] if len(row) > 1 else "",
                                "unique_users": row[2] if len(row) > 2 else "",
                                "avg_time": row[3] if len(row) > 3 else "",
                                "source_section": section_name
                            }
                            if page_data["page"]:
                                pages.append(page_data)

        return pages

    def _compile_events(self, sections: Dict) -> List[Dict[str, Any]]:
        """Compile events from sections"""
        events = []

        # Look for event-related sections
        for section_name, section_data in sections.items():
            if 'event' in section_name.lower():
                for table in section_data.get("tables", []):
                    for row in table[1:]:  # Skip header
                        if row:
                            events.append({
                                "name": row[0] if row else "",
                                "count": row[1] if len(row) > 1 else "",
                                "type": "extracted"
                            })

        return events

    def _compile_funnels(self, sections: Dict) -> List[Dict[str, Any]]:
        """Compile funnel data from sections"""
        funnels = []

        for section_name, section_data in sections.items():
            if 'funnel' in section_name.lower():
                funnel = {
                    "name": section_name,
                    "steps": [],
                    "conversion_rates": section_data.get("numbers", [])
                }
                funnels.append(funnel)

        return funnels

    def _compile_retention(self, sections: Dict) -> Dict[str, Any]:
        """Compile retention data from sections"""
        retention = {"values": []}

        for section_name, section_data in sections.items():
            if 'retention' in section_name.lower():
                # Look for percentage values
                for num in section_data.get("numbers", []):
                    if '%' in str(num):
                        retention["values"].append(num)

        return retention

    def get_extracted_data(self) -> Dict[str, Any]:
        """Get all extracted data"""
        return self._extracted_data

    def save_raw_data(self, filepath: str):
        """Save extracted data to JSON file"""
        os.makedirs(os.path.dirname(filepath) or '.', exist_ok=True)
        with open(filepath, 'w') as f:
            json.dump(self._extracted_data, f, indent=2, default=str)
        print(f"Raw data saved to: {filepath}")

    def __enter__(self):
        self.start_browser()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop_browser()
