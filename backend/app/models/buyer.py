from sqlalchemy import Column, Integer, String
from app.core.database import Base

class BuyerProfile(Base):
    __tablename__ = "buyer_profiles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=True)
    email = Column(String, nullable=True)
    location = Column(String, nullable=True)

    budget_min = Column(Integer, nullable=True)
    budget_max = Column(Integer, nullable=True)

    # Podríamos guardar los criterios y pesos como JSON en el futuro;
    # por ahora algo simple:
    criteria_raw = Column(String, nullable=True)  # JSON en texto si quieres
