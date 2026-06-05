# data_generator/generator.py
# ============================================================
# Generates realistic business data using Faker.
# Produces: customers, products, sales transactions,
#           inventory records, and marketing campaigns.
# ============================================================

import random
import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Any

import pandas as pd
from faker import Faker

from config import logger

fake = Faker("en_IN")  # Indian locale for region-appropriate data
random.seed(42)

# ── Constants ────────────────────────────────────────────────

REGIONS = ["Chennai", "Mumbai", "Delhi", "Bangalore", "Hyderabad",
           "Pune", "Kolkata", "Ahmedabad", "Jaipur", "Kochi"]

CATEGORIES = {
    "Electronics":   ["Laptop", "Smartphone", "Tablet", "Headphones", "Smart Watch",
                      "Webcam", "SSD Drive", "Monitor", "Keyboard", "Mouse"],
    "Clothing":      ["T-Shirt", "Jeans", "Jacket", "Saree", "Kurta",
                      "Sneakers", "Formal Shirt", "Leggings", "Blazer", "Shorts"],
    "Home & Kitchen":["Air Purifier", "Mixer Grinder", "Pressure Cooker", "Bedsheet",
                      "Pillow Set", "Table Lamp", "Wall Clock", "Cookware Set",
                      "Water Filter", "Induction Cooktop"],
    "Books":         ["Fiction Novel", "Self-Help Book", "Textbook", "Comics",
                      "Biography", "Cookbook", "Travel Guide", "Business Book",
                      "Science Book", "Children's Story"],
    "Sports":        ["Yoga Mat", "Dumbbells", "Cricket Bat", "Football",
                      "Badminton Set", "Cycling Gloves", "Running Shoes",
                      "Resistance Band", "Skipping Rope", "Water Bottle"],
}

PRICE_RANGES = {
    "Electronics":    (500,  80000),
    "Clothing":       (200,   5000),
    "Home & Kitchen": (300,  15000),
    "Books":          (100,   2000),
    "Sports":         (150,   8000),
}

PAYMENT_METHODS = ["Credit Card", "Debit Card", "UPI", "Net Banking",
                   "Cash on Delivery", "EMI"]

CHANNELS = ["Online", "In-Store", "Mobile App", "Phone Order"]

STATUSES = ["Completed", "Completed", "Completed",   # 3× weight for completed
            "Returned", "Cancelled", "Pending"]


# ── Generator functions ──────────────────────────────────────

def generate_customers(n: int = 500) -> pd.DataFrame:
    """Generate synthetic customer records."""
    logger.info(f"Generating {n} customer records...")

    customers = []
    for _ in range(n):
        reg_date = fake.date_between(start_date="-3y", end_date="today")
        customers.append({
            "customer_id":    str(uuid.uuid4())[:8].upper(),
            "name":           fake.name(),
            "email":          fake.email(),
            "phone":          fake.phone_number(),
            "city":           random.choice(REGIONS),
            "state":          fake.state(),
            "age":            random.randint(18, 70),
            "gender":         random.choice(["Male", "Female", "Other"]),
            "segment":        random.choice(["Premium", "Regular", "New"]),
            "registration_date": reg_date,
            "is_active":      random.random() > 0.1,
        })

    df = pd.DataFrame(customers)
    logger.success(f"Generated {len(df)} customers.")
    return df


def generate_products(n: int = 100) -> pd.DataFrame:
    """Generate synthetic product catalogue."""
    logger.info(f"Generating {n} product records...")

    products = []
    for _ in range(n):
        category = random.choice(list(CATEGORIES.keys()))
        name      = random.choice(CATEGORIES[category])
        low, high = PRICE_RANGES[category]
        cost      = round(random.uniform(low * 0.4, high * 0.6), 2)
        price     = round(cost * random.uniform(1.3, 2.5), 2)

        products.append({
            "product_id":   str(uuid.uuid4())[:8].upper(),
            "name":         name,
            "category":     category,
            "brand":        fake.company().split()[0],
            "cost_price":   cost,
            "selling_price": price,
            "margin_pct":   round((price - cost) / price * 100, 2),
            "stock_qty":    random.randint(0, 500),
            "reorder_level": random.randint(10, 50),
            "is_active":    random.random() > 0.05,
        })

    df = pd.DataFrame(products)
    logger.success(f"Generated {len(df)} products.")
    return df


