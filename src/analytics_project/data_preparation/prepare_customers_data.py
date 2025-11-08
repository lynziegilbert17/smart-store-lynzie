# prepare_customers_data.py
# Clean customers_data.csv and write data/prepared/customers_data_prepared.csv

from pathlib import Path
import pandas as pd

# --- Paths ---
ROOT = Path(__file__).resolve().parents[3]  # repo root
RAW = ROOT / "data" / "raw"
PREP = ROOT / "data" / "prepared"
PREP.mkdir(parents=True, exist_ok=True)

INFILE = RAW / "customers_data.csv"
OUTFILE = PREP / "customers_data_prepared.csv"

ALLOWED_CONTACT = {"Email", "SMS", "Phone"}


def iqr_filter(series: pd.Series, k: float = 1.5):
    """Boolean mask keeping non-outliers via IQR rule."""
    q1 = series.quantile(0.25)
    q3 = series.quantile(0.75)
    iqr = q3 - q1
    lo, hi = q1 - k * iqr, q3 + k * iqr
    return series.between(lo, hi)


def clean_customers(df: pd.DataFrame) -> pd.DataFrame:
    # Trim strings
    for c in df.select_dtypes(include="object").columns:
        df[c] = df[c].astype(str).str.strip()

    # Standardize Region
    if "Region" in df.columns:
        df["Region"] = df["Region"].str.title()

    # ContactMethod normalization
    if "ContactMethod" in df.columns:
        df["ContactMethod"] = df["ContactMethod"].replace({"": pd.NA, "nan": pd.NA, "None": pd.NA})
        replacements = {
            "e-mail": "Email",
            "E-mail": "Email",
            "email": "Email",
            "EMAIL": "Email",
            "sms": "SMS",
            "text": "SMS",
            "Txt": "SMS",
            "phone": "Phone",
            "PHONE": "Phone",
        }
        df["ContactMethod"] = df["ContactMethod"].replace(replacements)
        df = df[df["ContactMethod"].isin(ALLOWED_CONTACT)]

    # LoyaltyPointsQty
    if "LoyaltyPointsQty" in df.columns:
        df["LoyaltyPointsQty"] = pd.to_numeric(df["LoyaltyPointsQty"], errors="coerce")
        df = df[df["LoyaltyPointsQty"].ge(0)]
        df = df[iqr_filter(df["LoyaltyPointsQty"])]

    # Duplicates
    if "CustomerID" in df.columns:
        df = df.drop_duplicates(subset=["CustomerID"])
    else:
        df = df.drop_duplicates()

    return df


def main():
    raw = pd.read_csv(INFILE)
    raw_count = len(raw)
    cleaned = clean_customers(raw.copy())
    cleaned_count = len(cleaned)
    cleaned.to_csv(OUTFILE, index=False)
    print(f"Customers raw: {raw_count}  -> prepared: {cleaned_count}")
    print(f"Wrote: {OUTFILE.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
