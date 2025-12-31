"""
Command Line Interface for Heap Analytics Buddy
"""

import os
import sys
import click
from pathlib import Path
from typing import Optional

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.progress import Progress, SpinnerColumn, TextColumn
    from rich.table import Table
    from rich.prompt import Prompt, Confirm
    from rich import print as rprint
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

try:
    import questionary
    from questionary import Style
    QUESTIONARY_AVAILABLE = True
except ImportError:
    QUESTIONARY_AVAILABLE = False


# Initialize rich console
console = Console() if RICH_AVAILABLE else None

# Custom questionary style
if QUESTIONARY_AVAILABLE:
    custom_style = Style([
        ('question', 'bold'),
        ('answer', 'fg:green bold'),
        ('pointer', 'fg:cyan bold'),
        ('highlighted', 'fg:cyan bold'),
        ('selected', 'fg:green'),
    ])


def print_banner():
    """Print application banner"""
    banner = """
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║   ██╗  ██╗███████╗ █████╗ ██████╗     ██████╗ ██╗   ██╗██████╗   ║
║   ██║  ██║██╔════╝██╔══██╗██╔══██╗    ██╔══██╗██║   ██║██╔══██╗  ║
║   ███████║█████╗  ███████║██████╔╝    ██████╔╝██║   ██║██║  ██║  ║
║   ██╔══██║██╔══╝  ██╔══██║██╔═══╝     ██╔══██╗██║   ██║██║  ██║  ║
║   ██║  ██║███████╗██║  ██║██║         ██████╔╝╚██████╔╝██████╔╝  ║
║   ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚═╝         ╚═════╝  ╚═════╝ ╚═════╝   ║
║                                                               ║
║            Heap Analytics Report Generator                    ║
║                     Version 1.0.0                             ║
╚═══════════════════════════════════════════════════════════════╝
    """
    if RICH_AVAILABLE:
        console.print(banner, style="cyan")
    else:
        print(banner)


def get_browser_choice() -> str:
    """Interactive browser selection"""
    browsers = [
        {"name": "Firefox (Selenium) - Recommended", "value": "firefox"},
        {"name": "Chrome (Selenium)", "value": "chrome"},
        {"name": "Firefox (Playwright)", "value": "playwright-firefox"},
        {"name": "Chrome (Playwright)", "value": "playwright-chrome"},
        {"name": "WebKit (Playwright)", "value": "playwright-webkit"},
    ]

    if QUESTIONARY_AVAILABLE:
        choice = questionary.select(
            "Select browser to use:",
            choices=[b["name"] for b in browsers],
            style=custom_style
        ).ask()

        for b in browsers:
            if b["name"] == choice:
                return b["value"]
        return "firefox"
    else:
        print("\nSelect browser to use:")
        for i, b in enumerate(browsers, 1):
            print(f"  {i}. {b['name']}")

        while True:
            try:
                choice = int(input("\nEnter number (1-5): "))
                if 1 <= choice <= len(browsers):
                    return browsers[choice - 1]["value"]
            except ValueError:
                pass
            print("Invalid choice, please try again.")


def get_output_formats() -> list:
    """Interactive output format selection"""
    if QUESTIONARY_AVAILABLE:
        choices = questionary.checkbox(
            "Select output formats:",
            choices=[
                questionary.Choice("PDF Report", checked=True),
                questionary.Choice("Word Document (.docx)", checked=True),
            ],
            style=custom_style
        ).ask()

        formats = []
        if "PDF Report" in choices:
            formats.append("pdf")
        if "Word Document (.docx)" in choices:
            formats.append("docx")
        return formats or ["pdf"]
    else:
        print("\nSelect output formats (comma-separated, e.g., 1,2):")
        print("  1. PDF Report")
        print("  2. Word Document (.docx)")

        choice = input("\nEnter numbers: ").strip()
        formats = []
        if "1" in choice:
            formats.append("pdf")
        if "2" in choice:
            formats.append("docx")
        return formats or ["pdf"]


