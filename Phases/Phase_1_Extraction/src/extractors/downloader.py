import requests
import os
import json
import time

def download(url, dest_path, is_binary=False):
    print(f"Downloading {url} to {dest_path}...")
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    try:
        response = requests.get(url, headers=headers, stream=True, timeout=30)
        if response.status_code == 200:
            os.makedirs(os.path.dirname(dest_path), exist_ok=True)
            mode = 'wb' if is_binary else 'w'
            encoding = None if is_binary else 'utf-8'
            with open(dest_path, mode, encoding=encoding) as f:
                if is_binary:
                    for chunk in response.iter_content(chunk_size=1024):
                        f.write(chunk)
                else:
                    f.write(response.text)
            print(f"SUCCESS: {dest_path}")
            return True
        else:
            print(f"FAILED: Status {response.status_code} for {url}")
            return False
    except Exception as e:
        print(f"ERROR: {e} for {url}")
        return False

if __name__ == "__main__":
    with open('data/urls.json', 'r') as f:
        config = json.load(f)

    # Groww
    for url in config['groww']:
        slug = url.split('/')[-1]
        download(url, f'data/raw/groww/{slug}.html')
        time.sleep(1) # Be nice to servers

    # SEBI PDF
    for url in config['pdfs']:
        filename = url.split('/')[-1]
        download(url, f'data/raw/pdfs/{filename}', is_binary=True)
    
    # AMFI
    for url in config['amfi']:
        slug = "amfi_nav" if "net-asset-value" in url else "amfi_home"
        download(url, f'data/raw/amfi/{slug}.html')
        time.sleep(1)

    # AMC Factsheets
    for url in config['amc_factsheets']:
        slug = url.replace('https://www.', '').replace('https://', '').replace('/', '_').replace('.', '_')
        download(url, f'data/raw/amc/{slug}.html')
        time.sleep(1)
