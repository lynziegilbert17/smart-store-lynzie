# src/analytics_project/data_scrubber.py
from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Iterable, Optional, Sequence, Tuple
import pandas as pd


@dataclass
class Range:
    """Inclusive numeric range."""

    lo: float
    hi: float


def iqr_bounds(s: pd.Series, k: float = 1.5) -> Tuple[float, float]:
    q1 = s.quantile(0.25)
    q3 = s.quantile(0.75)
    iqr = q3 - q1
    return (q1 - k * iqr, q3 + k * iqr)


class DataScrubber:
    """
    Reusable, chainable cleaner for pandas DataFrames.

    Usage (example):
        scrub = DataScrubber(df)
        df2 = (
            scrub.trim_strings()
                 .parse_dates(["SaleDate"])
                 .coerce_numeric(["SaleAmount", "DiscountPct"])
                 .drop_negatives(["SaleAmount"])
                 .bound_range({"DiscountPct": Range(0, 100)})
                 .normalize_categories({
                     "PaymentType": {"gift card":"GiftCard","Gift Card":"GiftCard",
                                     "card":"Card","debit":"Card","credit":"Card",
                                     "cash":"Cash","ebt":"EBT","":pd.NA,"nan":pd.NA,"None":pd.NA}
                 })
                 .isin_allowlist({"PaymentType": {"Cash","Card","EBT","GiftCard"}})
                 .drop_duplicates(subset=["TransactionID"])
                 .remove_outliers_iqr(["SaleAmount","DiscountPct"])
                 .df
        )
    """

    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()

    # ---------- TEXT ----------
    def trim_strings(self, columns: Optional[Sequence[str]] = None) -> "DataScrubber":
        cols = columns or self.df.select_dtypes(include="object").columns
        for c in cols:
            self.df[c] = self.df[c].astype(str).str.strip()
        return self

    # ---------- DATES ----------
    def parse_dates(
        self, columns: Sequence[str], drop_bad: bool = True, fmt: Optional[str] = None
    ) -> "DataScrubber":
        for c in columns:
            self.df[c] = pd.to_datetime(self.df[c], errors="coerce", format=fmt)
        if drop_bad:
            self.df = self.df.dropna(subset=list(columns))
        return self

    # ---------- NUMERIC ----------
    def coerce_numeric(self, columns: Sequence[str], strip_commas: bool = True) -> "DataScrubber":
        for c in columns:
            s = self.df[c].astype(str)
            if strip_commas:
                s = s.str.replace(",", "", regex=False)
            self.df[c] = pd.to_numeric(s, errors="coerce")
        return self

    def drop_negatives(self, columns: Sequence[str]) -> "DataScrubber":
        for c in columns:
            self.df = self.df[self.df[c].ge(0)]
        return self

    def bound_range(self, ranges: Dict[str, Range], inclusive: str = "both") -> "DataScrubber":
        for c, r in ranges.items():
            self.df = self.df[self.df[c].between(r.lo, r.hi, inclusive=inclusive)]
        return self

    def remove_outliers_iqr(self, columns: Sequence[str], k: float = 1.5) -> "DataScrubber":
        for c in columns:
            lo, hi = iqr_bounds(self.df[c].dropna(), k)
            self.df = self.df[self.df[c].between(lo, hi)]
        return self

    def drop_nonpositive(self, columns: Sequence[str]) -> "DataScrubber":
        for c in columns:
            self.df = self.df[self.df[c].gt(0)]
        return self

    # ---------- CATEGORIES ----------
    def normalize_categories(self, mappings: Dict[str, Dict[object, object]]) -> "DataScrubber":
        for c, repl in mappings.items():
            self.df[c] = self.df[c].replace(repl)
        return self

    def isin_allowlist(self, allows: Dict[str, Iterable[object]]) -> "DataScrubber":
        for c, allowed in allows.items():
            self.df = self.df[self.df[c].isin(set(allowed))]
        return self

    # ---------- DEDUP ----------
    def drop_duplicates(
        self, subset: Optional[Sequence[str]] = None, keep: str = "first"
    ) -> "DataScrubber":
        self.df = self.df.drop_duplicates(subset=subset, keep=keep)
        return self
