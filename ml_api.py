import re
from typing import Optional
from playwright.async_api import async_playwright, Page, Browser

MAX_PRODUCTS = 200

_BROWSER: Optional[Browser] = None
_PLAY_CM = None


async def _get_browser() -> Browser:
    global _BROWSER, _PLAY_CM
    if _BROWSER is None:
        _PLAY_CM = async_playwright()
        playwright = await _PLAY_CM.__aenter__()
        _BROWSER = await playwright.chromium.launch(
            headless=True,
            args=["--disable-blink-features=AutomationControlled", "--no-sandbox"],
        )
    return _BROWSER


async def close_browser():
    global _BROWSER, _PLAY_CM
    if _BROWSER:
        await _BROWSER.close()
        _BROWSER = None
    if _PLAY_CM:
        await _PLAY_CM.__aexit__(None, None, None)
        _PLAY_CM = None


async def _new_page() -> Page:
    browser = await _get_browser()
    context = await browser.new_context(
        viewport={"width": 1280, "height": 800},
        locale="es-AR",
        timezone_id="America/Argentina/Buenos_Aires",
        user_agent=(
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        ),
    )
    return await context.new_page()


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


class MLApiClient:
    async def close(self):
        pass

    async def get_categories(self) -> list[dict]:
        try:
            page = await _new_page()
            try:
                await page.goto(
                    "https://www.mercadolibre.com.ar/categorias",
                    wait_until="load",
                    timeout=30000,
                )
                await page.wait_for_timeout(2000)

                cats = await page.evaluate("""
                    () => {
                        const links = document.querySelectorAll('a[href*="/c/"]');
                        const seen = new Set();
                        const result = [];
                        links.forEach(a => {
                            const href = a.getAttribute('href') || '';
                            const text = a.textContent?.trim();
                            if (text && text.length >= 3 && !seen.has(href)) {
                                seen.add(href);
                                result.push({ name: text, href });
                            }
                        });
                        return result;
                    }
                """)

                seen = set()
                result = []
                for c in cats:
                    href = c.get("href", "")
                    name = c.get("name", "")
                    m = re.search(r"/c/([^/#]+)", href)
                    if not m:
                        continue
                    slug = m.group(1)
                    if slug in seen or len(name) < 3:
                        continue
                    seen.add(slug)
                    result.append({"id": slug, "name": name})
                print(f"[scraper] Scraped {len(result)} categories", flush=True)
                return result
            except Exception as e:
                print(f"[scraper] Failed to scrape categories: {e}", flush=True)
                return []
            finally:
                await page.close()
        except Exception as e:
            print(f"[scraper] Browser error in get_categories: {e}", flush=True)
            return FALLBACK_CATEGORIES

    async def search_cheapest(
        self, category_id: str, category_name: str, limit: int = 50, offset: int = 0
    ) -> tuple[list[dict], Optional[int]]:
        slug = category_id
        url = f"https://www.mercadolibre.com.ar/c/{slug}"

        try:
            page = await _new_page()
        except Exception as e:
            print(f"[scraper] Failed to create page for {category_id}: {e}", flush=True)
            return [], None

        try:
            await page.goto(
                "https://www.mercadolibre.com.ar/",
                wait_until="load",
                timeout=20000,
            )
            await page.wait_for_timeout(1000)

            await page.evaluate("""
                const d = new Date(Date.now() + 3600000);
                document.cookie = '_bm_skipml=true; Path=/; domain=.mercadolibre.com.ar; expires=' + d.toUTCString();
            """)

            resp = await page.goto(url, wait_until="load", timeout=20000)
            if resp and resp.status == 404:
                print(f"[scraper] {category_id}: 404", flush=True)
                return [], 0
            if "blocked" in page.url.lower() or "account-verification" in page.url.lower():
                print(f"[scraper] {category_id}: blocked ({page.url})", flush=True)
                return [], 0

            await page.wait_for_timeout(2000)

            js_code = """
            () => {
                function parsePrice(fracEl) {
                    if (!fracEl) return null;
                    const text = fracEl.textContent.trim();
                    const num = parseInt(text.replace(/[.]/g, ''));
                    return isNaN(num) ? null : num;
                }

                const cards = document.querySelectorAll('.poly-card');
                const results = [];
                for (const card of cards) {
                    const links = Array.from(card.querySelectorAll('a'));
                    const isAd = links.some(l => (l.href || '').includes('is_advertising=true'));
                    if (isAd) continue;

                    const titleEl = card.querySelector('.poly-component__title, .poly-box__title, [class*="title"] a, h2, h3');
                    const title = titleEl ? (titleEl.textContent || titleEl.innerText || '').trim() : '';

                    const currentPriceEl = card.querySelector('.andes-money-amount--cents-superscript .andes-money-amount__fraction');
                    const prevPriceEl = card.querySelector('s.andes-money-amount--previous .andes-money-amount__fraction');
                    const discountEl = card.querySelector('.poly-price__disc_label--pill');
                    const genericPriceEl = card.querySelector('.andes-money-amount__fraction');

                    let price = null;
                    if (currentPriceEl) {
                        price = parsePrice(currentPriceEl);
                    } else if (genericPriceEl) {
                        price = parsePrice(genericPriceEl);
                    }

                    let original_price = null;
                    if (prevPriceEl) {
                        original_price = parsePrice(prevPriceEl);
                    }

                    let discount_percentage = null;
                    if (discountEl) {
                        const match = discountEl.textContent.trim().match(/(\\d+)%\\s*OFF/);
                        if (match) discount_percentage = parseInt(match[1]);
                    }

                    const shippingEl = card.querySelector('.poly-component__shipping, [class*="shipping"]');
                    const free_shipping = shippingEl && shippingEl.textContent.trim().toLowerCase().includes('env\\u00edo gratis') ? 1 : 0;

                    const conditionEl = card.querySelector('.poly-component__condition, [class*="condition"]');
                    let condition = null;
                    if (conditionEl) {
                        const t = conditionEl.textContent.trim().toLowerCase();
                        if (t.includes('nuevo')) condition = 'new';
                        else if (t.includes('usado')) condition = 'used';
                    }

                    const installmentsEl = card.querySelector('.poly-price__installments, [class*="installments"]');
                    const installments = installmentsEl ? installmentsEl.textContent.trim() : null;

                    const linkEl = links.find(l => (l.href || '').includes('mercadolibre') && !(l.href || '').includes('is_advertising') && !(l.href || '').includes('mclics'));
                    const permalink = linkEl ? linkEl.href : '';

                    const imgEl = card.querySelector('img');
                    let thumbnail = imgEl ? (imgEl.src || imgEl.getAttribute('data-src') || '') : '';
                    if (thumbnail && thumbnail.startsWith('//')) {
                        thumbnail = 'https:' + thumbnail;
                    }

                    const currencyEl = card.querySelector('.andes-money-amount__currency-symbol');
                    const currency_id = currencyEl ? currencyEl.textContent.trim() : 'ARS';

                    if (title && price) {
                        results.push({
                            title,
                            price,
                            original_price,
                            discount_percentage,
                            free_shipping,
                            condition,
                            installments,
                            currency_id,
                            permalink,
                            thumbnail,
                        });
                    }
                }
                return results;
            }
            """
            results = await page.evaluate(js_code)
            results.sort(key=lambda r: r.get("price", 0))

            total_text = ""
            try:
                total_text = await page.evaluate(
                    "document.querySelector('.ui-search-search-result__quantity-results')?.textContent || ''"
                )
            except Exception:
                pass

            total = None
            if total_text:
                nums = re.findall(r"[\d.]+", total_text.replace(".", ""))
                if nums:
                    total = int(nums[0])

            return results, total or len(results)
        except Exception as e:
            print(f"[scraper] Error in search_cheapest({category_id}): {e}", flush=True)
            return [], None
        finally:
            await page.close()

    async def fetch_all_cheapest(
        self, category_id: str, category_name: str, max_products: int = MAX_PRODUCTS
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
