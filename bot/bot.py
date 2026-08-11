import os
import re
import httpx
import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message
from aiogram.filters import CommandStart
from aiogram.client.session import aiohttp
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
API_BASE_URL = os.getenv("API_BASE_URL", "http://api:8000")
TELEGRAM_PROXY = os.getenv("TELEGRAM_PROXY")

# Создаём Bot с прокси
if TELEGRAM_PROXY:
    session = aiohttp.AiohttpSession(proxy=TELEGRAM_PROXY)
    bot = Bot(token=TOKEN, session=session)
else:
    bot = Bot(token=TOKEN)

dp = Dispatcher()

URL_RE = re.compile(r"https?://\S+")

@dp.message(CommandStart())
async def start_handler(message: Message):
    await message.answer(
        "Привет! Отправь ссылку на товар (RU/EN сайт), и я вытащу карточку в структурированном виде."
    )

@dp.message(F.text)
async def parse_handler(message: Message):
    text = message.text.strip()
    m = URL_RE.search(text)
    if not m:
        await message.answer("Пришли корректную ссылку (http/https).")
        return

    url = m.group(0)
    await message.answer("Обрабатываю ссылку, подожди...")

    try:
        async with httpx.AsyncClient(timeout=180) as client:
            r = await client.post(f"{API_BASE_URL}/extract", json={"url": url})
            r.raise_for_status()
            data = r.json()["data"]

        resp = (
            f"✅ Готово\n"
            f"Магазин: {data.get('store_name')}\n"
            f"Товар: {data.get('product_title')}\n"
            f"Цена: {data.get('price_current')} {data.get('currency')}\n"
            f"Старая цена: {data.get('price_old')}\n"
            f"В наличии: {data.get('in_stock')}\n"
            f"Бренд: {data.get('brand')}\n"
            f"SKU: {data.get('sku')}\n"
            f"Confidence: {data.get('confidence')}\n"
        )
        await message.answer(resp)

        imgs = data.get("image_urls") or []
        if imgs:
            await message.answer(f"Фото: {imgs[0]}")

    except Exception as e:
        await message.answer(f"Ошибка обработки: {e}")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
