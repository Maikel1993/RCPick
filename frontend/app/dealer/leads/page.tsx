import Link from "next/link";
import { getDealerLeads } from "@/lib/api";

export const dynamic = "force-dynamic";

export default async function DealerLeadsPage() {
  const leads = await getDealerLeads();

  return (
    <main className="p-6 space-y-4">
      <h1 className="text-2xl font-semibold">Dealer Leads</h1>
      {(!leads || leads.length === 0) && (
        <p className="text-gray-500">No hay leads todavía.</p>
      )}
      <ul className="space-y-2">
        {Array.isArray(leads) &&
          leads.map((lead: any) => (
            <li
              key={lead.id}
              className="border rounded-lg p-3 hover:bg-gray-50 transition"
            >
              <Link href={`/dealer/leads/${lead.id}`}>
                <span className="font-medium">
                  Lead #{lead.id} - {lead.name || lead.full_name || "Sin nombre"}
                </span>
              </Link>
              {lead.email && (
                <p className="text-sm text-gray-600">Email: {lead.email}</p>
              )}
            </li>
          ))}
      </ul>
    </main>
  );
}
