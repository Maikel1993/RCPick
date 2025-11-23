"use client";

import { useState } from "react";

export default function BuyerProfilesPage() {
  const [form, setForm] = useState({
    name: "",
    email: "",
    location: "",
    budget_min: "",
    budget_max: "",
  });

  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement>
  ) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const res = await fetch("http://127.0.0.1:8000/buyer-profiles/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          name: form.name || null,
          email: form.email || null,
          location: form.location || null,
          budget_min: form.budget_min ? Number(form.budget_min) : null,
          budget_max: form.budget_max ? Number(form.budget_max) : null,
          criteria: {
            price: 5,
            mileage: 4,
            year: 3,
          },
        }),
      });

      if (!res.ok) {
        throw new Error("Error al crear el perfil");
      }

      const data = await res.json();
      setResult(data);
    } catch (err: any) {
      setError(err.message || "Error inesperado");
    } finally {
      setLoading(false);
    }
  };

  return (
    <main style={{ padding: "2rem", maxWidth: "600px", margin: "0 auto" }}>
      <h1>Crear Buyer Profile</h1>
      <form onSubmit={handleSubmit} style={{ display: "grid", gap: "0.75rem", marginTop: "1rem" }}>
        <input
          name="name"
          placeholder="Nombre"
          value={form.name}
          onChange={handleChange}
        />
        <input
          name="email"
          placeholder="Email"
          value={form.email}
          onChange={handleChange}
        />
        <input
          name="location"
          placeholder="Ubicación (ciudad, estado)"
          value={form.location}
          onChange={handleChange}
        />
        <input
          name="budget_min"
          placeholder="Presupuesto mínimo"
          value={form.budget_min}
          onChange={handleChange}
        />
        <input
          name="budget_max"
          placeholder="Presupuesto máximo"
          value={form.budget_max}
          onChange={handleChange}
        />

        <button type="submit" disabled={loading}>
          {loading ? "Enviando..." : "Crear perfil"}
        </button>
      </form>

      {error && <p style={{ color: "red", marginTop: "1rem" }}>{error}</p>}

      {result && (
        <pre style={{ marginTop: "1rem", background: "#111", color: "#0f0", padding: "1rem" }}>
{JSON.stringify(result, null, 2)}
        </pre>
      )}
    </main>
  );
}
