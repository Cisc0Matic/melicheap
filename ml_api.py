import asyncio
import re
from typing import Optional

import httpx
from bs4 import BeautifulSoup

MAX_PRODUCTS = 200

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "es-AR,es;q=0.9,en;q=0.8",
}

FALLBACK_CATEGORIES = [
    {"id": "celulares", "name": "Celulares y Teléfonos"},
    {"id": "computacion", "name": "Computación"},
    {"id": "electronica-audio-y-video", "name": "Electrónica, Audio y Video"},
    {"id": "hogar-muebles-y-jardin", "name": "Hogar, Muebles y Jardín"},
    {"id": "electrodomesticos-y-aires-ac", "name": "Electrodomésticos"},
    {"id": "herramientas", "name": "Herramientas"},
    {"id": "construccion", "name": "Construcción"},
    {"id": "deportes-y-fitness", "name": "Deportes y Fitness"},
    {"id": "accesorios-para-vehiculos", "name": "Accesorios para Vehículos"},
    {"id": "animales-y-mascotas", "name": "Animales y Mascotas"},
    {"id": "ropa-y-accesorios", "name": "Ropa y Accesorios"},
    {"id": "juegos-y-juguetes", "name": "Juegos y Juguetes"},
    {"id": "bebes", "name": "Bebés"},
    {"id": "belleza-y-cuidado-personal", "name": "Belleza y Cuidado Personal"},
    {"id": "salud-y-equipamiento-medico", "name": "Salud y Equipamiento Médico"},
    {"id": "industrias-y-oficinas", "name": "Industrias y Oficinas"},
    {"id": "agro", "name": "Agro"},
    {"id": "servicios", "name": "Servicios"},
    {"id": "camaras-y-accesorios", "name": "Cámaras y Accesorios"},
    {"id": "consolas-y-videojuegos", "name": "Consolas y Videojuegos"},
    {"id": "alimentos-y-bebidas", "name": "Alimentos y Bebidas"},
    {"id": "antiguedades-y-colecciones", "name": "Antigüedades y Colecciones"},
    {"id": "arte-libreria-y-merceria", "name": "Arte, Librería y Mercería"},
    {"id": "autos-motos-y-otros", "name": "Autos, Motos y Otros"},
    {"id": "entradas-para-eventos", "name": "Entradas para Eventos"},
    {"id": "inmuebles", "name": "Inmuebles"},
    {"id": "instrumentos-musicales", "name": "Instrumentos Musicales"},
    {"id": "joyas-y-relojes", "name": "Joyas y Relojes"},
    {"id": "libros-revistas-y-comics", "name": "Libros, Revistas y Comics"},
    {"id": "musica-peliculas-y-series", "name": "Música, Películas y Series"},
    {"id": "souvenirs-cotillon-y-fiestas", "name": "Souvenirs, Cotillón y Fiestas"},
    {"id": "otras-categorias", "name": "Otras Categorías"},
]


def _parse_price(el) -> Optional[int]:
    if el is None:
        return None
    text = el.get_text(strip=True)
    num = int(text.replace(".", ""))
    return num


