from pydantic import BaseModel, EmailStr
from typing import Optional, Dict

class BuyerProfileBase(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    location: Optional[str] = None
    budget_min: Optional[int] = None
    budget_max: Optional[int] = None
    criteria: Optional[Dict[str, int]] = None  # ej: {"price": 5, "mileage": 4}

class BuyerProfileCreate(BuyerProfileBase):
    pass

class BuyerProfileOut(BuyerProfileBase):
    id: int

    class Config:
        orm_mode = True
