from sqlalchemy import String, Numeric, Boolean, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func
from db import Base
from datetime import datetime

class ProductSnapshot(Base):
    __tablename__ = "product_snapshots"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    url: Mapped[str] = mapped_column(Text, index=True)
    store_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    product_title: Mapped[str | None] = mapped_column(Text, nullable=True)
    price_current: Mapped[float | None] = mapped_column(Numeric(12, 2), nullable=True)
    price_old: Mapped[float | None] = mapped_column(Numeric(12, 2), nullable=True)
    currency: Mapped[str | None] = mapped_column(String(16), nullable=True)
    in_stock: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    image_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    sku: Mapped[str | None] = mapped_column(String(128), nullable=True)
    brand: Mapped[str | None] = mapped_column(String(255), nullable=True)
    confidence: Mapped[float | None] = mapped_column(Numeric(4, 3), nullable=True)
    raw_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())