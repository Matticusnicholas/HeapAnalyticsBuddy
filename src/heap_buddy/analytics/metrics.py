"""
Metrics calculation utilities
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import math


class MetricsCalculator:
    """
    Utility class for calculating various analytics metrics
    """

    @staticmethod
    def calculate_growth_rate(current: float, previous: float) -> float:
        """Calculate growth rate between two values"""
        if previous == 0:
            return 100.0 if current > 0 else 0.0
        return ((current - previous) / previous) * 100

    @staticmethod
    def calculate_engagement_score(
        page_views: int,
        avg_time: float,
        bounce_rate: float,
        pages_per_session: float
    ) -> float:
        """
        Calculate an engagement score from 0-100

        Weights:
        - Average time on site: 30%
        - Pages per session: 30%
        - Inverse bounce rate: 40%
        """
        # Normalize values
        time_score = min(avg_time / 300, 1.0) * 30  # 5 min = max
        pages_score = min(pages_per_session / 5, 1.0) * 30  # 5 pages = max
        bounce_score = ((100 - bounce_rate) / 100) * 40

        return round(time_score + pages_score + bounce_score, 1)

    @staticmethod
    def calculate_conversion_rate(conversions: int, total_visitors: int) -> float:
        """Calculate conversion rate"""
        if total_visitors == 0:
            return 0.0
        return round((conversions / total_visitors) * 100, 2)

    @staticmethod
    def calculate_churn_rate(
        users_start: int,
        users_lost: int
    ) -> float:
        """Calculate churn rate"""
        if users_start == 0:
            return 0.0
        return round((users_lost / users_start) * 100, 2)

    @staticmethod
    def calculate_ltv(
        avg_revenue_per_user: float,
        avg_customer_lifespan_months: float
    ) -> float:
        """Calculate customer lifetime value"""
        return round(avg_revenue_per_user * avg_customer_lifespan_months, 2)

    @staticmethod
    def calculate_percentile(values: List[float], percentile: int) -> float:
        """Calculate the nth percentile of a list of values"""
        if not values:
            return 0.0
        sorted_values = sorted(values)
        index = (percentile / 100) * (len(sorted_values) - 1)
        lower = int(math.floor(index))
        upper = int(math.ceil(index))
        if lower == upper:
            return sorted_values[lower]
        return sorted_values[lower] * (upper - index) + sorted_values[upper] * (index - lower)

    @staticmethod
    def calculate_average(values: List[float]) -> float:
        """Calculate average of values"""
        if not values:
            return 0.0
        return sum(values) / len(values)

    @staticmethod
    def calculate_median(values: List[float]) -> float:
        """Calculate median of values"""
        return MetricsCalculator.calculate_percentile(values, 50)

    @staticmethod
    def calculate_standard_deviation(values: List[float]) -> float:
        """Calculate standard deviation"""
        if not values or len(values) < 2:
            return 0.0
        avg = MetricsCalculator.calculate_average(values)
        variance = sum((x - avg) ** 2 for x in values) / (len(values) - 1)
        return math.sqrt(variance)

    @staticmethod
    def calculate_cohort_retention(
        cohort_size: int,
        retained_users_by_period: List[int]
    ) -> List[float]:
        """Calculate retention percentages for a cohort"""
        if cohort_size == 0:
            return []
        return [round((users / cohort_size) * 100, 1) for users in retained_users_by_period]

    @staticmethod
    def calculate_funnel_conversions(step_counts: List[int]) -> List[Dict[str, float]]:
        """
        Calculate funnel step-by-step conversion rates

        Returns list of dicts with:
        - step_conversion: conversion from previous step
        - overall_conversion: conversion from first step
        - drop_off: users lost at this step
        """
        if not step_counts:
            return []

        results = []
        first_step = step_counts[0]

        for i, count in enumerate(step_counts):
            if i == 0:
                results.append({
                    "step_conversion": 100.0,
                    "overall_conversion": 100.0,
                    "drop_off": 0.0
                })
            else:
                prev_count = step_counts[i - 1]
                step_conv = (count / prev_count * 100) if prev_count > 0 else 0
                overall_conv = (count / first_step * 100) if first_step > 0 else 0
                drop_off = prev_count - count

                results.append({
                    "step_conversion": round(step_conv, 1),
                    "overall_conversion": round(overall_conv, 1),
                    "drop_off": drop_off
                })

        return results

    @staticmethod
    def calculate_time_on_page_quality(avg_time: float, expected_time: float = 60) -> str:
        """
        Determine time-on-page quality

        Args:
            avg_time: Average time on page in seconds
            expected_time: Expected reasonable time for the page type

        Returns:
            Quality rating: 'poor', 'below_average', 'average', 'good', 'excellent'
        """
        ratio = avg_time / expected_time if expected_time > 0 else 0

        if ratio < 0.3:
            return "poor"
        elif ratio < 0.6:
            return "below_average"
        elif ratio < 1.0:
            return "average"
        elif ratio < 1.5:
            return "good"
        else:
            return "excellent"

    @staticmethod
    def calculate_event_velocity(
        event_counts: List[int],
        time_periods: int = 7
    ) -> Dict[str, float]:
        """
        Calculate event velocity metrics

        Args:
            event_counts: List of event counts per time period
            time_periods: Number of time periods

        Returns:
            Dict with average, trend, and velocity score
        """
        if not event_counts:
            return {"average": 0, "trend": 0, "velocity_score": 0}

        avg = sum(event_counts) / len(event_counts)

        # Calculate trend (simple linear regression slope)
        n = len(event_counts)
        if n > 1:
            x_mean = (n - 1) / 2
            y_mean = avg
            numerator = sum((i - x_mean) * (y - y_mean) for i, y in enumerate(event_counts))
            denominator = sum((i - x_mean) ** 2 for i in range(n))
            trend = numerator / denominator if denominator != 0 else 0
        else:
            trend = 0

        # Velocity score combines average and trend
        velocity = avg + (trend * 10)  # Weight trend

        return {
            "average": round(avg, 2),
            "trend": round(trend, 4),
            "velocity_score": round(max(0, velocity), 2)
        }

    @staticmethod
    def format_large_number(value: int) -> str:
        """Format large numbers with K/M suffixes"""
        if value >= 1_000_000:
            return f"{value / 1_000_000:.1f}M"
        elif value >= 1_000:
            return f"{value / 1_000:.1f}K"
        return str(value)

    @staticmethod
    def format_duration(seconds: float) -> str:
        """Format seconds into readable duration"""
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

    @staticmethod
    def format_percentage(value: float, decimals: int = 1) -> str:
        """Format percentage with specified decimals"""
        return f"{value:.{decimals}f}%"

    @staticmethod
    def compare_periods(
        current: Dict[str, float],
        previous: Dict[str, float]
    ) -> Dict[str, Dict[str, float]]:
        """
        Compare metrics between two periods

        Returns dict with each metric's current, previous, change, and change_percent
        """
        comparison = {}

        all_keys = set(current.keys()) | set(previous.keys())

        for key in all_keys:
            curr_val = current.get(key, 0)
            prev_val = previous.get(key, 0)
            change = curr_val - prev_val
            change_pct = MetricsCalculator.calculate_growth_rate(curr_val, prev_val)

            comparison[key] = {
                "current": curr_val,
                "previous": prev_val,
                "change": change,
                "change_percent": change_pct,
                "direction": "up" if change > 0 else "down" if change < 0 else "flat"
            }

        return comparison
