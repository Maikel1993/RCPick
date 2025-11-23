from app.models.dealer import Dealer
from app.models.lead import Lead
from app.models.listing import Listing


def build_lead_email(dealer: Dealer, lead: Lead, listing: Listing) -> dict:
    """
    Construye un asunto y cuerpo de correo para enviar un lead al dealer.
    No envía nada realmente, solo devuelve el contenido.
    """
    subject = f"Nuevo lead desde Autofinder - {listing.year} {listing.make} {listing.model}"

    body_lines = [
        f"Hola {dealer.name},",
        "",
        "Tienes un nuevo cliente interesado en uno de tus vehículos a través de Autofinder.",
        "",
        "Datos del cliente:",
        f"  Nombre : {lead.buyer_name}",
        f"  Email  : {lead.buyer_email}",
        f"  Teléfono: {lead.buyer_phone or 'No proporcionado'}",
        "",
        "Vehículo de interés:",
        f"  ID interno : {listing.id}",
        f"  {listing.year} {listing.make} {listing.model} {listing.trim or ''}".strip(),
        f"  Precio     : ${listing.price:,}",
        f"  Millas     : {listing.miles:,} mi",
        "",
        "Mensaje / notas del cliente:",
        f"  {lead.buyer_notes or 'Sin notas adicionales.'}",
        "",
        "Por favor contacta al cliente lo antes posible para concretar la visita o la prueba de manejo.",
        "",
        "— Equipo Autofinder (simulación de email, aún no se envía realmente)",
    ]

    body = "\n".join(body_lines)

    return {
        "to": dealer.email,
        "subject": subject,
        "body": body,
    }


def send_email_simulation(email_data: dict) -> None:
    """
    Simula el envío de un correo.
    Por ahora solo lo imprime en la consola del backend.
    """
    print("=== SIMULACIÓN DE ENVÍO DE EMAIL AL DEALER ===")
    print(f"Para   : {email_data.get('to')}")
    print(f"Asunto : {email_data.get('subject')}")
    print("Cuerpo :")
    print(email_data.get("body"))
    print("=== FIN SIMULACIÓN EMAIL ===")
