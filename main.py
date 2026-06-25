import asyncio
import json
from contextlib import asynccontextmanager
from datetime import datetime, timezone

from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.requests import Request

from database import init_db, get_session, Category, Product, PriceHistory, product_categories
from scraper import refresh_all, refresh_all_categories, refresh_cheapest_for_category, get_refresh_progress



@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="Meli Cheap", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")


@app.get("/api/categories")
async def list_categories():
    session = get_session()
    try:
        from sqlalchemy import func
        counts = dict(
            session.query(product_categories.c.category_id, func.count(product_categories.c.product_id))
            .group_by(product_categories.c.category_id)
            .all()
        )
        cats = session.query(Category).order_by(Category.name).all()
        return [
            {
                "id": c.id,
                "name": c.name,
                "product_count": counts.get(c.id, 0),
                "updated_at": c.updated_at.isoformat() if c.updated_at else None,
            }
            for c in cats
        ]
    finally:
        session.close()


@app.get("/api/products")
async def get_products(
    category_id: str = Query(...),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
):
    session = get_session()
    try:
        total = (
            session.query(Product)
            .join(product_categories)
            .filter(product_categories.c.category_id == category_id)
            .count()
        )
        products = (
            session.query(Product)
            .join(product_categories)
            .filter(product_categories.c.category_id == category_id)
            .order_by(Product.price.asc())
            .offset((page - 1) * per_page)
            .limit(per_page)
            .all()
        )
        return {
            "products": [
                {
                    "id": p.id,
                    "title": p.title,
                    "price": p.price,
                    "original_price": p.original_price,
                    "discount_percentage": p.discount_percentage,
                    "free_shipping": p.free_shipping,
                    "condition": p.condition,
                    "installments": p.installments,
                    "currency_id": p.currency_id,
                    "permalink": p.permalink,
                    "thumbnail": p.thumbnail,
                    "first_seen": p.first_seen.isoformat() if p.first_seen else None,
                    "last_seen": p.last_seen.isoformat() if p.last_seen else None,
                }
                for p in products
            ],
            "total": total,
            "page": page,
            "per_page": per_page,
        }
    finally:
        session.close()


@app.get("/api/deals")
async def get_deals(page: int = Query(1, ge=1), per_page: int = Query(20, ge=1, le=100)):
    session = get_session()
    try:
        total = session.query(Product).filter(Product.discount_percentage.isnot(None)).count()
        products = (
            session.query(Product)
            .filter(Product.discount_percentage.isnot(None))
            .order_by(Product.discount_percentage.desc())
            .offset((page - 1) * per_page)
            .limit(per_page)
            .all()
        )
        return {
            "products": [
                {
                    "id": p.id, "title": p.title, "price": p.price,
                    "original_price": p.original_price,
                    "discount_percentage": p.discount_percentage,
                    "free_shipping": p.free_shipping, "condition": p.condition,
                    "installments": p.installments, "currency_id": p.currency_id,
                    "permalink": p.permalink, "thumbnail": p.thumbnail,
                    "first_seen": p.first_seen.isoformat() if p.first_seen else None,
                    "last_seen": p.last_seen.isoformat() if p.last_seen else None,
                }
                for p in products
            ],
            "total": total,
            "page": page,
            "per_page": per_page,
        }
    finally:
        session.close()


@app.get("/api/price-history")
async def get_price_history(product_id: str = Query(...)):
    session = get_session()
    try:
        records = (
            session.query(PriceHistory)
            .filter(PriceHistory.product_id == product_id)
            .order_by(PriceHistory.recorded_at.asc())
            .all()
        )
        return [
            {
                "price": r.price,
                "recorded_at": r.recorded_at.isoformat() if r.recorded_at else None,
            }
            for r in records
        ]
    finally:
        session.close()


@app.get("/api/refresh/progress")
async def refresh_progress():
    return get_refresh_progress()


@app.get("/api/refresh/progress/stream")
async def refresh_progress_stream():
    async def event_generator():
        last_done = -1
        while True:
            progress = get_refresh_progress()
            done = progress.get("done", 0)
            if done != last_done or done == 0:
                last_done = done
                yield f"data: {json.dumps(progress)}\n\n"
                if done >= progress.get("total", 0) and progress.get("total", 0) > 0:
                    break
            await asyncio.sleep(0.3)
    return StreamingResponse(event_generator(), media_type="text/event-stream")


@app.post("/api/refresh")
async def trigger_refresh():
    async def _task():
        await refresh_all()
    asyncio.create_task(_task())
    return {"status": "started"}


@app.post("/api/refresh/categories")
async def trigger_refresh_categories():
    cats = await refresh_all_categories()
    return {"status": "ok", "count": len(cats)}


@app.get("/api/ping")
async def ping():
    return {"ok": True}


@app.post("/api/refresh/category/{category_id}")
async def trigger_refresh_category(category_id: str):
    session = get_session()
    try:
        cat = session.get(Category, category_id)
        if cat is None:
            raise HTTPException(status_code=404, detail="Category not found")
        cat_name = cat.name
    finally:
        session.close()
    await refresh_cheapest_for_category(category_id, cat_name)
    return {"status": "ok", "category_id": category_id}
