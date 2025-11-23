from typing import Dict, List, Tuple
from app.schemas.listing import ListingIn, ListingWithScore, MatchFilters

# Grupos y subcriterios (AHP jerárquico)
CRITERIA_STRUCTURE = {
    "economic": ["price", "fuel_efficiency"],
    "condition": ["miles", "year", "age_category", "mechanical_state"],
    "risk": ["title_condition", "accidents_count", "odometer_issue", "recalls_open"],
    "fit": ["seating_fit_score", "drivetrain_snow_score", "safety_score", "comfort_tech_score"],
}

# Mapeo importancia 1–5 -> escala tipo Saaty
IMPORTANCE_MAP = {
    1: 1,
    2: 2,
    3: 4,
    4: 6,
    5: 9,
}


# ---------------------------
# Utilidades de pesos
# ---------------------------

def _normalize(importance_dict: Dict[str, int]) -> Dict[str, float]:
    """
    Convierte importancias 1–5 en pesos normalizados.
    Si un criterio no aparece, se le asigna 3 (medio).
    """
    mapped: Dict[str, float] = {}
    for key, imp in importance_dict.items():
        i = max(1, min(5, imp))
        mapped[key] = IMPORTANCE_MAP[i]

    total = sum(mapped.values())
    if total <= 0:
        n = len(mapped) or 1
        return {k: 1.0 / n for k in mapped.keys()}
    return {k: v / total for k, v in mapped.items()}


def _default_main_importance() -> Dict[str, int]:
    # Valores razonables por defecto
    return {
        "economic": 5,
        "condition": 4,
        "risk": 5,
        "fit": 4,
    }


def _default_sub_importance() -> Dict[str, Dict[str, int]]:
    """
    Importancia por defecto de subcriterios si el usuario no los proporciona.
    Puedes tunear estos valores a tu gusto.
    """
    return {
        "economic": {
            "price": 5,
            "fuel_efficiency": 3,
        },
        "condition": {
            "miles": 5,
            "year": 3,
            "age_category": 4,
            "mechanical_state": 3,
        },
        "risk": {
            "title_condition": 5,
            "accidents_count": 4,
            "odometer_issue": 5,
            "recalls_open": 3,
        },
        "fit": {
            "seating_fit_score": 5,
            "drivetrain_snow_score": 5,
            "safety_score": 4,
            "comfort_tech_score": 3,
        },
    }


# ---------------------------
# Filtros duros
# ---------------------------

def _passes_filters(l: ListingIn, filters: MatchFilters | None) -> bool:
    if filters is None:
        return True

    # Edad: new/used/cpo
    if filters.age_categories_allowed and l.age_category is not None:
        if l.age_category.lower() not in [x.lower() for x in filters.age_categories_allowed]:
            return False

    # Año
    if filters.min_year is not None and l.year < filters.min_year:
        return False
    if filters.max_year is not None and l.year > filters.max_year:
        return False

    # Filas de asientos
    if filters.required_rows is not None and l.rows is not None:
        if l.rows < filters.required_rows:
            return False

    # Tracción (AWD/4x4/etc.)
    if filters.required_drivetrains and l.drivetrain is not None:
        if l.drivetrain.upper() not in [d.upper() for d in filters.required_drivetrains]:
            return False

    # Marca / modelo / trim
    if filters.allowed_makes and l.make is not None:
        if l.make.lower() not in [m.lower() for m in filters.allowed_makes]:
            return False

    if filters.allowed_models and l.model is not None:
        if l.model.lower() not in [m.lower() for m in filters.allowed_models]:
            return False

    if filters.allowed_trims and l.trim is not None:
        if l.trim.lower() not in [t.lower() for t in filters.allowed_trims]:
            return False

    return True


def _filter_listings(listings: List[ListingIn], filters: MatchFilters | None) -> List[ListingIn]:
    return [l for l in listings if _passes_filters(l, filters)]


# ---------------------------
# Utilidades de normalización numérica
# ---------------------------

def _get_min_max(listings: List[ListingIn], attr: str) -> Tuple[float, float]:
    values = []
    for l in listings:
        v = getattr(l, attr, None)
        if v is not None:
            values.append(float(v))
    if not values:
        return 0.0, 0.0
    return min(values), max(values)


