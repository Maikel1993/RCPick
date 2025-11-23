from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
import json

from app.core.database import get_db
from app.models.buyer import BuyerProfile
from app.schemas.buyer import BuyerProfileCreate, BuyerProfileOut

# ESTA variable es la que intenta importar main.py
router = APIRouter(
    prefix="/buyer-profiles",
    tags=["buyer-profiles"]
)

@router.post("/", response_model=BuyerProfileOut)
def create_buyer_profile(
    payload: BuyerProfileCreate,
    db: Session = Depends(get_db)
):
    db_obj = BuyerProfile(
        name=payload.name,
        email=payload.email,
        location=payload.location,
        budget_min=payload.budget_min,
        budget_max=payload.budget_max,
        criteria_raw=json.dumps(payload.criteria or {})
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

@router.get("/", response_model=List[BuyerProfileOut])
def list_buyer_profiles(
    db: Session = Depends(get_db),
    limit: int = 50
):
    profiles = db.query(BuyerProfile).limit(limit).all()
    return profiles

@router.get("/{profile_id}", response_model=BuyerProfileOut)
def get_buyer_profile(
    profile_id: int,
    db: Session = Depends(get_db)
):
    profile = db.query(BuyerProfile).filter(BuyerProfile.id == profile_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Perfil no encontrado")
    return profile

