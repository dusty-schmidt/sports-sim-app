import asyncio
import csv
import os
from playwright.async_api import async_playwright

# Constants
BASE_URL = "https://www.tennisabstract.com/cgi-bin/leaders.cgi"
STATS_TYPES = {
    "serve": {"selector": ".statso", "param": "o"},
    "return": {"selector": ".statsw", "param": "w"}
}
SURFACES = {
    "All": "#surfacedef",
    "Hard": "#surface0",
    "Clay": "#surface1",
    "Grass": "#surface2"
}
RANK_RANGES = ["1-50", "51-100"]
OUTPUT_DIR = "c:/Users/JANET/dusty/test-app/DEV-DOCS/SEED-DATA"

async def fetch_data():
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
        page.set_default_timeout(60000)

        for type_name, type_info in STATS_TYPES.items():
            print(f"--- Fetching {type_name.upper()} Stats ---")
            
            # Store data for this stat type across all rank ranges
            # Structure: { surface: {'headers': [], 'rows': []} }
            data_by_surface = {s: {'headers': [], 'rows': []} for s in SURFACES}

            for rank_range in RANK_RANGES:
                print(f"  Fetching Rank Range: {rank_range}...")
                
                # Navigate to specific rank range
                # Use query parameter 'players'
                url = f"{BASE_URL}?players={rank_range}"
                await page.goto(url)
                await page.wait_for_load_state("networkidle")
                
                # Reset/Select Stats Type (Serve/Return)
                selector = type_info['selector']
                
                # Check eligibility
                # Sometimes navigating resets to Serve.
                # We check and click if needed.
                # We retry a few times if needed.
                for _ in range(3):
                    try:
                        cls = await page.get_attribute(selector, "class")
                        if "likelink" in cls:
                            print(f"    Switching to {type_name}...")
                            await page.click(selector)
                            await page.wait_for_function(f"document.querySelector('{selector}').className.indexOf('likelink') === -1")
                            await page.wait_for_timeout(1000)
                        break
                    except Exception as e:
                        print(f"    Retry selecting type {type_name}: {e}")
                        await page.wait_for_timeout(1000)

                for surface_name, surface_id in SURFACES.items():
                    print(f"    Processing Surface: {surface_name}...")
                    
                    try:
                        # Select Surface
                        # 1. Expand menu if closed
                        surface_head_cls = await page.get_attribute("#surfacehead", "class")
                        if "closed" in surface_head_cls:
                            await page.click("#surfacehead")
                            # Wait for option to be visible
                            # For 'All', it's #surfacedef, might be visible or not.
                            # For others, wait for their ID
                            target_id = surface_id
                            if surface_name == "All":
                                # If all, we might not see #surfacedef in the dropdown list if it's the selected default header?
                                # Actually #surfacedef is the default row.
                                # Just wait a bit.
                                await page.wait_for_timeout(500)
                            else:
                                await page.wait_for_selector(target_id, state="visible", timeout=5000)
                        
                        # 2. Click Surface
                        # If 'All' and already selected, skip?
                        # But we must ensure it is selected.
                        is_sel = await page.get_attribute(surface_id, "class")
                        if "selected" not in is_sel:
                            await page.click(surface_id)
                            await page.wait_for_function(f"document.querySelector('{surface_id}').className.indexOf('selected') !== -1")
                            
                            # Wait for table
                            await page.wait_for_selector("table#matches tbody tr", state="visible")
                            await page.wait_for_timeout(1000)

                        # Extract Data
                        rows_locator = page.locator("table#matches tbody tr")
                        count = await rows_locator.count()
                        
                        if count == 0:
                            print(f"      No rows found for {surface_name} {rank_range}")
                            continue
                            
                        # Headers (capture only once)
                        if not data_by_surface[surface_name]['headers']:
                            head_loc = page.locator("table#matches thead th")
                            headers = await head_loc.all_inner_texts()
                            headers = [h.strip().replace('\n', ' ') for h in headers]
                            data_by_surface[surface_name]['headers'] = headers
                        
                        # Rows
                        current_rows = []
                        all_rows_loc = await rows_locator.all()
                        for row in all_rows_loc:
                            cells = await row.locator("td").all_inner_texts()
                            if cells:
                                current_rows.append(cells)
                        
                        data_by_surface[surface_name]['rows'].extend(current_rows)
                        print(f"      Extracted {len(current_rows)} rows.")
                        
                    except Exception as e:
                        print(f"      Error processing {surface_name}: {e}")
                        # await page.screenshot(path=f"debug_error_{type_name}_{surface_name}_{rank_range}.png")

            # Save aggregated data for this type
            print(f"--- Saving {type_name.upper()} Data ---")
            for surface_name, data in data_by_surface.items():
                if not data['rows']:
                    print(f"  No data for {surface_name}, skipping save.")
                    continue
                    
                filename = f"atp-{type_name}-{surface_name.lower()}.csv"
                filepath = os.path.join(OUTPUT_DIR, filename)
                
                with open(filepath, "w", newline="", encoding="utf-8") as f:
                    writer = csv.writer(f)
                    writer.writerow(data['headers'])
                    writer.writerows(data['rows'])
                
                print(f"  Saved {len(data['rows'])} total rows to {filename}")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(fetch_data())
