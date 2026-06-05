# etl/pipeline.py
# ============================================================
# ETL Pipeline — Extract from CSV, Transform, Load to PostgreSQL.
# Run this after data_generator/generator.py to populate the DB.
# ============================================================

import os
import pandas as pd
from datetime import datetime

from config import logger, settings
from database.connection import get_session, create_all_tables
from database.models import Customer, Product, Sale, InventorySnapshot


# ── Extract ──────────────────────────────────────────────────

def extract(filename: str, data_dir: str = None) -> pd.DataFrame:
    """Load a CSV file from the data directory."""
    data_dir = data_dir or settings.data_output_dir
    path = os.path.join(data_dir, filename)

    if not os.path.exists(path):
        raise FileNotFoundError(f"Data file not found: {path}")

    df = pd.read_csv(path)
    logger.info(f"Extracted {len(df):,} rows from {filename}")
    return df


# ── Transform ─────────────────────────────────────────────────

def transform_customers(df: pd.DataFrame) -> pd.DataFrame:
    """Clean and type-cast customer data."""
    df = df.copy()
    df["registration_date"] = pd.to_datetime(df["registration_date"]).dt.date
    df["is_active"]         = df["is_active"].astype(bool)
    df["age"]               = df["age"].fillna(0).astype(int)
    df.dropna(subset=["customer_id", "email"], inplace=True)
    df.drop_duplicates(subset=["customer_id"], inplace=True)
    logger.info(f"Transformed customers: {len(df):,} valid rows")
    return df


def transform_products(df: pd.DataFrame) -> pd.DataFrame:
    """Clean and type-cast product data."""
    df = df.copy()
    df["cost_price"]    = pd.to_numeric(df["cost_price"],    errors="coerce").fillna(0)
    df["selling_price"] = pd.to_numeric(df["selling_price"], errors="coerce").fillna(0)
    df["margin_pct"]    = pd.to_numeric(df["margin_pct"],    errors="coerce").fillna(0)
    df["is_active"]     = df["is_active"].astype(bool)
    df.dropna(subset=["product_id"], inplace=True)
    df.drop_duplicates(subset=["product_id"], inplace=True)
    logger.info(f"Transformed products: {len(df):,} valid rows")
    return df


def transform_sales(df: pd.DataFrame) -> pd.DataFrame:
    """Clean and type-cast sales data."""
    df = df.copy()
    df["sale_date"] = pd.to_datetime(df["sale_date"]).dt.date
    df["revenue"]   = pd.to_numeric(df["revenue"],   errors="coerce").fillna(0)
    df["quantity"]  = pd.to_numeric(df["quantity"],  errors="coerce").fillna(1).astype(int)
    df["sale_year"] = df["sale_year"].astype(int)

    # Remove invalid rows
    df = df[df["revenue"] > 0]
    df.dropna(subset=["transaction_id", "customer_id", "product_id"], inplace=True)
    df.drop_duplicates(subset=["transaction_id"], inplace=True)
    logger.info(f"Transformed sales: {len(df):,} valid rows")
    return df


def transform_inventory(df: pd.DataFrame) -> pd.DataFrame:
    """Clean and type-cast inventory data."""
    df = df.copy()
    df["snapshot_date"] = pd.to_datetime(df["snapshot_date"]).dt.date
    df["stock_qty"]     = pd.to_numeric(df["stock_qty"], errors="coerce").fillna(0).astype(int)
    df["needs_reorder"] = df["needs_reorder"].astype(bool)
    df.drop_duplicates(subset=["snapshot_id"], inplace=True)
    logger.info(f"Transformed inventory: {len(df):,} valid rows")
    return df


# ── Load ──────────────────────────────────────────────────────

def _bulk_upsert(session, model, records: list, pk_field: str):
    """Insert records, skipping duplicates by primary key."""
    existing_ids = {r[0] for r in session.query(getattr(model, pk_field)).all()}
    new_records  = [r for r in records if r.get(pk_field) not in existing_ids]

    if new_records:
        session.bulk_insert_mappings(model, new_records)
        logger.info(f"Inserted {len(new_records):,} new {model.__tablename__} records.")
    else:
        logger.info(f"No new records to insert into {model.__tablename__}.")

    return len(new_records)


def load_customers(df: pd.DataFrame) -> int:
    with get_session() as session:
        return _bulk_upsert(session, Customer, df.to_dict("records"), "customer_id")


def load_products(df: pd.DataFrame) -> int:
    with get_session() as session:
        return _bulk_upsert(session, Product, df.to_dict("records"), "product_id")


def load_sales(df: pd.DataFrame) -> int:
    with get_session() as session:
        return _bulk_upsert(session, Sale, df.to_dict("records"), "transaction_id")


def load_inventory(df: pd.DataFrame) -> int:
    with get_session() as session:
        return _bulk_upsert(session, InventorySnapshot, df.to_dict("records"), "snapshot_id")


# ── Full pipeline ─────────────────────────────────────────────

def run_full_pipeline(data_dir: str = None):
    """
    Run the complete ETL pipeline:
      1. Create DB tables
      2. Extract CSVs
      3. Transform each dataset
      4. Load into PostgreSQL
    """
    data_dir = data_dir or settings.data_output_dir
    start    = datetime.now()

    logger.info("=" * 50)
    logger.info("ETL PIPELINE STARTED")
    logger.info("=" * 50)

    # Step 1: Ensure schema exists
    create_all_tables()

    # Step 2-4: ETL per dataset
    pipeline_steps = [
        ("customers.csv", transform_customers, load_customers),
        ("products.csv",  transform_products,  load_products),
        ("sales.csv",     transform_sales,     load_sales),
        ("inventory.csv", transform_inventory, load_inventory),
    ]

    total_inserted = 0
    for filename, transform_fn, load_fn in pipeline_steps:
        try:
            df  = extract(filename, data_dir)
            df  = transform_fn(df)
            n   = load_fn(df)
            total_inserted += n
        except FileNotFoundError as e:
            logger.warning(str(e))
        except Exception as e:
            logger.error(f"ETL failed for {filename}: {e}")
            raise

    elapsed = (datetime.now() - start).total_seconds()
    logger.success(f"ETL COMPLETE — {total_inserted:,} records loaded in {elapsed:.1f}s")
    logger.info("=" * 50)


if __name__ == "__main__":
    run_full_pipeline()