def get_date_range() -> int:
    """Get date range for report"""
    options = [
        {"name": "Last 7 days", "value": 7},
        {"name": "Last 30 days (Recommended)", "value": 30},
        {"name": "Last 90 days", "value": 90},
        {"name": "Custom", "value": 0},
    ]

    if QUESTIONARY_AVAILABLE:
        choice = questionary.select(
            "Select date range for report:",
            choices=[o["name"] for o in options],
            style=custom_style
        ).ask()

        for o in options:
            if o["name"] == choice:
                if o["value"] == 0:
                    days = questionary.text(
                        "Enter number of days:",
                        validate=lambda x: x.isdigit() and int(x) > 0,
                        style=custom_style
                    ).ask()
                    return int(days)
                return o["value"]
        return 30
    else:
        print("\nSelect date range:")
        for i, o in enumerate(options, 1):
            print(f"  {i}. {o['name']}")

        while True:
            try:
                choice = int(input("\nEnter number: "))
                if 1 <= choice <= len(options):
                    if options[choice - 1]["value"] == 0:
                        days = int(input("Enter number of days: "))
                        return days
                    return options[choice - 1]["value"]
            except ValueError:
                pass
            print("Invalid choice, please try again.")


@click.group()
@click.version_option(version="1.0.0")
def cli():
    """Heap Analytics Buddy - Generate comprehensive analytics reports"""
    pass


@cli.command()
@click.option('--browser', '-b', type=click.Choice(['firefox', 'chrome', 'playwright-firefox', 'playwright-chrome']),
              help='Browser to use for scraping')
@click.option('--headless/--no-headless', default=False, help='Run browser in headless mode')
@click.option('--email', '-e', help='Heap Analytics email (or set HEAP_EMAIL env var)')
@click.option('--password', '-p', help='Heap Analytics password (or set HEAP_PASSWORD env var)')
@click.option('--output-dir', '-o', default='./reports', help='Output directory for reports')
@click.option('--format', '-f', 'formats', multiple=True, type=click.Choice(['pdf', 'docx']),
              help='Output format(s)')
