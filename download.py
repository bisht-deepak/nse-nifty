from pathlib import Path
import calendar
import requests
from time import sleep
from tqdm import tqdm

# ----------------------------
# Configuration
# ----------------------------

BASE_URL = (
    "https://www.niftyindices.com/"
    "Market_Capitalisation_Weightage_Beta_for_NIFTY_50_And_NIFTY_Next_50/"
)

OUTPUT_DIR = Path("data/raw/mcwb")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 Chrome/138.0 Safari/537.36"
    )
}

# ----------------------------
# Generate URLs
# ----------------------------

downloads = []

for year in range(2008, 2027):
    for month in range(1, 13):

        if year == 2026 and month > 6:
            break

        mon = calendar.month_abbr[month].lower()

        filename = f"mcwb_{mon}{str(year)[2:]}.zip"

        url = BASE_URL + filename

        downloads.append((url, filename))

# ----------------------------
# Download
# ----------------------------

failed = []

for url, filename in tqdm(downloads):

    outfile = OUTPUT_DIR / filename

    if outfile.exists():
        continue

    success = False

    for attempt in range(3):

        try:

            r = requests.get(
                url,
                headers=HEADERS,
                timeout=30
            )

            if r.status_code == 200:

                outfile.write_bytes(r.content)
                success = True
                break

        except Exception:
            pass

        sleep(2)

    if not success:
        failed.append(url)

# ----------------------------
# Summary
# ----------------------------

print(f"\nDownloaded: {len(downloads)-len(failed)}")
print(f"Failed: {len(failed)}")

if failed:

    with open("failed_downloads.txt", "w") as f:

        for url in failed:
            f.write(url + "\n")

    print("Failed URLs saved to failed_downloads.txt")