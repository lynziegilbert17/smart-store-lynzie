# src/analytics_project/data_preparation/prepare_products_data.py
from pathlib import Path
import pandas as pd

RAWFILE = Path("data/raw/products_data.csv")
OUTFILE = Path("data/prepared/products_data_prepared.csv")


def main() -> None:
    raw = pd.read_csv(RAWFILE)
    print(f"[0] start rows: {len(raw)}")
    df = raw.copy()

    # --- Fix comma decimals then to numeric ---
    s = df["UnitPrice"].astype(str)
    needs_dot = ~s.str.contains(r"\.")
    s.loc[needs_dot] = s.loc[needs_dot].str.replace(",", ".", regex=False)
    # also handle stray spaces/commas everywhere
    s = s.str.replace(",", ".", regex=False).str.strip()
    df["UnitPrice"] = pd.to_numeric(s, errors="coerce")
    print(f"[1] after UnitPrice to numeric (non-null): {df['UnitPrice'].notna().sum()}")

    # Stock to numeric
    df["StockQtyUnits"] = pd.to_numeric(df["StockQtyUnits"], errors="coerce")
    print(f"[2] after StockQtyUnits numeric (non-null): {df['StockQtyUnits'].notna().sum()}")

    # --- Gentle filters ---
    before = len(df)
    df = df[df["UnitPrice"] > 0]
    print(f"[3] drop nonpositive UnitPrice: {before} -> {len(df)}")

    before = len(df)
    df = df[df["StockQtyUnits"] >= 0]
    print(f"[4] drop negative stock: {before} -> {len(df)}")

    before = len(df)
    df = df.drop_duplicates(subset=["ProductID"])
    print(f"[5] drop dup ProductID: {before} -> {len(df)}")

    # --- Normalize Supplier names (no filtering) ---
    supplier_map = {
        "Acme": "Acme",
        "Globex": "Globex",
        "InHouse": "InHouse",
        "acme": "Acme",
        "ACME": "Acme",
        "globex": "Globex",
        "GLOBEX": "Globex",
        "inhouse": "InHouse",
        "Inhouse": "InHouse",
        "in house": "InHouse",
        "In house": "InHouse",
    }
    sup = df["Supplier"].astype(str).str.strip()
    df["Supplier"] = sup.map(supplier_map).fillna(sup)
    print(f"[6] suppliers (sample): {df['Supplier'].head().tolist()}")

    # --- Save & report ---
    OUTFILE.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTFILE, index=False)
    print(f"Products raw: {len(raw)}  -> prepared: {len(df)}")
    print(f"Wrote: {OUTFILE.as_posix()}")


if __name__ == "__main__":
    main()
