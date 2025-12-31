"""
Chart generation for analytics reports
"""

import os
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
import io

# Try to import plotting libraries
try:
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    from matplotlib.figure import Figure
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

try:
    import plotly.graph_objects as go
    import plotly.express as px
    from plotly.subplots import make_subplots
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False


class ChartGenerator:
    """
    Generates charts for analytics reports

    Supports both matplotlib (for PDF/static) and plotly (for interactive/HTML)
    """

    # Color palettes
    COLORS = {
        "modern": [
            "#4F46E5",  # Indigo
            "#10B981",  # Emerald
            "#F59E0B",  # Amber
            "#EF4444",  # Red
            "#8B5CF6",  # Violet
            "#06B6D4",  # Cyan
            "#EC4899",  # Pink
            "#84CC16",  # Lime
        ],
        "classic": [
            "#1f77b4",
            "#ff7f0e",
            "#2ca02c",
            "#d62728",
            "#9467bd",
            "#8c564b",
            "#e377c2",
            "#7f7f7f",
        ],
        "minimal": [
            "#2D3748",
            "#4A5568",
            "#718096",
            "#A0AEC0",
            "#CBD5E0",
            "#E2E8F0",
            "#EDF2F7",
            "#F7FAFC",
        ]
    }

    def __init__(self, style: str = "modern", output_dir: str = "./reports/charts"):
        """
        Initialize chart generator

        Args:
            style: Color style - 'modern', 'classic', or 'minimal'
            output_dir: Directory to save chart images
        """
        self.style = style
        self.colors = self.COLORS.get(style, self.COLORS["modern"])
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        if MATPLOTLIB_AVAILABLE:
            plt.style.use('seaborn-v0_8-whitegrid')
            plt.rcParams['figure.figsize'] = (10, 6)
            plt.rcParams['font.size'] = 10
            plt.rcParams['axes.titlesize'] = 14
            plt.rcParams['axes.labelsize'] = 12

    def _get_color(self, index: int) -> str:
        """Get color from palette by index"""
        return self.colors[index % len(self.colors)]

    def create_bar_chart(
        self,
        labels: List[str],
        values: List[float],
        title: str,
        xlabel: str = "",
        ylabel: str = "",
        horizontal: bool = True,
        filename: Optional[str] = None
    ) -> Optional[str]:
        """
        Create a bar chart

        Args:
            labels: Category labels
            values: Corresponding values
            title: Chart title
            xlabel: X-axis label
            ylabel: Y-axis label
            horizontal: If True, create horizontal bar chart
            filename: Output filename (without extension)

        Returns:
            Path to saved chart image or None if failed
        """
        if not MATPLOTLIB_AVAILABLE:
            print("Matplotlib not available for chart generation")
            return None

        fig, ax = plt.subplots(figsize=(12, max(6, len(labels) * 0.5)))

        # Truncate long labels
        display_labels = [l[:40] + "..." if len(l) > 40 else l for l in labels]

        colors = [self._get_color(i) for i in range(len(values))]

        if horizontal:
            bars = ax.barh(display_labels, values, color=colors)
            ax.set_xlabel(ylabel or "Value")
            ax.set_ylabel(xlabel or "")
            # Add value labels
            for bar, val in zip(bars, values):
                width = bar.get_width()
                ax.text(width + max(values) * 0.01, bar.get_y() + bar.get_height()/2,
                       f'{val:,.0f}', ha='left', va='center', fontsize=9)
        else:
            bars = ax.bar(display_labels, values, color=colors)
            ax.set_xlabel(xlabel or "")
            ax.set_ylabel(ylabel or "Value")
            plt.xticks(rotation=45, ha='right')
            # Add value labels
            for bar, val in zip(bars, values):
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2, height,
                       f'{val:,.0f}', ha='center', va='bottom', fontsize=9)

        ax.set_title(title, fontweight='bold', pad=20)
        plt.tight_layout()

        # Save chart
        filepath = self.output_dir / f"{filename or 'bar_chart'}.png"
        plt.savefig(filepath, dpi=150, bbox_inches='tight', facecolor='white')
        plt.close()

        return str(filepath)

    def create_pie_chart(
        self,
        labels: List[str],
        values: List[float],
        title: str,
        filename: Optional[str] = None,
        show_percentage: bool = True
    ) -> Optional[str]:
        """
        Create a pie chart

        Args:
            labels: Slice labels
            values: Slice values
            title: Chart title
            filename: Output filename
            show_percentage: Show percentages on slices

        Returns:
            Path to saved chart image
        """
        if not MATPLOTLIB_AVAILABLE:
            return None

        fig, ax = plt.subplots(figsize=(10, 8))

        # Truncate labels
        display_labels = [l[:25] + "..." if len(l) > 25 else l for l in labels]

        colors = [self._get_color(i) for i in range(len(values))]

        def make_autopct(values):
            def autopct(pct):
                total = sum(values)
                val = int(round(pct * total / 100.0))
                return f'{pct:.1f}%\n({val:,})' if pct > 5 else ''
            return autopct

        wedges, texts, autotexts = ax.pie(
            values,
            labels=display_labels,
            colors=colors,
            autopct=make_autopct(values) if show_percentage else None,
            startangle=90,
            explode=[0.02] * len(values)
        )

        ax.set_title(title, fontweight='bold', pad=20)

        # Equal aspect ratio ensures circular pie
        ax.axis('equal')
        plt.tight_layout()

        filepath = self.output_dir / f"{filename or 'pie_chart'}.png"
        plt.savefig(filepath, dpi=150, bbox_inches='tight', facecolor='white')
        plt.close()

        return str(filepath)

    def create_line_chart(
        self,
        labels: List[str],
        values: List[float],
        title: str,
        xlabel: str = "",
        ylabel: str = "",
        filename: Optional[str] = None,
        fill: bool = True
    ) -> Optional[str]:
        """
        Create a line chart

        Args:
            labels: X-axis labels
            values: Y-axis values
            title: Chart title
            xlabel: X-axis label
            ylabel: Y-axis label
            filename: Output filename
            fill: Fill area under the line

        Returns:
            Path to saved chart image
        """
        if not MATPLOTLIB_AVAILABLE:
            return None

        fig, ax = plt.subplots(figsize=(12, 6))

        color = self._get_color(0)

        ax.plot(labels, values, marker='o', linewidth=2, markersize=8, color=color)

        if fill:
            ax.fill_between(labels, values, alpha=0.3, color=color)

        # Add value labels at each point
        for i, (x, y) in enumerate(zip(labels, values)):
            ax.annotate(f'{y:.1f}%' if isinstance(y, float) else f'{y:,.0f}',
                       (i, y), textcoords="offset points",
                       xytext=(0, 10), ha='center', fontsize=9)

        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        ax.set_title(title, fontweight='bold', pad=20)

        # Rotate x labels if needed
        if len(labels) > 6:
            plt.xticks(rotation=45, ha='right')

        plt.tight_layout()

        filepath = self.output_dir / f"{filename or 'line_chart'}.png"
        plt.savefig(filepath, dpi=150, bbox_inches='tight', facecolor='white')
        plt.close()

        return str(filepath)

    def create_funnel_chart(
        self,
        labels: List[str],
        values: List[float],
        title: str,
        filename: Optional[str] = None
    ) -> Optional[str]:
        """
        Create a funnel chart

        Args:
            labels: Step labels
            values: Conversion rates or counts for each step
            title: Chart title
            filename: Output filename

        Returns:
            Path to saved chart image
        """
        if not MATPLOTLIB_AVAILABLE:
            return None

        fig, ax = plt.subplots(figsize=(12, 8))

        n = len(labels)
        if n == 0:
            plt.close()
            return None

        # Normalize values for visual width
        max_val = max(values) if values else 1
        normalized = [v / max_val for v in values]

        y_positions = list(range(n - 1, -1, -1))  # Reversed for top-to-bottom

        for i, (label, value, norm, y) in enumerate(zip(labels, values, normalized, y_positions)):
            # Create trapezoid shape
            width = norm * 0.8 + 0.2  # Minimum width of 0.2
            next_width = normalized[i + 1] * 0.8 + 0.2 if i < n - 1 else width

            left = (1 - width) / 2
            right = (1 + width) / 2
            next_left = (1 - next_width) / 2
            next_right = (1 + next_width) / 2

            color = self._get_color(i)

            # Draw trapezoid
            trapezoid = plt.Polygon([
                [left, y + 0.9],
                [right, y + 0.9],
                [next_right if i < n - 1 else right, y + 0.1],
                [next_left if i < n - 1 else left, y + 0.1]
            ], facecolor=color, edgecolor='white', linewidth=2)
            ax.add_patch(trapezoid)

            # Add label and value
            ax.text(0.5, y + 0.5, f"{label}\n{value:.1f}%" if isinstance(value, float) else f"{label}\n{value:,}",
                   ha='center', va='center', fontsize=11, fontweight='bold', color='white')

            # Add conversion rate between steps
            if i < n - 1:
                drop = values[i] - values[i + 1] if values[i] > 0 else 0
                conv = (values[i + 1] / values[i] * 100) if values[i] > 0 else 0
                ax.text(1.05, y + 0.5, f"↓ {conv:.1f}%",
                       ha='left', va='center', fontsize=10, color='#666')

        ax.set_xlim(-0.1, 1.3)
        ax.set_ylim(-0.5, n + 0.5)
        ax.set_title(title, fontweight='bold', fontsize=14, pad=20)
        ax.axis('off')

        plt.tight_layout()

        filepath = self.output_dir / f"{filename or 'funnel_chart'}.png"
        plt.savefig(filepath, dpi=150, bbox_inches='tight', facecolor='white')
        plt.close()

        return str(filepath)

    def create_retention_heatmap(
        self,
        retention_data: Dict[str, float],
        title: str = "User Retention",
        filename: Optional[str] = None
    ) -> Optional[str]:
        """
        Create a retention curve/heatmap

        Args:
            retention_data: Dict with period keys and retention values
            title: Chart title
            filename: Output filename

        Returns:
            Path to saved chart image
        """
        if not MATPLOTLIB_AVAILABLE:
            return None

        # Extract data
        periods = []
        values = []
        for key in sorted(retention_data.keys()):
            period_num = int(key.split("_")[1]) if "_" in key else 0
            periods.append(f"Week {period_num}")
            values.append(retention_data[key])

        if not periods:
            return None

        fig, ax = plt.subplots(figsize=(12, 4))

        # Create color gradient based on retention
        colors = []
        for v in values:
            if v >= 40:
                colors.append('#10B981')  # Green
            elif v >= 25:
                colors.append('#F59E0B')  # Amber
            elif v >= 15:
                colors.append('#EF4444')  # Red
            else:
                colors.append('#DC2626')  # Dark red

        bars = ax.bar(periods, values, color=colors, edgecolor='white', linewidth=1)

        # Add value labels
        for bar, val in zip(bars, values):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2, height + 1,
                   f'{val:.1f}%', ha='center', va='bottom', fontsize=10, fontweight='bold')

        ax.set_ylabel('Retention Rate (%)')
        ax.set_title(title, fontweight='bold', pad=20)
        ax.set_ylim(0, max(values) * 1.2 if values else 100)

        # Add threshold lines
        ax.axhline(y=40, color='#10B981', linestyle='--', alpha=0.5, label='Excellent (40%)')
        ax.axhline(y=25, color='#F59E0B', linestyle='--', alpha=0.5, label='Good (25%)')
        ax.axhline(y=15, color='#EF4444', linestyle='--', alpha=0.5, label='Fair (15%)')

        ax.legend(loc='upper right')
        plt.tight_layout()

        filepath = self.output_dir / f"{filename or 'retention_heatmap'}.png"
        plt.savefig(filepath, dpi=150, bbox_inches='tight', facecolor='white')
        plt.close()

        return str(filepath)

    def create_comparison_chart(
        self,
        labels: List[str],
        series1: List[float],
        series2: List[float],
        series1_name: str = "Current",
        series2_name: str = "Previous",
        title: str = "Comparison",
        filename: Optional[str] = None
    ) -> Optional[str]:
        """
        Create a grouped bar chart comparing two series

        Returns:
            Path to saved chart image
        """
        if not MATPLOTLIB_AVAILABLE:
            return None

        import numpy as np

        fig, ax = plt.subplots(figsize=(12, 6))

        x = np.arange(len(labels))
        width = 0.35

        bars1 = ax.bar(x - width/2, series1, width, label=series1_name, color=self._get_color(0))
        bars2 = ax.bar(x + width/2, series2, width, label=series2_name, color=self._get_color(1))

        ax.set_xlabel('')
        ax.set_ylabel('Value')
        ax.set_title(title, fontweight='bold', pad=20)
        ax.set_xticks(x)
        ax.set_xticklabels([l[:20] for l in labels], rotation=45, ha='right')
        ax.legend()

        plt.tight_layout()

        filepath = self.output_dir / f"{filename or 'comparison_chart'}.png"
        plt.savefig(filepath, dpi=150, bbox_inches='tight', facecolor='white')
        plt.close()

        return str(filepath)

    def create_summary_dashboard(
        self,
        metrics: Dict[str, Any],
        filename: Optional[str] = None
    ) -> Optional[str]:
        """
        Create a dashboard-style summary with multiple metrics

        Args:
            metrics: Dict with metric names and values
            filename: Output filename

        Returns:
            Path to saved chart image
        """
        if not MATPLOTLIB_AVAILABLE:
            return None

        # Calculate grid size
        n_metrics = len(metrics)
        cols = min(4, n_metrics)
        rows = (n_metrics + cols - 1) // cols

        fig, axes = plt.subplots(rows, cols, figsize=(4 * cols, 3 * rows))

        # Flatten axes for easier iteration
        if rows == 1 and cols == 1:
            axes = [[axes]]
        elif rows == 1:
            axes = [axes]
        elif cols == 1:
            axes = [[ax] for ax in axes]

        flat_axes = [ax for row in axes for ax in row]

        for i, (metric_name, value) in enumerate(metrics.items()):
            ax = flat_axes[i]
            ax.axis('off')

            # Format value
            if isinstance(value, float):
                if 'rate' in metric_name.lower() or '%' in str(value):
                    display_value = f"{value:.1f}%"
                else:
                    display_value = f"{value:,.1f}"
            elif isinstance(value, int):
                display_value = f"{value:,}"
            else:
                display_value = str(value)

            # Create metric card
            ax.add_patch(plt.Rectangle((0.05, 0.1), 0.9, 0.8, fill=True,
                        facecolor='#F8FAFC', edgecolor='#E2E8F0', linewidth=2, transform=ax.transAxes))

            ax.text(0.5, 0.65, display_value, ha='center', va='center',
                   fontsize=24, fontweight='bold', color=self._get_color(i), transform=ax.transAxes)

            ax.text(0.5, 0.3, metric_name.replace('_', ' ').title(), ha='center', va='center',
                   fontsize=11, color='#64748B', transform=ax.transAxes)

        # Hide unused axes
        for i in range(len(metrics), len(flat_axes)):
            flat_axes[i].axis('off')

        plt.suptitle('Key Metrics Overview', fontsize=16, fontweight='bold', y=1.02)
        plt.tight_layout()

        filepath = self.output_dir / f"{filename or 'summary_dashboard'}.png"
        plt.savefig(filepath, dpi=150, bbox_inches='tight', facecolor='white')
        plt.close()

        return str(filepath)

    def generate_all_charts(self, chart_data: Dict[str, Any]) -> Dict[str, str]:
        """
        Generate all charts from prepared chart data

        Args:
            chart_data: Dict with chart specifications from AnalyticsProcessor.get_chart_data()

        Returns:
            Dict mapping chart names to file paths
        """
        generated = {}

        # Page views chart
        if 'page_views_chart' in chart_data:
            data = chart_data['page_views_chart']
            path = self.create_bar_chart(
                labels=data.get('labels', []),
                values=data.get('values', []),
                title=data.get('title', 'Page Views'),
                filename='page_views'
            )
            if path:
                generated['page_views'] = path

        # Event distribution chart
        if 'event_distribution_chart' in chart_data:
            data = chart_data['event_distribution_chart']
            path = self.create_pie_chart(
                labels=data.get('labels', []),
                values=data.get('values', []),
                title=data.get('title', 'Event Distribution'),
                filename='event_distribution'
            )
            if path:
                generated['event_distribution'] = path

        # Retention curve chart
        if 'retention_curve_chart' in chart_data:
            data = chart_data['retention_curve_chart']
            path = self.create_line_chart(
                labels=data.get('labels', []),
                values=data.get('values', []),
                title=data.get('title', 'Retention Curve'),
                ylabel='Retention %',
                filename='retention_curve'
            )
            if path:
                generated['retention_curve'] = path

        # Funnel chart
        if 'funnel_chart' in chart_data:
            data = chart_data['funnel_chart']
            path = self.create_funnel_chart(
                labels=data.get('labels', []),
                values=data.get('values', []),
                title=data.get('title', 'Conversion Funnel'),
                filename='funnel'
            )
            if path:
                generated['funnel'] = path

        return generated
