import os
import json
import time
from supabase import create_client, Client
from playwright.sync_api import sync_playwright

# Configuration from GitHub Secrets
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

def scrape_ga():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        ).new_page()
        
        # Target: GATracker (Botto's data)
        print("Navigating to GATracker...")
        page.goto("https://gatracker.xyz/", wait_until="networkidle")
        time.sleep(5) # Allow JS to render
        
        # Extract data (Basic example - would be refined based on DOM)
        leaderboard = page.evaluate(''() => {
            const rows = Array.from(document.querySelectorAll('tr')).slice(1, 11);
            return rows.map(row => ({
                rank: row.cells[0]?.innerText,
                player: row.cells[1]?.innerText,
                points: row.cells[2]?.innerText,
                synergy: row.cells[3]?.innerText
            }));
        }'')
        
        # Push to Supabase
        data, count = supabase.table("ga_intelligence").insert({
            "contest_name": "Global Leaderboard",
            "leaderboard_data": leaderboard
        }).execute()
        
        print(f"Successfully pushed {len(leaderboard)} rows to Supabase.")
        browser.close()

if __name__ == "__main__":
    scrape_ga()
