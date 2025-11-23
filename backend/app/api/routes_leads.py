from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.lead import Lead
from app.models.listing import Listing
from app.models.dealer import Dealer
from app.models.lead_event import LeadEvent
from app.schemas.lead import (
    LeadCreate,
    LeadOut,
    LeadSendResponse,
    LeadAdminOut,
    LeadAdminPage,
    LeadDetailOut,
    LeadEventOut,
    LeadStatusUpdate,
)

router = APIRouter(
    prefix="/leads",
    tags=["leads"],
)


# ------------------------------
# CREATE LEAD
# ------------------------------
@router.post("/", response_model=LeadOut)
def create_lead(lead_in: LeadCreate, db: Session = Depends(get_db)):
    lead = Lead(
        buyer_name=lead_in.buyer_name,
        buyer_email=lead_in.buyer_email,
        buyer_phone=lead_in.buyer_phone,
        buyer_notes=lead_in.buyer_notes,
        listing_id=int(lead_in.listing_id),
        status="new",
        created_at=datetime.utcnow(),
    )

    db.add(lead)
    db.commit()
    db.refresh(lead)

    event = LeadEvent(
        lead_id=lead.id,
        action="created",
        description="Lead creado por el cliente",
        timestamp=datetime.utcnow(),
    )
    db.add(event)
    db.commit()

    return lead


# ------------------------------
# ADMIN LIST PAGINATED
# ------------------------------
@router.get("/admin", response_model=LeadAdminPage)
def list_leads_admin(
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=200),
):
    base_query = db.query(Lead).order_by(Lead.created_at.desc())

    total = base_query.count()
    pages = (total + limit - 1) // limit if total > 0 else 1
    if page > pages:
        page = pages

    leads = (
        base_query.offset((page - 1) * limit)
        .limit(limit)
        .all()
    )

    items: List[LeadAdminOut] = []

    for l in leads:
        listing = db.query(Listing).filter(Listing.id == l.listing_id).first()
        dealer = (
            db.query(Dealer).filter(Dealer.id == listing.dealer_id).first()
            if listing
            else None
        )

        if listing:
            base = f"{listing.year} {listing.make} {listing.model}".strip()
            listing_label = f"{base} {listing.trim or ''}".strip()
        else:
            listing_label = None

        items.append(
            LeadAdminOut(
                id=l.id,
                buyer_name=l.buyer_name,
                buyer_email=l.buyer_email,
                buyer_phone=l.buyer_phone,
                buyer_notes=l.buyer_notes,
                listing_id=l.listing_id,
                status=l.status,
                created_at=l.created_at,
                listing_label=listing_label,
                dealer_name=dealer.name if dealer else None,
            )
        )

    return LeadAdminPage(
        items=items,
        total=total,
        page=page,
        pages=pages,
    )


# ------------------------------
# SEND LEAD TO DEALER
# ------------------------------
@router.post("/{lead_id}/send-to-dealer", response_model=LeadSendResponse)
def send_lead_to_dealer(lead_id: int, db: Session = Depends(get_db)):
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead no existe")

    listing = db.query(Listing).filter(Listing.id == lead.listing_id).first()
    if not listing:
        raise HTTPException(status_code=404, detail="Listing no existe")

    dealer = db.query(Dealer).filter(Dealer.id == listing.dealer_id).first()
    if not dealer:
        raise HTTPException(status_code=404, detail="Dealer no existe")

    lead.status = "sent_to_dealer"
    db.commit()
    db.refresh(lead)

    event = LeadEvent(
        lead_id=lead.id,
        action="sent_to_dealer",
        description=f"Lead enviado al dealer {dealer.name}",
        timestamp=datetime.utcnow(),
    )
    db.add(event)
    db.commit()

    email_subject = f"Nuevo lead para {listing.year} {listing.make} {listing.model}"
    email_body = (
        f"Cliente: {lead.buyer_name}\n"
        f"Email: {lead.buyer_email}\n"
        f"Teléfono: {lead.buyer_phone or 'No proporcionado'}\n"
        f"Notas: {lead.buyer_notes or 'Sin notas'}\n\n"
        f"Vehículo: {listing.year} {listing.make} {listing.model} {listing.trim or ''}\n"
        f"Precio: {listing.price}\n"
        f"Millas: {listing.miles}\n"
        f"ID interno: {listing.id}"
    )

    return LeadSendResponse(
        lead=lead,
        dealer_name=dealer.name,
        dealer_email=dealer.email,
        dealer_phone=dealer.phone,
        email_subject=email_subject,
        email_body=email_body,
    )


# ------------------------------
# DETAIL
# ------------------------------
@router.get("/{lead_id}/detail", response_model=LeadDetailOut)
def get_lead_detail(lead_id: int, db: Session = Depends(get_db)):
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead no existe")

    listing = db.query(Listing).filter(Listing.id == lead.listing_id).first()
    dealer = (
        db.query(Dealer).filter(Dealer.id == listing.dealer_id).first()
        if listing
        else None
    )

    return LeadDetailOut(
        id=lead.id,
        buyer_name=lead.buyer_name,
        buyer_email=lead.buyer_email,
        buyer_phone=lead.buyer_phone,
        buyer_notes=lead.buyer_notes,
        listing_id=lead.listing_id,
        status=lead.status,
        created_at=lead.created_at,
        listing_year=listing.year if listing else None,
        listing_make=listing.make if listing else None,
        listing_model=listing.model if listing else None,
        listing_trim=listing.trim if listing else None,
        listing_price=listing.price if listing else None,
        listing_miles=listing.miles if listing else None,
        dealer_name=dealer.name if dealer else None,
        dealer_email=dealer.email if dealer else None,
        dealer_phone=dealer.phone if dealer else None,
        dealer_city=dealer.city if dealer else None,
        dealer_state=dealer.state if dealer else None,
    )