def _score_numeric_benefit(value: float, vmin: float, vmax: float) -> float:
    """Más es mejor."""
    if vmin == vmax:
        return 1.0
    return max(0.0, min(1.0, (value - vmin) / (vmax - vmin)))


def _score_numeric_cost(value: float, vmin: float, vmax: float) -> float:
    """Menos es mejor."""
    if vmin == vmax:
        return 1.0
    return max(0.0, min(1.0, (vmax - value) / (vmax - vmin)))


def _score_bool_negative(flag: bool | None) -> float:
    """Para cosas como odometer_issue: True = malo."""
    if flag is None:
        return 0.5
    return 0.1 if flag else 1.0


def _score_title_condition(title: str | None) -> float:
    t = (title or "").strip().lower()
    if t == "clean":
        return 1.0
    if t == "cpo":
        return 0.95
    if t == "rebuilt":
        return 0.5
    if t == "salvage":
        return 0.1
    return 0.4  # desconocido / otro


def _score_age_category(age_category: str | None) -> float:
    if not age_category:
        return 0.7
    t = age_category.lower()
    if t == "new":
        return 1.0
    if t == "cpo":
        return 0.9
    if t == "used":
        return 0.7
    return 0.7


def _score_rating_0_5(v: float | None) -> float:
    if v is None:
        return 0.5
    return max(0.0, min(1.0, v / 5.0))


def _score_comfort_0_1(v: float | None) -> float:
    if v is None:
        return 0.5
    return max(0.0, min(1.0, v))


def _score_seating_fit(l: ListingIn, required_rows: int | None) -> float:
    if required_rows is None:
        # si no se especificó, asumimos neutral
        return 0.5

    if l.rows is None:
        return 0.5

    if l.rows >= required_rows:
        return 1.0
    else:
        # si no cumple, pero igual tiene varias filas, le damos algo
        if required_rows >= 3 and l.rows == 2:
            return 0.3
        return 0.1


def _score_drivetrain_snow(l: ListingIn) -> float:
    if not l.drivetrain:
        return 0.5
    d = l.drivetrain.upper()
    if d in ["AWD", "4X4", "4WD"]:
        return 1.0
    if d == "FWD":
        return 0.6
    if d == "RWD":
        return 0.3
    return 0.5


# ---------------------------
# Motor principal
# ---------------------------

