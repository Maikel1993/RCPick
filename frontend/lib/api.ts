const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

async function handleResponse(res: Response) {
  if (!res.ok) {
    let text: string;
    try {
      text = await res.text();
    } catch {
      text = res.statusText;
    }
    throw new Error(`API error ${res.status}: ${text}`);
  }
  return res.json();
}

// --------- MATCH ---------

export interface SearchFilters {
  min_price?: number | null;
  max_price?: number | null;
  min_year?: number | null;
  max_year?: number | null;
  max_miles?: number | null;
}

export interface SearchWeights {
  weight_price: number;
  weight_miles: number;
  weight_year: number;
  weight_trim: number;
  weight_body_style: number;
  weight_condition: number;
}

export interface SearchRequest {
  filters: SearchFilters;
  weights: SearchWeights;
}

export interface ListingScoreResult {
  listing_id: number;
  score: number;      // 0-1
  score_100: number;  // 0-100

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
  created_at?: string | null;
}

export interface MatchResponse {
  total_candidates: number;
  returned: number;
  results: ListingScoreResult[];
}

export async function searchListings(payload: SearchRequest): Promise<ListingScoreResult[]> {
  const res = await fetch(`${API_BASE_URL}/match/`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });
  const data: MatchResponse = await handleResponse(res);
  return data.results ?? [];
}

// --------- LEADS ---------

export interface LeadCreatePayload {
  buyer_name: string;
  buyer_email: string;
  buyer_phone?: string;
  buyer_notes?: string;
  listing_id: string; // el backend espera string
}

export async function createLead(payload: LeadCreatePayload) {
  const res = await fetch(`${API_BASE_URL}/leads/`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });
  return handleResponse(res);
}

// Admin dashboard de leads
export async function getAdminLeads() {
  const res = await fetch(`${API_BASE_URL}/leads/admin`, {
    cache: "no-store",
  });
  return handleResponse(res);
}

// Vista dealer: por ahora reutiliza /leads/admin
// (si más adelante tienes un /leads/dealer/{dealer_id}, aquí lo cambiamos)
export async function getDealerLeads() {
  const res = await fetch(`${API_BASE_URL}/leads/admin`, {
    cache: "no-store",
  });
  return handleResponse(res);
}

export async function getDealerLeadById(id: string) {
  const res = await fetch(`${API_BASE_URL}/leads/${id}/detail`, {
    cache: "no-store",
  });

  if (res.status === 404) {
    return null;
  }

  return handleResponse(res);
}


export type LeadEvent = {
  id: number;
  lead_id: number;
  action: string;
  description?: string | null;
  timestamp: string;
};

export async function getAdminLeadById(id: string) {
  // Por ahora el admin reutiliza el mismo endpoint de detalle que el dealer.
  return getDealerLeadById(id);
}

export async function getLeadEvents(id: string) {
  const res = await fetch(`${API_BASE_URL}/leads/${id}/events`, {
    cache: "no-store",
  });

  if (res.status === 404) {
    // Sin eventos aún
    return [] as LeadEvent[];
  }

  return handleResponse(res);
}

export async function updateLeadStatus(id: string, status: string) {
  const res = await fetch(`${API_BASE_URL}/leads/${id}/status`, {
    method: "PATCH",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ status }),
  });

  return handleResponse(res);
}

