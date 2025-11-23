from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base
from app.models.listing import Listing



class Lead(Base):
    __tablename__ = "leads"

    id = Column(Integer, primary_key=True, index=True)

    # Info del comprador
    buyer_name = Column(String, nullable=False)
    buyer_email = Column(String, nullable=False)
    buyer_phone = Column(String, nullable=True)
    buyer_notes = Column(String, nullable=True)

    # Referencia al auto seleccionado
    listing_id = Column(Integer, ForeignKey("listings.id"), nullable=False)
    listing = relationship(Listing)

    # Estado del lead
    status = Column(String, nullable=False, default="new")

    # NUEVO: fecha de creación
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

