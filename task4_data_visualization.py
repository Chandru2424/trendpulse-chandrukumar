import os
import glob
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def get_latest_cleaned_csv(data_dir="data"):
    """Find the most recent cleaned trends CSV file in the data directory."""
    csv_files = glob.glob(os.path.join(data_dir, "cleaned_trends_*.csv"))
    if not csv_files:
        raise FileNotFoundError("No cleaned CSV file found in 'data/'. Please run Task 2 first.")
    
    return max(csv_files, key=os.path.getmtime)

def create_visualizations():
    """Load cleaned data and generate multi-panel visual report charts."""
    csv_path = get_latest_cleaned_csv()
    print(f"Loading dataset for visualization: {csv_path}")

    df = pd.read_csv(csv_path)

    if df.empty:
        print("Error: Cleaned dataset is empty.")
        return

    # Apply global Seaborn theme and styling
    sns.set_theme(style="whitegrid")
    plt.rcParams.update({"font.size": 10})

    # Create 2x2 grid dashboard layout
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle("TrendPulse Data Visualization Report", fontsize=16, fontweight="bold")

    # Chart 1: Story Count per Category
    sns.countplot(
        data=df, 
        x="category", 
        ax=axes[0, 0], 
        palette="viridis", 
        order=df["category"].value_counts().index
    )
    axes[0, 0].set_title("1. Story Count per Category", fontweight="bold")
    axes[0, 0].set_xlabel("Category")
    axes[0, 0].set_ylabel("Total Stories")
    axes[0, 0].tick_params(axis="x", rotation=25)

    # Chart 2: Average Upvotes (Score) by Category
    avg_scores = df.groupby("category")["score"].mean().reset_index()
    sns.barplot(
        data=avg_scores, 
        x="category", 
        y="score", 
        ax=axes[0, 1], 
        palette="magma"
    )
    axes[0, 1].set_title("2. Average Story Score by Category", fontweight="bold")
    axes[0, 1].set_xlabel("Category")
    axes[0, 1].set_ylabel("Average Upvotes")
    axes[0, 1].tick_params(axis="x", rotation=25)

    # Chart 3: Correlation (Score vs. Comments)
    sns.scatterplot(
        data=df, 
        x="score", 
        y="num_comments", 
        hue="category", 
        alpha=0.85, 
        ax=axes[1, 0]
    )
    axes[1, 0].set_title("3. Score vs. Number of Comments", fontweight="bold")
    axes[1, 0].set_xlabel("Score (Upvotes)")
    axes[1, 0].set_ylabel("Number of Comments")

    # Chart 4: Score Spread per Category (Box Plot)
    sns.boxplot(
        data=df, 
        x="category", 
        y="score", 
        ax=axes[1, 1], 
        palette="Set2"
    )
    axes[1, 1].set_title("4. Score Distribution across Categories", fontweight="bold")
    axes[1, 1].set_xlabel("Category")
    axes[1, 1].set_ylabel("Score")
    axes[1, 1].tick_params(axis="x", rotation=25)

    # Adjust layout padding
    plt.tight_layout(rect=[0, 0.03, 1, 0.95])

    # Save visual plot to data directory
    os.makedirs("data", exist_ok=True)
    output_plot_path = os.path.join("data", "trendpulse_visualizations.png")
    plt.savefig(output_plot_path, dpi=300)
    plt.close()

    print(f"Visualization report successfully exported to: {output_plot_path}")

if __name__ == "__main__":
    create_visualizations()