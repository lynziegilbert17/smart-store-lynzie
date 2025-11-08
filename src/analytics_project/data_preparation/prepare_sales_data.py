# prepare_sales_data.py
# Clean sales_data.csv and write data/prepared/sales_data_prepared.csv

from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
RAW = ROOT / "data" / "raw"
PREP = ROOT / "data" / "prepared"
PREP.mkdir(parents=True, exist_ok=True)

INFILE = RAW / "sales_data.csv"
OUTFILE = PREP / "sales_data_prepared.csv"

ALLOWED_PAY = {"Cash", "Card", "EBT", "GiftCard"}


def iqr_keep(series: pd.Series, k: float = 1.5):
    q1, q3 = series.quantile([0.25, 0.75])
    iqr = q3 - q1
    lo, hi = q1 - k * iqr, q3 + k * iqr
    return series.between(lo, hi)


def clean_sales(df: pd.DataFrame) -> pd.DataFrame:
    # Trim strings
    for c in df.select_dtypes(include="object").columns:
        df[c] = df[c].astype(str).str.strip()

    # Dates to datetime (coerce bad ones to NaT, then drop)
    if "SaleDate" in df.columns:
        df["SaleDate"] = pd.to_datetime(df["SaleDate"], errors="coerce")
        df = df.dropna(subset=["SaleDate"])

    # SaleAmount numeric > 0 and remove outliers
    if "SaleAmount" in df.columns:
        df["SaleAmount"] = pd.to_numeric(df["SaleAmount"], errors="coerce")
        df = df[df["SaleAmount"].gt(0)]
        df = df[iqr_keep(df["SaleAmount"])]

    # DiscountPct numeric in [0,100] and remove outliers
    if "DiscountPct" in df.columns:
        df["DiscountPct"] = pd.to_numeric(df["DiscountPct"], errors="coerce")
        df = df[df["DiscountPct"].between(0, 100, inclusive="both")]
        df = df[iqr_keep(df["DiscountPct"])]

    # PaymentType normalization
    if "PaymentType" in df.columns:
        repl = {
            "gift card": "GiftCard",
            "Gift Card": "GiftCard",
            "card": "Card",
            "debit": "Card",
            "credit": "Card",
            "cash": "Cash",
            "ebt": "EBT",
            "": pd.NA,
            "nan": pd.NA,
            "None": pd.NA,
        }
        df["PaymentType"] = df["PaymentType"].replace(repl)
        df = df[df["PaymentType"].isin(ALLOWED_PAY)]

    # Drop duplicate transactions by TransactionID
    if "TransactionID" in df.columns:
        df = df.drop_duplicates(subset=["TransactionID"])
    else:
        df = df.drop_duplicates()

    return df


def main():
    raw = pd.read_csv(INFILE)
    raw_count = len(raw)
    cleaned = clean_sales(raw.copy())
    cleaned_count = len(cleaned)
    cleaned.to_csv(OUTFILE, index=False)
    print(f"Sales raw: {raw_count}  -> prepared: {cleaned_count}")
    print(f"Wrote: {OUTFILE.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
