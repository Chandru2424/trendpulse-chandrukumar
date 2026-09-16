import os
import glob
import json
import pandas as pd
from datetime import datetime

def get_latest_json_file(data_dir="data"):
    """Find the most recent trends JSON file in the data directory."""
    json_files = glob.glob(os.path.join(data_dir, "trends_*.json"))
    if not json_files:
        raise FileNotFoundError("No trends JSON file found in 'data/'. Please run Task 1 first.")
    
    # Return the most recently modified JSON file
    return max(json_files, key=os.path.getmtime)

def clean_trends_data():
    """Load JSON data, apply cleaning transformations, and save to CSV."""
    json_path = get_latest_json_file()
    print(f"Reading input file: {json_path}")

    # Load JSON content
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if not data:
        print("Error: JSON file is empty.")
        return

    # Load into Pandas DataFrame
    df = pd.DataFrame(data)
    initial_rows = len(df)
    print(f"Loaded {initial_rows} raw records.")

    # 1. Remove duplicates based on unique post_id
    df.drop_duplicates(subset=["post_id"], keep="first", inplace=True)

    # 2. Handle missing / NaN values across required fields
    df["title"] = df["title"].fillna("Untitled").astype(str)
    df["category"] = df["category"].fillna("uncategorized").astype(str)
    df["author"] = df["author"].fillna("unknown").astype(str)
    df["score"] = pd.to_numeric(df["score"], errors="coerce").fillna(0).astype(int)
    df["num_comments"] = pd.to_numeric(df["num_comments"], errors="coerce").fillna(0).astype(int)

    # 3. Text cleaning: strip extra whitespace and normalize category names
    df["title"] = df["title"].str.strip()
    df["category"] = df["category"].str.strip().str.lower()
    df["author"] = df["author"].str.strip()

    # 4. Ensure non-negative integers for numeric metrics
    df["score"] = df["score"].apply(lambda x: max(0, x))
    df["num_comments"] = df["num_comments"].apply(lambda x: max(0, x))

    # 5. Format output file path and save
    today_str = datetime.now().strftime("%Y%m%d")
    output_csv_path = os.path.join("data", f"cleaned_trends_{today_str}.csv")
    
    os.makedirs("data", exist_ok=True)
    df.to_csv(output_csv_path, index=False, encoding="utf-8")

    print(f"Data cleaning complete: {initial_rows} -> {len(df)} rows.")
    print(f"Saved cleaned CSV to: {output_csv_path}")

if __name__ == "__main__":
    clean_trends_data()