"""
Enhanced data extraction from Heap Analytics
Handles parsing and structuring of raw scraped data
"""

import re
import json
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field, asdict


@dataclass
class PageMetrics:
    """Metrics for a single page"""
    url: str
    page_title: str = ""
    total_views: int = 0
    unique_visitors: int = 0
    avg_time_on_page: float = 0.0  # seconds
    bounce_rate: float = 0.0
    exit_rate: float = 0.0
    entries: int = 0


@dataclass
class EventMetrics:
    """Metrics for an event"""
    name: str
    event_type: str = "custom"  # custom, pageview, click, form_submit, etc.
    total_count: int = 0
    unique_users: int = 0
    first_seen: Optional[datetime] = None
    last_seen: Optional[datetime] = None


@dataclass
class UserJourney:
    """Represents a user journey/path"""
    path_id: str
    steps: List[str] = field(default_factory=list)
    user_count: int = 0
    conversion_rate: float = 0.0
    avg_duration: float = 0.0


@dataclass
class FunnelStep:
    """A step in a funnel"""
    name: str
    visitors: int = 0
    conversion_rate: float = 0.0
    drop_off_rate: float = 0.0


@dataclass
class FunnelAnalysis:
    """Complete funnel analysis"""
    funnel_name: str
    steps: List[FunnelStep] = field(default_factory=list)
    overall_conversion: float = 0.0
    total_entries: int = 0


@dataclass
class RetentionCohort:
    """Retention data for a cohort"""
    cohort_date: str
    initial_users: int = 0
    retention_by_period: Dict[int, float] = field(default_factory=dict)  # period -> retention %


@dataclass
class AnalyticsOverview:
    """High-level analytics overview"""
    total_users: int = 0
    new_users: int = 0
    returning_users: int = 0
    total_sessions: int = 0
    total_pageviews: int = 0
    avg_session_duration: float = 0.0
    bounce_rate: float = 0.0
    pages_per_session: float = 0.0


