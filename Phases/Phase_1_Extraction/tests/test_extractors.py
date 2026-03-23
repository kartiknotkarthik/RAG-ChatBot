import pytest
import os
import json
from src.extractors.groww_parser import parse_groww_html
from src.extractors.merger import BROWSER_EXTRACTS

# Create a dummy HTML for testing groww parser
@pytest.fixture
def mock_groww_html(tmp_path):
    html_content = """
    <html>
        <body>
            <h1 class="header_schemeName__rLWiE">Sample Growth Fund</h1>
            <div class="pill12Pill bodySmallHeavy">Equity</div>
            <div class="pill12Pill bodySmallHeavy">Large Cap</div>
            <div class="fundDetails_fundDetailsContainer">
                <div>
                    <div class="fundDetails_gap4">NAV:</div>
                    <div class="bodyXLargeHeavy">\u20b9250.50</div>
                </div>
                <div>
                    <div class="fundDetails_gap4">Expense ratio:</div>
                    <div class="bodyXLargeHeavy">0.75%</div>
                </div>
            </div>
            <img class="header_fundLogo" alt="HDFC Mutual Fund Logo">
        </body>
    </html>
    """
    html_file = tmp_path / "sample.html"
    html_file.write_text(html_content, encoding='utf-8')
    return str(html_file)

def test_groww_parser(mock_groww_html):
    data = parse_groww_html(mock_groww_html)
    assert data['fund_name'] == "Sample Growth Fund"
    assert "Equity" in data['categories']
    assert data['nav'] == "\u20b9250.50"
    assert data['expense_ratio'] == "0.75%"
    assert data['amc_name'] == "HDFC"

def test_merger_logic():
    # Test if merger can map a fund slug to correct browser metadata
    fund_slug = "hdfc-large-and-mid-cap-fund-direct-growth"
    assert fund_slug in BROWSER_EXTRACTS
    assert BROWSER_EXTRACTS[fund_slug]['benchmark_index'] == "NIFTY Large Midcap 250 Total Return Index"

if __name__ == "__main__":
    # If run directly, just run pytest
    import sys
    sys.exit(pytest.main([__file__]))
