# src/analytics_project/data_prep.py
from pathlib import Path
import logging
import pandas as pd

# repo root (two levels up from this file)
ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw"

FILES = {
    "customers": "customers_data.csv",
    "products": "products_data.csv",
    "sales": "sales_data.csv",
}


def setup_logging():
    log_file = ROOT / "project.log"
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
        filename=str(log_file),
        filemode="a",
    )
    return log_file


def load_raw_to_dfs():
    dfs = {}
    for name, fname in FILES.items():
        path = RAW / fname
        df = pd.read_csv(path)
        dfs[name] = df
        logging.info("Loaded %s from %s with shape %s", name, path.name, df.shape)
    return dfs


def main():
    setup_logging()
    logging.info("=== data_prep start ===")
    dfs = load_raw_to_dfs()
    for k, v in dfs.items():
        print(f"{k}: {v.shape}")
    logging.info("=== data_prep done ===")


if __name__ == "__main__":
    main()