def compute_ahp_scores(
    listings: List[ListingIn],
    filters: MatchFilters | None,
    criteria_importance_main: Dict[str, int] | None,
    criteria_importance_sub: Dict[str, Dict[str, int]] | None,
) -> List[ListingWithScore]:

    # 1) Filtros duros
    filtered_listings = _filter_listings(listings, filters)
    if not filtered_listings:
        return []

    # 2) Importancias principales (grupos)
    if not criteria_importance_main:
        criteria_importance_main = _default_main_importance()

    # Asegurar que tengamos clave para cada grupo definido
    for g in CRITERIA_STRUCTURE.keys():
        if g not in criteria_importance_main:
            criteria_importance_main[g] = 3  # importancia media por defecto

    weights_groups = _normalize(criteria_importance_main)

    # 3) Importancias de subcriterios
    if not criteria_importance_sub:
        criteria_importance_sub = _default_sub_importance()
    else:
        # asegurar que todos los subcriterios tengan algún valor
        default_sub = _default_sub_importance()
        for g, subs in default_sub.items():
            if g not in criteria_importance_sub:
                criteria_importance_sub[g] = subs
            else:
                for sk, sval in subs.items():
                    if sk not in criteria_importance_sub[g]:
                        criteria_importance_sub[g][sk] = sval

    # Normalizar subcriterios dentro de cada grupo
    weights_sub_local: Dict[str, Dict[str, float]] = {}
    for group, sub_list in CRITERIA_STRUCTURE.items():
        important_dict: Dict[str, int] = {}
        for sub in sub_list:
            important_dict[sub] = criteria_importance_sub.get(group, {}).get(sub, 3)
        weights_sub_local[group] = _normalize(important_dict)

    # 4) Pesos globales por subcriterio = peso_grupo * peso_sub_local
    weights_sub_global: Dict[str, float] = {}
    for group, sub_dict in weights_sub_local.items():
        g_weight = weights_groups.get(group, 0.0)
        for sub, w_local in sub_dict.items():
            weights_sub_global[sub] = g_weight * w_local

    # 5) Pre-calcular min/max para numéricos
    price_min, price_max = _get_min_max(filtered_listings, "price")
    miles_min, miles_max = _get_min_max(filtered_listings, "miles")
    year_min, year_max = _get_min_max(filtered_listings, "year")
    fe_min, fe_max = _get_min_max(filtered_listings, "fuel_efficiency")
    acc_min, acc_max = _get_min_max(filtered_listings, "accidents_count")
    rec_min, rec_max = _get_min_max(filtered_listings, "recalls_open")

    results: List[ListingWithScore] = []

    for l in filtered_listings:
        sub_scores: Dict[str, float] = {}

        # --- C1: Económico ---
        sub_scores["price"] = _score_numeric_cost(float(l.price), price_min, price_max)

        if l.fuel_efficiency is not None and fe_min != fe_max:
            sub_scores["fuel_efficiency"] = _score_numeric_benefit(
                float(l.fuel_efficiency), fe_min, fe_max
            )
        else:
            sub_scores["fuel_efficiency"] = 0.5

        # --- C2: Estado / Desgaste ---
        sub_scores["miles"] = _score_numeric_cost(float(l.miles), miles_min, miles_max)
        sub_scores["year"] = _score_numeric_benefit(float(l.year), year_min, year_max)
        sub_scores["age_category"] = _score_age_category(l.age_category)
        sub_scores["mechanical_state"] = _score_rating_0_5(l.mechanical_state)

        # --- C3: Riesgo legal / historial ---
        sub_scores["title_condition"] = _score_title_condition(l.title_condition)

        if l.accidents_count is not None and acc_min != acc_max:
            sub_scores["accidents_count"] = _score_numeric_cost(
                float(l.accidents_count), acc_min, acc_max
            )
        else:
            # si no hay accidentes reportados, le damos un buen score
            sub_scores["accidents_count"] = 1.0 if (l.accidents_count or 0) == 0 else 0.7

        sub_scores["odometer_issue"] = _score_bool_negative(l.odometer_issue)

        if l.recalls_open is not None and rec_min != rec_max:
            sub_scores["recalls_open"] = _score_numeric_cost(
                float(l.recalls_open), rec_min, rec_max
            )
        else:
            sub_scores["recalls_open"] = 1.0 if (l.recalls_open or 0) == 0 else 0.7

        # --- C4: Adecuación al uso / características ---
        required_rows = filters.required_rows if filters else None
        sub_scores["seating_fit_score"] = _score_seating_fit(l, required_rows)
        sub_scores["drivetrain_snow_score"] = _score_drivetrain_snow(l)
        sub_scores["safety_score"] = _score_rating_0_5(l.safety_score)
        sub_scores["comfort_tech_score"] = _score_comfort_0_1(l.comfort_tech_score)

        # 6) Score global = Σ (peso_sub_global * sub_score)
        total = 0.0
        for sub_name, s_val in sub_scores.items():
            w = weights_sub_global.get(sub_name, 0.0)
            total += w * s_val

        score_global = total * 100.0

        # 7) Contribución por grupo (para explicación)
        group_scores: Dict[str, float] = {}
        for group, subs in CRITERIA_STRUCTURE.items():
            g_sum = 0.0
            for sub in subs:
                w = weights_sub_global.get(sub, 0.0)
                s = sub_scores.get(sub, 0.5)
                g_sum += w * s
            group_scores[group] = g_sum * 100.0  # contribución en puntos

        results.append(
            ListingWithScore(
                listing=l,
                score=round(score_global, 2),
                sub_scores=sub_scores,
                group_scores=group_scores,
                weights_sub=weights_sub_global,
                weights_groups=weights_groups,
            )
        )

    # Ordenar por score final
    results.sort(key=lambda x: x.score, reverse=True)
    return results
