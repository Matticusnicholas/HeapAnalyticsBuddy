"""
Configuration module for Heap Analytics Buddy
"""

import os
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional, List
from dotenv import load_dotenv
import yaml

# Load environment variables
load_dotenv()


@dataclass
class BrowserConfig:
    """Browser configuration settings"""
    browser_type: str = "firefox"  # firefox, chrome, or playwright
    headless: bool = False  # Run in headless mode
    profile_path: Optional[str] = None  # Path to browser profile (for existing logins)
    user_data_dir: Optional[str] = None  # Chrome user data directory
    firefox_profile: Optional[str] = None  # Firefox profile name
    timeout: int = 30  # Default timeout in seconds
    implicit_wait: int = 10  # Implicit wait time
    window_width: int = 1920
    window_height: int = 1080


@dataclass
class HeapConfig:
    """Heap Analytics configuration"""
    base_url: str = "https://heapanalytics.com"
    login_url: str = "https://heapanalytics.com/login"
    dashboard_url: str = "https://heapanalytics.com/app"
    email: Optional[str] = None
    password: Optional[str] = None
    organization_id: Optional[str] = None


@dataclass
class ReportConfig:
    """Report generation configuration"""
    output_dir: str = "./reports"
    output_format: List[str] = field(default_factory=lambda: ["pdf", "docx"])
    include_charts: bool = True
    chart_style: str = "modern"  # modern, classic, minimal
    date_range_days: int = 30
    include_raw_data: bool = False
    report_title: str = "Heap Analytics Report"
    company_name: Optional[str] = None
    logo_path: Optional[str] = None


@dataclass
class AppConfig:
    """Main application configuration"""
    browser: BrowserConfig = field(default_factory=BrowserConfig)
    heap: HeapConfig = field(default_factory=HeapConfig)
    report: ReportConfig = field(default_factory=ReportConfig)
    verbose: bool = False
    debug: bool = False


def load_config(config_path: Optional[str] = None) -> AppConfig:
    """Load configuration from file and environment variables"""
    config = AppConfig()

    # Check for config file
    if config_path and Path(config_path).exists():
        with open(config_path, 'r') as f:
            yaml_config = yaml.safe_load(f)
            if yaml_config:
                _apply_yaml_config(config, yaml_config)

    # Override with environment variables
    _apply_env_config(config)

    return config


def _apply_yaml_config(config: AppConfig, yaml_config: dict):
    """Apply YAML configuration to config object"""
    if 'browser' in yaml_config:
        for key, value in yaml_config['browser'].items():
            if hasattr(config.browser, key):
                setattr(config.browser, key, value)

    if 'heap' in yaml_config:
        for key, value in yaml_config['heap'].items():
            if hasattr(config.heap, key):
                setattr(config.heap, key, value)

    if 'report' in yaml_config:
        for key, value in yaml_config['report'].items():
            if hasattr(config.report, key):
                setattr(config.report, key, value)


def _apply_env_config(config: AppConfig):
    """Apply environment variables to config"""
    # Heap credentials from env
    if os.getenv('HEAP_EMAIL'):
        config.heap.email = os.getenv('HEAP_EMAIL')
    if os.getenv('HEAP_PASSWORD'):
        config.heap.password = os.getenv('HEAP_PASSWORD')
    if os.getenv('HEAP_ORG_ID'):
        config.heap.organization_id = os.getenv('HEAP_ORG_ID')

    # Browser settings from env
    if os.getenv('BROWSER_TYPE'):
        config.browser.browser_type = os.getenv('BROWSER_TYPE')
    if os.getenv('BROWSER_HEADLESS'):
        config.browser.headless = os.getenv('BROWSER_HEADLESS').lower() == 'true'
    if os.getenv('FIREFOX_PROFILE'):
        config.browser.firefox_profile = os.getenv('FIREFOX_PROFILE')
    if os.getenv('CHROME_USER_DATA'):
        config.browser.user_data_dir = os.getenv('CHROME_USER_DATA')

    # Report settings from env
    if os.getenv('REPORT_OUTPUT_DIR'):
        config.report.output_dir = os.getenv('REPORT_OUTPUT_DIR')


def save_config(config: AppConfig, config_path: str):
    """Save configuration to YAML file"""
    config_dict = {
        'browser': {
            'browser_type': config.browser.browser_type,
            'headless': config.browser.headless,
            'profile_path': config.browser.profile_path,
            'timeout': config.browser.timeout,
        },
        'heap': {
            'base_url': config.heap.base_url,
            'organization_id': config.heap.organization_id,
            # Note: Don't save credentials to file
        },
        'report': {
            'output_dir': config.report.output_dir,
            'output_format': config.report.output_format,
            'include_charts': config.report.include_charts,
            'chart_style': config.report.chart_style,
            'date_range_days': config.report.date_range_days,
            'report_title': config.report.report_title,
            'company_name': config.report.company_name,
        }
    }

    Path(config_path).parent.mkdir(parents=True, exist_ok=True)
    with open(config_path, 'w') as f:
        yaml.dump(config_dict, f, default_flow_style=False)
