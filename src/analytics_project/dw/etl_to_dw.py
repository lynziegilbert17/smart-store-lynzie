from __future__ import annotations

import csv
import sqlite3
from pathlib import Path

from analytics_project.utils_logger import logger

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

# This file is src/analytics_project/dw/etl_to_dw.py
# parents[3] -> project root
PROJECT_ROOT = Path(__file__).resolve().parents[3]

DATA_DIR = PROJECT_ROOT / "data"
PREPARED_DIR = DATA_DIR / "prepared"
DW_DIR = DATA_DIR / "dw"
DW_DIR.mkdir(parents=True, exist_ok=True)

DB_PATH = DW_DIR / "smart_store_dw.db"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _first_present(row: dict[str, str], keys: list[str]) -> str | None:
    """Return the first non-empty value for any of the given keys in the row."""
    for key in keys:
        if key in row:
            value = row[key]
            if value is not None and str(value).strip() != "":
                return value
    return None


def _to_int(value: str | None) -> int | None:
    if value is None or str(value).strip() == "":
        return None
    return int(float(value))


def _to_float(value: str | None) -> float | None:
    if value is None or str(value).strip() == "":
        return None
    return float(value)


def get_connection() -> sqlite3.Connection:
    """Create a connection to the DW database."""
    logger.info(f"Connecting to DW at {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    return conn


# ---------------------------------------------------------------------------
# Schema creation
# ---------------------------------------------------------------------------


def create_tables(cursor: sqlite3.Cursor) -> None:
    """Create dimension and fact tables if they do not already exist."""

    # Customers dimension
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS customer (
            customer_id INTEGER PRIMARY KEY,
            name        TEXT,
            region      TEXT,
            join_date   TEXT
        );
        """
    )

    # Products dimension
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS product (
            product_id   INTEGER PRIMARY KEY,
            product_name TEXT,
            category     TEXT,
            unit_price   REAL,
            stock_qty    INTEGER,
            supplier     TEXT
        );
        """
    )

    # Sales fact
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS sale (
            sale_id      INTEGER PRIMARY KEY,
            customer_id  INTEGER,
            product_id   INTEGER,
            store_id     INTEGER,
            campaign_id  INTEGER,
            sale_amount  REAL,
            discount_pct REAL,
            payment_type TEXT,
            sale_date    TEXT,
            FOREIGN KEY (customer_id) REFERENCES customer (customer_id),
            FOREIGN KEY (product_id) REFERENCES product (product_id)
        );
        """
    )


# ---------------------------------------------------------------------------
# Load dimension tables
# ---------------------------------------------------------------------------


def load_customers(cursor: sqlite3.Cursor) -> None:
    """Load customers from prepared CSV into customer dimension."""
    path = PREPARED_DIR / "customers_data_prepared.csv"
    logger.info(f"Loading customers from {path}")

    rows: list[tuple] = []

    with path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        for row in reader:
            customer_id = _to_int(
                _first_present(
                    row,
                    ["CustomerID", "customer_id", "Customer ID"],
                )
            )

            name = _first_present(
                row,
                ["Name", "name", "Customer Name"],
            )

            region = _first_present(
                row,
                ["Region", "region"],
            )

            join_date = _first_present(
                row,
                ["JoinDate", "join_date", "Join Date"],
            )

            if customer_id is None:
                # skip bad rows
                continue

            rows.append((customer_id, name, region, join_date))

    cursor.execute("DELETE FROM customer")
    if rows:
        cursor.executemany(
            """
            INSERT INTO customer (customer_id, name, region, join_date)
            VALUES (?, ?, ?, ?)
            """,
            rows,
        )

    logger.info(f"Loaded {len(rows)} customers into DW.")


def load_products(cursor: sqlite3.Cursor) -> None:
    """Load products from prepared CSV into product dimension."""
    path = PREPARED_DIR / "products_data_prepared.csv"
    logger.info(f"Loading products from {path}")

    rows: list[tuple] = []

    with path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        for row in reader:
            product_id = _to_int(
                _first_present(
                    row,
                    ["ProductID", "product_id", "Product ID"],
                )
            )

            product_name = _first_present(
                row,
                ["ProductName", "product_name"],
            )

            category = _first_present(
                row,
                ["Category", "category"],
            )

            unit_price = _to_float(
                _first_present(
                    row,
                    ["UnitPrice", "unit_price"],
                )
            )

            stock_qty = _to_int(
                _first_present(
                    row,
                    ["StockQtyUnits", "stock_qty", "StockQty"],
                )
            )

            supplier = _first_present(
                row,
                ["Supplier", "supplier"],
            )

            if product_id is None:
                continue

            rows.append((product_id, product_name, category, unit_price, stock_qty, supplier))

    cursor.execute("DELETE FROM product")
    if rows:
        cursor.executemany(
            """
            INSERT INTO product (
                product_id,
                product_name,
                category,
                unit_price,
                stock_qty,
                supplier
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            rows,
        )

    logger.info(f"Loaded {len(rows)} products into DW.")