def generate_sales(
    customers: pd.DataFrame,
    products: pd.DataFrame,
    n: int = 5000,
    start_date: str = "2023-01-01",
    end_date: str = "2024-12-31",
) -> pd.DataFrame:
    """Generate synthetic sales transactions."""
    logger.info(f"Generating {n} sales transactions...")

    start = datetime.strptime(start_date, "%Y-%m-%d")
    end   = datetime.strptime(end_date,   "%Y-%m-%d")
    delta = (end - start).days

    customer_ids = customers["customer_id"].tolist()
    customer_cities = dict(zip(customers["customer_id"], customers["city"]))
    product_ids   = products["product_id"].tolist()
    product_prices = dict(zip(products["product_id"], products["selling_price"]))
    product_cats   = dict(zip(products["product_id"], products["category"]))

    sales = []
    for _ in range(n):
        cust_id = random.choice(customer_ids)
        prod_id = random.choice(product_ids)
        qty     = random.randint(1, 5)
        price   = product_prices[prod_id]
        discount = round(random.uniform(0, 0.25), 2)  # 0–25% discount
        revenue  = round(price * qty * (1 - discount), 2)
        sale_date = start + timedelta(days=random.randint(0, delta))

        sales.append({
            "transaction_id": str(uuid.uuid4())[:12].upper(),
            "customer_id":    cust_id,
            "product_id":     prod_id,
            "category":       product_cats[prod_id],
            "region":         customer_cities.get(cust_id, random.choice(REGIONS)),
            "quantity":       qty,
            "unit_price":     price,
            "discount_pct":   discount,
            "revenue":        revenue,
            "payment_method": random.choice(PAYMENT_METHODS),
            "channel":        random.choice(CHANNELS),
            "status":         random.choice(STATUSES),
            "sale_date":      sale_date.strftime("%Y-%m-%d"),
            "sale_month":     sale_date.strftime("%Y-%m"),
            "sale_year":      sale_date.year,
            "sale_quarter":   f"Q{(sale_date.month - 1) // 3 + 1}",
        })

    df = pd.DataFrame(sales)
    logger.success(f"Generated {len(df)} sales transactions.")
    return df


def generate_inventory_snapshots(products: pd.DataFrame, n_days: int = 30) -> pd.DataFrame:
    """Generate daily inventory snapshots for the last n_days."""
    logger.info(f"Generating inventory snapshots for {n_days} days...")

    snapshots = []
    today = datetime.today()
    for day_offset in range(n_days):
        snap_date = (today - timedelta(days=day_offset)).strftime("%Y-%m-%d")
        for _, prod in products.iterrows():
            change = random.randint(-20, 30)
            new_stock = max(0, int(prod["stock_qty"]) + change)
            snapshots.append({
                "snapshot_id": str(uuid.uuid4())[:8].upper(),
                "product_id":  prod["product_id"],
                "product_name": prod["name"],
                "category":    prod["category"],
                "stock_qty":   new_stock,
                "reorder_level": prod["reorder_level"],
                "needs_reorder": new_stock < prod["reorder_level"],
                "snapshot_date": snap_date,
            })

    df = pd.DataFrame(snapshots)
    logger.success(f"Generated {len(df)} inventory snapshots.")
    return df


# ── Main entry point ─────────────────────────────────────────

def generate_all_data(output_dir: str = "./data/raw") -> Dict[str, pd.DataFrame]:
    """Generate the full dataset suite and save to CSV."""
    import os
    os.makedirs(output_dir, exist_ok=True)

    logger.info("=== Starting full data generation ===")

    customers = generate_customers(500)
    products  = generate_products(100)
    sales     = generate_sales(customers, products, 5000)
    inventory = generate_inventory_snapshots(products, 30)

    datasets = {
        "customers": customers,
        "products":  products,
        "sales":     sales,
        "inventory": inventory,
    }

    for name, df in datasets.items():
        path = os.path.join(output_dir, f"{name}.csv")
        df.to_csv(path, index=False)
        logger.info(f"Saved {name}.csv — {len(df):,} rows → {path}")

    logger.success("=== Data generation complete ===")
    return datasets


if __name__ == "__main__":
    generate_all_data()
