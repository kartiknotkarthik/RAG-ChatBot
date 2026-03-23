from bs4 import BeautifulSoup
import json
import os
import re

def parse_groww_html(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')
    
    data = {}
    
    # Fund Name
    name_tag = soup.find('h1', class_=re.compile('header_schemeName'))
    data['fund_name'] = name_tag.text.strip() if name_tag else "Unknown"
    
    # Category and sub-category
    pills = soup.find_all('div', class_=re.compile('pill12Pill'))
    data['categories'] = [p.text.strip() for p in pills]
    
    # Main Stats (NAV, Min SIP, Fund Size, Expense Ratio)
    # These often share the same class 'bodyXLargeHeavy'
    stats_labels = soup.find_all('div', class_=re.compile('fundDetails_gap4'))
    stats_values = soup.find_all('div', class_=re.compile('bodyXLargeHeavy'))
    
    # Map them by looking at the sibling or parent text
    # A more robust way is to find the containers
    containers = soup.find_all('div', class_=re.compile('fundDetails_fundDetailsContainer'))
    if containers:
        items = containers[0].find_all('div', recursive=False)
        for item in items:
            label_div = item.find('div', class_=re.compile('fundDetails_gap4'))
            value_div = item.find('div', class_=re.compile('bodyXLargeHeavy'))
            if label_div and value_div:
                label = label_div.text.split(':')[0].strip().lower().replace('.', '').replace(' ', '_')
                data[label] = value_div.text.strip()

    # Returns / Performance from Return Calculator
    returns = {}
    rows = soup.find_all('tr', class_=re.compile('returnCalculator_tableRow'))
    for row in rows:
        tds = row.find_all('td')
        if len(tds) >= 5:
            period = tds[0].text.strip()
            return_val = tds[4].text.strip()
            returns[period] = return_val
    data['performance'] = returns

    # Risk Metrics (if available on page)
    # Often in a section called "Riskometer"
    risk_pills = [p for p in data['categories'] if 'Risk' in p]
    data['risk_level'] = risk_pills[0] if risk_pills else "Unknown"

    # AMC Name
    # Extract from breadcrumbs or AMC logo alt
    logo = soup.find('img', class_=re.compile('header_fundLogo'))
    if logo and 'alt' in logo.attrs:
        data['amc_name'] = logo.attrs['alt'].split(' ')[0]
    
    return data

if __name__ == "__main__":
    raw_dir = 'data/raw/groww'
    processed_dir = 'data/processed/groww'
    os.makedirs(processed_dir, exist_ok=True)
    
    for filename in os.listdir(raw_dir):
        if filename.endswith('.html'):
            print(f"Parsing {filename}...")
            result = parse_groww_html(os.path.join(raw_dir, filename))
            output_file = os.path.join(processed_dir, filename.replace('.html', '.json'))
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=4)
            print(f"Saved to {output_file}")
