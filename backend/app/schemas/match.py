from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


# --------- FILTROS QUE VIENEN DEL FRONTEND ---------


class MatchFilters(BaseModel):
    min_price: Optional[int] = None
    max_price: Optional[int] = None
    min_year: Optional[int] = None
    max_year: Optional[int] = None
    max_miles: Optional[int] = None

    # Para más adelante, si tu modelo Listing tiene estas columnas:
    conditions: Optional[List[str]] = None  # ["new", "used", "cpo"]
    require_third_row: bool = False
    require_awd: bool = False


class MatchWeights(BaseModel):
    # 1 a 5, donde 1 = poco importante, 5 = muy importante
    price: int = 3
    mileage: int = 3
    year: int = 3
    third_row: int = 3
    awd: int = 3
    condition: int = 3
    body_style: int = 3


class MatchRequest(BaseModel):
    filters: MatchFilters
    weights: MatchWeights
    body_style_preference: Optional[str] = None  # ej: "SUV", "Sedan"
    limit_results: int = 20


# --------- RESPUESTA HACIA EL FRONTEND ---------


class ListingScoreOut(BaseModel):
    listing_id: int
    score: float         # 0.0 - 1.0
    score_100: int       # 0 - 100, redondeado

    year: Optional[int] = None
    make: Optional[str] = None
    model: Optional[str] = None
    trim: Optional[str] = None
    price: Optional[int] = None
    miles: Optional[int] = None
    body_style: Optional[str] = None
    condition: Optional[str] = None

    dealer_name: Optional[str] = None
    source: Optional[str] = None
    url: Optional[str] = None

    created_at: Optional[datetime] = None  # por si luego lo agregas a Listing


class MatchResponse(BaseModel):
    total_candidates: int   # autos que pasaron los filtros
    returned: int           # autos devueltos (limit_results)
    results: List[ListingScoreOut]
