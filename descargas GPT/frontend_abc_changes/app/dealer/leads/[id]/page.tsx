
import Link from "next/link";
import { revalidatePath } from "next/cache";
import {
  getDealerLeadById,
  getLeadEvents,
  updateLeadStatus,
  LeadEvent,
} from "@/lib/api";

export const dynamic = "force-dynamic";

interface DealerLeadDetailPageProps {
  params: Promise<{ id: string }>;
}

const STATUS_OPTIONS = [
  "new",
  "sent_to_dealer",
  "contacted",
  "test_drive_scheduled",
  "sold",
  "lost",
];

function formatDate(value?: string) {
  if (!value) return "";
  const d = new Date(value);
  if (Number.isNaN(d.getTime())) return value ?? "";
  return d.toLocaleString();
}

export default async function DealerLeadDetailPage({
  params,
}: DealerLeadDetailPageProps) {
  const { id } = await params;

  const [lead, events] = await Promise.all([
    getDealerLeadById(id),
    getLeadEvents(id),
  ]);

  if (!lead) {
    return (
      <main className="container py-4">
        <div className="d-flex justify-content-between align-items-center mb-3">
          <h1 className="h4 mb-0">Lead #{id}</h1>
          <Link
            href="/dealer/leads"
            className="btn btn-outline-secondary btn-sm"
          >
            ← Volver a leads
          </Link>
        </div>

        <div className="alert alert-danger">
          No se encontró información para este lead.
        </div>
      </main>
    );
  }

  async function changeStatus(formData: FormData) {
    "use server";
    const newStatus = formData.get("status");
    if (typeof newStatus !== "string" || !newStatus) return;

    await updateLeadStatus(String(lead.id), newStatus);
    revalidatePath(`/dealer/leads/${lead.id}`);
  }

  const buyerName = lead.buyer_name ?? "N/D";
  const buyerContact = [lead.buyer_email, lead.buyer_phone]
    .filter(Boolean)
    .join(" · ");
  const vehicleTitle =
    lead.listing_title ||
    [lead.listing_year, lead.listing_make, lead.listing_model]
      .filter(Boolean)
      .join(" ") ||
    "N/D";
  const dealerName = lead.dealer_name || "N/D";

  return (
    <main className="container py-4">
      <div className="d-flex flex-column flex-md-row justify-content-between align-items-md-center mb-3 gap-2">
        <div>
          <h1 className="h4 mb-1">Lead #{lead.id} – Portal del dealer</h1>
          <p className="text-muted mb-0">
            Aquí ves los datos del cliente interesados en uno de tus vehículos,
            junto con el historial de eventos.
          </p>
        </div>
        <div className="d-flex gap-2">
          <span className="badge text-bg-secondary">
            Estado actual: {lead.status || "new"}
          </span>
          <Link
            href="/dealer/leads"
            className="btn btn-outline-secondary btn-sm"
          >
            ← Volver a leads
          </Link>
        </div>
      </div>

      {/* Top cards */}
      <div className="row g-3 mb-4">
        <div className="col-md-4">
          <div className="card h-100 shadow-sm">
            <div className="card-body">
              <h5 className="card-title mb-3">Cliente</h5>
              <p className="mb-1">
                <strong>Nombre: </strong>
                {buyerName}
              </p>
              <p className="mb-1">
                <strong>Contacto: </strong>
                {buyerContact || "N/D"}
              </p>
              <p className="mb-0">
                <strong>Notas: </strong>
                {lead.buyer_notes || "Sin notas del cliente."}
              </p>
            </div>
          </div>
        </div>

        <div className="col-md-4">
          <div className="card h-100 shadow-sm">
            <div className="card-body">
              <h5 className="card-title mb-3">Lead</h5>
              <p className="mb-1">
                <strong>ID: </strong>
                {lead.id}
              </p>
              <p className="mb-1">
                <strong>Creado: </strong>
                {formatDate(lead.created_at)}
              </p>
              <p className="mb-1">
                <strong>Estado: </strong>
                {lead.status || "new"}
              </p>
              <p className="mb-0">
                <strong>Listing ID: </strong>
                {lead.listing_id}
              </p>
            </div>
          </div>
        </div>

        <div className="col-md-4">
          <div className="card h-100 shadow-sm">
            <div className="card-body">
              <h5 className="card-title mb-3">Vehículo</h5>
              <p className="mb-1">
                <strong>Dealer: </strong>
                {dealerName}
              </p>
              <p className="mb-1">
                <strong>Vehículo: </strong>
                {vehicleTitle}
              </p>
              <p className="mb-0">
                <strong>Precio / millas: </strong>
                {lead.listing_price
                  ? `$${lead.listing_price.toLocaleString()}`
                  : "N/D"}{" "}
                {lead.listing_miles
                  ? ` · ${lead.listing_miles.toLocaleString()} mi`
                  : ""}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Acciones de estado */}
      <div className="card mb-4">
        <div className="card-body">
          <h5 className="card-title mb-3">Acciones del dealer</h5>
          <form action={changeStatus} className="row g-2 align-items-end">
            <div className="col-md-4">
              <label className="form-label mb-1 small">
                Actualizar estado del lead
              </label>
              <select
                name="status"
                defaultValue={lead.status || "new"}
                className="form-select form-select-sm"
              >
                {STATUS_OPTIONS.map((s) => (
                  <option key={s} value={s}>
                    {s}
                  </option>
                ))}
              </select>
            </div>
            <div className="col-md-2">
              <button
                type="submit"
                className="btn btn-sm btn-primary mt-3 mt-md-0"
              >
                Guardar
              </button>
            </div>
            <div className="col-md-6 small text-muted">
              El cambio de estado se registra automáticamente en el timeline.
            </div>
          </form>
        </div>
      </div>

      {/* Timeline de eventos */}
      <div className="row g-3">
        <div className="col-md-8">
          <div className="card mb-3">
            <div className="card-body">
              <h5 className="card-title mb-3">Timeline de eventos</h5>
              {events.length === 0 ? (
                <p className="text-muted mb-0">
                  Todavía no hay eventos registrados para este lead.
                </p>
              ) : (
                <ul className="list-group list-group-flush">
                  {events.map((event: LeadEvent) => (
                    <li
                      key={event.id}
                      className="list-group-item d-flex justify-content-between"
                    >
                      <div>
                        <div className="fw-semibold">{event.action}</div>
                        {event.description && (
                          <div className="small text-muted">
                            {event.description}
                          </div>
                        )}
                      </div>
                      <div className="small text-muted ms-3">
                        {formatDate(event.timestamp as unknown as string)}
                      </div>
                    </li>
                  ))}
                </ul>
              )}
            </div>
          </div>
        </div>

        {/* JSON bruto para debug */}
        <div className="col-md-4">
          <div className="card mb-3">
            <div className="card-body">
              <h5 className="card-title mb-3">Payload completo</h5>
              <pre className="small mb-0">
                {JSON.stringify(lead, null, 2)}
              </pre>
            </div>
          </div>
        </div>
      </div>
    </main>
  );
}
