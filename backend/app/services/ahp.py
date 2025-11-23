from typing import List, Dict, Any, Optional

from sqlalchemy.orm import Session

from app.models.listing import Listing
from app.models.dealer import Dealer
from app.schemas.match import MatchFilters, MatchWeights


def _normalize_weights(weights: MatchWeights) -> Dict[str, float]:
    """
    Convierte los pesos enteros (0-5) en un vector que suma 1.
    Si todos los pesos son 0, reparte el peso por igual.
    """
    raw = {
        "price": max(weights.price, 0),
        "mileage": max(weights.mileage, 0),
        "year": max(weights.year, 0),
        "third_row": max(weights.third_row, 0),
        "awd": max(weights.awd, 0),
        "condition": max(weights.condition, 0),
        "body_style": max(weights.body_style, 0),
    }
    total = sum(raw.values())
    if total <= 0:
        # todos cero: dar pesos iguales
        n = len(raw)
        return {k: 1.0 / n for k in raw}
    return {k: v / total for k, v in raw.items()}


def rank_listings_with_ahp(
    db: Session,
    filters: MatchFilters,
    weights: MatchWeights,
    body_style_preference: Optional[str] = None,
    limit_results: int = 20,
) -> List[Dict[str, Any]]:
    """
    Devuelve una lista de dicts con:
      - info básica del listing
      - score (0-1, NORMALIZADO entre los candidatos)
      - score_100 (0-100)
    Ordenados de mayor a menor score.
    """

    # 1) Construir query base con filtros duros
    query = db.query(Listing)

    if filters.min_price is not None and hasattr(Listing, "price"):
        query = query.filter(Listing.price >= filters.min_price)
    if filters.max_price is not None and hasattr(Listing, "price"):
        query = query.filter(Listing.price <= filters.max_price)

    if filters.min_year is not None and hasattr(Listing, "year"):
        query = query.filter(Listing.year >= filters.min_year)
    if filters.max_year is not None and hasattr(Listing, "year"):
        query = query.filter(Listing.year <= filters.max_year)

    if filters.max_miles is not None and hasattr(Listing, "miles"):
        query = query.filter(Listing.miles <= filters.max_miles)

    if filters.conditions and hasattr(Listing, "condition"):
        query = query.filter(Listing.condition.in_(filters.conditions))

    if filters.require_third_row and hasattr(Listing, "has_third_row"):
        query = query.filter(Listing.has_third_row.is_(True))

    if filters.require_awd and hasattr(Listing, "is_awd"):
        query = query.filter(Listing.is_awd.is_(True))

    candidates: List[Listing] = query.all()
    total_candidates = len(candidates)

    if total_candidates == 0:
        return []

    # 2) Normalizar pesos (AHP simplificado)
    w = _normalize_weights(weights)

    # 3) Preparar min/max para numéricos
    prices = [c.price for c in candidates if getattr(c, "price", None) is not None]
    miles_list = [c.miles for c in candidates if getattr(c, "miles", None) is not None]
    years = [c.year for c in candidates if getattr(c, "year", None) is not None]

    p_min = min(prices) if prices else None
    p_max = max(prices) if prices else None
    m_min = min(miles_list) if miles_list else None
    m_max = max(miles_list) if miles_list else None
    y_min = min(years) if years else None
    y_max = max(years) if years else None

    eps = 1e-6

    def norm_minimize(value, v_min, v_max) -> float:
        """
        Criterio a minimizar (precio, millas):
        menor valor => score más alto (cercano a 1).
        """
        if value is None or v_min is None or v_max is None or v_max == v_min:
            return 0.5
        return (v_max - value) / (v_max - v_min + eps)

    def norm_maximize(value, v_min, v_max) -> float:
        """
        Criterio a maximizar (año):
        mayor valor => score más alto.
        """
        if value is None or v_min is None or v_max is None or v_max == v_min:
            return 0.5
        return (value - v_min) / (v_max - v_min + eps)

    results: List[Dict[str, Any]] = []

    # 4) Calcular score bruto por candidato (antes de reescalar 0-1)
    for c in candidates:
        price_val = getattr(c, "price", None)
        miles_val = getattr(c, "miles", None)
        year_val = getattr(c, "year", None)

        s_price = norm_minimize(price_val, p_min, p_max)
        s_miles = norm_minimize(miles_val, m_min, m_max)
        s_year = norm_maximize(year_val, y_min, y_max)

        has_third = getattr(c, "has_third_row", False)
        s_third = 1.0 if has_third else 0.0

        is_awd = getattr(c, "is_awd", False)
        s_awd = 1.0 if is_awd else 0.0

        cond_val = getattr(c, "condition", None)
        if filters.conditions and cond_val in filters.conditions:
            s_condition = 1.0
        elif filters.conditions:
            s_condition = 0.0
        else:
            s_condition = 0.5  # sin preferencia clara

        body_style = getattr(c, "body_style", None)
        if body_style_preference and body_style:
            if body_style.lower() == body_style_preference.lower():
                s_body = 1.0
            else:
                s_body = 0.0
        else:
            s_body = 0.5

        # Score bruto: suma ponderada según pesos normalizados
        raw_score = (
            w["price"] * s_price
            + w["mileage"] * s_miles
            + w["year"] * s_year
            + w["third_row"] * s_third
            + w["awd"] * s_awd
            + w["condition"] * s_condition
            + w["body_style"] * s_body
        )

        dealer_name = None
        if getattr(c, "dealer_id", None) is not None:
            dealer = db.query(Dealer).filter(Dealer.id == c.dealer_id).first()
            if dealer:
                dealer_name = dealer.name

        results.append(
            {
                "listing_id": c.id,
                "raw_score": raw_score,
                "year": getattr(c, "year", None),
                "make": getattr(c, "make", None),
                "model": getattr(c, "model", None),
                "trim": getattr(c, "trim", None),
                "price": getattr(c, "price", None),
                "miles": getattr(c, "miles", None),
                "body_style": getattr(c, "body_style", None),
                "condition": getattr(c, "condition", None),
                "dealer_name": dealer_name,
                "source": getattr(c, "source", None),
                "url": getattr(c, "url", None),
                "created_at": getattr(c, "created_at", None),
            }
        )

    # 5) Re-escalar los scores a [0,1] entre los candidatos
    raw_values = [r["raw_score"] for r in results]
    s_min = min(raw_values)
    s_max = max(raw_values)

    for r in results:
        if s_max == s_min:
            # todos tienen mismo score: dejar todo a 0.5
            norm = 0.5
        else:
            norm = (r["raw_score"] - s_min) / (s_max - s_min + eps)
        r["score"] = norm
        r["score_100"] = int(round(norm * 100))

    # 6) Ordenar de mayor a menor score normalizado
    results.sort(key=lambda x: x["score"], reverse=True)

    if limit_results > 0:
        results = results[:limit_results]

    return results
