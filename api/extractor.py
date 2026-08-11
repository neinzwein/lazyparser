import os
import re
import json
import httpx
from urllib.parse import urlparse
from schemas import ProductData

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://ollama:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:3b")

def clean_text(html: str) -> str:
    text = re.sub(r"<script.*?>.*?</script>", " ", html, flags=re.S | re.I)
    text = re.sub(r"<style.*?>.*?</style>", " ", text, flags=re.S | re.I)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text[:30000]

async def fetch_rendered_html(url: str) -> str:
    async with httpx.AsyncClient() as client:
        r = await client.get(url, timeout=30)
        return r.text

def build_prompt(url: str, domain: str, text: str) -> str:
    return f"""You are a product data extractor for e-commerce pages.
Return ONLY valid JSON. No markdown, no comments.

Schema:
{{
  "store_name": "string or null",
  "product_title": "string or null",
  "price_current": "number or null",
  "price_old": "number or null",
  "currency": "string or null",
  "in_stock": "true|false|null",
  "brand": "string or null",
  "sku": "string or null",
  "image_urls": ["url1", "url2"],
  "specs": {{
    "spec_name": "value"
  }},
  "confidence": "0..1"
}}

Extract:
- product_title: Full product name
- price_current: Current price (number only)
- price_old: Old/original price if exists
- currency: Currency code
- brand: Brand/manufacturer
- sku: Product code/SKU/article
- specs: ONLY important specs that define the product:
  * For appliances: power, dimensions, capacity, type
  * For plants: type, size, purpose
  * For food: weight, origin, brand, type
  * Ignore: reviews, shipping info, store info

Rules:
- Extract only from text, don't invent
- OMIT any field if value is null/missing (don't include it)
- specs keys should be in Russian if Russian text, English if English
- confidence = your certainty 0-1
- Don't write schemas with value "None or null" just skip them
- If you are unsure which schema it belongs to, do not follow them strictly; instead, label it in a way that best reflects the essence of the matter and aligns with them.

URL: {url}
Page text:
{text}
"""

async def call_ollama(prompt: str) -> dict:
    async with httpx.AsyncClient(timeout=120) as client:
        r = await client.post(
            f"{OLLAMA_URL}/api/generate",
            json={
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False
            },
        )
        r.raise_for_status()
        data = r.json()
        raw = data.get("response", "").strip()
        start = raw.find("{")
        end = raw.rfind("}")
        if start == -1 or end == -1:
            raise ValueError("LLM did not return JSON")
        return json.loads(raw[start:end+1])

async def extract_product(url: str) -> ProductData:
    domain = urlparse(url).netloc
    html = await fetch_rendered_html(url)
    text = clean_text(html)
    prompt = build_prompt(url, domain, text)
    parsed = await call_ollama(prompt)
    model = ProductData.model_validate(parsed)
    return model