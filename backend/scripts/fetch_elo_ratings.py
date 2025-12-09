import asyncio
import csv
import os
from playwright.async_api import async_playwright

# Constants
URLS = {
    "atp_elo": "https://tennisabstract.com/reports/atp_elo_ratings.html",
    "wta_elo": "https://tennisabstract.com/reports/wta_elo_ratings.html",
    "atp_yelo": "https://tennisabstract.com/reports/atp_season_yelo_ratings.html",
    "wta_yelo": "https://tennisabstract.com/reports/wta_season_yelo_ratings.html",
}
OUTPUT_DIR = "c:/Users/JANET/dusty/test-app/DEV-DOCS/SEED-DATA"

async def fetch_elo_data():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=['--no-sandbox', '--disable-setuid-sandbox']
        )
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={'width': 1280, 'height': 800}
        )
        page = await context.new_page()

        for name, url in URLS.items():
            print(f"--- Fetching {name} from {url} ---")
            try:
                await page.goto(url)
                await page.wait_for_load_state("networkidle")
                
                # These are usually simple tables. Let's look for the main table.
                # Usually table#report or just the first table.
                # We'll wait for any table.
                await page.wait_for_selector("table")
                
                # Find the correct table
                # We look for a table that has "Rank" and "Player" in its header or first row
                tables = await page.locator("table").all()
                target_table = None
                headers = []
                
                for table in tables:
                    # Check visibility
                    if not await table.is_visible():
                        continue
                        
                    # Get potential headers
                    # Check thead first
                    thead_rows = await table.locator("thead tr").all()
                    candidate_headers = []
                    if thead_rows:
                         # Use last row of thead usually
                         candidate_headers = await thead_rows[-1].locator("th, td").all_inner_texts()
                    
                    if not candidate_headers:
                        # Check first row of tbody or just tr
                        first_tr = table.locator("tr").first
                        if await first_tr.count() > 0:
                            candidate_headers = await first_tr.locator("th, td").all_inner_texts()
                    
                    # Clean headers for check
                    candidate_headers = [h.strip().replace('\xa0', ' ') for h in candidate_headers]
                    
                    # Print debug info
                    if candidate_headers:
                        print(f"  Found table with headers: {candidate_headers[:5]}...")

                    # Heuristic: Must contain "Rank" and "Player"
                    # We check flexibly for "Rank" (e.g. "Elo Rank")
                    has_rank = any("Rank" in h for h in candidate_headers)
                    has_player = "Player" in candidate_headers
                    
                    if has_rank and has_player:
                        print(f"  Checking candidate table with {len(candidate_headers)} columns...")
                        
                        # Verify content structure: Check first few rows
                        # If rows have only 1 cell, it's likely a layout/text dump
                        sample_rows = await table.locator("tr").all()
                        valid_rows = 0
                        checked_rows = 0
                        full_data_rows = [] # Buffer to avoid re-reading
                        
                        # Check up to 5 rows deep to validate
                        for r in sample_rows[:15]: 
                            c = await r.locator("td").all_inner_texts()
                            if not c: continue
                            
                            checked_rows += 1
                            if len(c) > 1 and len(c) >= len(candidate_headers) - 1:
                                valid_rows += 1
                        
                        if valid_rows == 0 and checked_rows > 0:
                            print("  Skipping: Rows imply text dump (single column).")
                            continue
                            
                        # If it passes validation, accept it
                        target_table = table
                        headers = candidate_headers
                        break
                
                if not target_table:
                    print(f"Could not find data table for {name}")
                    continue

                # Extract rows from the found target table
                all_rows = await target_table.locator("tr").all()
                
                data = []
                for row in all_rows:
                    cells = await row.locator("td").all_inner_texts()
                    if not cells:
                         # Try th?
                         cells = await row.locator("th").all_inner_texts()
                    
                    if not cells:
                        continue
                        
                    # Clean cells
                    row_data = [c.strip().replace('\xa0', ' ') for c in cells]

                    # Skip empty rows or header rows or rows with mismatched columns
                    # Strict length check: must be within 1-2 columns of header length
                    if abs(len(row_data) - len(headers)) > 3:
                        continue
                        
                    if row_data == headers:
                        continue
                    
                    # Additional check for redundant headers that didn't match exactly
                    if "Rank" in row_data[0] and "Player" in row_data[1]:
                        continue
                        
                    data.append(row_data)

                if not data:
                    print(f"No data rows extracted for {name}")
                    continue

                filename = f"{name.replace('_', '-')}.csv"
                filepath = os.path.join(OUTPUT_DIR, filename)
                
                with open(filepath, "w", newline="", encoding="utf-8") as f:
                    writer = csv.writer(f)
                    writer.writerow(headers)
                    writer.writerows(data)
                    
                print(f"Saved {len(data)} rows to {filename}")

            except Exception as e:
                print(f"Error extracting {name}: {e}")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(fetch_elo_data())