@click.option('--days', '-d', default=30, help='Number of days for report')
@click.option('--company', '-c', help='Company name for report')
@click.option('--title', '-t', default='Heap Analytics Report', help='Report title')
@click.option('--interactive/--no-interactive', '-i', default=True, help='Run in interactive mode')
def generate(browser, headless, email, password, output_dir, formats, days, company, title, interactive):
    """
    Generate a Heap Analytics report

    This command opens a browser, navigates to Heap Analytics,
    extracts data, and generates comprehensive reports.
    """
    print_banner()

    # Interactive mode for missing options
    if interactive:
        if not browser:
            browser = get_browser_choice()

        if not formats:
            formats = get_output_formats()
        else:
            formats = list(formats)

        days = get_date_range()

        if not company:
            if QUESTIONARY_AVAILABLE:
                company = questionary.text(
                    "Company name (optional, press Enter to skip):",
                    style=custom_style
                ).ask()
            else:
                company = input("\nCompany name (optional, press Enter to skip): ").strip()
                company = company or None

    # Set defaults
    browser = browser or "firefox"
    formats = list(formats) if formats else ["pdf", "docx"]

    if RICH_AVAILABLE:
        console.print(Panel.fit(
            f"[bold]Configuration[/bold]\n"
            f"Browser: {browser}\n"
            f"Headless: {headless}\n"
            f"Date Range: {days} days\n"
            f"Output Formats: {', '.join(formats)}\n"
            f"Output Directory: {output_dir}",
            title="Report Settings"
        ))
    else:
        print(f"\n--- Configuration ---")
        print(f"Browser: {browser}")
        print(f"Headless: {headless}")
        print(f"Date Range: {days} days")
        print(f"Output Formats: {', '.join(formats)}")
        print(f"Output Directory: {output_dir}")
        print("-------------------\n")

    # Confirm before proceeding
    if interactive:
        if QUESTIONARY_AVAILABLE:
            proceed = questionary.confirm(
                "Proceed with report generation?",
                default=True,
                style=custom_style
            ).ask()
        else:
            proceed = input("\nProceed with report generation? (Y/n): ").strip().lower() != 'n'

        if not proceed:
            print("Report generation cancelled.")
            return

    # Import and run the scraper
    try:
        from .config import AppConfig, BrowserConfig, ReportConfig
        from .scraper import HeapScraper
        from .scraper.data_extractor import HeapDataExtractor
        from .reports import ReportBuilder

        # Create configuration
        config = AppConfig(
            browser=BrowserConfig(
                browser_type=browser,
                headless=headless,
            ),
            report=ReportConfig(
                output_dir=output_dir,
                output_format=formats,
                date_range_days=days,
                report_title=title,
                company_name=company,
            )
        )

        # Override with credentials if provided
        if email:
            config.heap.email = email
        if password:
            config.heap.password = password

        print("\n" + "=" * 60)
        print("STARTING HEAP ANALYTICS DATA EXTRACTION")
        print("=" * 60)

        # Start scraper
        with HeapScraper(config) as scraper:
            # Login
            print("\n[Step 1] Starting browser and navigating to Heap Analytics...")
            if not scraper.login():
                print("Failed to login. Please check your credentials or login manually.")
                return

            # Extract data
            print("\n[Step 2] Extracting analytics data...")
            raw_data = scraper.extract_all_data(date_range_days=days)

            # Save raw data
            raw_data_path = Path(output_dir) / "raw_data.json"
            scraper.save_raw_data(str(raw_data_path))
            print(f"\n[Step 3] Raw data saved to: {raw_data_path}")

        # Process data
        print("\n[Step 4] Processing extracted data...")
        extractor = HeapDataExtractor()
        extractor.load_raw_data(raw_data)
        processed_data = extractor.process_all()

        # Generate reports
        print("\n[Step 5] Generating reports...")
        builder = ReportBuilder(
            output_dir=output_dir,
            report_title=title,
            company_name=company,
            chart_style="modern"
        )
        results = builder.build_report(
            processed_data=processed_data,
            output_formats=formats,
            date_range_days=days
        )

        # Print results
        if RICH_AVAILABLE:
            table = Table(title="Generated Reports")
            table.add_column("Format", style="cyan")
            table.add_column("File Path", style="green")
            for fmt, path in results.items():
                table.add_row(fmt.upper(), path)
            console.print(table)
        else:
            print("\n--- Generated Reports ---")
            for fmt, path in results.items():
                print(f"  {fmt.upper()}: {path}")

        print("\n✓ Report generation complete!")

    except ImportError as e:
        print(f"\nError: Missing required dependency - {e}")
        print("Please install all requirements: pip install -r requirements.txt")
    except Exception as e:
        print(f"\nError during report generation: {e}")
        if os.getenv('DEBUG'):
            import traceback
            traceback.print_exc()


@cli.command()
@click.argument('json_file', type=click.Path(exists=True))
@click.option('--output-dir', '-o', default='./reports', help='Output directory')
@click.option('--format', '-f', 'formats', multiple=True, type=click.Choice(['pdf', 'docx']))
@click.option('--company', '-c', help='Company name for report')
@click.option('--title', '-t', default='Heap Analytics Report', help='Report title')
def from_file(json_file, output_dir, formats, company, title):
    """
    Generate reports from a saved JSON data file

    Use this when you have previously extracted data saved as JSON.
    """
    print_banner()

    formats = list(formats) if formats else ["pdf", "docx"]

    print(f"\nGenerating reports from: {json_file}")
    print(f"Output formats: {', '.join(formats)}")

    try:
        from .reports import ReportBuilder

        builder = ReportBuilder(
            output_dir=output_dir,
            report_title=title,
            company_name=company
        )
        results = ReportBuilder.from_json_file(
            json_path=json_file,
            output_dir=output_dir,
            output_formats=formats
        )

        print("\n✓ Reports generated successfully!")
        for fmt, path in results.items():
            print(f"  {fmt.upper()}: {path}")

    except Exception as e:
        print(f"\nError: {e}")


