"""
PDF Report Generator for Heap Analytics reports
"""

import os
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path

try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib.colors import HexColor, black, white, grey
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle,
        PageBreak, KeepTogether, ListFlowable, ListItem
    )
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False


class PDFReportGenerator:
    """
    Generates professional PDF reports from Heap Analytics data
    """

    # Color scheme
    COLORS = {
        "primary": HexColor("#4F46E5") if REPORTLAB_AVAILABLE else None,
        "secondary": HexColor("#10B981") if REPORTLAB_AVAILABLE else None,
        "accent": HexColor("#F59E0B") if REPORTLAB_AVAILABLE else None,
        "danger": HexColor("#EF4444") if REPORTLAB_AVAILABLE else None,
        "text": HexColor("#1F2937") if REPORTLAB_AVAILABLE else None,
        "text_light": HexColor("#6B7280") if REPORTLAB_AVAILABLE else None,
        "background": HexColor("#F9FAFB") if REPORTLAB_AVAILABLE else None,
        "border": HexColor("#E5E7EB") if REPORTLAB_AVAILABLE else None,
    }

    def __init__(
        self,
        output_path: str,
        title: str = "Heap Analytics Report",
        company_name: Optional[str] = None,
        logo_path: Optional[str] = None,
        page_size: str = "letter"
    ):
        """
        Initialize PDF generator

        Args:
            output_path: Path for output PDF file
            title: Report title
            company_name: Company name for header
            logo_path: Path to company logo image
            page_size: 'letter' or 'a4'
        """
        if not REPORTLAB_AVAILABLE:
            raise ImportError("reportlab is required for PDF generation. Install with: pip install reportlab")

        self.output_path = Path(output_path)
        self.output_path.parent.mkdir(parents=True, exist_ok=True)

        self.title = title
        self.company_name = company_name
        self.logo_path = logo_path
        self.page_size = letter if page_size.lower() == "letter" else A4

        self.elements = []
        self.styles = self._create_styles()

    def _create_styles(self) -> Dict[str, Any]:
        """Create custom paragraph styles"""
        base_styles = getSampleStyleSheet()

        custom_styles = {
            "Title": ParagraphStyle(
                "CustomTitle",
                parent=base_styles["Title"],
                fontSize=28,
                textColor=self.COLORS["primary"],
                spaceAfter=30,
                alignment=TA_CENTER,
            ),
            "Heading1": ParagraphStyle(
                "CustomH1",
                parent=base_styles["Heading1"],
                fontSize=20,
                textColor=self.COLORS["primary"],
                spaceBefore=20,
                spaceAfter=12,
                borderWidth=0,
                borderPadding=0,
            ),
            "Heading2": ParagraphStyle(
                "CustomH2",
                parent=base_styles["Heading2"],
                fontSize=16,
                textColor=self.COLORS["text"],
                spaceBefore=16,
                spaceAfter=8,
            ),
            "Heading3": ParagraphStyle(
                "CustomH3",
                parent=base_styles["Heading3"],
                fontSize=13,
                textColor=self.COLORS["text"],
                spaceBefore=12,
                spaceAfter=6,
            ),
            "Body": ParagraphStyle(
                "CustomBody",
                parent=base_styles["Normal"],
                fontSize=10,
                textColor=self.COLORS["text"],
                spaceAfter=8,
                alignment=TA_JUSTIFY,
            ),
            "Subtitle": ParagraphStyle(
                "Subtitle",
                parent=base_styles["Normal"],
                fontSize=12,
                textColor=self.COLORS["text_light"],
                alignment=TA_CENTER,
                spaceAfter=20,
            ),
            "Metric": ParagraphStyle(
                "Metric",
                parent=base_styles["Normal"],
                fontSize=24,
                textColor=self.COLORS["primary"],
                alignment=TA_CENTER,
                fontName="Helvetica-Bold",
            ),
            "MetricLabel": ParagraphStyle(
                "MetricLabel",
                parent=base_styles["Normal"],
                fontSize=10,
                textColor=self.COLORS["text_light"],
                alignment=TA_CENTER,
            ),
            "Insight": ParagraphStyle(
                "Insight",
                parent=base_styles["Normal"],
                fontSize=10,
                textColor=self.COLORS["text"],
                leftIndent=20,
                spaceBefore=4,
                spaceAfter=4,
            ),
            "Highlight": ParagraphStyle(
                "Highlight",
                parent=base_styles["Normal"],
                fontSize=11,
                textColor=self.COLORS["secondary"],
                fontName="Helvetica-Bold",
            ),
        }

        return custom_styles

    def add_title_page(
        self,
        subtitle: Optional[str] = None,
        date_range: Optional[str] = None
    ):
        """Add title page to report"""
        # Logo
        if self.logo_path and os.path.exists(self.logo_path):
            self.elements.append(Spacer(1, 1 * inch))
            logo = Image(self.logo_path, width=2 * inch, height=2 * inch)
            logo.hAlign = 'CENTER'
            self.elements.append(logo)
            self.elements.append(Spacer(1, 0.5 * inch))

        self.elements.append(Spacer(1, 1.5 * inch))

        # Title
        self.elements.append(Paragraph(self.title, self.styles["Title"]))

        # Subtitle
        if subtitle:
            self.elements.append(Paragraph(subtitle, self.styles["Subtitle"]))

        # Company name
        if self.company_name:
            self.elements.append(Spacer(1, 0.3 * inch))
            self.elements.append(Paragraph(f"Prepared for: {self.company_name}", self.styles["Subtitle"]))

        # Date range
        if date_range:
            self.elements.append(Paragraph(f"Reporting Period: {date_range}", self.styles["Subtitle"]))

        # Generation date
        gen_date = datetime.now().strftime("%B %d, %Y")
        self.elements.append(Paragraph(f"Generated: {gen_date}", self.styles["Subtitle"]))

        self.elements.append(PageBreak())

    def add_section(self, title: str, level: int = 1):
        """Add a section heading"""
        style_key = f"Heading{min(level, 3)}"
        self.elements.append(Paragraph(title, self.styles[style_key]))

    def add_paragraph(self, text: str, style: str = "Body"):
        """Add a paragraph of text"""
        self.elements.append(Paragraph(text, self.styles.get(style, self.styles["Body"])))

    def add_spacer(self, height: float = 0.25):
        """Add vertical space"""
        self.elements.append(Spacer(1, height * inch))

    def add_page_break(self):
        """Add page break"""
        self.elements.append(PageBreak())

    def add_executive_summary(self, summary: Dict[str, Any]):
        """Add executive summary section"""
        self.add_section("Executive Summary")

        # Key metrics in a grid
        key_metrics = summary.get("key_metrics", {})
        if key_metrics:
            self._add_metrics_grid(key_metrics)

        # Highlights
        highlights = summary.get("highlights", [])
        if highlights:
            self.add_spacer(0.3)
            self.add_section("Key Highlights", level=2)
            for highlight in highlights:
                self.elements.append(Paragraph(f"• {highlight}", self.styles["Insight"]))

        self.add_spacer(0.5)

    def _add_metrics_grid(self, metrics: Dict[str, Any], cols: int = 4):
        """Add a grid of metrics"""
        items = list(metrics.items())
        rows_data = []

        for i in range(0, len(items), cols):
            row_items = items[i:i + cols]
            row = []
            for name, value in row_items:
                # Format value
                if isinstance(value, float):
                    display = f"{value:.1f}%" if "rate" in name.lower() else f"{value:,.1f}"
                elif isinstance(value, int):
                    display = f"{value:,}"
                else:
                    display = str(value)

                # Create cell content
                cell_content = [
                    Paragraph(display, self.styles["Metric"]),
                    Paragraph(name.replace("_", " ").title(), self.styles["MetricLabel"])
                ]
                row.append(cell_content)

            # Pad row if needed
            while len(row) < cols:
                row.append("")

            rows_data.append(row)

        if rows_data:
            table = Table(rows_data, colWidths=[self.page_size[0] / cols - 0.5 * inch] * cols)
            table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('TOPPADDING', (0, 0), (-1, -1), 12),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
                ('BACKGROUND', (0, 0), (-1, -1), self.COLORS["background"]),
                ('BOX', (0, 0), (-1, -1), 1, self.COLORS["border"]),
                ('INNERGRID', (0, 0), (-1, -1), 0.5, self.COLORS["border"]),
            ]))
            self.elements.append(table)

    def add_chart(self, chart_path: str, title: Optional[str] = None, width: float = 6):
        """Add a chart image to the report"""
        if not os.path.exists(chart_path):
            return

        if title:
            self.add_section(title, level=2)

        img = Image(chart_path, width=width * inch)
        img.hAlign = 'CENTER'
        self.elements.append(img)
        self.add_spacer(0.3)

    def add_data_table(
        self,
        headers: List[str],
        data: List[List[Any]],
        title: Optional[str] = None
    ):
        """Add a data table"""
        if title:
            self.add_section(title, level=2)

        # Prepare table data
        table_data = [headers] + data

        # Create table
        col_width = (self.page_size[0] - 1.5 * inch) / len(headers)
        table = Table(table_data, colWidths=[col_width] * len(headers))

        # Style table
        table.setStyle(TableStyle([
            # Header
            ('BACKGROUND', (0, 0), (-1, 0), self.COLORS["primary"]),
            ('TEXTCOLOR', (0, 0), (-1, 0), white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('TOPPADDING', (0, 0), (-1, 0), 12),
            # Body
            ('BACKGROUND', (0, 1), (-1, -1), white),
            ('TEXTCOLOR', (0, 1), (-1, -1), self.COLORS["text"]),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
            ('TOPPADDING', (0, 1), (-1, -1), 8),
            # Grid
            ('GRID', (0, 0), (-1, -1), 0.5, self.COLORS["border"]),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            # Alternating rows
            *[('BACKGROUND', (0, i), (-1, i), self.COLORS["background"])
              for i in range(2, len(table_data), 2)]
        ]))

        self.elements.append(table)
        self.add_spacer(0.3)

    def add_insights_section(self, insights: List[Dict[str, str]]):
        """Add insights section"""
        self.add_section("Key Insights")

        for insight in insights:
            # Insight title
            priority = insight.get("priority", "medium")
            title = insight.get("title", "")
            description = insight.get("description", "")

            priority_color = {
                "high": self.COLORS["danger"],
                "medium": self.COLORS["accent"],
                "low": self.COLORS["secondary"]
            }.get(priority, self.COLORS["text"])

            self.elements.append(Paragraph(
                f"<font color='{priority_color}'><b>{title}</b></font>",
                self.styles["Body"]
            ))
            self.elements.append(Paragraph(description, self.styles["Insight"]))
            self.add_spacer(0.15)

    def add_recommendations_section(self, recommendations: List[Dict[str, str]]):
        """Add recommendations section"""
        self.add_section("Recommendations")

        for i, rec in enumerate(recommendations, 1):
            area = rec.get("area", "General")
            priority = rec.get("priority", "Medium")
            text = rec.get("recommendation", "")
            impact = rec.get("impact", "")

            self.elements.append(Paragraph(
                f"<b>{i}. {area}</b> (Priority: {priority})",
                self.styles["Heading3"]
            ))
            self.elements.append(Paragraph(text, self.styles["Body"]))
            if impact:
                self.elements.append(Paragraph(
                    f"<i>Expected Impact: {impact}</i>",
                    self.styles["Insight"]
                ))
            self.add_spacer(0.2)

    def add_page_analysis(self, page_analysis: Dict[str, Any]):
        """Add page performance analysis section"""
        self.add_section("Page Performance Analysis")

        # Summary metrics
        self.add_paragraph(
            f"Analyzed <b>{page_analysis.get('total_pages', 0)}</b> pages with "
            f"<b>{page_analysis.get('total_pageviews', 0):,}</b> total pageviews."
        )

        # Top pages table
        top_pages = page_analysis.get("top_pages_by_views", [])[:10]
        if top_pages:
            headers = ["Page URL", "Views", "Unique Visitors", "Avg Time"]
            data = []
            for page in top_pages:
                data.append([
                    page.get("url", "")[:40],
                    f"{page.get('total_views', 0):,}",
                    f"{page.get('unique_visitors', 0):,}",
                    f"{page.get('avg_time_on_page', 0):.0f}s"
                ])
            self.add_data_table(headers, data, "Top 10 Pages by Views")

        # High bounce pages
        high_bounce = page_analysis.get("pages_with_high_bounce", [])
        if high_bounce:
            self.add_section("Pages Needing Attention", level=2)
            self.add_paragraph(
                "The following pages have bounce rates above 70% and may need optimization:"
            )
            for page in high_bounce[:5]:
                self.add_paragraph(
                    f"• {page.get('url', 'Unknown')}: {page.get('bounce_rate', 0):.1f}% bounce rate"
                )

    def add_event_analysis(self, event_analysis: Dict[str, Any]):
        """Add event tracking analysis section"""
        self.add_section("Event Tracking Analysis")

        total_events = event_analysis.get("total_events_tracked", 0)
        total_count = event_analysis.get("total_event_count", 0)

        self.add_paragraph(
            f"Tracking <b>{total_events}</b> unique events with <b>{total_count:,}</b> total occurrences."
        )

        # Top events table
        top_events = event_analysis.get("top_events", [])[:15]
        if top_events:
            headers = ["Event Name", "Type", "Count", "Unique Users"]
            data = []
            for event in top_events:
                data.append([
                    event.get("name", "")[:35],
                    event.get("event_type", "custom"),
                    f"{event.get('total_count', 0):,}",
                    f"{event.get('unique_users', 0):,}"
                ])
            self.add_data_table(headers, data, "Top Events")

    def add_journey_analysis(self, journey_analysis: Dict[str, Any]):
        """Add user journey analysis section"""
        self.add_section("User Journey Analysis")

        total_journeys = journey_analysis.get("total_journeys", 0)
        avg_length = journey_analysis.get("avg_journey_length", 0)

        self.add_paragraph(
            f"Analyzed <b>{total_journeys}</b> user journeys with an average of "
            f"<b>{avg_length:.1f}</b> steps per journey."
        )

        # Common entry points
        entry_points = journey_analysis.get("common_entry_points", [])
        if entry_points:
            self.add_section("Most Common Entry Points", level=2)
            for entry, count in entry_points[:5]:
                self.add_paragraph(f"• {entry}: {count:,} users")

        # Common exit points
        exit_points = journey_analysis.get("common_exit_points", [])
        if exit_points:
            self.add_section("Most Common Exit Points", level=2)
            for exit_pt, count in exit_points[:5]:
                self.add_paragraph(f"• {exit_pt}: {count:,} users")

    def add_retention_analysis(self, retention_analysis: Dict[str, Any]):
        """Add retention analysis section"""
        self.add_section("User Retention Analysis")

        week1 = retention_analysis.get("week_1_retention", 0)
        health = retention_analysis.get("retention_health", "unknown")

        self.add_paragraph(
            f"Week 1 retention rate: <b>{week1:.1f}%</b> "
            f"(Health status: <b>{health.title()}</b>)"
        )

        # Recommendations
        recs = retention_analysis.get("recommendations", [])
        if recs:
            self.add_section("Retention Improvement Recommendations", level=2)
            for rec in recs:
                self.add_paragraph(f"• {rec}")

    def generate(self) -> str:
        """
        Generate the PDF report

        Returns:
            Path to generated PDF file
        """
        doc = SimpleDocTemplate(
            str(self.output_path),
            pagesize=self.page_size,
            rightMargin=0.75 * inch,
            leftMargin=0.75 * inch,
            topMargin=0.75 * inch,
            bottomMargin=0.75 * inch
        )

        doc.build(self.elements)
        return str(self.output_path)

    def generate_full_report(
        self,
        analysis_results: Dict[str, Any],
        chart_paths: Dict[str, str],
        date_range_days: int = 30
    ) -> str:
        """
        Generate a complete report from analysis results

        Args:
            analysis_results: Results from AnalyticsProcessor.analyze_all()
            chart_paths: Dict of chart names to file paths
            date_range_days: Number of days in the report period

        Returns:
            Path to generated PDF file
        """
        # Title page
        self.add_title_page(
            subtitle="Comprehensive Analytics Report",
            date_range=f"Last {date_range_days} days"
        )

        # Executive summary
        summary = analysis_results.get("summary", {})
        if summary:
            self.add_executive_summary(summary)

        # Charts section
        self.add_page_break()
        self.add_section("Visual Analytics")

        for chart_name, chart_path in chart_paths.items():
            if os.path.exists(chart_path):
                title = chart_name.replace("_", " ").title()
                self.add_chart(chart_path, title)

        # Page analysis
        self.add_page_break()
        page_analysis = analysis_results.get("page_analysis", {})
        if page_analysis and page_analysis.get("status") != "no_data":
            self.add_page_analysis(page_analysis)

        # Event analysis
        self.add_page_break()
        event_analysis = analysis_results.get("event_analysis", {})
        if event_analysis and event_analysis.get("status") != "no_data":
            self.add_event_analysis(event_analysis)

        # Journey analysis
        journey_analysis = analysis_results.get("journey_analysis", {})
        if journey_analysis and journey_analysis.get("status") != "no_data":
            self.add_journey_analysis(journey_analysis)

        # Retention analysis
        self.add_page_break()
        retention_analysis = analysis_results.get("retention_analysis", {})
        if retention_analysis and retention_analysis.get("status") != "no_data":
            self.add_retention_analysis(retention_analysis)

        # Insights
        insights = analysis_results.get("insights", [])
        if insights:
            self.add_page_break()
            self.add_insights_section(insights)

        # Recommendations
        recommendations = analysis_results.get("recommendations", [])
        if recommendations:
            self.add_page_break()
            self.add_recommendations_section(recommendations)

        return self.generate()
