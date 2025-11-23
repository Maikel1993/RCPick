
import { getAdminLeads } from "@/lib/api";
import AdminLeadsClient, { Lead as AdminLead } from "./AdminLeadsClient";

export const dynamic = "force-dynamic";

function formatNumber(value: unknown) {
  const n = typeof value === "number" ? value : Number(value ?? 0);
  if (Number.isNaN(n)) return 0;
  return n;
}

export default async function AdminLeadsPage() {
  const apiBase =
    process.env.NEXT_PUBLIC_API_BASE_URL || "http://127.0.0.1:8000";

  // Cargamos leads + resumen en paralelo
  const [data, summary] = await Promise.all([
    getAdminLeads(),
    fetch(`${apiBase}/leads/admin/summary`, { cache: "no-store" })
      .then(async (res) => {
        if (!res.ok) {
          // Si el backend devuelve HTML o texto de error, evitamos romper el frontend
          try {
            const text = await res.text();
            console.error("Error summary:", res.status, text);
          } catch (e) {
            console.error("Error summary:", res.status);
          }
          return null;
        }
        try {
          return await res.json();
        } catch (err) {
          console.error("Error parseando JSON de summary", err);
          return null;
        }
      })
      .catch((err) => {
        console.error("Error cargando summary", err);
        return null;
      }),
  ]);

  const leads: AdminLead[] = data?.items ?? [];

  return (
    <main className="container py-4">
      <div className="d-flex justify-content-between align-items-center mb-3">
        <div>
          <h1 className="h4 mb-1">Leads (Admin)</h1>
          <p className="text-muted mb-0">
            Dashboard de leads de RCPick. Aquí ves volumen, score e intereses y
            puedes navegar a la vista de detalle / dealer.
          </p>
        </div>
        <span className="badge bg-primary-subtle text-primary-emphasis">
          Total: {formatNumber(summary?.total ?? leads.length)}
        </span>
      </div>

      {/* Tarjetas resumen */}
      {summary && (
        <div className="row mb-4 g-2">
          <div className="col-md-3 mb-2">
            <div className="card shadow-sm">
              <div className="card-body py-2">
                <div className="small text-muted">Leads totales</div>
                <div className="fs-5 fw-bold">{summary.total ?? 0}</div>
              </div>
            </div>
          </div>
          <div className="col-md-3 mb-2">
            <div className="card shadow-sm">
              <div className="card-body py-2">
                <div className="small text-muted">Hoy</div>
                <div className="fs-5 fw-bold">{summary.today ?? 0}</div>
              </div>
            </div>
          </div>
          <div className="col-md-3 mb-2">
            <div className="card shadow-sm">
              <div className="card-body py-2">
                <div className="small text-muted">Score promedio</div>
                <div className="fs-5 fw-bold">
                  {summary.avg_score ? summary.avg_score.toFixed(1) : "N/D"}
                </div>
              </div>
            </div>
          </div>
          <div className="col-md-3 mb-2">
            <div className="card shadow-sm">
              <div className="card-body py-2">
                <div className="small text-muted">High value</div>
                <div className="fs-5 fw-bold">{summary.high_value ?? 0}</div>
              </div>
            </div>
          </div>
        </div>
      )}

      {leads.length === 0 ? (
        <div className="alert alert-light border text-muted">
          No hay leads todavía.
        </div>
      ) : (
        <AdminLeadsClient leads={leads} />
      )}
    </main>
  );
}