# ------------------------------
# TIMELINE / EVENTS
# ------------------------------
@router.get("/{lead_id}/events", response_model=List[LeadEventOut])
def get_lead_events(lead_id: int, db: Session = Depends(get_db)):
    events = (
        db.query(LeadEvent)
        .filter(LeadEvent.lead_id == lead_id)
        .order_by(LeadEvent.timestamp.desc())
        .all()
    )

    return [
        LeadEventOut(
            id=e.id,
            lead_id=e.lead_id,
            action=e.action,
            description=e.description,
            timestamp=e.timestamp,
        )
        for e in events
    ]


# ------------------------------
# UPDATE STATUS (dealer / admin)
# ------------------------------
@router.patch("/{lead_id}/status", response_model=LeadOut)
def update_lead_status(
    lead_id: int,
    payload: LeadStatusUpdate,
    db: Session = Depends(get_db),
):
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead no existe")

    old_status = lead.status
    lead.status = payload.status
    db.commit()
    db.refresh(lead)

    event = LeadEvent(
        lead_id=lead.id,
        action="status_changed",
        description=f"Estado cambiado de '{old_status}' a '{payload.status}'",
        timestamp=datetime.utcnow(),
    )
    db.add(event)
    db.commit()

    return lead


# ------------------------------
# LEADS VISTA DEALER
# ------------------------------
@router.get("/dealer/{dealer_id}", response_model=List[LeadAdminOut])
def get_dealer_leads(dealer_id: int, db: Session = Depends(get_db)):
    """
    Devuelve todos los leads asociados a un dealer concreto.
    Se usa para la vista del portal del dealer.
    """
    listings = db.query(Listing).filter(Listing.dealer_id == dealer_id).all()
    listing_ids = [l.id for l in listings]

    if not listing_ids:
        return []

    leads = (
        db.query(Lead)
        .filter(Lead.listing_id.in_(listing_ids))
        .order_by(Lead.created_at.desc())
        .all()
    )

    dealer = db.query(Dealer).filter(Dealer.id == dealer_id).first()

    results: List[LeadAdminOut] = []
    for lead in leads:
        listing = next((l for l in listings if l.id == lead.listing_id), None)
        if listing:
            base = f"{listing.year} {listing.make} {listing.model}".strip()
            listing_label = f"{base} {listing.trim or ''}".strip()
        else:
            listing_label = None

        results.append(
            LeadAdminOut(
                id=lead.id,
                buyer_name=lead.buyer_name,
                buyer_email=lead.buyer_email,
                buyer_phone=lead.buyer_phone,
                buyer_notes=lead.buyer_notes,
                listing_id=lead.listing_id,
                status=lead.status,
                created_at=lead.created_at,
                listing_label=listing_label,
                dealer_name=dealer.name if dealer else None,
            )
        )

    return results



# === Summary endpoint for admin leads ===
@router.get("/admin/summary", response_model=dict)
def get_leads_summary(db: Session = Depends(get_db)):
    """Resumen simple de leads para el panel admin.

    Esta implementación es defensiva: funciona aunque el modelo Lead
    no tenga todavía campos como score_100 o flags de monetización.
    """
    from datetime import datetime
    from sqlalchemy import func

    total = db.query(Lead).count()

    # Conteo de leads creados hoy (usando created_at si existe)
    today_start = datetime.utcnow().replace(
        hour=0, minute=0, second=0, microsecond=0
    )

    if hasattr(Lead, "created_at"):
        today = db.query(Lead).filter(Lead.created_at >= today_start).count()
    else:
        today = 0

    # Promedio de score si existe el campo score_100
    if hasattr(Lead, "score_100"):
        avg_score = db.query(func.avg(getattr(Lead, "score_100"))).scalar() or 0.0
    else:
        avg_score = 0.0

    # Flags de monetización: si las columnas no existen devolvemos 0
    def safe_count(attr_name: str) -> int:
        if hasattr(Lead, attr_name):
            return db.query(Lead).filter(getattr(Lead, attr_name) == True).count()  # type: ignore
        return 0

    financing = safe_count("needs_financing")
    insurance = safe_count("wants_insurance")
    warranty = safe_count("wants_warranty")

    # Score >= 80 e high_value sólo si existe score_100
    if hasattr(Lead, "score_100"):
        score80 = db.query(Lead).filter(getattr(Lead, "score_100") >= 80).count()
        if any(hasattr(Lead, name) for name in ["needs_financing", "wants_insurance", "wants_warranty"]):
            query = db.query(Lead).filter(getattr(Lead, "score_100") >= 80)
            if hasattr(Lead, "needs_financing"):
                query = query.filter(getattr(Lead, "needs_financing") == True)  # type: ignore
            if hasattr(Lead, "wants_insurance"):
                query = query.union(
                    db.query(Lead).filter(getattr(Lead, "score_100") >= 80).filter(
                        getattr(Lead, "wants_insurance") == True  # type: ignore
                    )
                )
            if hasattr(Lead, "wants_warranty"):
                query = query.union(
                    db.query(Lead).filter(getattr(Lead, "score_100") >= 80).filter(
                        getattr(Lead, "wants_warranty") == True  # type: ignore
                    )
                )
            high_value = query.count()
        else:
            high_value = 0
    else:
        score80 = 0
        high_value = 0

    return {
        "total": int(total),
        "today": int(today),
        "avg_score": float(avg_score),
        "financing": int(financing),
        "insurance": int(insurance),
        "warranty": int(warranty),
        "score80": int(score80),
        "high_value": int(high_value),
    }
