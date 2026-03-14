import os
import json
import requests
import pandas as pd
from urllib.parse import quote
from pathlib import Path
from dotenv import load_dotenv

# --- Configuration ---
load_dotenv()

APP_ID = os.getenv("APP_ID")
ACCESS_KEY = os.getenv("ACCESS_KEY")
TABLE_NAME = os.getenv("TABLE_NAME")
CSV_FILE = "metadata.csv"
DOWNLOAD_DIR = "images"

# AppSheet API Endpoint for Metadata (JSON Actions)
url = f"https://api.appsheet.com/api/v2/apps/{APP_ID}/tables/{TABLE_NAME}/Action"
headers = {
    'ApplicationAccessKey': ACCESS_KEY,
    'Content-Type': 'application/json'
}

body = {
    "Action": "Find",
    "Properties": {
        "Locale": "en-GB",
        "Timezone": "Pakistan Standard Time"
    },
    "Rows": []
}

def main():
    # --- 1. Fetch & Merge Metadata ---
    try:
        print(f"Fetching metadata for table: {TABLE_NAME}...")
        response = requests.post(url, headers=headers, data=json.dumps(body))
        
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, dict) and data.get("Success") is False:
                print(f"API Error: {data}")
                return
            elif isinstance(data, list) and len(data) > 0:
                new_df = pd.DataFrame(data)
                if Path(CSV_FILE).exists():
                    existing_df = pd.read_csv(CSV_FILE)
                    combined_df = pd.concat([existing_df, new_df], ignore_index=True)
                else:
                    combined_df = new_df

                combined_df.drop_duplicates(subset=['ID'], keep='last', inplace=True)
                combined_df.to_csv(CSV_FILE, index=False)
                print(f"Metadata updated. Total records: {len(combined_df)}")
                
                # --- 2. Download Images ---
                print("Starting image downloads...")
                
                os.makedirs(DOWNLOAD_DIR, exist_ok=True)
                
                for index, row in combined_df.iterrows():
                    if 'Image' not in row or pd.isna(row['Image']) or not str(row['Image']).strip():
                        continue
                        
                    file_path = str(row['Image']) 
                    unique_id = str(row['ID']) 
                    _, file_extension = os.path.splitext(file_path)
                    
                    new_filename = f"{unique_id}{file_extension}"
                    local_filename = os.path.join(DOWNLOAD_DIR, new_filename)
                    
                    if os.path.exists(local_filename):
                        continue
                    
                    enc_table = quote(TABLE_NAME, safe='')
                    enc_file = quote(file_path, safe='')
                    
                    image_url = (
                        f"https://www.appsheet.com/template/gettablefileurl"
                        f"?appName={APP_ID}" 
                        f"&tableName={enc_table}"
                        f"&fileName={enc_file}"
                        f"&ApplicationAccessKey={ACCESS_KEY}" 
                    )
                    
                    try:
                        img_response = requests.get(image_url, headers={
                            'User-Agent': 'Mozilla/5.0'
                        })
                        
                        if img_response.status_code == 200:
                            with open(local_filename, "wb") as f:
                                f.write(img_response.content)
                            print(f"Downloaded: {file_path} -> Saved as: {new_filename}")
                        else:
                            print(f"Failed: {file_path} (Status: {img_response.status_code})")
                            print(f"Debug URL: {image_url}")
                                
                    except Exception as img_err:
                        print(f"Error downloading {file_path}: {img_err}")
            else:
                print("No data returned from API.")
        else:
            print(f"API Request Failed with status: {response.status_code}")

    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()