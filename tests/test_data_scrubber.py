import pandas as pd
from src.analytics_project.data_scrubber import DataScrubber, Range

def test_data_scrubber_basic_sales_flow():
    # 5 rows with several issues; we expect only 2 to survive cleaning
    df = pd.DataFrame({
        "TransactionID": [1, 1, 2, 3, 4],       # duplicate ID at first two rows
        "SaleDate": ["2024-01-01", "bad", "2024-03-15", "2024-04-01", "2024-05-01"],
        "SaleAmount": ["1,000", "-50", "200", "0", "300"],  # comma, negative, zero
        "DiscountPct": ["10", "150", "-5", "5", " 20 "],    # out-of-range, whitespace
        "PaymentType": [" card ", "gift card", "", "Cash", "EBT"]  # spacing, variant, blank
    })

    allowed_pay = {"Cash", "Card", "EBT", "GiftCard"}
    mappings = {
        "PaymentType": {
            "gift card": "GiftCard", "Gift Card": "GiftCard",
            "card": "Card", "debit": "Card", "credit": "Card",
            "cash": "Cash", "ebt": "EBT", "": pd.NA, "nan": pd.NA, "None": pd.NA, " card ": "Card"
        }
    }

    scrub = DataScrubber(df)
    out = (
        scrub
        .trim_strings()
        .parse_dates(["SaleDate"], drop_bad=True)
        .coerce_numeric(["SaleAmount", "DiscountPct"], strip_commas=True)
        .drop_nonpositive(["SaleAmount"])
        .bound_range({"DiscountPct": Range(0, 100)})
        .normalize_categories(mappings)
        .isin_allowlist({"PaymentType": allowed_pay})
        .drop_duplicates(subset=["TransactionID"])
        .df
    )

    # After cleaning:
    # - Row 2 dropped (bad date)
    # - Row 1 duplicate of row 0 dropped by TransactionID dedupe
    # - Negative/zero SaleAmount rows dropped
    # - DiscountPct out-of-range rows dropped
    # - Blank/invalid PaymentType rows dropped
    # Expect remaining TransactionIDs: {2,4}
    assert set(out["TransactionID"]) == {1, 4}
    assert len(out) == 2
    assert out["PaymentType"].isin(allowed_pay).all()
    assert out["DiscountPct"].between(0, 100, inclusive="both").all()
