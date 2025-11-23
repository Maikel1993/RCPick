from __future__ import annotations

import json
from typing import List, Callable, Dict
from urllib.parse import urlparse

import requests
from requests.exceptions import RequestException
from bs4 import BeautifulSoup
from sqlalchemy.orm import Session

from app.models.listing import Listing

# User-Agent para evitar bloqueos básicos
DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0 Safari/537.36"
    )
}


def _is_valid_url(url: str) -> bool:
    try:
        parsed = urlparse(url)
        return parsed.scheme in ("http", "https") and bool(parsed.netloc)
    except Exception:
        return False


# ============================================================
#   PARSERS ESPECÍFICOS POR DOMINIO
# ============================================================

def parse_cars_com_listings(soup: BeautifulSoup) -> List[Listing]:
    """
    Intenta extraer autos de una página de resultados de cars.com.
    OJO: los selectores pueden necesitar ajustes según el HTML real.
    """
    listings: List[Listing] = []

    # cars.com suele usar algo como .vehicle-card o .shop-srp-listings__listing
    cards = soup.select("div.vehicle-card, div.shop-srp-listings__listing")

    for card in cards:
        # Título: a menudo está en a.vehicle-card-link o similar
        title_el = (
            card.select_one("a.vehicle-card-link")
            or card.select_one("h2")
            or card.select_one(".title")
        )
        price_el = (
            card.select_one(".primary-price")
            or card.select_one(".vehicle-card-price")
            or card.select_one(".price")
        )
        miles_el = (
            card.select_one(".mileage")
            or card.select_one(".mileage-amount")
            or card.select_one(".miles")
        )
        year_el = None  # podemos intentar sacarlo del título luego

        if not (title_el and price_el):
            continue

        title_text = title_el.get_text(strip=True)

        # Helpers de parseo
        def parse_int(text: str, default: int = 0) -> int:
            text = text.replace(",", "").replace("mi.", "").replace("mi", "")
            digits = "".join(ch for ch in text if ch.isdigit())
            return int(digits) if digits else default

        price = parse_int(price_el.get_text(), 0)
        miles = parse_int(miles_el.get_text(), 0) if miles_el else 0

        # Intentar sacar el año del título (primer número de 4 dígitos)
        year = 0
        for token in title_text.split():
            if token.isdigit() and len(token) == 4:
                year = int(token)
                break

        # Separar marca/modelo de forma muy básica
        parts = title_text.split()
        make = parts[1] if len(parts) > 1 and parts[0].isdigit() else (parts[0] if parts else None)
        model = parts[2] if len(parts) > 2 and parts[0].isdigit() else (parts[1] if len(parts) > 1 else None)

        listing = Listing(
            price=price,
            miles=miles,
            year=year or 0,
            age_category="used",      # cars.com suele indicar "Used", "New", etc., lo podrías buscar en el card
            title_condition="clean",  # real vendrá de Carfax u otras fuentes
            accidents_count=None,
            odometer_issue=None,
            recalls_open=None,
            fuel_efficiency=None,
            mechanical_state=None,
            safety_score=None,
            drivetrain=None,
            seats=None,
            rows=None,
            comfort_tech_score=None,
            make=make,
            model=model,
            trim=None,
        )
        listings.append(listing)

    return listings


def parse_cars_com_detail(soup: BeautifulSoup) -> List[Listing]:
    """
    Intenta extraer información de una PÁGINA DE DETALLE de cars.com usando JSON-LD y etiquetas visibles.
    Si no encuentra nada claro, devuelve lista vacía.
    """
    # 1) Intentar con JSON-LD (application/ld+json)
    for script in soup.select('script[type="application/ld+json"]'):
        try:
            data = json.loads(script.string or "")
        except Exception:
            continue

        # a veces es lista, a veces dict
        if isinstance(data, list):
            for item in data:
                listing = _listing_from_ld_json(item)
                if listing:
                    return [listing]
        elif isinstance(data, dict):
            listing = _listing_from_ld_json(data)
            if listing:
                return [listing]

    # 2) Fallback: buscar precio/título simples
    title_el = soup.select_one("h1, .vehicle-info__title, .cui-heading-2")
    price_el = soup.select_one(".primary-price, .vehicle-info__price-display, .cui-heading-3")

    if not (title_el and price_el):
        return []

    title_text = title_el.get_text(strip=True)

    def parse_int(text: str, default: int = 0) -> int:
        text = text.replace(",", "").replace("$", "")
        digits = "".join(ch for ch in text if ch.isdigit())
        return int(digits) if digits else default

    price = parse_int(price_el.get_text(), 0)
    miles_el = (
        soup.select_one(".mileage, .mileage-amount")
        or soup.find(string=lambda t: t and "mi" in t.lower())
    )
    miles = 0
    if miles_el:
        miles = parse_int(getattr(miles_el, "get_text", lambda: str(miles_el))())

    # año y make/model del título
    year = 0
    make = None
    model = None
    parts = title_text.split()
    for token in parts:
        if token.isdigit() and len(token) == 4:
            year = int(token)
            break
    if parts:
        if parts[0].isdigit() and len(parts) > 2:
            make = parts[1]
            model = parts[2]
        elif len(parts) > 1:
            make = parts[0]
            model = parts[1]

    listing = Listing(
        price=price,
        miles=miles,
        year=year or 0,
        age_category="used",
        title_condition="clean",
        accidents_count=None,
        odometer_issue=None,
        recalls_open=None,
        fuel_efficiency=None,
        mechanical_state=None,
        safety_score=None,
        drivetrain=None,
        seats=None,
        rows=None,
        comfort_tech_score=None,
        make=make,
        model=model,
        trim=None,
    )
    return [listing]


