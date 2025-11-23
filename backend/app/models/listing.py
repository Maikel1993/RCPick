from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from app.core.database import Base


class Listing(Base):
    __tablename__ = "listings"

    id = Column(Integer, primary_key=True, index=True)

    # FK al dealer (puede ser null en algunos casos)
    dealer_id = Column(Integer, ForeignKey("dealers.id"), nullable=True)
    dealer = relationship("Dealer", back_populates="listings")

    # Datos básicos
    price = Column(Integer, nullable=False)
    miles = Column(Integer, nullable=False)
    year = Column(Integer, nullable=False)

    # Nuevo / Usado / CPO
    age_category = Column(String, nullable=True)  # "new", "used", "cpo"

    # Estado legal / historial
    title_condition = Column(String, nullable=True)  # "clean", "rebuilt", "salvage", etc.
    accidents_count = Column(Integer, nullable=True)
    odometer_issue = Column(Boolean, nullable=True)
    recalls_open = Column(Integer, nullable=True)

    # Estado / comportamiento
    fuel_efficiency = Column(Float, nullable=True)  # mpg o km/l
    mechanical_state = Column(Float, nullable=True)  # 0–5
    safety_score = Column(Float, nullable=True)      # 0–5

    # Adecuación al uso
    drivetrain = Column(String, nullable=True)  # "AWD","4x4","FWD","RWD"
    seats = Column(Integer, nullable=True)
    rows = Column(Integer, nullable=True)
    comfort_tech_score = Column(Float, nullable=True)  # 0–1

    # Marca / modelo / trim
    make = Column(String, nullable=True)
    model = Column(String, nullable=True)
    trim = Column(String, nullable=True)