@cli.command()
def setup():
    """
    Interactive setup wizard for Heap Analytics Buddy

    Helps configure browser drivers and test the connection.
    """
    print_banner()

    print("\n" + "=" * 60)
    print("SETUP WIZARD")
    print("=" * 60)

    # Check dependencies
    print("\n[1/4] Checking dependencies...\n")

    dependencies = {
        "selenium": False,
        "playwright": False,
        "reportlab": False,
        "python-docx": False,
        "matplotlib": False,
        "rich": RICH_AVAILABLE,
        "questionary": QUESTIONARY_AVAILABLE,
    }

    try:
        import selenium
        dependencies["selenium"] = True
    except ImportError:
        pass

    try:
        import playwright
        dependencies["playwright"] = True
    except ImportError:
        pass

    try:
        import reportlab
        dependencies["reportlab"] = True
    except ImportError:
        pass

    try:
        import docx
        dependencies["python-docx"] = True
    except ImportError:
        pass

    try:
        import matplotlib
        dependencies["matplotlib"] = True
    except ImportError:
        pass

    if RICH_AVAILABLE:
        table = Table(title="Dependency Status")
        table.add_column("Package", style="cyan")
        table.add_column("Status", style="green")
        for pkg, installed in dependencies.items():
            status = "✓ Installed" if installed else "✗ Missing"
            style = "green" if installed else "red"
            table.add_row(pkg, f"[{style}]{status}[/{style}]")
        console.print(table)
    else:
        for pkg, installed in dependencies.items():
            status = "✓ Installed" if installed else "✗ Missing"
            print(f"  {pkg}: {status}")

    missing = [pkg for pkg, installed in dependencies.items() if not installed]
    if missing:
        print(f"\nMissing packages: {', '.join(missing)}")
        print("Install with: pip install -r requirements.txt")

    # Test browser
    print("\n[2/4] Testing browser availability...")

    if dependencies["selenium"]:
        print("  Selenium is available for Firefox/Chrome automation")

    if dependencies["playwright"]:
        print("  Playwright is available for browser automation")
        print("  Run 'playwright install' to download browser binaries")

    # Setup config file
    print("\n[3/4] Configuration...")

    if QUESTIONARY_AVAILABLE:
        create_config = questionary.confirm(
            "Create a configuration file?",
            default=True,
            style=custom_style
        ).ask()
    else:
        create_config = input("Create a configuration file? (Y/n): ").strip().lower() != 'n'

    if create_config:
        config_content = """# Heap Analytics Buddy Configuration
browser:
  browser_type: firefox  # firefox, chrome, playwright-firefox, playwright-chrome
  headless: false
  timeout: 30

heap:
  base_url: https://heapanalytics.com
  # email and password should be set via environment variables:
  # HEAP_EMAIL and HEAP_PASSWORD

report:
  output_dir: ./reports
  output_format:
    - pdf
    - docx
  include_charts: true
  chart_style: modern
  date_range_days: 30
"""
        config_path = Path("heap_buddy_config.yaml")
        config_path.write_text(config_content)
        print(f"\n  Configuration saved to: {config_path}")

    # Environment variables
    print("\n[4/4] Environment Variables")
    print("\nSet these environment variables for automatic login:")
    print("  export HEAP_EMAIL='your-email@example.com'")
    print("  export HEAP_PASSWORD='your-password'")

    print("\n" + "=" * 60)
    print("Setup complete! Run 'heap-buddy generate' to create a report.")
    print("=" * 60)


@cli.command()
def browsers():
    """List available browsers and their status"""
    print_banner()

    from .browser import list_available_browsers

    browsers = list_available_browsers()

    if RICH_AVAILABLE:
        table = Table(title="Available Browsers")
        table.add_column("Name", style="cyan")
        table.add_column("Description")
        table.add_column("Requires")

        for b in browsers:
            table.add_row(b["name"], b["description"], b["requires"])
        console.print(table)
    else:
        print("\nAvailable Browsers:")
        for b in browsers:
            print(f"  {b['name']}: {b['description']} (requires: {b['requires']})")


def main():
    """Main entry point"""
    cli()


if __name__ == "__main__":
    main()
