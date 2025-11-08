# src/analytics_project/data_preparation/prepare_sales_data.py
from __future__ import annotations

from pathlib import Path
import pandas as pd

from src.analytics_project.data_scrubber import DataScrubber, Range


RAWFILE = Path("data/raw/sales_data.csv")
OUTFILE = Path("data/prepared/sales_data_prepared.csv")


def main() -> None:
    # 1) Load raw
    raw = pd.read_csv(RAWFILE)

    # 2) Define category normalization + allow-list
    allowed_pay = {"Cash", "Card", "EBT", "GiftCard"}
    mappings = {
        "PaymentType": {
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
    }

    # 3) Clean with reusable scrubber
    scrub = DataScrubber(raw)
    cleaned = (
        scrub.trim_strings()
        .parse_dates(["SaleDate"], drop_bad=True)
        .coerce_numeric(["SaleAmount", "DiscountPct"], strip_commas=True)
        .drop_nonpositive(["SaleAmount"])  # remove <= 0
        .bound_range({"DiscountPct": Range(0, 100)})  # keep 0–100
        .normalize_categories(mappings)
        .isin_allowlist({"PaymentType": allowed_pay})
        .drop_duplicates(subset=["TransactionID"])
        .remove_outliers_iqr(["SaleAmount", "DiscountPct"])  # IQR filter
        .df
    )

    # 4) Save
    OUTFILE.parent.mkdir(parents=True, exist_ok=True)
    cleaned.to_csv(OUTFILE, index=False)

    # 5) Report
    print(f"Sales raw: {len(raw)}  -> prepared: {len(cleaned)}")
    print(f"Wrote: {OUTFILE.as_posix()}")


if __name__ == "__main__":
    main()
