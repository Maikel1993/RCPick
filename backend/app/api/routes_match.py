from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.match import (
    MatchRequest,
    MatchResponse,
    ListingScoreOut,
)
from app.services.ahp import rank_listings_with_ahp

router = APIRouter(
    prefix="/match",
    tags=["match"],
)


@router.post("/", response_model=MatchResponse)
def match_cars(req: MatchRequest, db: Session = Depends(get_db)):
    """
    Endpoint que aplica el algoritmo tipo AHP a los listings.
    Devuelve un 'puntaje' de 0 a 100 para cada vehículo.
    """
    results_raw = rank_listings_with_ahp(
        db=db,
        filters=req.filters,
        weights=req.weights,
        body_style_preference=req.body_style_preference,
        limit_results=req.limit_results,
    )

    total_candidates = len(results_raw)  # ya vienen filtrados y limitados en la función

    items: List[ListingScoreOut] = []
    for r in results_raw:
        items.append(
            ListingScoreOut(
                listing_id=r["listing_id"],
                score=r["score"],
                score_100=r["score_100"],
                year=r.get("year"),
                make=r.get("make"),
                model=r.get("model"),
                trim=r.get("trim"),
                price=r.get("price"),
                miles=r.get("miles"),
                body_style=r.get("body_style"),
                condition=r.get("condition"),
                dealer_name=r.get("dealer_name"),
                source=r.get("source"),
                url=r.get("url"),
                created_at=r.get("created_at"),
            )
        )

    return MatchResponse(
        total_candidates=total_candidates,
        returned=len(items),
        results=items,
    )
