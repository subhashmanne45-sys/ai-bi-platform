# database/models.py
# ============================================================
# SQLAlchemy ORM models — defines the PostgreSQL schema.
# Tables: customers, products, sales, inventory_snapshots,
#         ai_query_logs, generated_reports
# ============================================================

from datetime import datetime
from sqlalchemy import (
    Column, String, Integer, Float, Boolean,
    DateTime, Date, Text, ForeignKey, Index
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Customer(Base):
    __tablename__ = "customers"

    customer_id       = Column(String(8),  primary_key=True)
    name              = Column(String(120), nullable=False)
    email             = Column(String(120), unique=True)
    phone             = Column(String(20))
    city              = Column(String(60))
    state             = Column(String(60))
    age               = Column(Integer)
    gender            = Column(String(10))
    segment           = Column(String(20))   # Premium / Regular / New
    registration_date = Column(Date)
    is_active         = Column(Boolean, default=True)
    created_at        = Column(DateTime, default=datetime.utcnow)

    sales = relationship("Sale", back_populates="customer")

    __table_args__ = (
        Index("idx_customers_city",    "city"),
        Index("idx_customers_segment", "segment"),
    )

    def __repr__(self):
        return f"<Customer {self.customer_id} — {self.name}>"


class Product(Base):
    __tablename__ = "products"

    product_id    = Column(String(8),   primary_key=True)
    name          = Column(String(120), nullable=False)
    category      = Column(String(60),  nullable=False)
    brand         = Column(String(60))
    cost_price    = Column(Float,       nullable=False)
    selling_price = Column(Float,       nullable=False)
    margin_pct    = Column(Float)
    stock_qty     = Column(Integer,     default=0)
    reorder_level = Column(Integer,     default=20)
    is_active     = Column(Boolean,     default=True)
    created_at    = Column(DateTime,    default=datetime.utcnow)

    sales      = relationship("Sale",              back_populates="product")
    inventory  = relationship("InventorySnapshot", back_populates="product")

    __table_args__ = (
        Index("idx_products_category", "category"),
    )

    def __repr__(self):
        return f"<Product {self.product_id} — {self.name}>"


class Sale(Base):
    __tablename__ = "sales"

    transaction_id = Column(String(12),  primary_key=True)
    customer_id    = Column(String(8),   ForeignKey("customers.customer_id"))
    product_id     = Column(String(8),   ForeignKey("products.product_id"))
    category       = Column(String(60))
    region         = Column(String(60))
    quantity       = Column(Integer,     nullable=False)
    unit_price     = Column(Float,       nullable=False)
    discount_pct   = Column(Float,       default=0.0)
    revenue        = Column(Float,       nullable=False)
    payment_method = Column(String(30))
    channel        = Column(String(20))
    status         = Column(String(20))  # Completed / Returned / Cancelled
    sale_date      = Column(Date,        nullable=False)
    sale_month     = Column(String(7))   # e.g. "2024-03"
    sale_year      = Column(Integer)
    sale_quarter   = Column(String(2))   # Q1 / Q2 / Q3 / Q4
    created_at     = Column(DateTime,    default=datetime.utcnow)

    customer = relationship("Customer", back_populates="sales")
    product  = relationship("Product",  back_populates="sales")

    __table_args__ = (
        Index("idx_sales_date",     "sale_date"),
        Index("idx_sales_region",   "region"),
        Index("idx_sales_category", "category"),
        Index("idx_sales_month",    "sale_month"),
        Index("idx_sales_status",   "status"),
    )

    def __repr__(self):
        return f"<Sale {self.transaction_id} ₹{self.revenue}>"


class InventorySnapshot(Base):
    __tablename__ = "inventory_snapshots"

    snapshot_id   = Column(String(8),  primary_key=True)
    product_id    = Column(String(8),  ForeignKey("products.product_id"))
    product_name  = Column(String(120))
    category      = Column(String(60))
    stock_qty     = Column(Integer,    nullable=False)
    reorder_level = Column(Integer)
    needs_reorder = Column(Boolean,    default=False)
    snapshot_date = Column(Date,       nullable=False)
    created_at    = Column(DateTime,   default=datetime.utcnow)

    product = relationship("Product", back_populates="inventory")

    __table_args__ = (
        Index("idx_inventory_date",    "snapshot_date"),
        Index("idx_inventory_product", "product_id"),
    )


class AIQueryLog(Base):
    """Logs every natural language query and the SQL generated."""
    __tablename__ = "ai_query_logs"

    id            = Column(Integer,  primary_key=True, autoincrement=True)
    question      = Column(Text,     nullable=False)
    generated_sql = Column(Text)
    result_rows   = Column(Integer)
    ai_explanation = Column(Text)
    execution_ms  = Column(Float)
    success       = Column(Boolean,  default=True)
    error_message = Column(Text)
    created_at    = Column(DateTime, default=datetime.utcnow)


class GeneratedReport(Base):
    """Stores AI-generated business reports."""
    __tablename__ = "generated_reports"

    id           = Column(Integer,  primary_key=True, autoincrement=True)
    report_type  = Column(String(60))    # daily / weekly / anomaly / custom
    title        = Column(String(200))
    content      = Column(Text)
    insights     = Column(Text)          # JSON string of key insights
    generated_by = Column(String(60))   # agent name
    period_start = Column(Date)
    period_end   = Column(Date)
    created_at   = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index("idx_reports_type", "report_type"),
        Index("idx_reports_date", "created_at"),
    )
