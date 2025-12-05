import pandas as pd


def main():
    # 1. Load prepared sales data
    df = pd.read_csv("data/prepared/sales_data_prepared.csv")

    # 2. Create fake dates spread across the year for nicer charts
    #    (hypothetical Blossoms & Bees seasonality)
    fake_dates = pd.date_range(start="2024-01-01", periods=len(df), freq="7D")
    df["YearMonth"] = fake_dates.to_period("M").astype(str)

    # 3. Group by product and store (treat these as product + sales channel)
    summary = (
        df.groupby(["ProductID", "StoreID", "YearMonth"])
        .agg(
            total_revenue=("SaleAmount", "sum"),
            transaction_count=("TransactionID", "count"),
        )
        .reset_index()
    )

    # 4. Save result for Power BI
    summary.to_csv("data/analysis/blossoms_bees_summary.csv", index=False)
    print("Wrote data/analysis/blossoms_bees_summary.csv")


if __name__ == "__main__":
    main()
