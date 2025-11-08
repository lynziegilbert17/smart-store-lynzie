# src/analytics_project/data_preparation/prepare_customers_data.py
from __future__ import annotations

from pathlib import Path
import pandas as pd

from src.analytics_project.data_scrubber import DataScrubber, Range

RAWFILE = Path("data/raw/customers_data.csv")
OUTFILE = Path("data/prepared/customers_data_prepared.csv")


def main() -> None:
    raw = pd.read_csv(RAWFILE)

    # Normalize contact method variants -> {Email, SMS, Phone}
    allowed_contact = {"Email", "SMS", "Phone"}
    contact_map = {
        "e-mail": "Email",
        "email": "Email",
        "Email ": "Email",
        "text": "SMS",
        "sms": "SMS",
        "phone": "Phone",
        "call": "Phone",
        "": pd.NA,
        "nan": pd.NA,
        "None": pd.NA,
    }

    scrub = DataScrubber(raw)
    cleaned = (
        scrub.trim_strings()
        .parse_dates(["JoinDate"], drop_bad=True)
        .coerce_numeric(["LoyaltyPointsQty"], strip_commas=True)
        .drop_nonpositive(["LoyaltyPointsQty"])  # must be > 0
        .normalize_categories({"ContactMethod": contact_map})
        .isin_allowlist({"ContactMethod": allowed_contact})
        .drop_duplicates(subset=["CustomerID"])
        .remove_outliers_iqr(["LoyaltyPointsQty"])  # clamp extreme fakes
        .df
    )

    OUTFILE.parent.mkdir(parents=True, exist_ok=True)
    cleaned.to_csv(OUTFILE, index=False)

    print(f"Customers raw: {len(raw)}  -> prepared: {len(cleaned)}")
    print(f"Wrote: {OUTFILE.as_posix()}")


if __name__ == "__main__":
    main()
