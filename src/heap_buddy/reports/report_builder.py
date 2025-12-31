"""
High-level report builder that orchestrates all report generation
"""

import os
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path

from .charts import ChartGenerator
from .pdf_generator import PDFReportGenerator
from .word_generator import WordReportGenerator
from ..analytics.processor import AnalyticsProcessor


class ReportBuilder:
    """
    Orchestrates the complete report generation process
    """

    def __init__(
        self,
        output_dir: str = "./reports",
        report_title: str = "Heap Analytics Report",
        company_name: Optional[str] = None,
        logo_path: Optional[str] = None,
        chart_style: str = "modern"
    ):
        """
        Initialize report builder

        Args:
            output_dir: Directory for output files
            report_title: Title for the report
            company_name: Company name to include
            logo_path: Path to company logo
            chart_style: Style for charts ('modern', 'classic', 'minimal')
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.report_title = report_title
        self.company_name = company_name
        self.logo_path = logo_path
        self.chart_style = chart_style

        # Create subdirectories
        self.charts_dir = self.output_dir / "charts"
        self.charts_dir.mkdir(exist_ok=True)

        self.screenshots_dir = self.output_dir / "screenshots"
        self.screenshots_dir.mkdir(exist_ok=True)

    def build_report(
        self,
        processed_data: Dict[str, Any],
        output_formats: List[str] = ["pdf", "docx"],
        date_range_days: int = 30
    ) -> Dict[str, str]:
        """
        Build complete report(s) from processed data

        Args:
            processed_data: Processed data from HeapDataExtractor.get_processed_data()
            output_formats: List of formats to generate ('pdf', 'docx')
            date_range_days: Number of days in the reporting period

        Returns:
            Dict mapping format to output file path
        """
        print("\n" + "=" * 60)
        print("GENERATING REPORTS")
        print("=" * 60)

        results = {}

        # Step 1: Process and analyze data
        print("\n[1/4] Analyzing data...")
        processor = AnalyticsProcessor(processed_data)
        analysis_results = processor.analyze_all()
        print("     ✓ Data analysis complete")

        # Step 2: Generate charts
        print("\n[2/4] Generating charts...")
        chart_generator = ChartGenerator(
            style=self.chart_style,
            output_dir=str(self.charts_dir)
        )
        chart_data = processor.get_chart_data()
        chart_paths = chart_generator.generate_all_charts(chart_data)

        # Generate summary dashboard
        summary_metrics = {
            "Total Users": analysis_results.get("summary", {}).get("key_metrics", {}).get("total_users", 0),
            "Total Sessions": analysis_results.get("summary", {}).get("key_metrics", {}).get("total_sessions", 0),
            "Bounce Rate": analysis_results.get("summary", {}).get("key_metrics", {}).get("bounce_rate", 0),
            "Avg Session": analysis_results.get("summary", {}).get("key_metrics", {}).get("avg_session_duration_formatted", "0s"),
        }
        dashboard_path = chart_generator.create_summary_dashboard(summary_metrics, "summary_dashboard")
        if dashboard_path:
            chart_paths["summary_dashboard"] = dashboard_path

        print(f"     ✓ Generated {len(chart_paths)} charts")

        # Step 3: Generate PDF report
        if "pdf" in output_formats:
            print("\n[3/4] Generating PDF report...")
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            pdf_path = self.output_dir / f"heap_analytics_report_{timestamp}.pdf"

            try:
                pdf_generator = PDFReportGenerator(
                    output_path=str(pdf_path),
                    title=self.report_title,
                    company_name=self.company_name,
                    logo_path=self.logo_path
                )
                pdf_output = pdf_generator.generate_full_report(
                    analysis_results=analysis_results,
                    chart_paths=chart_paths,
                    date_range_days=date_range_days
                )
                results["pdf"] = pdf_output
                print(f"     ✓ PDF report saved to: {pdf_output}")
            except ImportError as e:
                print(f"     ✗ PDF generation skipped: {e}")
            except Exception as e:
                print(f"     ✗ PDF generation error: {e}")

        # Step 4: Generate Word report
        if "docx" in output_formats:
            print("\n[4/4] Generating Word report...")
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            docx_path = self.output_dir / f"heap_analytics_report_{timestamp}.docx"

            try:
                word_generator = WordReportGenerator(
                    output_path=str(docx_path),
                    title=self.report_title,
                    company_name=self.company_name,
                    logo_path=self.logo_path
                )
                docx_output = word_generator.generate_full_report(
                    analysis_results=analysis_results,
                    chart_paths=chart_paths,
                    date_range_days=date_range_days
                )
                results["docx"] = docx_output
                print(f"     ✓ Word report saved to: {docx_output}")
            except ImportError as e:
                print(f"     ✗ Word generation skipped: {e}")
            except Exception as e:
                print(f"     ✗ Word generation error: {e}")

        # Save raw analysis data
        analysis_path = self.output_dir / "analysis_results.json"
        import json
        with open(analysis_path, 'w') as f:
            json.dump(analysis_results, f, indent=2, default=str)
        results["analysis_json"] = str(analysis_path)

        print("\n" + "=" * 60)
        print("REPORT GENERATION COMPLETE")
        print("=" * 60)
        print(f"\nOutput directory: {self.output_dir}")
        print(f"Generated files:")
        for fmt, path in results.items():
            print(f"  - {fmt}: {path}")

        return results

    def quick_report(
        self,
        raw_data: Dict[str, Any],
        output_format: str = "pdf"
    ) -> Optional[str]:
        """
        Generate a quick single-format report

        Args:
            raw_data: Raw extracted data from HeapScraper
            output_format: 'pdf' or 'docx'

        Returns:
            Path to generated report or None if failed
        """
        from ..scraper.data_extractor import HeapDataExtractor

        # Process raw data
        extractor = HeapDataExtractor()
        extractor.load_raw_data(raw_data)
        processed_data = extractor.process_all()

        # Generate report
        results = self.build_report(
            processed_data=processed_data,
            output_formats=[output_format],
            date_range_days=raw_data.get("date_range_days", 30)
        )

        return results.get(output_format)

    @staticmethod
    def from_json_file(
        json_path: str,
        output_dir: str = "./reports",
        output_formats: List[str] = ["pdf", "docx"]
    ) -> Dict[str, str]:
        """
        Generate reports from a saved JSON data file

        Args:
            json_path: Path to JSON file with raw or processed data
            output_dir: Output directory for reports
            output_formats: Formats to generate

        Returns:
            Dict of generated file paths
        """
        import json

        with open(json_path, 'r') as f:
            data = json.load(f)

        # Check if it's raw or processed data
        if "overview" in data and "pages" in data:
            # Already processed
            processed_data = data
        else:
            # Raw data, needs processing
            from ..scraper.data_extractor import HeapDataExtractor
            extractor = HeapDataExtractor()
            extractor.load_raw_data(data)
            processed_data = extractor.process_all()

        builder = ReportBuilder(output_dir=output_dir)
        return builder.build_report(
            processed_data=processed_data,
            output_formats=output_formats,
            date_range_days=data.get("date_range_days", processed_data.get("metadata", {}).get("date_range_days", 30))
        )
