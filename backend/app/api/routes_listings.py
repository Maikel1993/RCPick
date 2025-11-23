from fastapi import APIRouter, Depends
from typing import List
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.listing import Listing
from app.schemas.listing import ListingIn, ScrapeUrlsRequest
from app.services.scraper import scrape_and_save_listings

router = APIRouter(
    prefix="/listings",
    tags=["listings"]
)


def _to_schema(l: Listing) -> ListingIn:
    """
    Convierte un objeto Listing (SQLAlchemy) en ListingIn (Pydantic).
    El id de la BD (int) lo devolvemos como string.
    """
    return ListingIn(
        id=str(l.id),
        price=l.price,
        miles=l.miles,
        year=l.year,
        age_category=l.age_category,
        title_condition=l.title_condition,
        accidents_count=l.accidents_count,
        odometer_issue=l.odometer_issue,
        recalls_open=l.recalls_open,
        fuel_efficiency=l.fuel_efficiency,
        mechanical_state=l.mechanical_state,
        safety_score=l.safety_score,
        drivetrain=l.drivetrain,
        seats=l.seats,
        rows=l.rows,
        comfort_tech_score=l.comfort_tech_score,
        make=l.make,
        model=l.model,
        trim=l.trim,
        extra=None,
    )


from app.models.dealer import Dealer
...
def _seed_demo_data(db: Session):
    """
    Inserta 1 dealer y 3 listings de ejemplo en la BD si la tabla está vacía.
    """

    # Crear dealer de demo
    demo_dealer = Dealer(
        name="Demo Dealer Miami",
        email="ventas@demodealer.com",
        phone="+1-305-000-0000",
        city="Miami",
        state="FL",
        website="https://demodealer.example.com",
        notes="Dealer de prueba para el entorno de desarrollo.",
    )
    db.add(demo_dealer)
    db.commit()
    db.refresh(demo_dealer)

    demo_listings = [
        Listing(
            dealer_id=demo_dealer.id,
            price=13000,
            miles=90000,
            year=2017,
            age_category="used",
            title_condition="clean",
            accidents_count=0,
            odometer_issue=False,
            recalls_open=0,
            fuel_efficiency=27,
            mechanical_state=4.0,
            safety_score=4.5,
            drivetrain="AWD",
            seats=7,
            rows=3,
            comfort_tech_score=0.8,
            make="Honda",
            model="Pilot",
            trim="EX-L",
        ),
        Listing(
            dealer_id=demo_dealer.id,
            price=11500,
            miles=120000,
            year=2015,
            age_category="used",
            title_condition="clean",
            accidents_count=1,
            odometer_issue=False,
            recalls_open=0,
            fuel_efficiency=25,
            mechanical_state=3.5,
            safety_score=4.0,
            drivetrain="FWD",
            seats=7,
            rows=3,
            comfort_tech_score=0.6,
            make="Toyota",
            model="Highlander",
            trim="LE",
        ),
        Listing(
            dealer_id=demo_dealer.id,
            price=16500,
            miles=70000,
            year=2018,
            age_category="cpo",
            title_condition="clean",
            accidents_count=0,
            odometer_issue=False,
            recalls_open=0,
            fuel_efficiency=29,
            mechanical_state=4.5,
            safety_score=5.0,
            drivetrain="AWD",
            seats=7,
            rows=3,
            comfort_tech_score=0.9,
            make="Kia",
            model="Sorento",
            trim="EX",
        ),
    ]

    db.add_all(demo_listings)
    db.commit()


@router.get("/demo", response_model=List[ListingIn])
def get_demo_listings(db: Session = Depends(get_db)):
    """
    Devuelve listings desde la BD.
    Si la tabla está vacía, primero inserta 3 registros de prueba.
    """
    existing = db.query(Listing).all()
    if not existing:
        _seed_demo_data(db)
        existing = db.query(Listing).all()

    return [_to_schema(l) for l in existing]


@router.get("/", response_model=List[ListingIn])
def list_all_listings(db: Session = Depends(get_db)):
    """
    Devuelve todos los listings de la BD.
    """
    existing = db.query(Listing).all()
    return [_to_schema(l) for l in existing]


@router.post("/from-urls", response_model=List[ListingIn])
def import_from_urls(payload: ScrapeUrlsRequest, db: Session = Depends(get_db)):
    """
    Recibe una lista de URLs, ejecuta el scraper para cada una,
    guarda los resultados en la BD y devuelve los listings creados.
    """
    created: List[Listing] = []

    for url in payload.urls:
        scraped = scrape_and_save_listings(db, url)
        created.extend(scraped)

    return [_to_schema(l) for l in created]
