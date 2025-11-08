# prepare_products_data.py
# Clean products_data.csv and write data/prepared/products_data_prepared.csv

from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
RAW = ROOT / "data" / "raw"
PREP = ROOT / "data" / "prepared"
PREP.mkdir(parents=True, exist_ok=True)

INFILE = RAW / "products_data.csv"
OUTFILE = PREP / "products_data_prepared.csv"

ALLOWED_SUPPLIERS = {"Acme", "Globex", "InHouse"}


def iqr_keep(series: pd.Series, k: float = 1.5):
    q1, q3 = series.quantile([0.25, 0.75])
    iqr = q3 - q1
    lo, hi = q1 - k * iqr, q3 + k * iqr
    return series.between(lo, hi)


def clean_products(df: pd.DataFrame) -> pd.DataFrame:
    # Trim strings
    for c in df.select_dtypes(include="object").columns:
        df[c] = df[c].astype(str).str.strip()

    # Standardize Category (Title case)
    if "Category" in df.columns:
        df["Category"] = df["Category"].str.title()

    # UnitPrice → numeric (handle commas) and remove nonpositive/outliers
    if "UnitPrice" in df.columns:
        df["UnitPrice"] = (
            df["UnitPrice"]
            .astype(str)
            .str.replace(",", "", regex=False)
            .pipe(pd.to_numeric, errors="coerce")
        )
        df = df[df["UnitPrice"].gt(0)]
        df = df[iqr_keep(df["UnitPrice"])]

    # StockQtyUnits → numeric, no negatives, outliers removed
    if "StockQtyUnits" in df.columns:
        df["StockQtyUnits"] = pd.to_numeric(df["StockQtyUnits"], errors="coerce")
        df = df[df["StockQtyUnits"].ge(0)]
        df = df[iqr_keep(df["StockQtyUnits"])]

    # Supplier normalization
    if "Supplier" in df.columns:
        repl = {
            "acme": "Acme",
            "ACME": "Acme",
            "globex": "Globex",
            "GLOBEX": "Globex",
            "inhouse": "InHouse",
            "In House": "InHouse",
            "INHOUSE": "InHouse",
            "": pd.NA,
            "nan": pd.NA,
            "None": pd.NA,
        }
        df["Supplier"] = df["Supplier"].replace(repl)
        df = df[df["Supplier"].isin(ALLOWED_SUPPLIERS)]

    # Drop duplicate products by ProductID
    if "ProductID" in df.columns:
        df = df.drop_duplicates(subset=["ProductID"])
    else:
        df = df.drop_duplicates()

    return df


def main():
    raw = pd.read_csv(INFILE)
    raw_count = len(raw)
    cleaned = clean_products(raw.copy())
    cleaned_count = len(cleaned)
    cleaned.to_csv(OUTFILE, index=False)
    print(f"Products raw: {raw_count}  -> prepared: {cleaned_count}")
    print(f"Wrote: {OUTFILE.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