class HeapDataExtractor:
    """
    Processes and structures raw Heap Analytics data
    """

    def __init__(self):
        self._raw_data: Dict[str, Any] = {}
        self._processed_data: Dict[str, Any] = {}

    def load_raw_data(self, data: Dict[str, Any]):
        """Load raw extracted data"""
        self._raw_data = data if data is not None else {}
        return self

    def load_from_file(self, filepath: str):
        """Load raw data from JSON file"""
        with open(filepath, 'r') as f:
            self._raw_data = json.load(f)
        return self

    def process_all(self) -> Dict[str, Any]:
        """Process all raw data into structured format"""
        self._processed_data = {
            "overview": self._process_overview(),
            "pages": self._process_pages(),
            "events": self._process_events(),
            "journeys": self._process_journeys(),
            "funnels": self._process_funnels(),
            "retention": self._process_retention(),
            "insights": self._generate_insights(),
            "metadata": {
                "processed_at": datetime.now().isoformat(),
                "data_source": "heap_analytics",
                "date_range_days": self._raw_data.get("date_range_days", 30)
            }
        }
        return self._processed_data

    def _parse_number(self, value: Any) -> int:
        """Parse a string number (handles commas, K, M suffixes)"""
        if isinstance(value, (int, float)):
            return int(value)
        if not value or not isinstance(value, str):
            return 0

        value = value.strip().upper()

        # Remove commas
        value = value.replace(',', '')

        # Handle K/M suffixes
        multiplier = 1
        if value.endswith('K'):
            multiplier = 1000
            value = value[:-1]
        elif value.endswith('M'):
            multiplier = 1000000
            value = value[:-1]

        try:
            return int(float(value) * multiplier)
        except (ValueError, TypeError):
            return 0

    def _parse_percentage(self, value: Any) -> float:
        """Parse a percentage string"""
        if isinstance(value, (int, float)):
            return float(value)
        if not value or not isinstance(value, str):
            return 0.0

        # Remove % sign and parse
        value = value.strip().replace('%', '')
        try:
            return float(value)
        except (ValueError, TypeError):
            return 0.0

    def _parse_duration(self, value: Any) -> float:
        """Parse duration string to seconds"""
        if isinstance(value, (int, float)):
            return float(value)
        if not value or not isinstance(value, str):
            return 0.0

        value = value.strip().lower()

        # Try to match patterns like "2m 30s", "1h 5m", "45s"
        total_seconds = 0

        # Hours
        hours_match = re.search(r'(\d+(?:\.\d+)?)\s*h', value)
        if hours_match:
            total_seconds += float(hours_match.group(1)) * 3600

        # Minutes
        mins_match = re.search(r'(\d+(?:\.\d+)?)\s*m(?:in)?', value)
        if mins_match:
            total_seconds += float(mins_match.group(1)) * 60

        # Seconds
        secs_match = re.search(r'(\d+(?:\.\d+)?)\s*s(?:ec)?', value)
        if secs_match:
            total_seconds += float(secs_match.group(1))

        # If no pattern matched, try parsing as seconds
        if total_seconds == 0:
            try:
                total_seconds = float(re.sub(r'[^\d.]', '', value))
            except ValueError:
                pass

        return total_seconds

    def _process_overview(self) -> Dict[str, Any]:
        """Process dashboard metrics into overview"""
        metrics = self._raw_data.get("dashboard_metrics", {})

        overview = AnalyticsOverview()

        # Map common metric names to our structure
        metric_mappings = {
            "total_users": ["total users", "users", "all users", "total visitors"],
            "new_users": ["new users", "new visitors", "first time users"],
            "returning_users": ["returning users", "return visitors"],
            "total_sessions": ["sessions", "total sessions", "visits"],
            "total_pageviews": ["pageviews", "page views", "total pageviews"],
            "bounce_rate": ["bounce rate", "bounces"],
            "avg_session_duration": ["avg session duration", "session duration", "avg time"],
            "pages_per_session": ["pages / session", "pages per session", "avg pages"],
        }

        for attr, keywords in metric_mappings.items():
            for key, value in metrics.items():
                if any(kw in key.lower() for kw in keywords):
                    if "rate" in attr or "per" in attr:
                        setattr(overview, attr, self._parse_percentage(value))
                    elif "duration" in attr:
                        setattr(overview, attr, self._parse_duration(value))
                    else:
                        setattr(overview, attr, self._parse_number(value))
                    break

        return asdict(overview)

    def _process_pages(self) -> List[Dict[str, Any]]:
        """Process page analytics data"""
        raw_pages = self._raw_data.get("page_analytics", [])
        processed_pages = []

        for page_data in raw_pages:
            if not page_data:
                continue

            page = PageMetrics(
                url=page_data.get("page", page_data.get("url", "")),
                page_title=page_data.get("title", ""),
                total_views=self._parse_number(page_data.get("views", page_data.get("pageviews", 0))),
                unique_visitors=self._parse_number(page_data.get("unique_users", page_data.get("visitors", 0))),
                avg_time_on_page=self._parse_duration(page_data.get("avg_time", page_data.get("time_on_page", 0))),
                bounce_rate=self._parse_percentage(page_data.get("bounce_rate", 0)),
                exit_rate=self._parse_percentage(page_data.get("exit_rate", 0)),
            )

            if page.url:
                processed_pages.append(asdict(page))

        # Sort by views descending
        processed_pages.sort(key=lambda x: x["total_views"], reverse=True)

        return processed_pages

    def _process_events(self) -> List[Dict[str, Any]]:
        """Process event data"""
        raw_events = self._raw_data.get("events", [])
        processed_events = []

        for event_data in raw_events:
            if not event_data:
                continue

            event = EventMetrics(
                name=event_data.get("name", ""),
                event_type=event_data.get("type", "custom"),
                total_count=self._parse_number(event_data.get("count", 0)),
                unique_users=self._parse_number(event_data.get("unique_users", event_data.get("users", 0))),
            )

            if event.name:
                processed_events.append(asdict(event))

        # Sort by count descending
        processed_events.sort(key=lambda x: x["total_count"], reverse=True)

        return processed_events

    def _process_journeys(self) -> List[Dict[str, Any]]:
        """Process user journey/path data"""
        raw_paths = self._raw_data.get("user_paths", [])
        processed_journeys = []

        for i, path_data in enumerate(raw_paths):
            if not path_data:
                continue

            steps = path_data.get("path", [])
            if isinstance(steps, str):
                steps = [s.strip() for s in steps.split("->")]

            journey = UserJourney(
                path_id=f"path_{i+1}",
                steps=steps,
                user_count=self._parse_number(path_data.get("users", path_data.get("count", 0))),
                conversion_rate=self._parse_percentage(path_data.get("conversion_rate", 0)),
            )

            if journey.steps:
                processed_journeys.append(asdict(journey))

        return processed_journeys

    def _process_funnels(self) -> List[Dict[str, Any]]:
        """Process funnel data"""
        raw_funnels = self._raw_data.get("funnels", [])
        processed_funnels = []

        for i, funnel_data in enumerate(raw_funnels):
            if not funnel_data:
                continue

            steps = []
            step_names = funnel_data.get("steps", [])
            conversion_rates = funnel_data.get("conversion_rates", [])

            for j, step_name in enumerate(step_names):
                conv_rate = 0.0
                if j < len(conversion_rates):
                    conv_rate = self._parse_percentage(conversion_rates[j])

                step = FunnelStep(
                    name=step_name,
                    conversion_rate=conv_rate,
                    drop_off_rate=100 - conv_rate if j > 0 else 0
                )
                steps.append(asdict(step))

            overall_conversion = 0.0
            if steps:
                # Overall conversion is product of all step conversions
                conv = 1.0
                for step in steps[1:]:  # Skip first step
                    conv *= (step["conversion_rate"] / 100)
                overall_conversion = conv * 100

            funnel = FunnelAnalysis(
                funnel_name=funnel_data.get("name", f"Funnel {i+1}"),
                steps=steps,
                overall_conversion=overall_conversion,
            )

            processed_funnels.append(asdict(funnel))

        return processed_funnels

    def _process_retention(self) -> Dict[str, Any]:
        """Process retention data"""
        raw_retention = self._raw_data.get("retention", {})
        values = raw_retention.get("values", [])

        retention_data = {
            "cohorts": [],
            "average_retention": {},
        }

        # Parse retention percentages
        retention_percentages = []
        for val in values:
            pct = self._parse_percentage(val)
            if pct > 0:
                retention_percentages.append(pct)

        # Calculate average retention by period
        if retention_percentages:
            # Assume these are weekly retention values
            for i, pct in enumerate(retention_percentages[:8]):  # Up to 8 weeks
                retention_data["average_retention"][f"week_{i+1}"] = pct

        return retention_data

    def _generate_insights(self) -> List[Dict[str, str]]:
        """Generate insights from the processed data"""
        insights = []

        # Page insights
        pages = self._processed_data.get("pages", []) if self._processed_data else self._process_pages()
        if pages:
            top_page = pages[0]
            insights.append({
                "category": "pages",
                "type": "top_performer",
                "title": "Most Viewed Page",
                "description": f"'{top_page['url']}' is your most visited page with {top_page['total_views']:,} views."
            })

            # Pages with high bounce rate
            high_bounce_pages = [p for p in pages if p.get("bounce_rate", 0) > 70]
            if high_bounce_pages:
                insights.append({
                    "category": "pages",
                    "type": "attention_needed",
                    "title": "High Bounce Rate Alert",
                    "description": f"{len(high_bounce_pages)} pages have bounce rates above 70%. Consider reviewing content and UX."
                })

        # Event insights
        events = self._processed_data.get("events", []) if self._processed_data else self._process_events()
        if events:
            total_events = sum(e.get("total_count", 0) for e in events)
            insights.append({
                "category": "events",
                "type": "summary",
                "title": "Event Tracking Summary",
                "description": f"Tracking {len(events)} unique events with {total_events:,} total occurrences."
            })

        # Journey insights
        journeys = self._processed_data.get("journeys", []) if self._processed_data else self._process_journeys()
        if journeys:
            common_path = journeys[0] if journeys else None
            if common_path and common_path.get("steps"):
                path_str = " → ".join(common_path["steps"][:5])
                insights.append({
                    "category": "journeys",
                    "type": "common_pattern",
                    "title": "Common User Journey",
                    "description": f"Most common path: {path_str}"
                })

        # Retention insights
        retention = self._processed_data.get("retention", {}) if self._processed_data else self._process_retention()
        avg_retention = retention.get("average_retention", {})
        if avg_retention:
            week1 = avg_retention.get("week_1", 0)
            if week1 > 0:
                insights.append({
                    "category": "retention",
                    "type": "metric",
                    "title": "Week 1 Retention",
                    "description": f"{week1:.1f}% of users return within the first week."
                })

        return insights

    def get_processed_data(self) -> Dict[str, Any]:
        """Get processed data"""
        if not self._processed_data:
            self.process_all()
        return self._processed_data

    def get_summary_stats(self) -> Dict[str, Any]:
        """Get summary statistics"""
        if not self._processed_data:
            self.process_all()

        pages = self._processed_data.get("pages", [])
        events = self._processed_data.get("events", [])
        overview = self._processed_data.get("overview", {})

        return {
            "total_pages_tracked": len(pages),
            "total_events_tracked": len(events),
            "total_users": overview.get("total_users", 0),
            "total_sessions": overview.get("total_sessions", 0),
            "total_pageviews": sum(p.get("total_views", 0) for p in pages),
            "avg_session_duration": overview.get("avg_session_duration", 0),
            "bounce_rate": overview.get("bounce_rate", 0),
        }

    def export_to_json(self, filepath: str):
        """Export processed data to JSON"""
        import os
        os.makedirs(os.path.dirname(filepath) or '.', exist_ok=True)
        with open(filepath, 'w') as f:
            json.dump(self.get_processed_data(), f, indent=2, default=str)
