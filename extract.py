from pathlib import Path
from zipfile import ZipFile
import shutil
from tqdm import tqdm

# ==========================================================
# Configuration
# ==========================================================

RAW_DIR = Path("data/raw/mcwb")

NIFTY50_DIR = Path("data/extracted/nifty50")
NEXT50_DIR = Path("data/extracted/niftynext50")

NIFTY50_DIR.mkdir(parents=True, exist_ok=True)
NEXT50_DIR.mkdir(parents=True, exist_ok=True)

# ==========================================================
# Filename patterns
# ==========================================================

NIFTY50_PATTERNS = [
    "nifty50",
    "niftymcwb",
]

NEXT50_PATTERNS = [
    "niftynext50",
    "niftynext",
    "jrnifty",
]


def matches(filename: str, patterns: list[str]) -> bool:
    """Returns True if any pattern appears in filename."""
    return any(pattern in filename for pattern in patterns)


def normalize(filename: str) -> str:
    """
    Normalizes filenames to make matching easier.
    """
    return (
        filename.lower()
        .replace(" ", "")
        .replace("-", "_")
    )


def get_period(zip_path: Path) -> str:
    """
    mcwb_jan08.zip -> jan08
    """
    return zip_path.stem.replace("mcwb_", "")


# ==========================================================
# Extraction
# ==========================================================

zip_files = sorted(RAW_DIR.glob("*.zip"))

nifty50_count = 0
next50_count = 0

missing_nifty50 = []
missing_next50 = []

print(f"Found {len(zip_files)} ZIP files.\n")

for zip_path in tqdm(zip_files, desc="Extracting", unit="zip"):

    period = get_period(zip_path)

    found_nifty50 = False
    found_next50 = False

    try:

        with ZipFile(zip_path) as archive:

            for member in archive.namelist():

                filename = normalize(Path(member).name)

                # Ignore directories and non-csv files
                if not filename.endswith(".csv"):
                    continue

                # ------------------------------------------------------
                # NIFTY NEXT 50
                # (check this FIRST since filename also contains "nifty")
                # ------------------------------------------------------

                if matches(filename, NEXT50_PATTERNS):

                    output = NEXT50_DIR / f"niftynext50_{period}.csv"

                    with archive.open(member) as src, open(output, "wb") as dst:
                        shutil.copyfileobj(src, dst)

                    found_next50 = True
                    next50_count += 1

                # ------------------------------------------------------
                # NIFTY 50
                # ------------------------------------------------------

                elif matches(filename, NIFTY50_PATTERNS):

                    output = NIFTY50_DIR / f"nifty50_{period}.csv"

                    with archive.open(member) as src, open(output, "wb") as dst:
                        shutil.copyfileobj(src, dst)

                    found_nifty50 = True
                    nifty50_count += 1

        if not found_nifty50:
            missing_nifty50.append(zip_path.name)

        if not found_next50:
            missing_next50.append(zip_path.name)

    except Exception as e:
        print(f"\nError processing {zip_path.name}: {e}")

# ==========================================================
# Summary
# ==========================================================

print("\n" + "=" * 60)
print("Extraction Complete")
print("=" * 60)

print(f"ZIP files processed        : {len(zip_files)}")
print(f"NIFTY 50 files extracted   : {nifty50_count}")
print(f"NIFTY Next 50 extracted    : {next50_count}")

print(f"\nZIPs missing NIFTY 50 file : {len(missing_nifty50)}")
print(f"ZIPs missing Next 50 file  : {len(missing_next50)}")

if missing_nifty50:
    print("\nMissing NIFTY 50 CSV:")
    for f in missing_nifty50:
        print("  ", f)

if missing_next50:
    print("\nMissing NIFTY Next 50 CSV:")
    for f in missing_next50:
        print("  ", f)

print("=" * 60)