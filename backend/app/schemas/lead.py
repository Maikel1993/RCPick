from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, EmailStr


# ---------- CREATE ----------

class LeadCreate(BaseModel):
    buyer_name: str
    buyer_email: EmailStr
    buyer_phone: Optional[str] = None
    buyer_notes: Optional[str] = None
    listing_id: str  # llega como string desde el frontend


# ---------- BASE / OUT ----------

class LeadOut(BaseModel):
    id: int
    buyer_name: str
    buyer_email: EmailStr
    buyer_phone: Optional[str] = None
    buyer_notes: Optional[str] = None
    listing_id: int
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


# ---------- SEND TO DEALER ----------

class LeadSendResponse(BaseModel):
    lead: LeadOut
    dealer_name: Optional[str] = None
    dealer_email: Optional[EmailStr] = None
    dealer_phone: Optional[str] = None

    email_subject: Optional[str] = None
    email_body: Optional[str] = None


# ---------- ADMIN LIST ----------

class LeadAdminOut(BaseModel):
    id: int
    buyer_name: str
    buyer_email: EmailStr
    buyer_phone: Optional[str] = None
    buyer_notes: Optional[str] = None
    listing_id: int
    status: str
    created_at: datetime

    listing_label: Optional[str] = None
    dealer_name: Optional[str] = None

    class Config:
        from_attributes = True


class LeadAdminPage(BaseModel):
    items: List[LeadAdminOut]
    total: int
    page: int
    pages: int


# ---------- DETAIL ----------

class LeadDetailOut(BaseModel):
    id: int
    buyer_name: str
    buyer_email: EmailStr
    buyer_phone: Optional[str] = None
    buyer_notes: Optional[str] = None
    listing_id: int
    status: str
    created_at: datetime

    # Vehículo
    listing_year: Optional[int] = None
    listing_make: Optional[str] = None
    listing_model: Optional[str] = None
    listing_trim: Optional[str] = None
    listing_price: Optional[int] = None
    listing_miles: Optional[int] = None

    # Dealer
    dealer_name: Optional[str] = None
    dealer_email: Optional[EmailStr] = None
    dealer_phone: Optional[str] = None
    dealer_city: Optional[str] = None
    dealer_state: Optional[str] = None

    class Config:
        from_attributes = True


# ---------- EVENTS / TIMELINE ----------

class LeadEventOut(BaseModel):
    id: int
    lead_id: int
    action: str
    description: Optional[str] = None
    timestamp: datetime

    class Config:
        from_attributes = True


# ---------- STATUS UPDATE (dealer / admin) ----------

class LeadStatusUpdate(BaseModel):
    status: str  # ej: "contacted", "test_drive_scheduled", "sold", etc.
