from pydantic import BaseModel, EmailStr
from typing import Optional


class DealerBase(BaseModel):
    name: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    website: Optional[str] = None
    notes: Optional[str] = None


class DealerCreate(DealerBase):
    pass


class DealerOut(DealerBase):
    id: int

    class Config:
        orm_mode = True
