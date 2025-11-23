from pydantic import BaseModel
from typing import Optional, List, Dict, Any


class ListingIn(BaseModel):
    """
    Representa un auto candidato a ser evaluado.
    Muchos campos son opcionales para que puedas ir incorporándolos poco a poco.
    """
    id: str  # puede ser ID interno, VIN, etc.

    # Datos básicos
    price: int
    miles: int
    year: int

    # Nuevo / Usado / CPO
    age_category: Optional[str] = None  # "new", "used", "cpo"

    # Estado legal / historial
    title_condition: Optional[str] = None  # "clean", "rebuilt", "salvage", etc.
    accidents_count: Optional[int] = None
    odometer_issue: Optional[bool] = None
    recalls_open: Optional[int] = None

    # Estado / comportamiento
    fuel_efficiency: Optional[float] = None  # mpg o km/l
    mechanical_state: Optional[float] = None  # 0–5 (lo que diga tu IA/inspección)
    safety_score: Optional[float] = None      # 0–5 (NHTSA/IIHS/IA)

    # Adecuación al uso
    drivetrain: Optional[str] = None  # "AWD","4x4","FWD","RWD", etc.
    seats: Optional[int] = None
    rows: Optional[int] = None
    comfort_tech_score: Optional[float] = None  # 0–1 (features: cámara, CarPlay, etc.)

    # Para filtros blandos (si luego quieres):
    make: Optional[str] = None
    model: Optional[str] = None
    trim: Optional[str] = None

    extra: Optional[Dict[str, Any]] = None


class ListingWithScore(BaseModel):
    listing: ListingIn
    score: float
    sub_scores: Dict[str, float]      # score por subcriterio
    group_scores: Dict[str, float]    # contribución por grupo
    weights_sub: Dict[str, float]     # pesos globales por subcriterio
    weights_groups: Dict[str, float]  # pesos de grupos


class MatchFilters(BaseModel):
    # Qué tipos de edad acepta el usuario
    age_categories_allowed: Optional[List[str]] = None  # ["new","used","cpo"]

    # Año
    min_year: Optional[int] = None
    max_year: Optional[int] = None

    # Asientos / filas
    required_rows: Optional[int] = None  # si se requiere 3 filas, por ej.

    # Tracción
    required_drivetrains: Optional[List[str]] = None  # ["AWD","4x4"], etc.

    # Marca / modelo / trim
    allowed_makes: Optional[List[str]] = None
    allowed_models: Optional[List[str]] = None
    allowed_trims: Optional[List[str]] = None


class MatchRequest(BaseModel):
    """
    Petición para evaluar y ordenar autos según preferencias.
    """
    listings: List[ListingIn]

    filters: Optional[MatchFilters] = None

    # Importancia 1–5 de cada grupo principal
    # Claves esperadas: "economic", "condition", "risk", "fit"
    criteria_importance_main: Optional[Dict[str, int]] = None

    # Importancia 1–5 de cada subcriterio dentro de su grupo
    # Ejemplo:
    # {
    #   "economic": { "price": 5, "fuel_efficiency": 3 },
    #   "condition": { "miles": 5, "year": 3, "age_category": 4, "mechanical_state": 3 },
    #   "risk": {...},
    #   "fit": {...}
    # }
    criteria_importance_sub: Optional[Dict[str, Dict[str, int]]] = None


class MatchResponse(BaseModel):
    results: List[ListingWithScore]

class ScrapeUrlsRequest(BaseModel):
    urls: List[str]