# ---------------------------------------------------------------------------
# Load fact table
# ---------------------------------------------------------------------------


def load_sales(cursor: sqlite3.Cursor) -> None:
    """Load sales from prepared CSV into sales fact table."""
    path = PREPARED_DIR / "sales_data_prepared.csv"
    logger.info(f"Loading sales from {path}")

    rows: list[tuple] = []

    with path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        for row in reader:
            sale_id = _to_int(
                _first_present(
                    row,
                    ["TransactionID", "transaction_id", "SaleID"],
                )
            )

            sale_date = _first_present(
                row,
                ["SaleDate", "sale_date"],
            )

            customer_id = _to_int(
                _first_present(
                    row,
                    ["CustomerID", "customer_id"],
                )
            )

            product_id = _to_int(
                _first_present(
                    row,
                    ["ProductID", "product_id"],
                )
            )

            store_id = _to_int(
                _first_present(
                    row,
                    ["StoreID", "store_id"],
                )
            )

            campaign_id = _to_int(
                _first_present(
                    row,
                    ["CampaignID", "campaign_id"],
                )
            )

            sale_amount = _to_float(
                _first_present(
                    row,
                    ["SaleAmount", "sale_amount"],
                )
            )

            discount_pct = _to_float(
                _first_present(
                    row,
                    ["DiscountPct", "discount_pct"],
                )
            )

            payment_type = _first_present(
                row,
                ["PaymentType", "payment_type"],
            )

            if sale_id is None:
                continue

            rows.append(
                (
                    sale_id,
                    customer_id,
                    product_id,
                    store_id,
                    campaign_id,
                    sale_amount,
                    discount_pct,
                    payment_type,
                    sale_date,
                )
            )

    cursor.execute("DELETE FROM sale")
    if rows:
        cursor.executemany(
            """
            INSERT INTO sale (
                sale_id,
                customer_id,
                product_id,
                store_id,
                campaign_id,
                sale_amount,
                discount_pct,
                payment_type,
                sale_date
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            rows,
        )

    logger.info(f"Loaded {len(rows)} sales into DW.")


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------


def create_dw() -> None:
    """Create the DW schema and load data."""
    conn: sqlite3.Connection | None = None

    try:
        conn = get_connection()
        cur = conn.cursor()

        create_tables(cur)
        load_customers(cur)
        load_products(cur)
        load_sales(cur)

        conn.commit()
        logger.info("DW schema created and data loaded successfully.")
    except sqlite3.Error as e:
        logger.error(f"SQLite error while creating/loading DW: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error while creating/loading DW: {e}")
        raise
    finally:
        if conn is not None:
            conn.close()
            logger.info("DW connection closed.")


def main() -> None:
    create_dw()


if __name__ == "__main__":
    main()
