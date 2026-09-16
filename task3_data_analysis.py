import os
import glob
import pandas as pd
import numpy as np

def get_latest_cleaned_csv(data_dir="data"):
    """Find the most recent cleaned trends CSV file in the data directory."""
    csv_files = glob.glob(os.path.join(data_dir, "cleaned_trends_*.csv"))
    if not csv_files:
        raise FileNotFoundError("No cleaned CSV file found in 'data/'. Please run Task 2 first.")
    
    return max(csv_files, key=os.path.getmtime)

def analyze_trends_data():
    """Perform data analysis using Pandas and NumPy."""
    csv_path = get_latest_cleaned_csv()
    print(f"Loading data from: {csv_path}\n")

    df = pd.read_csv(csv_path)

    if df.empty:
        print("Error: Cleaned CSV dataset is empty.")
        return

    # --- 1. Category-level Aggregations (Pandas) ---
    print("=" * 50)
    print(" CATEGORY-LEVEL SUMMARY ")
    print("=" * 50)
    
    category_summary = df.groupby("category").agg(
        total_posts=("post_id", "count"),
        avg_score=("score", "mean"),
        max_score=("score", "max"),
        avg_comments=("num_comments", "mean"),
        total_comments=("num_comments", "sum")
    ).round(2)

    print(category_summary.to_string())
    print("\n")

    # --- 2. Highlights & Top Performers ---
    top_scored_story = df.loc[df["score"].idxmax()]
    top_commented_story = df.loc[df["num_comments"].idxmax()]

    print("=" * 50)
    print(" TOP PERFORMING STORIES ")
    print("=" * 50)
    print(f"Highest Scored Post: '{top_scored_story['title']}' ({top_scored_story['score']} points) [{top_scored_story['category']}]")
    print(f"Most Commented Post: '{top_commented_story['title']}' ({top_commented_story['num_comments']} comments) [{top_commented_story['category']}]\n")

    # --- 3. Statistical Metrics using NumPy ---
    scores = df["score"].to_numpy()
    comments = df["num_comments"].to_numpy()

    mean_score = np.mean(scores)
    median_score = np.median(scores)
    std_score = np.std(scores)
    p75_score = np.percentile(scores, 75)

    # Correlation between score and comments
    corr_matrix = np.corrcoef(scores, comments)
    score_comment_corr = corr_matrix[0, 1]

    print("=" * 50)
    print(" NUMPY STATISTICAL METRICS ")
    print("=" * 50)
    print(f"Mean Score: {mean_score:.2f}")
    print(f"Median Score: {median_score:.2f}")
    print(f"Score Std Deviation: {std_score:.2f}")
    print(f"75th Percentile Score: {p75_score:.2f}")
    print(f"Score vs. Comments Correlation: {score_comment_corr:.4f}\n")

    # --- 4. Save Summary Report ---
    os.makedirs("data", exist_ok=True)
    summary_path = os.path.join("data", "analysis_summary.csv")
    category_summary.to_csv(summary_path, encoding="utf-8")
    print(f"Category summary report exported to: {summary_path}")

if __name__ == "__main__":
    analyze_trends_data()