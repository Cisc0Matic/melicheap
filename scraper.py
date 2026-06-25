import asyncio
import re
from datetime import datetime
from database import get_session, Category, Product, PriceHistory, product_categories
from ml_api import MLApiClient


def extract_product_id(permalink: str) -> str:
    m = re.search(r"/(ML[AU]?\d{6,12})", permalink)
    if m:
        return m.group(1)
    m = re.search(r"ML[AU]?[-]?(\d{6,12})", permalink)
    if m:
        return f"MLA{m.group(1)}"
    return permalink


async def refresh_all_categories() -> list[Category]:
    client = MLApiClient()
    try:
        api_categories = await client.get_categories()
        session = get_session()
        try:
            categories = []
            for cat_data in api_categories:
                cat = session.get(Category, cat_data["id"])
                if cat is None:
                    cat = Category(id=cat_data["id"], name=cat_data["name"])
                    session.add(cat)
                else:
                    cat.name = cat_data["name"]
                cat.updated_at = datetime.now()
                categories.append(cat)
            session.commit()
            return categories
        finally:
            session.close()
    finally:
        await client.close()


async def refresh_cheapest_for_category(category_id: str, category_name: str):
    client = MLApiClient()
    try:
        results, total = await client.search_cheapest(
            category_id, category_name, limit=50, offset=0
        )
        all_results = list(results)

        session = get_session()
        try:
            now = datetime.now()
            seen_ids = set()
            for item in all_results:
                permalink = item.get("permalink", "")
                product_id = extract_product_id(permalink)
                if product_id in seen_ids:
                    continue
                seen_ids.add(product_id)

                price = item.get("price", 0) or 0
                title = item.get("title", "")
                thumbnail = item.get("thumbnail", "")
                currency_id = item.get("currency_id", "ARS")

                if not title:
                    continue

                product = session.get(Product, product_id)
                if product is None:
                    product = Product(
                        id=product_id,
                        title=title,
                        price=price,
                        original_price=item.get("original_price"),
                        discount_percentage=item.get("discount_percentage"),
                        free_shipping=item.get("free_shipping"),
                        condition=item.get("condition"),
                        installments=item.get("installments"),
                        currency_id=currency_id,
                        permalink=permalink,
                        thumbnail=thumbnail,
                        first_seen=now,
                        last_seen=now,
                    )
                    session.add(product)
                    session.flush()
                else:
                    product.title = title
                    if product.price != price:
                        product.price = price
                    product.original_price = item.get("original_price", product.original_price)
                    product.discount_percentage = item.get("discount_percentage", product.discount_percentage)
                    product.free_shipping = item.get("free_shipping", product.free_shipping)
                    product.condition = item.get("condition", product.condition)
                    product.installments = item.get("installments", product.installments)
                    product.last_seen = now

                cat = session.get(Category, category_id)
                if cat and cat not in product.categories:
                    product.categories.append(cat)

                session.add(PriceHistory(
                    product_id=product_id, price=price, recorded_at=now
                ))

            session.commit()
        finally:
            session.close()
    finally:
        await client.close()


_refresh_progress = {"total": 0, "done": 0, "current": ""}


def get_refresh_progress() -> dict:
    return dict(_refresh_progress)


async def refresh_all():
    client = MLApiClient()
    try:
        api_categories = await client.get_categories()
    finally:
        await client.close()

    session = get_session()
    try:
        existing = {c.id: c.name for c in session.query(Category).all()}
        for cat_data in api_categories:
            cat_id, cat_name = cat_data["id"], cat_data["name"]
            if cat_id not in existing:
                cat = Category(id=cat_id, name=cat_name)
                session.add(cat)
            existing[cat_id] = cat_name
        session.commit()
    finally:
        session.close()

    _refresh_progress["total"] = len(api_categories)
    _refresh_progress["done"] = 0

    sem = asyncio.Semaphore(3)

    async def scrape_one(cat_data):
        async with sem:
            _refresh_progress["current"] = cat_data["name"]
            await refresh_cheapest_for_category(cat_data["id"], cat_data["name"])
            _refresh_progress["done"] += 1

    tasks = [scrape_one(c) for c in api_categories]
    await asyncio.gather(*tasks)
    _refresh_progress["current"] = ""
