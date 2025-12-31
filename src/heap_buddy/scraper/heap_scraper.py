"""
Heap Analytics web scraper for data extraction
"""

import time
import json
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
    """

    # Common Heap Analytics selectors (may need updates as Heap UI changes)
    SELECTORS = {
        # Login page
        "email_input": "input[type='email'], input[name='email'], #email",
        "password_input": "input[type='password'], input[name='password'], #password",
        "login_button": "button[type='submit'], input[type='submit'], .login-button",

        # Dashboard navigation
        "dashboard_nav": "[data-testid='nav-dashboard'], .nav-dashboard, a[href*='dashboard']",
        "analyze_nav": "[data-testid='nav-analyze'], .nav-analyze, a[href*='analyze']",
        "users_nav": "[data-testid='nav-users'], .nav-users, a[href*='users']",
        "events_nav": "[data-testid='nav-events'], .nav-events, a[href*='events']",

        # Date picker
        "date_picker": ".date-picker, [data-testid='date-picker'], .date-range-selector",
        "date_preset_7d": "[data-value='7d'], .preset-7d",
        "date_preset_30d": "[data-value='30d'], .preset-30d",
        "date_preset_90d": "[data-value='90d'], .preset-90d",

        # Data tables and charts
        "data_table": ".data-table, table, [data-testid='data-table']",
        "chart_container": ".chart-container, .chart, [data-testid='chart']",
        "metric_card": ".metric-card, .kpi-card, [data-testid='metric']",

        # User list
        "user_row": ".user-row, tr[data-user-id], .user-list-item",

        # Event list
        "event_row": ".event-row, tr[data-event], .event-list-item",

        # Loading indicators
        "loading": ".loading, .spinner, [data-loading='true']",
    }

    def __init__(self, config: AppConfig):
        self.config = config
        self.browser: Optional[BaseBrowser] = None
        self._is_logged_in = False
        self._extracted_data: Dict[str, Any] = {}

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

        # Check if already logged in (redirected to dashboard)
        current_url = self.browser.get_current_url()
        if "/app" in current_url or "dashboard" in current_url:
            print("Already logged in via browser session!")
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
            if not self.browser.wait_for_element(self.SELECTORS["email_input"], timeout=10):
                print("Could not find email input field")
                return False

            self.browser.type_text(self.SELECTORS["email_input"], email)
            time.sleep(0.5)

            # Enter password
            self.browser.type_text(self.SELECTORS["password_input"], password)
            time.sleep(0.5)

            # Click login button
            self.browser.click(self.SELECTORS["login_button"])

            # Wait for redirect to dashboard
            time.sleep(3)
            self.browser.wait_for_page_load()

            current_url = self.browser.get_current_url()
            if "/app" in current_url or "dashboard" in current_url:
                print("Login successful!")
                self._is_logged_in = True
                return True
            else:
                print("Login may have failed. Current URL:", current_url)
                return self._wait_for_manual_login()

        except Exception as e:
            print(f"Login error: {e}")
            return self._wait_for_manual_login()

    def _wait_for_manual_login(self, timeout: int = 300) -> bool:
        """Wait for user to complete manual login"""
        print(f"Waiting up to {timeout} seconds for login...")
        start_time = time.time()

        while time.time() - start_time < timeout:
            current_url = self.browser.get_current_url()
            if "/app" in current_url or "dashboard" in current_url:
                print("Login detected!")
                self._is_logged_in = True
                return True
            time.sleep(2)

        print("Login timeout. Please try again.")
        return False

    def is_logged_in(self) -> bool:
        """Check if currently logged in"""
        return self._is_logged_in

    def navigate_to_section(self, section: str) -> bool:
        """Navigate to a specific section of Heap"""
        section_map = {
            "dashboard": "/app/dashboard",
            "analyze": "/app/analyze",
            "users": "/app/users",
            "events": "/app/events",
            "funnels": "/app/funnels",
            "retention": "/app/retention",
            "paths": "/app/paths",
        }

        if section.lower() in section_map:
            url = f"{self.config.heap.base_url}{section_map[section.lower()]}"
            self.browser.navigate(url)
            self.browser.wait_for_page_load()
            self._wait_for_loading()
            return True
        return False

    def _wait_for_loading(self, timeout: int = 30):
        """Wait for loading indicators to disappear"""
        start = time.time()
        while time.time() - start < timeout:
            if not self.browser.is_element_visible(self.SELECTORS["loading"]):
                time.sleep(1)  # Additional buffer
                return
            time.sleep(0.5)

    def set_date_range(self, days: int = 30) -> bool:
        """Set the date range for data extraction"""
        try:
            # Click date picker
            if self.browser.click(self.SELECTORS["date_picker"]):
                time.sleep(1)

                # Select preset
                preset_selector = None
                if days <= 7:
                    preset_selector = self.SELECTORS["date_preset_7d"]
                elif days <= 30:
                    preset_selector = self.SELECTORS["date_preset_30d"]
                else:
                    preset_selector = self.SELECTORS["date_preset_90d"]

                if preset_selector and self.browser.click(preset_selector):
                    self._wait_for_loading()
                    return True

            return False
        except Exception as e:
            print(f"Error setting date range: {e}")
            return False

    def extract_dashboard_metrics(self) -> Dict[str, Any]:
        """Extract metrics from the main dashboard"""
        print("Extracting dashboard metrics...")
        metrics = {}

        try:
            self.navigate_to_section("dashboard")
            time.sleep(2)

            # Extract metric cards
            metric_cards = self.browser.find_elements(self.SELECTORS["metric_card"])
            for card in metric_cards:
                try:
                    # Try to get metric name and value
                    card_text = card.text if hasattr(card, 'text') else str(card)
                    lines = card_text.strip().split('\n')
                    if len(lines) >= 2:
                        metric_name = lines[0].strip()
                        metric_value = lines[1].strip()
                        metrics[metric_name] = metric_value
                except Exception:
                    continue

            # Take screenshot of dashboard
            self.browser.take_screenshot("reports/screenshots/dashboard.png")

            self._extracted_data['dashboard_metrics'] = metrics
            print(f"Extracted {len(metrics)} dashboard metrics")

        except Exception as e:
            print(f"Error extracting dashboard metrics: {e}")

        return metrics

    def extract_page_analytics(self) -> List[Dict[str, Any]]:
        """Extract page view analytics - which pages users spend time on"""
        print("Extracting page analytics...")
        pages = []

        try:
            # Navigate to analyze section for pageviews
            self.browser.navigate(f"{self.config.heap.base_url}/app/analyze")
            self.browser.wait_for_page_load()
            time.sleep(2)

            # Try to extract page data from tables
            tables = self.browser.find_elements(self.SELECTORS["data_table"])
            for table in tables:
                try:
                    rows = table.find_elements("css", "tr")
                    for row in rows[1:]:  # Skip header
                        cells = row.find_elements("css", "td")
                        if len(cells) >= 2:
                            page_data = {
                                "page": cells[0].text if hasattr(cells[0], 'text') else "",
                                "views": cells[1].text if len(cells) > 1 and hasattr(cells[1], 'text') else "",
                                "unique_users": cells[2].text if len(cells) > 2 and hasattr(cells[2], 'text') else "",
                                "avg_time": cells[3].text if len(cells) > 3 and hasattr(cells[3], 'text') else "",
                            }
                            if page_data["page"]:
                                pages.append(page_data)
                except Exception:
                    continue

            # Also try to get data from JavaScript
            try:
                js_data = self.browser.execute_script("""
                    // Try to extract data from React state or window objects
                    if (window.__HEAP_DATA__) return JSON.stringify(window.__HEAP_DATA__);
                    if (window.heapData) return JSON.stringify(window.heapData);
                    return null;
                """)
                if js_data:
                    parsed = json.loads(js_data)
                    if isinstance(parsed, dict) and 'pages' in parsed:
                        pages.extend(parsed['pages'])
            except Exception:
                pass

            self._extracted_data['page_analytics'] = pages
            print(f"Extracted {len(pages)} page analytics records")

        except Exception as e:
            print(f"Error extracting page analytics: {e}")

        return pages

    def extract_user_paths(self) -> List[Dict[str, Any]]:
        """Extract user journey paths and patterns"""
        print("Extracting user paths...")
        paths = []

        try:
            # Navigate to paths section
            self.browser.navigate(f"{self.config.heap.base_url}/app/paths")
            self.browser.wait_for_page_load()
            time.sleep(3)
            self._wait_for_loading()

            # Take screenshot of paths
            self.browser.take_screenshot("reports/screenshots/paths.png")

            # Try to extract path data
            path_elements = self.browser.find_elements(".path-node, .journey-step, [data-path]")
            current_path = []

            for elem in path_elements:
                try:
                    step_text = elem.text if hasattr(elem, 'text') else ""
                    if step_text:
                        current_path.append(step_text)
                except Exception:
                    continue

            if current_path:
                paths.append({
                    "path": current_path,
                    "type": "common_journey"
                })

            # Extract from JavaScript if available
            try:
                js_paths = self.browser.execute_script("""
                    // Look for path data in page
                    const pathData = [];
                    document.querySelectorAll('[data-path], .path-visualization').forEach(el => {
                        pathData.push(el.innerText);
                    });
                    return JSON.stringify(pathData);
                """)
                if js_paths:
                    parsed = json.loads(js_paths)
                    for p in parsed:
                        if p:
                            paths.append({"path": p.split(" -> ") if " -> " in p else [p], "type": "extracted"})
            except Exception:
                pass

            self._extracted_data['user_paths'] = paths
            print(f"Extracted {len(paths)} user paths")

        except Exception as e:
            print(f"Error extracting user paths: {e}")

        return paths

    def extract_events(self) -> List[Dict[str, Any]]:
        """Extract event data"""
        print("Extracting events...")
        events = []

        try:
            # Navigate to events section
            self.browser.navigate(f"{self.config.heap.base_url}/app/events")
            self.browser.wait_for_page_load()
            time.sleep(2)
            self._wait_for_loading()

            # Extract from event rows
            event_rows = self.browser.find_elements(self.SELECTORS["event_row"])
            for row in event_rows:
                try:
                    row_text = row.text if hasattr(row, 'text') else ""
                    parts = row_text.split('\n')
                    if parts:
                        event = {
                            "name": parts[0] if len(parts) > 0 else "",
                            "count": parts[1] if len(parts) > 1 else "",
                            "type": "auto" if "auto" in row_text.lower() else "custom"
                        }
                        if event["name"]:
                            events.append(event)
                except Exception:
                    continue

            # Take screenshot
            self.browser.take_screenshot("reports/screenshots/events.png")

            self._extracted_data['events'] = events
            print(f"Extracted {len(events)} events")

        except Exception as e:
            print(f"Error extracting events: {e}")

        return events

    def extract_user_segments(self) -> List[Dict[str, Any]]:
        """Extract user segment data"""
        print("Extracting user segments...")
        segments = []

        try:
            # Navigate to users section
            self.browser.navigate(f"{self.config.heap.base_url}/app/users")
            self.browser.wait_for_page_load()
            time.sleep(2)
            self._wait_for_loading()

            # Extract segment information
            segment_elements = self.browser.find_elements(".segment, .user-segment, [data-segment]")
            for elem in segment_elements:
                try:
                    segment_text = elem.text if hasattr(elem, 'text') else ""
                    if segment_text:
                        segments.append({
                            "name": segment_text.split('\n')[0],
                            "count": segment_text.split('\n')[1] if '\n' in segment_text else ""
                        })
                except Exception:
                    continue

            self._extracted_data['user_segments'] = segments
            print(f"Extracted {len(segments)} user segments")

        except Exception as e:
            print(f"Error extracting user segments: {e}")

        return segments

    def extract_funnel_data(self) -> List[Dict[str, Any]]:
        """Extract funnel analysis data"""
        print("Extracting funnel data...")
        funnels = []

        try:
            # Navigate to funnels section
            self.browser.navigate(f"{self.config.heap.base_url}/app/funnels")
            self.browser.wait_for_page_load()
            time.sleep(2)
            self._wait_for_loading()

            # Take screenshot
            self.browser.take_screenshot("reports/screenshots/funnels.png")

            # Extract funnel steps
            funnel_steps = self.browser.find_elements(".funnel-step, .conversion-step, [data-funnel-step]")
            current_funnel = {"steps": [], "conversion_rates": []}

            for step in funnel_steps:
                try:
                    step_text = step.text if hasattr(step, 'text') else ""
                    if step_text:
                        lines = step_text.split('\n')
                        current_funnel["steps"].append(lines[0] if lines else "")
                        if len(lines) > 1:
                            # Try to extract conversion rate
                            for line in lines[1:]:
                                if '%' in line:
                                    current_funnel["conversion_rates"].append(line)
                except Exception:
                    continue

            if current_funnel["steps"]:
                funnels.append(current_funnel)

            self._extracted_data['funnels'] = funnels
            print(f"Extracted {len(funnels)} funnels")

        except Exception as e:
            print(f"Error extracting funnel data: {e}")

        return funnels

    def extract_retention_data(self) -> Dict[str, Any]:
        """Extract retention analysis data"""
        print("Extracting retention data...")
        retention = {}

        try:
            # Navigate to retention section
            self.browser.navigate(f"{self.config.heap.base_url}/app/retention")
            self.browser.wait_for_page_load()
            time.sleep(2)
            self._wait_for_loading()

            # Take screenshot
            self.browser.take_screenshot("reports/screenshots/retention.png")

            # Extract retention metrics
            retention_elements = self.browser.find_elements(".retention-cell, .cohort-cell, [data-retention]")
            retention_values = []

            for elem in retention_elements:
                try:
                    value = elem.text if hasattr(elem, 'text') else ""
                    if value and '%' in value:
                        retention_values.append(value)
                except Exception:
                    continue

            retention['values'] = retention_values

            self._extracted_data['retention'] = retention
            print(f"Extracted retention data with {len(retention_values)} values")

        except Exception as e:
            print(f"Error extracting retention data: {e}")

        return retention

    def extract_all_data(self, date_range_days: int = 30) -> Dict[str, Any]:
        """Extract all available data from Heap Analytics"""
        print(f"\nExtracting all Heap Analytics data for the last {date_range_days} days...")
        print("=" * 60)

        # Ensure screenshot directory exists
        import os
        os.makedirs("reports/screenshots", exist_ok=True)

        # Set date range
        self.set_date_range(date_range_days)

        # Extract all data types
        all_data = {
            "extraction_date": datetime.now().isoformat(),
            "date_range_days": date_range_days,
            "dashboard_metrics": self.extract_dashboard_metrics(),
            "page_analytics": self.extract_page_analytics(),
            "user_paths": self.extract_user_paths(),
            "events": self.extract_events(),
            "user_segments": self.extract_user_segments(),
            "funnels": self.extract_funnel_data(),
            "retention": self.extract_retention_data(),
        }

        self._extracted_data = all_data
        print("=" * 60)
        print("Data extraction complete!")

        return all_data

    def get_extracted_data(self) -> Dict[str, Any]:
        """Get all extracted data"""
        return self._extracted_data

    def save_raw_data(self, filepath: str):
        """Save extracted data to JSON file"""
        import os
        os.makedirs(os.path.dirname(filepath) or '.', exist_ok=True)
        with open(filepath, 'w') as f:
            json.dump(self._extracted_data, f, indent=2, default=str)
        print(f"Raw data saved to: {filepath}")

    def __enter__(self):
        self.start_browser()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop_browser()
