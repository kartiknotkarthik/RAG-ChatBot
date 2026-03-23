import json
import os

# Manual data from browser subagent (to override or fill gaps)
BROWSER_EXTRACTS = {
    "hdfc-large-and-mid-cap-fund-direct-growth": {
        "fund_managers": [
            {"name": "Gopal Agrawal", "tenure": "Jul 2020 - Present", "num_funds": 4},
            {"name": "Dhruv Muchhal", "tenure": "Jun 2023 - Present", "num_funds": 18}
        ],
        "investment_strategy": "The scheme seeks to generate long-term capital appreciation/income from a portfolio predominantly invested in equity and equity-related instruments.",
        "benchmark_index": "NIFTY Large Midcap 250 Total Return Index"
    },
    "sbi-gold-fund-direct-growth": {
        "fund_managers": [
            {"name": "Pradeep Kesavan", "tenure": "Dec 2023 - Present", "num_funds": 5},
            {"name": "Viral Chhadva", "tenure": "Mar 2024 - Present", "num_funds": 16}
        ],
        "investment_strategy": "The Scheme seeks to provide returns that closely correspond to returns provided by SBI Gold Exchange Traded Scheme (SBI GETS).",
        "benchmark_index": "Domestic Price of Gold"
    },
    "hdfc-silver-etf-fof-direct-growth": {
        "fund_managers": [
            {"name": "Arun Agarwal", "tenure": "Feb 2023 - Present", "num_funds": 22}
        ],
        "investment_strategy": "The scheme seeks capital appreciation by investing in units of HDFC Silver ETF (HSETF).",
        "benchmark_index": "Domestic Price of Silver"
    }
}

def merge_data():
    groww_processed_dir = 'data/processed/groww'
    master_file = 'data/processed/fund_master.json'
    
    master_list = []
    
    if not os.path.exists(groww_processed_dir):
        print(f"Error: {groww_processed_dir} does not exist. Run parser first.")
        return

    for filename in os.listdir(groww_processed_dir):
        if filename.endswith('.json'):
            fund_slug = filename.replace('.json', '')
            with open(os.path.join(groww_processed_dir, filename), 'r') as f:
                core_data = json.load(f)
            
            # Enrich with browser details
            if fund_slug in BROWSER_EXTRACTS:
                core_data.update(BROWSER_EXTRACTS[fund_slug])
            
            # Use consistent citation links
            core_data['citation_url'] = f"https://groww.in/mutual-funds/{fund_slug}"
            
            master_list.append(core_data)
            
    with open(master_file, 'w', encoding='utf-8') as f:
        json.dump(master_list, f, indent=4)
    print(f"Successfully merged {len(master_list)} funds to {master_file}")

if __name__ == "__main__":
    merge_data()
