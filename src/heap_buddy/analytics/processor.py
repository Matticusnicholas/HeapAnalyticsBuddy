"""
Analytics data processor for generating insights and visualizations
"""

from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass
import json


@dataclass
class AnalyticsInsight:
    """Represents an analytics insight"""
    category: str  # pages, events, users, journeys, etc.
    insight_type: str  # trend, anomaly, recommendation, summary
    priority: str  # high, medium, low
    title: str
    description: str
    data: Dict[str, Any]


class AnalyticsProcessor:
    """
    Processes extracted Heap data to generate insights and report-ready data
    """

    def __init__(self, data: Dict[str, Any]):
        """
        Initialize with extracted and processed Heap data

        Args:
            data: Processed data from HeapDataExtractor
        """
        self.data = data if data is not None else {}
        self.insights: List[AnalyticsInsight] = []

    def analyze_all(self) -> Dict[str, Any]:
        """Run all analyses and return comprehensive results"""
        results = {
            "summary": self.generate_executive_summary(),
            "page_analysis": self.analyze_pages(),
            "event_analysis": self.analyze_events(),
            "journey_analysis": self.analyze_journeys(),
            "funnel_analysis": self.analyze_funnels(),
            "retention_analysis": self.analyze_retention(),
            "insights": self.generate_all_insights(),
            "recommendations": self.generate_recommendations(),
        }
        return results

    def generate_executive_summary(self) -> Dict[str, Any]:
        """Generate executive summary of analytics"""
        overview = self.data.get("overview", {})
        pages = self.data.get("pages", [])
        events = self.data.get("events", [])

        total_pageviews = sum(p.get("total_views", 0) for p in pages)
        total_events = sum(e.get("total_count", 0) for e in events)

        summary = {
            "reporting_period": {
                "days": self.data.get("metadata", {}).get("date_range_days", 30),
                "generated_at": datetime.now().isoformat()
            },
            "key_metrics": {
                "total_users": overview.get("total_users", 0),
                "total_sessions": overview.get("total_sessions", 0),
                "total_pageviews": total_pageviews,
                "total_events": total_events,
                "avg_session_duration_seconds": overview.get("avg_session_duration", 0),
                "avg_session_duration_formatted": self._format_duration(overview.get("avg_session_duration", 0)),
                "bounce_rate": overview.get("bounce_rate", 0),
                "pages_per_session": overview.get("pages_per_session", 0),
            },
            "growth_indicators": {
                "new_users": overview.get("new_users", 0),
                "returning_users": overview.get("returning_users", 0),
                "return_rate": self._calculate_return_rate(overview),
            },
            "highlights": self._generate_highlights(),
        }

        return summary

    def _format_duration(self, seconds: float) -> str:
        """Format seconds into human readable duration"""
        if seconds < 60:
            return f"{int(seconds)}s"
        elif seconds < 3600:
            mins = int(seconds // 60)
            secs = int(seconds % 60)
            return f"{mins}m {secs}s"
        else:
            hours = int(seconds // 3600)
            mins = int((seconds % 3600) // 60)
            return f"{hours}h {mins}m"

    def _calculate_return_rate(self, overview: Dict) -> float:
        """Calculate user return rate"""
        total = overview.get("total_users", 0)
        returning = overview.get("returning_users", 0)
        if total > 0:
            return round((returning / total) * 100, 1)
        return 0.0

    def _generate_highlights(self) -> List[str]:
        """Generate key highlights for the summary"""
        highlights = []
        pages = self.data.get("pages", [])
        events = self.data.get("events", [])

        if pages:
            top_page = pages[0]
            highlights.append(f"Top page: {top_page.get('url', 'N/A')} with {top_page.get('total_views', 0):,} views")

        if events:
            top_event = events[0]
            highlights.append(f"Most triggered event: {top_event.get('name', 'N/A')} ({top_event.get('total_count', 0):,} times)")

        overview = self.data.get("overview", {})
        if overview.get("bounce_rate", 0) > 0:
            bounce = overview["bounce_rate"]
            if bounce > 70:
                highlights.append(f"High bounce rate ({bounce}%) - consider UX improvements")
            elif bounce < 40:
                highlights.append(f"Excellent bounce rate ({bounce}%) - users are engaged")

        return highlights

    def analyze_pages(self) -> Dict[str, Any]:
        """Analyze page performance"""
        pages = self.data.get("pages", [])

        if not pages:
            return {"status": "no_data", "pages": []}

        # Sort by different metrics
        by_views = sorted(pages, key=lambda x: x.get("total_views", 0), reverse=True)
        by_time = sorted(pages, key=lambda x: x.get("avg_time_on_page", 0), reverse=True)
        by_bounce = sorted(pages, key=lambda x: x.get("bounce_rate", 0), reverse=True)

        # Calculate aggregates
        total_views = sum(p.get("total_views", 0) for p in pages)
        avg_time_all = sum(p.get("avg_time_on_page", 0) for p in pages) / len(pages) if pages else 0

        analysis = {
            "total_pages": len(pages),
            "total_pageviews": total_views,
            "avg_time_across_pages": avg_time_all,
            "top_pages_by_views": by_views[:10],
            "top_pages_by_engagement": by_time[:10],
            "pages_with_high_bounce": [p for p in by_bounce if p.get("bounce_rate", 0) > 70][:5],
            "page_distribution": self._calculate_page_distribution(pages),
        }

        return analysis

    def _calculate_page_distribution(self, pages: List[Dict]) -> Dict[str, int]:
        """Categorize pages by URL patterns"""
        distribution = {
            "home": 0,
            "product": 0,
            "blog": 0,
            "checkout": 0,
            "account": 0,
            "other": 0
        }

        for page in pages:
            url = page.get("url", "").lower()
            views = page.get("total_views", 0)

            if url in ['/', '/home', 'home'] or url.endswith('/'):
                distribution["home"] += views
            elif any(x in url for x in ['product', 'item', 'shop', 'store']):
                distribution["product"] += views
            elif any(x in url for x in ['blog', 'article', 'post', 'news']):
                distribution["blog"] += views
            elif any(x in url for x in ['checkout', 'cart', 'payment', 'order']):
                distribution["checkout"] += views
            elif any(x in url for x in ['account', 'profile', 'settings', 'login', 'signup']):
                distribution["account"] += views
            else:
                distribution["other"] += views

        return distribution

    def analyze_events(self) -> Dict[str, Any]:
        """Analyze event data"""
        events = self.data.get("events", [])

        if not events:
            return {"status": "no_data", "events": []}

        # Categorize events
        auto_events = [e for e in events if e.get("event_type") == "auto"]
        custom_events = [e for e in events if e.get("event_type") == "custom"]

        total_count = sum(e.get("total_count", 0) for e in events)

        analysis = {
            "total_events_tracked": len(events),
            "total_event_count": total_count,
            "auto_tracked_events": len(auto_events),
            "custom_events": len(custom_events),
            "top_events": sorted(events, key=lambda x: x.get("total_count", 0), reverse=True)[:15],
            "event_frequency": self._calculate_event_frequency(events),
            "event_categories": self._categorize_events(events),
        }

        return analysis

    def _calculate_event_frequency(self, events: List[Dict]) -> Dict[str, Any]:
        """Calculate event frequency statistics"""
        counts = [e.get("total_count", 0) for e in events]
        if not counts:
            return {}

        return {
            "average": sum(counts) / len(counts),
            "max": max(counts),
            "min": min(counts),
            "median": sorted(counts)[len(counts) // 2],
        }

    def _categorize_events(self, events: List[Dict]) -> Dict[str, List[Dict]]:
        """Categorize events by type/pattern"""
        categories = {
            "clicks": [],
            "forms": [],
            "pageviews": [],
            "navigation": [],
            "other": []
        }

        for event in events:
            name = event.get("name", "").lower()

            if any(x in name for x in ["click", "tap", "press", "button"]):
                categories["clicks"].append(event)
            elif any(x in name for x in ["form", "submit", "input", "fill"]):
                categories["forms"].append(event)
            elif any(x in name for x in ["view", "page", "visit"]):
                categories["pageviews"].append(event)
            elif any(x in name for x in ["navigate", "scroll", "swipe", "route"]):
                categories["navigation"].append(event)
            else:
                categories["other"].append(event)

        return categories

    def analyze_journeys(self) -> Dict[str, Any]:
        """Analyze user journey patterns"""
        journeys = self.data.get("journeys", [])

        if not journeys:
            return {"status": "no_data", "journeys": []}

        # Find common patterns
        entry_points = {}
        exit_points = {}
        step_counts = {}

        for journey in journeys:
            steps = journey.get("steps", [])
            if steps:
                # Entry point
                entry = steps[0]
                entry_points[entry] = entry_points.get(entry, 0) + journey.get("user_count", 1)

                # Exit point
                exit_pt = steps[-1]
                exit_points[exit_pt] = exit_points.get(exit_pt, 0) + journey.get("user_count", 1)

                # Step count
                count = len(steps)
                step_counts[count] = step_counts.get(count, 0) + 1

        analysis = {
            "total_journeys": len(journeys),
            "common_entry_points": sorted(entry_points.items(), key=lambda x: x[1], reverse=True)[:5],
            "common_exit_points": sorted(exit_points.items(), key=lambda x: x[1], reverse=True)[:5],
            "journey_length_distribution": step_counts,
            "avg_journey_length": sum(len(j.get("steps", [])) for j in journeys) / len(journeys) if journeys else 0,
            "top_journeys": journeys[:10],
        }

        return analysis

    def analyze_funnels(self) -> Dict[str, Any]:
        """Analyze funnel performance"""
        funnels = self.data.get("funnels", [])

        if not funnels:
            return {"status": "no_data", "funnels": []}

        analysis = {
            "total_funnels": len(funnels),
            "funnels": []
        }

        for funnel in funnels:
            steps = funnel.get("steps", [])
            if not steps:
                continue

            funnel_analysis = {
                "name": funnel.get("funnel_name", "Unnamed"),
                "total_steps": len(steps),
                "overall_conversion": funnel.get("overall_conversion", 0),
                "steps": steps,
                "biggest_drop": self._find_biggest_drop(steps),
            }

            analysis["funnels"].append(funnel_analysis)

        return analysis

    def _find_biggest_drop(self, steps: List[Dict]) -> Dict[str, Any]:
        """Find the step with the biggest conversion drop"""
        biggest_drop = None
        max_drop = 0

        for i, step in enumerate(steps[1:], 1):
            drop = step.get("drop_off_rate", 0)
            if drop > max_drop:
                max_drop = drop
                biggest_drop = {
                    "step_number": i + 1,
                    "step_name": step.get("name", ""),
                    "drop_off_rate": drop
                }

        return biggest_drop or {}

    def analyze_retention(self) -> Dict[str, Any]:
        """Analyze user retention"""
        retention = self.data.get("retention", {})
        avg_retention = retention.get("average_retention", {})

        if not avg_retention:
            return {"status": "no_data"}

        # Calculate retention curve
        weeks = []
        for key, value in sorted(avg_retention.items()):
            week_num = int(key.split("_")[1]) if "_" in key else 0
            weeks.append({"week": week_num, "retention": value})

        # Determine retention health
        week1 = avg_retention.get("week_1", 0)
        health = "poor"
        if week1 >= 40:
            health = "excellent"
        elif week1 >= 25:
            health = "good"
        elif week1 >= 15:
            health = "fair"

        analysis = {
            "retention_curve": weeks,
            "week_1_retention": week1,
            "retention_health": health,
            "recommendations": self._generate_retention_recommendations(week1, weeks),
        }

        return analysis

    def _generate_retention_recommendations(self, week1: float, weeks: List[Dict]) -> List[str]:
        """Generate retention improvement recommendations"""
        recommendations = []

        if week1 < 15:
            recommendations.append("Critical: Week 1 retention is very low. Focus on onboarding experience.")
            recommendations.append("Consider implementing welcome emails or tutorials.")
        elif week1 < 25:
            recommendations.append("Week 1 retention has room for improvement. Review first-time user experience.")

        if len(weeks) >= 2:
            week1_val = weeks[0].get("retention", 0) if weeks else 0
            week2_val = weeks[1].get("retention", 0) if len(weeks) > 1 else 0
            if week2_val > 0 and (week1_val - week2_val) > 15:
                recommendations.append("Large drop between week 1 and 2. Users may not be finding continued value.")

        return recommendations

    def generate_all_insights(self) -> List[Dict[str, Any]]:
        """Generate all insights from the data"""
        insights = []

        # Add existing insights from data
        existing_insights = self.data.get("insights", [])
        insights.extend(existing_insights)

        # Generate additional insights
        insights.extend(self._generate_page_insights())
        insights.extend(self._generate_event_insights())
        insights.extend(self._generate_journey_insights())

        return insights

    def _generate_page_insights(self) -> List[Dict[str, Any]]:
        """Generate page-specific insights"""
        insights = []
        pages = self.data.get("pages", [])

        if not pages:
            return insights

        # High performing pages
        total_views = sum(p.get("total_views", 0) for p in pages)
        if pages and total_views > 0:
            top_page = pages[0]
            top_share = (top_page.get("total_views", 0) / total_views) * 100

            if top_share > 50:
                insights.append({
                    "category": "pages",
                    "type": "concentration",
                    "priority": "medium",
                    "title": "Traffic Concentration",
                    "description": f"Your top page accounts for {top_share:.1f}% of all traffic. Consider diversifying."
                })

        # Low engagement pages
        low_engagement = [p for p in pages if p.get("avg_time_on_page", 0) < 10 and p.get("total_views", 0) > 100]
        if low_engagement:
            insights.append({
                "category": "pages",
                "type": "attention_needed",
                "priority": "high",
                "title": "Low Engagement Pages",
                "description": f"{len(low_engagement)} pages have very low time-on-page despite significant traffic."
            })

        return insights

    def _generate_event_insights(self) -> List[Dict[str, Any]]:
        """Generate event-specific insights"""
        insights = []
        events = self.data.get("events", [])

        if not events:
            return insights

        # Check for conversion events
        conversion_keywords = ["purchase", "signup", "subscribe", "checkout", "complete", "submit"]
        conversion_events = [e for e in events if any(kw in e.get("name", "").lower() for kw in conversion_keywords)]

        if conversion_events:
            total_conversions = sum(e.get("total_count", 0) for e in conversion_events)
            insights.append({
                "category": "events",
                "type": "conversion",
                "priority": "high",
                "title": "Conversion Events Detected",
                "description": f"Found {len(conversion_events)} conversion-related events with {total_conversions:,} total occurrences."
            })

        return insights

    def _generate_journey_insights(self) -> List[Dict[str, Any]]:
        """Generate journey-specific insights"""
        insights = []
        journeys = self.data.get("journeys", [])

        if journeys:
            avg_length = sum(len(j.get("steps", [])) for j in journeys) / len(journeys)
            if avg_length > 7:
                insights.append({
                    "category": "journeys",
                    "type": "complexity",
                    "priority": "medium",
                    "title": "Long User Journeys",
                    "description": f"Average journey has {avg_length:.1f} steps. Consider simplifying user flows."
                })

        return insights

    def generate_recommendations(self) -> List[Dict[str, str]]:
        """Generate actionable recommendations"""
        recommendations = []

        # Based on page analysis
        pages = self.data.get("pages", [])
        if pages:
            high_bounce = [p for p in pages if p.get("bounce_rate", 0) > 70]
            if high_bounce:
                recommendations.append({
                    "area": "User Experience",
                    "priority": "High",
                    "recommendation": f"Review {len(high_bounce)} pages with high bounce rates. Consider improving content, load times, or CTAs.",
                    "impact": "Could significantly improve engagement and conversions."
                })

        # Based on event analysis
        events = self.data.get("events", [])
        if len(events) < 10:
            recommendations.append({
                "area": "Tracking",
                "priority": "Medium",
                "recommendation": "Consider implementing more custom events to better understand user behavior.",
                "impact": "Better insights into user actions and conversion paths."
            })

        # Based on retention
        retention = self.data.get("retention", {})
        if retention.get("average_retention", {}).get("week_1", 0) < 20:
            recommendations.append({
                "area": "Retention",
                "priority": "High",
                "recommendation": "Week 1 retention is below 20%. Focus on improving onboarding and first-time user experience.",
                "impact": "Direct impact on user lifetime value and growth."
            })

        # Based on journeys
        journeys = self.data.get("journeys", [])
        if journeys:
            short_journeys = [j for j in journeys if len(j.get("steps", [])) <= 2]
            if len(short_journeys) > len(journeys) * 0.5:
                recommendations.append({
                    "area": "Engagement",
                    "priority": "Medium",
                    "recommendation": "Many users have very short journeys. Consider adding more engaging content or features.",
                    "impact": "Increased page views and time on site."
                })

        return recommendations

    def get_chart_data(self) -> Dict[str, Any]:
        """Prepare data specifically formatted for chart generation"""
        return {
            "page_views_chart": self._prepare_page_views_chart(),
            "event_distribution_chart": self._prepare_event_distribution_chart(),
            "retention_curve_chart": self._prepare_retention_chart(),
            "funnel_chart": self._prepare_funnel_chart(),
            "journey_sankey": self._prepare_journey_data(),
        }

    def _prepare_page_views_chart(self) -> Dict[str, Any]:
        """Prepare page views bar chart data"""
        pages = self.data.get("pages", [])[:10]
        return {
            "labels": [p.get("url", "")[:30] for p in pages],
            "values": [p.get("total_views", 0) for p in pages],
            "title": "Top 10 Pages by Views",
            "type": "bar"
        }

    def _prepare_event_distribution_chart(self) -> Dict[str, Any]:
        """Prepare event distribution pie chart data"""
        events = self.data.get("events", [])[:8]
        total = sum(e.get("total_count", 0) for e in events)
        return {
            "labels": [e.get("name", "")[:20] for e in events],
            "values": [e.get("total_count", 0) for e in events],
            "percentages": [(e.get("total_count", 0) / total * 100) if total > 0 else 0 for e in events],
            "title": "Event Distribution",
            "type": "pie"
        }

    def _prepare_retention_chart(self) -> Dict[str, Any]:
        """Prepare retention curve line chart data"""
        retention = self.data.get("retention", {})
        avg = retention.get("average_retention", {})
        weeks = []
        values = []
        for key in sorted(avg.keys()):
            week_num = int(key.split("_")[1]) if "_" in key else 0
            weeks.append(f"Week {week_num}")
            values.append(avg[key])
        return {
            "labels": weeks,
            "values": values,
            "title": "User Retention Over Time",
            "type": "line"
        }

    def _prepare_funnel_chart(self) -> Dict[str, Any]:
        """Prepare funnel chart data"""
        funnels = self.data.get("funnels", [])
        if not funnels:
            return {"labels": [], "values": [], "type": "funnel"}

        funnel = funnels[0]  # Use first funnel
        steps = funnel.get("steps", [])
        return {
            "labels": [s.get("name", "") for s in steps],
            "values": [s.get("conversion_rate", 0) for s in steps],
            "title": funnel.get("funnel_name", "Conversion Funnel"),
            "type": "funnel"
        }

    def _prepare_journey_data(self) -> Dict[str, Any]:
        """Prepare journey data for sankey diagram"""
        journeys = self.data.get("journeys", [])
        nodes = set()
        links = []

        for journey in journeys[:10]:
            steps = journey.get("steps", [])
            count = journey.get("user_count", 1)
            for i in range(len(steps) - 1):
                nodes.add(steps[i])
                nodes.add(steps[i + 1])
                links.append({
                    "source": steps[i],
                    "target": steps[i + 1],
                    "value": count
                })

        return {
            "nodes": list(nodes),
            "links": links,
            "title": "User Journey Flow",
            "type": "sankey"
        }
