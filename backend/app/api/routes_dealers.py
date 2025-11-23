from fastapi import APIRouter, Depends, HTTPException
from typing import List
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.dealer import Dealer
from app.schemas.dealer import DealerCreate, DealerOut

router = APIRouter(
    prefix="/dealers",
    tags=["dealers"],
)


@router.post("/", response_model=DealerOut)
def create_dealer(payload: DealerCreate, db: Session = Depends(get_db)):
    dealer = Dealer(
        name=payload.name,
        email=payload.email,
        phone=payload.phone,
        city=payload.city,
        state=payload.state,
        website=payload.website,
        notes=payload.notes,
    )
    db.add(dealer)
    db.commit()
    db.refresh(dealer)
    return dealer


@router.get("/", response_model=List[DealerOut])
def list_dealers(db: Session = Depends(get_db)):
    dealers = db.query(Dealer).order_by(Dealer.id).all()
    return dealers


@router.get("/{dealer_id}", response_model=DealerOut)
def get_dealer(dealer_id: int, db: Session = Depends(get_db)):
    dealer = db.query(Dealer).filter(Dealer.id == dealer_id).first()
    if not dealer:
        raise HTTPException(status_code=404, detail="Dealer no encontrado")
    return dealer