class MLApiClient:
    async def close(self):
        pass

    async def get_categories(self) -> list[dict]:
        try:
            async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
                resp = await client.get(
                    "https://www.mercadolibre.com.ar/categorias",
                    headers=HEADERS,
                )
                resp.raise_for_status()
                soup = BeautifulSoup(resp.text, "lxml")
                seen = set()
                result = []
                for a in soup.select('a[href*="/c/"]'):
                    href = a.get("href", "")
                    text = a.get_text(strip=True)
                    if not text or len(text) < 3:
                        continue
                    m = re.search(r"/c/([^/#]+)", href)
                    if not m:
                        continue
                    slug = m.group(1)
                    if slug in seen:
                        continue
                    seen.add(slug)
                    result.append({"id": slug, "name": text})
                if result:
                    print(f"[scraper] Scraped {len(result)} categories", flush=True)
                    return result
                return []
        except Exception as e:
            print(f"[scraper] Failed to scrape categories: {e}", flush=True)
            return FALLBACK_CATEGORIES

    async def search_cheapest(
        self, category_id: str, category_name: str, limit: int = 50, offset: int = 0
    ) -> tuple[list[dict], Optional[int]]:
        slug = category_id
        url = f"https://www.mercadolibre.com.ar/c/{slug}"

        try:
            async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
                client.cookies.set("_bm_skipml", "true", domain=".mercadolibre.com.ar")

                await client.get("https://www.mercadolibre.com.ar/", headers=HEADERS)

                resp = await client.get(url, headers=HEADERS)
                if resp.status_code == 404:
                    print(f"[scraper] {category_id}: 404", flush=True)
                    return [], 0

                url_lower = str(resp.url).lower()
                if "blocked" in url_lower or "account-verification" in url_lower:
                    print(f"[scraper] {category_id}: blocked ({resp.url})", flush=True)
                    return [], 0

                soup = BeautifulSoup(resp.text, "lxml")
                cards = soup.select(".poly-card")

                results = []
                for card in cards:
                    links = card.select("a")
                    is_ad = any(
                        "is_advertising=true" in (l.get("href", "") or "")
                        for l in links
                    )
                    if is_ad:
                        continue

                    title_el = card.select_one(
                        ".poly-component__title, .poly-box__title, "
                        '[class*="title"] a, h2, h3'
                    )
                    title = title_el.get_text(strip=True) if title_el else ""

                    current_price_el = card.select_one(
                        ".andes-money-amount--cents-superscript "
                        ".andes-money-amount__fraction"
                    )
                    generic_price_el = card.select_one(
                        ".andes-money-amount__fraction"
                    )

                    if current_price_el:
                        price = _parse_price(current_price_el)
                    elif generic_price_el:
                        price = _parse_price(generic_price_el)
                    else:
                        price = None

                    prev_price_el = card.select_one(
                        "s.andes-money-amount--previous "
                        ".andes-money-amount__fraction"
                    )
                    original_price = _parse_price(prev_price_el)

                    discount_el = card.select_one(
                        ".poly-price__disc_label--pill"
                    )
                    discount_percentage = None
                    if discount_el:
                        match = re.search(
                            r"(\d+)%\s*OFF",
                            discount_el.get_text(strip=True),
                        )
                        if match:
                            discount_percentage = int(match[1])

                    shipping_el = card.select_one(
                        '.poly-component__shipping, [class*="shipping"]'
                    )
                    free_shipping = 0
                    if shipping_el:
                        txt = shipping_el.get_text(strip=True).lower()
                        if "envío gratis" in txt:
                            free_shipping = 1

                    condition_el = card.select_one(
                        '.poly-component__condition, [class*="condition"]'
                    )
                    condition = None
                    if condition_el:
                        t = condition_el.get_text(strip=True).lower()
                        if "nuevo" in t:
                            condition = "new"
                        elif "usado" in t:
                            condition = "used"

                    installments_el = card.select_one(
                        '.poly-price__installments, [class*="installments"]'
                    )
                    installments = (
                        installments_el.get_text(strip=True)
                        if installments_el
                        else None
                    )

                    permalink = ""
                    for l in links:
                        href = l.get("href", "") or ""
                        if (
                            "mercadolibre" in href
                            and "is_advertising" not in href
                            and "mclics" not in href
                        ):
                            permalink = href
                            break

                    img_el = card.select_one("img")
                    thumbnail = ""
                    if img_el:
                        thumbnail = (
                            img_el.get("src")
                            or img_el.get("data-src")
                            or ""
                        )
                        if thumbnail.startswith("//"):
                            thumbnail = "https:" + thumbnail

                    currency_el = card.select_one(
                        ".andes-money-amount__currency-symbol"
                    )
                    currency_id = (
                        currency_el.get_text(strip=True)
                        if currency_el
                        else "ARS"
                    )

                    if title and price:
                        results.append({
                            "title": title,
                            "price": price,
                            "original_price": original_price,
                            "discount_percentage": discount_percentage,
                            "free_shipping": free_shipping,
                            "condition": condition,
                            "installments": installments,
                            "currency_id": currency_id,
                            "permalink": permalink,
                            "thumbnail": thumbnail,
                        })

                results.sort(key=lambda r: r.get("price", 0))

                total_el = soup.select_one(
                    ".ui-search-search-result__quantity-results"
                )
                total = None
                if total_el:
                    nums = re.findall(
                        r"[\d.]+",
                        total_el.get_text(strip=True).replace(".", ""),
                    )
                    if nums:
                        total = int(nums[0])

                return results, total or len(results)
        except Exception as e:
            print(
                f"[scraper] Error in search_cheapest({category_id}): {e}",
                flush=True,
            )
            return [], None

    async def fetch_all_cheapest(
        self,
        category_id: str,
        category_name: str,
        max_products: int = MAX_PRODUCTS,
    ) -> list[dict]:
        all_results = []
        offset = 0
        limit = 50

        while len(all_results) < max_products:
            results, total = await self.search_cheapest(
                category_id, category_name, limit=limit, offset=offset
            )
            if not results:
                break
            all_results.extend(results)
            offset += limit
            if total and offset >= total:
                break
            await asyncio.sleep(0.5)

        return all_results[:max_products]
