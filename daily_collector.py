import requests
import pandas as pd
import time
import os
from datetime import date

# 1. Define file path
HISTORY_FILE = 'xueqiu_hot_history.csv'

def fetch_and_save():
    # 2. Get Cookie from GitHub Secrets (Environment Variable)
    # We do not hardcode it here anymore for security!
    token_cookie = os.environ.get("XUEQIU_TOKEN")
    u_cookie = '4265859008' # This one usually doesn't change often, hardcoding is okay-ish
    
    if not token_cookie:
        print("Error: No XUEQIU_TOKEN found in environment variables.")
        return

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
        'Referer': 'https://xueqiu.com/',
    }
    cookies = {'u': u_cookie, 'xq_a_token': token_cookie}
    
    timestamp = int(time.time() * 1000)
    url = f"https://stock.xueqiu.com/v5/stock/hot_stock/list.json?page=1&size=100&order=desc&order_by=value&_={timestamp}&type=20&x=0.5"

    print("Fetching data from Xueqiu...")
    
    try:
        res = requests.get(url, headers=headers, cookies=cookies, timeout=10)
        data = res.json()
        
        # Check if cookie is invalid
        if data.get('error_code') != 0:
            print(f"Error from API: {data}")
            print("Likely cause: Cookie expired.")
            exit(1) # Fail the workflow so you get an email alert

        items = data['data']['items']
        
        # 3. Process Data
        new_df = pd.DataFrame(items)
        cols = ['name', 'symbol', 'current', 'percent', 'chg', 'exchange', 'value', 'rank_change']
        # Filter columns that exist
        new_df = new_df[[c for c in cols if c in new_df.columns]]
        
        # Add Date
        today_str = date.today().strftime('%Y-%m-%d')
        new_df.insert(0, 'date', today_str)

        # 4. Save to CSV
        # Check if file exists to determine if we need a header
        file_exists = os.path.exists(HISTORY_FILE)
        
        new_df.to_csv(HISTORY_FILE, mode='a', header=not file_exists, index=False, encoding='utf-8_sig')
        print(f"Successfully saved {len(new_df)} rows for {today_str}")

    except Exception as e:
        print(f"Script Failed: {e}")
        exit(1)

if __name__ == "__main__":
    fetch_and_save()