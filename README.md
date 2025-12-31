# Heap Analytics Buddy

A powerful command-line tool that extracts data from Heap Analytics using browser automation and generates comprehensive reports in PDF and Word formats with charts and visualizations.

## Features

- **Browser Automation**: Uses simulated browsers (Firefox preferred, Chrome as fallback) to access your Heap Analytics account
- **Multiple Browser Support**:
  - Firefox via Selenium (recommended)
  - Chrome via Selenium
  - Firefox, Chrome, or WebKit via Playwright
- **Existing Session Support**: Use your existing browser profile to leverage saved login sessions
- **Comprehensive Data Extraction**:
  - Dashboard metrics
  - Page analytics (views, time on page, bounce rates)
  - Event tracking data
  - User journey paths and patterns
  - Funnel analysis
  - Retention metrics
- **Professional Reports**:
  - PDF reports with charts and tables
  - Word documents (.docx) with full formatting
  - Visual charts and graphs
  - Executive summaries
  - Actionable insights and recommendations
- **Interactive CLI**: User-friendly command-line interface with interactive prompts

## Installation

### Prerequisites

- Python 3.9 or higher
- Firefox or Chrome browser installed
- For Firefox: geckodriver (auto-installed)
- For Chrome: chromedriver (auto-installed)

### Install from Source

```bash
# Clone the repository
git clone https://github.com/Matticusnicholas/HeapAnalyticsBuddy.git
cd HeapAnalyticsBuddy

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install the package
pip install -e .

# For Playwright (optional)
playwright install
```

## Quick Start

### 1. Run the Setup Wizard

```bash
heap-buddy setup
```

This will:
- Check all dependencies
- Create a configuration file
- Guide you through initial setup

### 2. Set Your Credentials

Either set environment variables:
```bash
export HEAP_EMAIL='your-email@example.com'
export HEAP_PASSWORD='your-password'
```

Or the tool will prompt you to log in manually in the browser.

### 3. Generate a Report

```bash
# Interactive mode (recommended)
heap-buddy generate

# Quick mode with options
heap-buddy generate --browser firefox --days 30 --format pdf --format docx
```

## Usage

### Interactive Mode

Simply run:
```bash
heap-buddy generate
```

You'll be guided through:
1. Browser selection (Firefox, Chrome, or Playwright variants)
2. Output format selection (PDF, Word, or both)
3. Date range selection
4. Optional company name for the report

### Command-Line Options

```bash
heap-buddy generate [OPTIONS]

Options:
  -b, --browser [firefox|chrome|playwright-firefox|playwright-chrome]
                                  Browser to use for scraping
  --headless / --no-headless      Run browser in headless mode
  -e, --email TEXT                Heap Analytics email
  -p, --password TEXT             Heap Analytics password
  -o, --output-dir TEXT           Output directory for reports [default: ./reports]
  -f, --format [pdf|docx]         Output format(s) (can specify multiple)
  -d, --days INTEGER              Number of days for report [default: 30]
  -c, --company TEXT              Company name for report
  -t, --title TEXT                Report title
  -i, --interactive               Run in interactive mode [default: true]
```

### Generate from Saved Data

If you've previously extracted data:
```bash
heap-buddy from-file ./reports/raw_data.json --format pdf --format docx
```

### List Available Browsers

```bash
heap-buddy browsers
```

## Configuration

### Configuration File

Create `heap_buddy_config.yaml` in your working directory:

```yaml
browser:
  browser_type: firefox
  headless: false
  timeout: 30

heap:
  base_url: https://heapanalytics.com

report:
  output_dir: ./reports
  output_format:
    - pdf
    - docx
  include_charts: true
  chart_style: modern
  date_range_days: 30
  report_title: "My Analytics Report"
  company_name: "My Company"
```

### Environment Variables

```bash
# Required
HEAP_EMAIL=your-email@example.com
HEAP_PASSWORD=your-password

# Optional
BROWSER_TYPE=firefox
BROWSER_HEADLESS=false
REPORT_OUTPUT_DIR=./reports
```

### Using Existing Browser Sessions

To use your logged-in browser session:

**Firefox:**
```yaml
browser:
  browser_type: firefox
  firefox_profile: default  # or your profile name
```

**Chrome:**
```yaml
browser:
  browser_type: chrome
  user_data_dir: ~/.config/google-chrome/Default
```

## Report Contents

The generated reports include:

### Executive Summary
- Key metrics overview (users, sessions, pageviews)
- Engagement metrics (bounce rate, session duration)
- Growth indicators

### Visual Analytics
- Top pages by views (bar chart)
- Event distribution (pie chart)
- Retention curve (line chart)
- Conversion funnels (funnel chart)

### Page Performance Analysis
- Top 10 pages by views
- Pages with high bounce rates
- Time on page analysis

### Event Tracking Analysis
- Top events by frequency
- Event categorization
- Unique users per event

### User Journey Analysis
- Common entry points
- Common exit points
- Journey length distribution

### Retention Analysis
- Week-over-week retention
- Retention health assessment
- Improvement recommendations

### Insights & Recommendations
- Data-driven insights
- Prioritized recommendations
- Expected impact analysis

## Available Metrics (Heap Free Plan)

This tool extracts all available data from Heap's free plan:

| Category | Metrics |
|----------|---------|
| **Users** | Total users, new users, returning users |
| **Sessions** | Total sessions, avg duration, pages per session |
| **Pages** | Views, unique visitors, time on page, bounce rate |
| **Events** | Event counts, unique users, event types |
| **Journeys** | User paths, entry/exit points, path length |
| **Funnels** | Step conversion rates, drop-off analysis |
| **Retention** | Weekly retention rates, cohort analysis |

## Project Structure

```
HeapAnalyticsBuddy/
├── src/
│   └── heap_buddy/
│       ├── __init__.py
│       ├── cli.py              # Command-line interface
│       ├── config.py           # Configuration management
│       ├── browser/            # Browser automation
│       │   ├── base.py         # Base browser interface
│       │   ├── firefox_driver.py
│       │   ├── chrome_driver.py
│       │   ├── playwright_driver.py
│       │   └── factory.py
│       ├── scraper/            # Heap Analytics scraper
│       │   ├── heap_scraper.py
│       │   └── data_extractor.py
│       ├── analytics/          # Data processing
│       │   ├── processor.py
│       │   └── metrics.py
│       ├── reports/            # Report generation
│       │   ├── charts.py
│       │   ├── pdf_generator.py
│       │   ├── word_generator.py
│       │   └── report_builder.py
│       └── utils/              # Utilities
│           └── helpers.py
├── requirements.txt
├── setup.py
├── heap_buddy_config.example.yaml
├── .env.example
└── README.md
```

## Troubleshooting

### Browser Won't Start

1. Ensure Firefox or Chrome is installed
2. Run `heap-buddy setup` to check dependencies
3. For Playwright, run `playwright install`

### Login Issues

1. Try running without headless mode: `--no-headless`
2. Use your browser profile to leverage saved sessions
3. Login manually when prompted

### Missing Data

1. Ensure you have data in Heap for the selected date range
2. Try a longer date range (e.g., 90 days)
3. Check if you're connected to the correct Heap organization

### PDF/Word Generation Fails

1. Install reportlab: `pip install reportlab`
2. Install python-docx: `pip install python-docx`
3. Check write permissions for output directory

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License - see LICENSE file for details.

## Disclaimer

This tool is not officially affiliated with Heap Analytics. It uses browser automation to access the Heap Analytics web interface. Please use responsibly and in accordance with Heap's Terms of Service.
