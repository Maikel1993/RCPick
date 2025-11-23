
'use client';

import Link from "next/link";
import { useMemo, useState } from "react";

export interface Lead {
  id: number;
  created_at?: string;
  client_name?: string;
  name?: string;
  full_name?: string;
  email?: string;
  phone?: string;
  vehicle_title?: string;
  vehicle_year?: number;
  vehicle_make?: string;
  vehicle_model?: string;
  dealer_name?: string;
  status?: string;
}

function formatDate(value?: string) {
  if (!value) return "";
  const d = new Date(value);
  if (Number.isNaN(d.getTime())) return value;
  return d.toLocaleString();
}

interface Props {
  leads: Lead[];
}

export default function AdminLeadsClient({ leads }: Props) {
  const [statusFilter, setStatusFilter] = useState<string>("all");
  const [dealerFilter, setDealerFilter] = useState<string>("all");
  const [search, setSearch] = useState<string>("");

  const { statuses, dealers, filteredLeads } = useMemo(() => {
    const statusesSet = new Set<string>();
    const dealersSet = new Set<string>();

    const norm = (v: unknown) =>
      (typeof v === "string" ? v : String(v ?? "")).toLowerCase();

    const computed = leads.map((lead) => {
      const status = (lead.status || "new").trim();
      const dealerName = lead.dealer_name || "N/D";
      if (status) statusesSet.add(status);
      if (dealerName) dealersSet.add(dealerName);

      const clientName =
        lead.client_name || lead.name || lead.full_name || "N/D";
      const contact = [lead.email, lead.phone].filter(Boolean).join(" · ");
      const vehicleTitle =
        lead.vehicle_title ||
        [lead.vehicle_year, lead.vehicle_make, lead.vehicle_model]
          .filter(Boolean)
          .join(" ") ||
        "N/D";

      return {
        ...lead,
        _status: status,
        _dealerName: dealerName,
        _clientName: clientName,
        _contact: contact,
        _vehicleTitle: vehicleTitle,
      };
    });

    let filtered = computed;

    // filtros se aplicarán fuera usando closures; devolvemos sólo computed
    return {
      statuses: Array.from(statusesSet),
      dealers: Array.from(dealersSet),
      filteredLeads: computed,
    };
  }, [leads]);

  const lowerSearch = search.toLowerCase().trim();

  const finalLeads = useMemo(() => {
    return filteredLeads.filter((lead: any) => {
      if (statusFilter !== "all" && lead._status !== statusFilter) {
        return false;
      }
      if (dealerFilter !== "all" && lead._dealerName !== dealerFilter) {
        return false;
      }

      if (lowerSearch) {
        const haystack = [
          lead._clientName,
          lead._contact,
          lead._vehicleTitle,
          lead._dealerName,
          lead._status,
        ]
          .join(" ")
          .toLowerCase();
        if (!haystack.includes(lowerSearch)) return false;
      }

      return true;
    });
  }, [filteredLeads, statusFilter, dealerFilter, lowerSearch]);

  return (
    <>
      {/* Filtros */}
      <div className="card mb-3">
        <div className="card-body py-3">
          <div className="row g-2 align-items-end">
            <div className="col-md-4">
              <label className="form-label mb-1 small">Buscar</label>
              <input
                type="text"
                className="form-control form-control-sm"
                placeholder="Nombre, email, vehículo, dealer..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
              />
            </div>
            <div className="col-md-3">
              <label className="form-label mb-1 small">Estado</label>
              <select
                className="form-select form-select-sm"
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
              >
                <option value="all">Todos</option>
                {statuses.map((s) => (
                  <option key={s} value={s}>
                    {s}
                  </option>
                ))}
              </select>
            </div>
            <div className="col-md-3">
              <label className="form-label mb-1 small">Dealer</label>
              <select
                className="form-select form-select-sm"
                value={dealerFilter}
                onChange={(e) => setDealerFilter(e.target.value)}
              >
                <option value="all">Todos</option>
                {dealers.map((d) => (
                  <option key={d} value={d}>
                    {d}
                  </option>
                ))}
              </select>
            </div>
            <div className="col-md-2 text-end">
              <button
                type="button"
                className="btn btn-sm btn-outline-secondary mt-3 mt-md-0"
                onClick={() => {
                  setSearch("");
                  setStatusFilter("all");
                  setDealerFilter("all");
                }}
              >
                Limpiar filtros
              </button>
            </div>
          </div>
        </div>
      </div>

      {finalLeads.length === 0 ? (
        <div className="alert alert-light border text-muted">
          No hay leads que coincidan con los filtros.
        </div>
      ) : (
        <div className="table-responsive">
          <table className="table table-sm align-middle">
            <thead>
              <tr>
                <th>Fecha</th>
                <th>Cliente</th>
                <th>Contacto</th>
                <th>Vehículo</th>
                <th>Dealer</th>
                <th>Estado</th>
                <th>Acciones</th>
              </tr>
            </thead>
            <tbody>
              {finalLeads.map((lead: any) => {
                return (
                  <tr key={lead.id}>
                    <td>{formatDate(lead.created_at)}</td>
                    <td>{lead._clientName}</td>
                    <td>{lead._contact}</td>
                    <td>{lead._vehicleTitle}</td>
                    <td>{lead._dealerName}</td>
                    <td>{lead._status}</td>
                    <td>
                      <Link
                        href={`/admin/leads/${lead.id}`}
                        className="btn btn-sm btn-outline-primary"
                      >
                        Ver detalles
                      </Link>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </>
  );
}
