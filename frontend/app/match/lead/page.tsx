"use client";

import "bootstrap/dist/css/bootstrap.min.css";
import { FormEvent, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { createLead } from "@/lib/api";

export default function MatchLeadPage() {
  const router = useRouter();
  const searchParams = useSearchParams();

  const listingId = searchParams.get("listing_id");
  const listingTitle = searchParams.get("title") || "Vehículo seleccionado";

  const [buyerName, setBuyerName] = useState("");
  const [buyerEmail, setBuyerEmail] = useState("");
  const [buyerPhone, setBuyerPhone] = useState("");
  const [buyerNotes, setBuyerNotes] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  if (!listingId) {
    return (
      <main className="container my-4">
        <div className="alert alert-danger">
          Falta el parámetro <code>listing_id</code>. Vuelve a la página de{" "}
          <a href="/match">búsqueda</a> e inténtalo de nuevo.
        </div>
      </main>
    );
  }

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    setSuccess(false);
    setLoading(true);

    try {
      await createLead({
        buyer_name: buyerName,
        buyer_email: buyerEmail,
        buyer_phone: buyerPhone || undefined,
        buyer_notes: buyerNotes || undefined,
        listing_id: listingId, // el backend lo espera como string
      });

      setSuccess(true);
      setBuyerName("");
      setBuyerEmail("");
      setBuyerPhone("");
      setBuyerNotes("");
    } catch (err: any) {
      console.error(err);
      setError(
        err?.message ??
          "Ocurrió un error al registrar tu interés. Inténtalo de nuevo."
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="container my-4">
      <div className="row justify-content-center">
        <div className="col-md-6">
          <div className="card">
            <div className="card-body">
              <h5 className="card-title mb-3">Me interesa este auto</h5>
              <p className="text-muted mb-3">
                Estás solicitando información sobre:
                <br />
                <strong>{listingTitle}</strong> (ID: {listingId})
              </p>

              {error && <div className="alert alert-danger">{error}</div>}
              {success && (
                <div className="alert alert-success">
                  ¡Listo! Hemos registrado tu interés. Un dealer se pondrá en
                  contacto contigo pronto.
                </div>
              )}

              <form onSubmit={handleSubmit}>
                <div className="mb-3">
                  <label className="form-label">Nombre</label>
                  <input
                    type="text"
                    className="form-control"
                    value={buyerName}
                    onChange={(e) => setBuyerName(e.target.value)}
                    required
                  />
                </div>

                <div className="mb-3">
                  <label className="form-label">Email</label>
                  <input
                    type="email"
                    className="form-control"
                    value={buyerEmail}
                    onChange={(e) => setBuyerEmail(e.target.value)}
                    required
                  />
                </div>

                <div className="mb-3">
                  <label className="form-label">Teléfono (opcional)</label>
                  <input
                    type="tel"
                    className="form-control"
                    value={buyerPhone}
                    onChange={(e) => setBuyerPhone(e.target.value)}
                  />
                </div>

                <div className="mb-3">
                  <label className="form-label">
                    Comentarios (opcional)
                  </label>
                  <textarea
                    className="form-control"
                    rows={3}
                    value={buyerNotes}
                    onChange={(e) => setBuyerNotes(e.target.value)}
                  />
                </div>

                <div className="d-flex justify-content-between">
                  <button
                    type="button"
                    className="btn btn-outline-secondary"
                    onClick={() => router.push("/match")}
                    disabled={loading}
                  >
                    Volver a resultados
                  </button>
                  <button
                    type="submit"
                    className="btn btn-primary"
                    disabled={loading}
                  >
                    {loading ? "Enviando..." : "Enviar interés"}
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      </div>
    </main>
  );
}
