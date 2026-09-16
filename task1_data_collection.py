import os
import json
import time
import re
import requests
from datetime import datetime

HEADERS = {"User-Agent": "TrendPulse/1.0"}

# Keywords expanded slightly to ensure >100 matches across HackerNews items
CATEGORIES = {
    "technology": ["ai", "software", "tech", "code", "computer", "data", "cloud", "api", "gpu", "llm", "app", "python", "linux", "dev", "web"],
    "worldnews": ["war", "government", "country", "president", "election", "climate", "attack", "global", "us", "uk", "police", "court", "law", "china"],
    "sports": ["nfl", "nba", "fifa", "sport", "game", "team", "player", "league", "championship", "cup", "match", "win", "football"],
    "science": ["research", "study", "space", "physics", "biology", "discovery", "nasa", "genome", "science", "health", "brain", "earth", "scientist"],
    "entertainment": ["movie", "film", "music", "netflix", "game", "book", "show", "award", "streaming", "media", "video", "art", "tv", "actor"]
}

def matches_category(title, keywords):
    """Check if any keyword matches words in the title (case-insensitive)."""
    if not title:
        return False
    title_lower = title.lower()
    for kw in keywords:
        pattern = r'\b' + re.escape(kw.lower()) + r'\b'
        if re.search(pattern, title_lower):
            return True
    return False

def collect_trending_stories():
    session = requests.Session()
    session.headers.update(HEADERS)

    # Combine topstories and newstories to ensure a large enough pool
    story_ids = []
    for endpoint in ["topstories.json", "newstories.json"]:
        try:
            res = session.get(f"https://hacker-news.firebaseio.com/v0/{endpoint}", timeout=10)
            if res.status_code == 200:
                story_ids.extend(res.json())
        except requests.RequestException:
            continue

    # Deduplicate IDs while preserving order
    unique_ids = list(dict.fromkeys(story_ids))[:800]
    print(f"Retrieved {len(unique_ids)} story IDs. Downloading story details...")

    fetched_stories = []
    for idx, s_id in enumerate(unique_ids, start=1):
        if idx % 100 == 0 or idx == len(unique_ids):
            print(f" -> Downloaded {idx}/{len(unique_ids)} details...")
        
        try:
            item_res = session.get(f"https://hacker-news.firebaseio.com/v0/item/{s_id}.json", timeout=5)
            if item_res.status_code == 200 and item_res.json():
                item = item_res.json()
                if item.get("type") == "story":
                    fetched_stories.append(item)
        except requests.RequestException:
            continue

    print(f"\nCategorizing {len(fetched_stories)} stories...")

    all_collected = []
    seen_ids = set()
    category_list = list(CATEGORIES.keys())

    for idx, category in enumerate(category_list):
        keywords = CATEGORIES[category]
        category_stories = []

        for story in fetched_stories:
            if len(category_stories) >= 25:
                break

            s_id = story.get("id")
            if s_id in seen_ids:
                continue

            title = story.get("title", "")
            if matches_category(title, keywords):
                category_stories.append({
                    "post_id": s_id,
                    "title": title,
                    "category": category,
                    "score": story.get("score", 0),
                    "num_comments": story.get("descendants", 0),
                    "author": story.get("by", "unknown"),
                    "collected_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })
                seen_ids.add(s_id)

        print(f" -> Collected {len(category_stories)} stories for '{category}'.")
        all_collected.extend(category_stories)

        if idx < len(category_list) - 1:
            time.sleep(2)

    return all_collected

def save_to_json(data):
    """Save stories to data/trends_YYYYMMDD.json file."""
    os.makedirs("data", exist_ok=True)
    today_str = datetime.now().strftime("%Y%m%d")
    file_path = os.path.join("data", f"trends_{today_str}.json")

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

    print(f"\nCollected {len(data)} stories. Saved to {file_path}")

if __name__ == "__main__":
    stories = collect_trending_stories()
    save_to_json(stories)