def _listing_from_ld_json(data: dict) -> Listing | None:
    """
    Intenta crear un Listing a partir de un objeto JSON-LD de tipo Vehicle.
    Muy genérico: puede que necesites adaptarlo al JSON real de cars.com.
    """
    try:
        if "@type" not in data or "Vehicle" not in str(data.get("@type")):
            return None

        # Muchos sitios usan propiedades estándar de schema.org/Vehicle
        name = data.get("name") or ""
        price = 0
        miles = 0
        year = 0

        offers = data.get("offers") or {}
        if isinstance(offers, dict):
            price = int(float(offers.get("price", 0)))

        mileage = data.get("mileage") or {}
        if isinstance(mileage, dict):
            miles = int(float(mileage.get("value", 0)))

        if "modelDate" in data:
            year = int(data["modelDate"])
        elif "productionDate" in data:
            year = int(str(data["productionDate"])[:4])

        # make / model
        make = None
        model = None
        if "brand" in data:
            brand = data["brand"]
            if isinstance(brand, dict):
                make = brand.get("name")
            elif isinstance(brand, str):
                make = brand

        if "model" in data:
            m = data["model"]
            if isinstance(m, dict):
                model = m.get("name")
            elif isinstance(m, str):
                model = m

        # fallback si name tiene "YYYY Make Model"
        if not (year and make and model) and name:
            parts = name.split()
            for token in parts:
                if token.isdigit() and len(token) == 4:
                    year = year or int(token)
                    break
            if parts:
                if parts[0].isdigit() and len(parts) > 2:
                    make = make or parts[1]
                    model = model or parts[2]
                elif len(parts) > 1:
                    make = make or parts[0]
                    model = model or parts[1]

        return Listing(
            price=price,
            miles=miles,
            year=year or 0,
            age_category="used",
            title_condition="clean",
            accidents_count=None,
            odometer_issue=None,
            recalls_open=None,
            fuel_efficiency=None,
            mechanical_state=None,
            safety_score=None,
            drivetrain=None,
            seats=None,
            rows=None,
            comfort_tech_score=None,
            make=make,
            model=model,
            trim=None,
        )
    except Exception:
        return None


# ============================================================
#   PARSER GENÉRICO / REGISTRO DE DOMINIOS
# ============================================================

def parse_generic_page(soup: BeautifulSoup) -> List[Listing]:
    """
    Parser genérico muy básico.
    De momento devolvemos vacío; la idea es que añadas lógica
    cuando quieras soportar otros sitios.
    """
    return []


PARSERS_BY_DOMAIN: Dict[str, Callable[[BeautifulSoup, str], List[Listing]]] = {}


def _register_default_parsers():
    """
    Registra parsers por dominio. Esto te permite más adelante
    añadir otros sitios fácilmente.
    """
    def cars_parser(soup: BeautifulSoup, path: str) -> List[Listing]:
        # Si el path contiene 'vehicledetail' asumimos página de detalle
        if "vehicledetail" in path:
            return parse_cars_com_detail(soup)
        # Si no, lo tratamos como página de resultados
        return parse_cars_com_listings(soup)

    # Para cars.com
    PARSERS_BY_DOMAIN["cars.com"] = cars_parser

    # Genérico (fallback)
    PARSERS_BY_DOMAIN["*"] = lambda s, p: parse_generic_page(s)


_register_default_parsers()


# ============================================================
#   FUNCIÓN PÚBLICA: SCRAPE + GUARDAR
# ============================================================

def scrape_and_save_listings(db: Session, url: str) -> List[Listing]:
    """
    Llama al scraper para una URL y guarda los listings en la BD.
    - Selecciona parser específico según el dominio (cars.com, etc.)
    - Ignora URLs inválidas o errores de red.
    """
    if not _is_valid_url(url):
        return []

    parsed = urlparse(url)
    domain = parsed.netloc.lower()
    path = parsed.path or "/"

    # Elegir parser según dominio; si no hay, usar genérico
    parser = PARSERS_BY_DOMAIN.get(domain)
    if parser is None:
        parser = PARSERS_BY_DOMAIN.get("*", lambda s, p: [])

    try:
        resp = requests.get(url, headers=DEFAULT_HEADERS, timeout=15)
        resp.raise_for_status()
    except RequestException:
        return []

    soup = BeautifulSoup(resp.text, "html.parser")

    try:
        scraped = parser(soup, path)
    except Exception:
        scraped = []

    if not scraped:
        return []

    for l in scraped:
        db.add(l)
    db.commit()

    for l in scraped:
        db.refresh(l)

    return scraped
