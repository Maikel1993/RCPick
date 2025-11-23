"use client";

import { useState } from "react";
import Link from "next/link";

type ImportResult = {
  id: string;
  price: number;
  miles: number;
  year: number;
  make?: string | null;
  model?: string | null;
  trim?: string | null;
};

export default function ImportarPage() {
  const [urlsText, setUrlsText] = useState("");
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<ImportResult[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResults(null);

    try {
      // 1) Convertir el textarea en un array de URLs
      const urls = urlsText
  .split("\n")
  .map((l) => l.trim())
  .filter((l) => l.length > 0)
  .filter((l) => l.startsWith("http://") || l.startsWith("https://"));

      if (urls.length === 0) {
        throw new Error("Por favor escribe al menos una URL.");
      }

      const payload = { urls };

      // 2) Llamar al backend
      const res = await fetch("http://127.0.0.1:8000/listings/from-urls", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
      });

      if (!res.ok) {
        const txt = await res.text();
        throw new Error(`Error ${res.status}: ${txt}`);
      }

      const data = await res.json();
      setResults(data);
    } catch (err: any) {
      setError(err.message || "Error inesperado");
    } finally {
      setLoading(false);
    }
  };

  return (
    <main
      style={{
        padding: "2rem",
        maxWidth: "800px",
        margin: "0 auto",
        display: "grid",
        gap: "1.5rem",
      }}
    >
      <header>
        <h1>Importar autos desde URLs</h1>
        <p style={{ fontSize: "0.95rem", color: "#555" }}>
          Pega aquí uno o varios enlaces de páginas de resultados de autos (por ejemplo, de un sitio
          específico que luego tu scraper procese) y el sistema intentará extraer la información y
          guardarla en la base de datos.
        </p>
        <p style={{ fontSize: "0.85rem", color: "#777" }}>
          * Recuerda que tienes que adaptar el scraper en el backend a la estructura real del sitio
          (HTML, clases, etc.).
        </p>
      </header>

      <form
        onSubmit={handleSubmit}
        style={{
          display: "grid",
          gap: "1rem",
          padding: "1rem",
          border: "1px solid #ddd",
          borderRadius: "8px",
        }}
      >
        <label style={{ display: "grid", gap: "0.5rem" }}>
          <span>URLs (una por línea):</span>
          <textarea
            rows={6}
            placeholder={`https://ejemplo.com/listado-de-autos-1\nhttps://ejemplo.com/listado-de-autos-2`}
            value={urlsText}
            onChange={(e) => setUrlsText(e.target.value)}
            style={{ width: "100%", fontFamily: "monospace", fontSize: "0.9rem" }}
          />
        </label>

        <button type="submit" disabled={loading}>
          {loading ? "Importando..." : "Importar autos"}
        </button>
      </form>

      {error && (
        <div
          style={{
            border: "1px solid #f99",
            borderRadius: "8px",
            padding: "0.75rem 1rem",
            color: "#900",
            background: "#fff5f5",
          }}
        >
          <strong>Error:</strong> {error}
        </div>
      )}

      {results && (
        <section
          style={{
            border: "1px solid #ddd",
            borderRadius: "8px",
            padding: "1rem",
            display: "grid",
            gap: "0.75rem",
          }}
        >
          <h2>Resultados de la importación</h2>
          <p style={{ fontSize: "0.9rem", color: "#555" }}>
            Se importaron <strong>{results.length}</strong> autos desde las URLs proporcionadas.
          </p>

          {results.length > 0 && (
            <div style={{ display: "grid", gap: "0.5rem" }}>
              {results.map((r) => (
                <div
                  key={r.id}
                  style={{
                    border: "1px solid #eee",
                    borderRadius: "6px",
                    padding: "0.5rem 0.75rem",
                    background: "#fafafa",
                    fontSize: "0.9rem",
                  }}
                >
                  <div style={{ fontWeight: "bold" }}>
                    {r.year} {r.make} {r.model} {r.trim}
                  </div>
                  <div style={{ color: "#555" }}>
                    ${r.price.toLocaleString()} · {r.miles.toLocaleString()} mi
                  </div>
                  <div style={{ fontSize: "0.8rem", color: "#777" }}>ID interno: {r.id}</div>
                </div>
              ))}
            </div>
          )}

          <div style={{ marginTop: "0.75rem", fontSize: "0.9rem" }}>
            Ahora puedes ir a{" "}
            <Link href="/match" style={{ color: "#0a7", fontWeight: "bold" }}>
              la página de match
            </Link>{" "}
            para usar estos autos en el ranking AHP.
          </div>
        </section>
      )}
    </main>
  );
}
