from pydantic import BaseModel, HttpUrl, Field
from typing import Optional, List

class ExtractRequest(BaseModel):
    url: HttpUrl

class ProductData(BaseModel):
    store_name: Optional[str] = None
    product_title: Optional[str] = None
    price_current: Optional[float] = None
    price_old: Optional[float] = None
    currency: Optional[str] = None
    in_stock: Optional[bool] = None
    image_urls: List[str] = Field(default_factory=list)
    sku: Optional[str] = None
    brand: Optional[str] = None
    confidence: Optional[float] = None