import os
from datetime import datetime, timezone
from sqlalchemy import create_engine, Column, String, Float, DateTime, Integer, ForeignKey, Table
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from config import DB_PATH

DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DB_PATH}")

if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
else:
    engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

product_categories = Table(
    "product_categories", Base.metadata,
    Column("product_id", String, ForeignKey("products.id"), primary_key=True),
    Column("category_id", String, ForeignKey("categories.id"), primary_key=True),
)


class Category(Base):
    __tablename__ = "categories"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    products = relationship("Product", secondary=product_categories, back_populates="categories",
                            lazy="selectin", order_by="Product.price.asc()")


class Product(Base):
    __tablename__ = "products"

    id = Column(String, primary_key=True)
    title = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    original_price = Column(Float, nullable=True)
    discount_percentage = Column(Integer, nullable=True)
    free_shipping = Column(Integer, nullable=True)
    condition = Column(String, nullable=True)
    installments = Column(String, nullable=True)
    currency_id = Column(String, default="ARS")
    permalink = Column(String)
    thumbnail = Column(String)
    first_seen = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    last_seen = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    categories = relationship("Category", secondary=product_categories, back_populates="products",
                              lazy="selectin")
    price_history = relationship("PriceHistory", back_populates="product", lazy="selectin",
                                 order_by="PriceHistory.recorded_at.desc()")


class PriceHistory(Base):
    __tablename__ = "price_history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(String, ForeignKey("products.id"), nullable=False)
    price = Column(Float, nullable=False)
    recorded_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    product = relationship("Product", back_populates="price_history")


def init_db():
    Base.metadata.create_all(engine)


def get_session():
    return SessionLocal()
