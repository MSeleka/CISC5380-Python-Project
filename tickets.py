
import re
import csv
from playwright.sync_api import sync_playwright

URL = "https://worththen.com/prices/entertainment/movie-ticket"
OUTPUT_FILE = "movie_ticket_prices_1980_2025.csv"

prices = {}

def extract_price(text):
    """Extract the movie ticket price from a year's page."""

    patterns = [
        r"Movie Ticket cost\s*\$\s*([\d,]+(?:\.\d+)?)",
        r"\b\d{4}\s+Price\s*\$\s*([\d,]+(?:\.\d+)?)"
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)

        if match:
            return float(match.group(1).replace(",", ""))

    return None


with sync_playwright() as p:

    browser = p.chromium.launch(headless=True)
    page = browser.new_page()

    print("Starting movie ticket price extraction...\n")

    for year in range(1980, 2026):

        year_url = f"{URL}/{year}"

        try:
            print(f"Extracting {year}...")

            page.goto(
                year_url,
                wait_until="domcontentloaded",
                timeout=60000
            )

            # Allow page content to render
            page.wait_for_timeout(1000)

            page_text = page.locator("body").inner_text()

            price = extract_price(page_text)

            if price is not None:
                prices[year] = price
                print(f"  Found: ${price:.2f}")

            else:
                print(f"  Price not found for {year}")

        except Exception as e:
            print(f"  Error extracting {year}: {e}")

    browser.close()


# Check for missing years
missing_years = [
    year for year in range(1980, 2026)
    if year not in prices
]

# Export results to CSV
with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as file:

    writer = csv.writer(file)

    writer.writerow(["Year", "Price"])

    for year in sorted(prices):
        writer.writerow([year, prices[year]])


# Display results
print("\n--------------------------------")
print("EXTRACTION COMPLETE")
print("--------------------------------")

print("CSV created:", OUTPUT_FILE)
print("Records extracted:", len(prices))

if missing_years:
    print("Missing years:", missing_years)
else:
    print("All 46 years successfully extracted!")

print("\nExtracted prices:")

for year in sorted(prices):
    print(f"{year}: ${prices[year]:.2f}")
