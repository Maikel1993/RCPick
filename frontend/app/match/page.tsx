
"use client";

// === RCPick frontend – Match Page ===
// Esta página consume el endpoint POST /match/.
// Si llega ?profile_id=X en la URL, mandamos buyer_profile_id en el body
// para que el backend ajuste filtros/pesos según el BuyerProfile.
// Además, desde aquí el usuario puede crear un Lead con "Me interesa este auto".

import { useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";

type MatchFilters = {
  min_price?: number | null;
  max_price?: number | null;
  min_year?: number | null;
  max_year?: number | null;
  max_miles?: number | null;
  conditions?: string[] | null;
  require_third_row: boolean;
  require_awd: boolean;
};

type MatchWeights = {
  price: number;
  mileage: number;
  year: number;
  third_row: number;
  awd: number;
  condition: number;
  body_style: number;
};

type ListingScoreOut = {
  listing_id: number;
  score: number;
  score_100: number;
  year?: number | null;
  make?: string | null;
  model?: string | null;
  trim?: string | null;
  price?: number | null;
  miles?: number | null;
  body_style?: string | null;
  condition?: string | null;
  dealer_name?: string | null;
  source?: string | null;
  url?: string | null;
};

type MatchResponse = {
  total_candidates: number;
  returned: number;
  results: ListingScoreOut[];
};

// Campos mínimos para crear un lead (compatibles con el backend actual)
type LeadFormState = {
  buyer_name: string;
  buyer_email: string;
  buyer_phone: string;
  buyer_notes: string;
};

const initialLeadForm: LeadFormState = {
  buyer_name: "",
  buyer_email: "",
  buyer_phone: "",
  buyer_notes: "",
};

export default function MatchPage() {
  const searchParams = useSearchParams();
  const profileIdParam = searchParams.get("profile_id");

  const [filters, setFilters] = useState<MatchFilters>({
    min_price: undefined,
    max_price: undefined,
    min_year: undefined,
    max_year: undefined,
    max_miles: undefined,
    conditions: null,
    require_third_row: false,
    require_awd: false,
  });

  const [weights] = useState<MatchWeights>({
    price: 3,
    mileage: 3,
    year: 3,
    third_row: 3,
    awd: 3,
    condition: 3,
    body_style: 3,
  });

  const [loading, setLoading] = useState(false);
  const [data, setData] = useState<MatchResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  // --- Lead form state ---
  const [leadListing, setLeadListing] = useState<ListingScoreOut | null>(null);
  const [leadForm, setLeadForm] = useState<LeadFormState>(initialLeadForm);
  const [leadSubmitting, setLeadSubmitting] = useState(false);
  const [leadMessage, setLeadMessage] = useState<string | null>(null);
  const [leadError, setLeadError] = useState<string | null>(null);

  const apiBase =
    process.env.NEXT_PUBLIC_API_BASE_URL || "http://127.0.0.1:8000";

  const handleFetch = async () => {
    setLoading(true);
    setError(null);

    const buyer_profile_id = profileIdParam
      ? Number(profileIdParam)
      : undefined;

    const payload = {
      filters: {
        ...filters,
      },
      weights,
      body_style_preference: null,
      buyer_profile_id,
      limit_results: 20,
    };

    try {
      const res = await fetch(`${apiBase}/match/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
      });

      if (!res.ok) {
        const text = await res.text();
        throw new Error(text || "Error en /match/");
      }

      const json: MatchResponse = await res.json();
      setData(json);
    } catch (err: any) {
      setError(err.message || "Error inesperado");
      setData(null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (profileIdParam) {
      handleFetch();
    }
  }, [profileIdParam]);

  // ------------ Lead handlers ------------

  const openLeadForm = (listing: ListingScoreOut) => {
    setLeadListing(listing);
    setLeadForm(initialLeadForm);
    setLeadError(null);
    setLeadMessage(null);
  };

  const closeLeadForm = () => {
    setLeadListing(null);
    setLeadError(null);
    setLeadMessage(null);
  };

  const handleLeadChange = (
    e:
      | React.ChangeEvent<HTMLInputElement>
      | React.ChangeEvent<HTMLTextAreaElement>
  ) => {
    const { name, value } = e.target;
    setLeadForm((prev) => ({ ...prev, [name]: value }));
  };

  const handleLeadSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!leadListing) return;

    setLeadSubmitting(true);
    setLeadError(null);
    setLeadMessage(null);

    const payload = {
      buyer_name: leadForm.buyer_name,
      buyer_email: leadForm.buyer_email,
      buyer_phone: leadForm.buyer_phone || undefined,
      buyer_notes: leadForm.buyer_notes || undefined,
      listing_id: String(leadListing.listing_id),
    };

    try {
      const res = await fetch(`${apiBase}/leads/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
      });

      if (!res.ok) {
        const text = await res.text();
        throw new Error(text || "Error al crear el lead");
      }

      setLeadMessage(
        "¡Listo! Hemos registrado tu interés. Un dealer se pondrá en contacto contigo pronto."
      );
      // No cerramos inmediatamente para que vea el mensaje.
    } catch (err: any) {
      setLeadError(err.message || "Error inesperado creando el lead");
    } finally {
      setLeadSubmitting(false);
    }
  };

  return (
    <main className="min-h-screen bg-zinc-50 py-10 text-zinc-900">
      <div className="mx-auto max-w-5xl rounded-xl bg-white p-6 shadow-sm relative">
        <header className="mb-6 border-b pb-4 flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-zinc-900">
              Resultados RCPick
            </h1>
            <p className="mt-1 text-sm text-zinc-600">
              Ordenamos los autos según tu perfil y tus prioridades.
            </p>
            {profileIdParam && (
              <p className="mt-1 text-xs text-zinc-500">
                Usando perfil #{profileIdParam}.
              </p>
            )}
          </div>
          <button
            onClick={handleFetch}
            disabled={loading}
            className="rounded-md bg-blue-600 px-4 py-2 text-sm font-semibold text-white disabled:opacity-60"
          >
            {loading ? "Buscando..." : "Buscar / actualizar"}
          </button>
        </header>

        <section className="mb-6 grid gap-4 md:grid-cols-4 text-sm">
          <div>
            <label className="block mb-1 font-medium">Precio máx.</label>
            <input
              type="number"
              className="w-full rounded-md border px-2 py-1"
              value={filters.max_price ?? ""}
              onChange={(e) =>
                setFilters((prev) => ({
                  ...prev,
                  max_price: e.target.value
                    ? Number(e.target.value)
                    : undefined,
                }))
              }
            />
          </div>
          <div>
            <label className="block mb-1 font-medium">Año mín.</label>
            <input
              type="number"
              className="w-full rounded-md border px-2 py-1"
              value={filters.min_year ?? ""}
              onChange={(e) =>
                setFilters((prev) => ({
                  ...prev,
                  min_year: e.target.value
                    ? Number(e.target.value)
                    : undefined,
                }))
              }
            />
          </div>
          <div>
            <label className="block mb-1 font-medium">Millas máx.</label>
            <input
              type="number"
              className="w-full rounded-md border px-2 py-1"
              value={filters.max_miles ?? ""}
              onChange={(e) =>
                setFilters((prev) => ({
                  ...prev,
                  max_miles: e.target.value
                    ? Number(e.target.value)
                    : undefined,
                }))
              }
            />
          </div>
          <div className="flex items-center gap-3">
            <label className="flex items-center gap-1">
              <input
                type="checkbox"
                checked={filters.require_third_row}
                onChange={(e) =>
                  setFilters((prev) => ({
                    ...prev,
                    require_third_row: e.target.checked,
                  }))
                }
              />
              3 filas
            </label>
            <label className="flex items-center gap-1">
              <input
                type="checkbox"
                checked={filters.require_awd}
                onChange={(e) =>
                  setFilters((prev) => ({
                    ...prev,
                    require_awd: e.target.checked,
                  }))
                }
              />
              AWD / 4x4
            </label>
          </div>
        </section>

        {error && (
          <div className="mb-4 rounded-md bg-red-100 px-3 py-2 text-xs text-red-700">
            {error}
          </div>
        )}

        <section className="space-y-3">
          {data && (
            <p className="text-xs text-zinc-500">
              {data.returned} autos mostrados de{" "}
              {data.total_candidates} candidatos.
            </p>
          )}

          {data?.results?.length ? (
            <ul className="space-y-3">
              {data.results.map((item) => (
                <li
                  key={item.listing_id}
                  className="rounded-lg border px-4 py-3 text-sm flex flex-col md:flex-row md:items-center md:justify-between gap-2"
                >
                  <div>
                    <div className="font-semibold">
                      {item.year} {item.make} {item.model}{" "}
                      {item.trim && <span>{item.trim}</span>}
                    </div>
                    <div className="text-xs text-zinc-600">
                      {item.price
                        ? `$${item.price.toLocaleString()}`
                        : "Sin precio"}{" "}
                      ·{" "}
                      {item.miles
                        ? `${item.miles.toLocaleString()} millas`
                        : "Sin millas"}
                    </div>
                    <div className="text-xs text-zinc-500">
                      {item.dealer_name && <span>{item.dealer_name} · </span>}
                      {item.body_style && <span>{item.body_style} · </span>}
                      {item.condition && <span>{item.condition}</span>}
                    </div>
                    {item.url && (
                      <a
                        href={item.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="mt-1 inline-block text-xs text-blue-600 underline"
                      >
                        Ver ficha original
                      </a>
                    )}
                  </div>
                  <div className="flex items-center gap-2 md:flex-col md:items-end">
                    <span
                      className={`inline-flex items-center justify-center rounded-full px-3 py-1 text-xs font-semibold ${
                        item.score_100 >= 80
                          ? "bg-green-100 text-green-700"
                          : item.score_100 >= 60
                          ? "bg-yellow-100 text-yellow-700"
                          : "bg-zinc-100 text-zinc-700"
                      }`}
                    >
                      Score {item.score_100}
                    </span>
                    <button
                      type="button"
                      onClick={() => openLeadForm(item)}
                      className="rounded-md bg-emerald-600 px-3 py-1 text-xs font-semibold text-white"
                    >
                      Me interesa este auto
                    </button>
                  </div>
                </li>
              ))}
            </ul>
          ) : (
            <p className="text-xs text-zinc-500">
              No hay resultados aún. Ajusta filtros y pulsa en “Buscar /
              actualizar”.
            </p>
          )}
        </section>

        {/* Modal simple para el lead */}
        {leadListing && (
          <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
            <div className="w-full max-w-md rounded-lg bg-white p-4 shadow-lg">
              <div className="mb-3 flex items-start justify-between gap-2">
                <div>
                  <h2 className="text-sm font-semibold text-zinc-900">
                    Me interesa este auto
                  </h2>
                  <p className="text-xs text-zinc-600">
                    {leadListing.year} {leadListing.make} {leadListing.model}{" "}
                    {leadListing.trim && <span>{leadListing.trim}</span>}{" "}
                    (ID: {leadListing.listing_id})
                  </p>
                </div>
                <button
                  type="button"
                  onClick={closeLeadForm}
                  className="text-xs text-zinc-500 hover:text-zinc-800"
                >
                  Cerrar
                </button>
              </div>

              {leadMessage && (
                <div className="mb-2 rounded-md bg-emerald-50 px-3 py-2 text-[11px] text-emerald-700">
                  {leadMessage}
                </div>
              )}

              {leadError && (
                <div className="mb-2 rounded-md bg-red-50 px-3 py-2 text-[11px] text-red-700">
                  {leadError}
                </div>
              )}

              <form onSubmit={handleLeadSubmit} className="space-y-2 text-xs">
                <div>
                  <label className="mb-1 block font-medium">Nombre</label>
                  <input
                    type="text"
                    name="buyer_name"
                    className="w-full rounded-md border px-2 py-1"
                    value={leadForm.buyer_name}
                    onChange={handleLeadChange}
                    required
                  />
                </div>
                <div>
                  <label className="mb-1 block font-medium">Email</label>
                  <input
                    type="email"
                    name="buyer_email"
                    className="w-full rounded-md border px-2 py-1"
                    value={leadForm.buyer_email}
                    onChange={handleLeadChange}
                    required
                  />
                </div>
                <div>
                  <label className="mb-1 block font-medium">Teléfono (opcional)</label>
                  <input
                    type="text"
                    name="buyer_phone"
                    className="w-full rounded-md border px-2 py-1"
                    value={leadForm.buyer_phone}
                    onChange={handleLeadChange}
                  />
                </div>
                <div>
                  <label className="mb-1 block font-medium">
                    Comentarios (opcional)
                  </label>
                  <textarea
                    name="buyer_notes"
                    className="w-full rounded-md border px-2 py-1"
                    rows={3}
                    value={leadForm.buyer_notes}
                    onChange={handleLeadChange}
                    placeholder="Ej. ¿Cuándo me pueden contactar? ¿Aceptan trade-in?, etc."
                  />
                </div>

                <div className="mt-3 flex items-center justify-between">
                  <button
                    type="button"
                    onClick={closeLeadForm}
                    className="rounded-md border px-3 py-1 text-[11px] text-zinc-700"
                  >
                    Cancelar
                  </button>
                  <button
                    type="submit"
                    disabled={leadSubmitting}
                    className="rounded-md bg-emerald-600 px-4 py-1 text-[11px] font-semibold text-white disabled:opacity-60"
                  >
                    {leadSubmitting ? "Enviando..." : "Enviar interés"}
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}
      </div>
    </main>
  );
}
