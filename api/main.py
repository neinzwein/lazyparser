import json
from fastapi import FastAPI, HTTPException
from sqlalchemy.orm import Session
from db import Base, engine, SessionLocal
from models import ProductSnapshot
from schemas import ExtractRequest
from extractor import extract_product

app = FastAPI(title="Universal Product Extractor")

Base.metadata.create_all(bind=engine)

@app.get("/health")
def health():
    return {"ok": True}

@app.post("/extract")
async def extract(req: ExtractRequest):
    try:
        result = await extract_product(str(req.url))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    db: Session = SessionLocal()
    try:
        snapshot = ProductSnapshot(
            url=str(req.url),
            store_name=result.store_name,
            product_title=result.product_title,
            price_current=result.price_current,
            price_old=result.price_old,
            currency=result.currency,
            in_stock=result.in_stock,
            image_url=(result.image_urls[0] if result.image_urls else None),
            sku=result.sku,
            brand=result.brand,
            confidence=result.confidence,
            raw_json=json.dumps(result.model_dump(), ensure_ascii=False),
        )
        db.add(snapshot)
        db.commit()
        db.refresh(snapshot)
    finally:
        db.close()

    return {"id": snapshot.id, "data": result.model_dump()}