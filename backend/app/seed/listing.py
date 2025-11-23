"""Script sencillo para poblar la base de datos con listings de prueba.

Ejemplo de ejecución (desde la carpeta backend/):

    uvicorn app.main:app --reload  # en otra terminal

    # Crear datos de prueba
    python -m app.seed_listings

"""

from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.models.dealer import Dealer
from app.models.listing import Listing


def _get_or_create_demo_dealer(db: Session) -> Dealer:
    dealer = db.query(Dealer).filter(Dealer.name == "Demo Dealer").first()
    if dealer:
        return dealer

    dealer = Dealer(
        name="Demo Dealer",
        city="Demo City",
        state="KS",
        phone="555-000-0000",
        email="demo@dealer.com",
    )
    db.add(dealer)
    db.commit()
    db.refresh(dealer)
    return dealer


def seed_listings(db: Session) -> None:
    dealer = _get_or_create_demo_dealer(db)

    # Limpia opcionalmente los listings anteriores del dealer demo
    # db.query(Listing).filter(Listing.dealer_id == dealer.id).delete()
    # db.commit()

    demo_listings = [
        # SUVs 3 filas
        Listing(
            dealer_id=dealer.id,
            year=2016,
            make="Honda",
            model="Pilot",
            trim="EX-L",
            body_style="SUV",
            rows=3,
            seats=8,
            drivetrain="FWD",
            fuel_type="gasoline",
            mileage=105000,
            price=18990,
            condition="used",
            third_row=True,
            awd=False,
            has_backup_camera=True,
            has_apple_carplay=False,
            has_android_auto=False,
            photo_url="https://example.com/pilot-2016.jpg",
            created_source="seed_script",
        ),
        Listing(
            dealer_id=dealer.id,
            year=2019,
            make="Honda",
            model="Pilot",
            trim="EX-L",
            body_style="SUV",
            rows=3,
            seats=8,
            drivetrain="AWD",
            fuel_type="gasoline",
            mileage=72000,
            price=27990,
            condition="used",
            third_row=True,
            awd=True,
            has_backup_camera=True,
            has_apple_carplay=True,
            has_android_auto=True,
            has_sunroof=True,
            photo_url="https://example.com/pilot-2019.jpg",
            created_source="seed_script",
        ),
        Listing(
            dealer_id=dealer.id,
            year=2020,
            make="Toyota",
            model="Highlander",
            trim="XLE",
            body_style="SUV",
            rows=3,
            seats=7,
            drivetrain="AWD",
            fuel_type="gasoline",
            mileage=55000,
            price=32990,
            condition="used",
            third_row=True,
            awd=True,
            has_backup_camera=True,
            has_apple_carplay=True,
            has_android_auto=True,
            photo_url="https://example.com/highlander-2020.jpg",
            created_source="seed_script",
        ),
        Listing(
            dealer_id=dealer.id,
            year=2021,
            make="Kia",
            model="Telluride",
            trim="EX",
            body_style="SUV",
            rows=3,
            seats=7,
            drivetrain="AWD",
            fuel_type="gasoline",
            mileage=41000,
            price=38990,
            condition="used",
            third_row=True,
            awd=True,
            has_backup_camera=True,
            has_apple_carplay=True,
            has_android_auto=True,
            has_sunroof=True,
            photo_url="https://example.com/telluride-2021.jpg",
            created_source="seed_script",
        ),
        # SUVs 2 filas
        Listing(
            dealer_id=dealer.id,
            year=2018,
            make="Honda",
            model="CR-V",
            trim="EX",
            body_style="SUV",
            rows=2,
            seats=5,
            drivetrain="AWD",
            fuel_type="gasoline",
            mileage=68000,
            price=22990,
            condition="used",
            third_row=False,
            awd=True,
            has_backup_camera=True,
            has_apple_carplay=True,
            has_android_auto=True,
            photo_url="https://example.com/crv-2018.jpg",
            created_source="seed_script",
        ),
        Listing(
            dealer_id=dealer.id,
            year=2022,
            make="Toyota",
            model="RAV4",
            trim="XLE",
            body_style="SUV",
            rows=2,
            seats=5,
            drivetrain="AWD",
            fuel_type="hybrid",
            mileage=24000,
            price=33990,
            condition="used",
            third_row=False,
            awd=True,
            has_backup_camera=True,
            has_apple_carplay=True,
            has_android_auto=True,
            photo_url="https://example.com/rav4-2022.jpg",
            created_source="seed_script",
        ),
        # Sedanes
        Listing(
            dealer_id=dealer.id,
            year=2019,
            make="Honda",
            model="Accord",
            trim="Sport",
            body_style="Sedan",
            rows=2,
            seats=5,
            drivetrain="FWD",
            fuel_type="gasoline",
            mileage=45000,
            price=24990,
            condition="used",
            third_row=False,
            awd=False,
            has_backup_camera=True,
            photo_url="https://example.com/accord-2019.jpg",
            created_source="seed_script",
        ),
        Listing(
            dealer_id=dealer.id,
            year=2020,
            make="Toyota",
            model="Camry",
            trim="SE",
            body_style="Sedan",
            rows=2,
            seats=5,
            drivetrain="FWD",
            fuel_type="gasoline",
            mileage=38000,
            price=25990,
            condition="used",
            third_row=False,
            awd=False,
            has_backup_camera=True,
            photo_url="https://example.com/camry-2020.jpg",
            created_source="seed_script",
        ),
        # Pickup
        Listing(
            dealer_id=dealer.id,
            year=2017,
            make="Ford",
            model="F-150",
            trim="XLT",
            body_style="Truck",
            rows=2,
            seats=5,
            drivetrain="4WD",
            fuel_type="gasoline",
            mileage=89000,
            price=29990,
            condition="used",
            third_row=False,
            awd=True,
            has_backup_camera=True,
            photo_url="https://example.com/f150-2017.jpg",
            created_source="seed_script",
        ),
        # Compacto económico
        Listing(
            dealer_id=dealer.id,
            year=2016,
            make="Toyota",
            model="Corolla",
            trim="LE",
            body_style="Sedan",
            rows=2,
            seats=5,
            drivetrain="FWD",
            fuel_type="gasoline",
            mileage=98000,
            price=13990,
            condition="used",
            third_row=False,
            awd=False,
            has_backup_camera=True,
            photo_url="https://example.com/corolla-2016.jpg",
            created_source="seed_script",
        ),
    ]

    db.add_all(demo_listings)
    db.commit()

    print(f"Se han insertado {len(demo_listings)} listings de prueba para el dealer {dealer.name} (ID {dealer.id}).")


def main() -> None:
    db = SessionLocal()
    try:
        seed_listings(db)
    finally:
        db.close()


if __name__ == "__main__":
    main()
