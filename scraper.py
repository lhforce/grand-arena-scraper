import os
import json
import time
import re
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
        
        print("Navigating to GATracker...")
        page.goto("https://gatracker.xyz/", wait_until="networkidle")
        time.sleep(10) # Heavy React render wait
        
        leaderboard = page.evaluate(''' () => {
            const data = [];
            // New Selector Strategy: Find ID tags (#123) and traverse to siblings/parents
            const idSpans = Array.from(document.querySelectorAll('span')).filter(s => /^#\\d+$/.test(s.innerText.trim()));
            
            idSpans.forEach(span => {
                const row = span.closest('div[role="row"]') || span.closest('button') || span.parentElement.parentElement;
                if (row) {
                    const text = row.innerText.split('\\n');
                    data.push({
                        id: span.innerText,
                        name: text[0] || 'Unknown',
                        stats: text.join(' | ')
                    });
                }
            });
            return data.slice(0, 50);
        } ''')
        
        # Push to Supabase
        supabase.table("ga_intelligence").insert({
            "contest_name": "Global Leaderboard (Patch v2)",
            "leaderboard_data": leaderboard
        }).execute()
        
        print(f"Successfully pushed {len(leaderboard)} rows to Supabase.")
        browser.close()

if __name__ == "__main__":
    scrape_ga()
