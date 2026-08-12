import type { CaseSummary, GenerateResponse, MarketIntelligenceReport } from "./types";

const BASE = import.meta.env.VITE_API_BASE ?? "";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    headers: { "Content-Type": "application/json", ...(init?.headers ?? {}) },
    ...init,
  });
  if (!res.ok) {
    const text = await res.text();
    try {
      const parsed = JSON.parse(text) as { detail?: string };
      throw new Error(parsed.detail || text || `Request failed (${res.status})`);
    } catch (e) {
      if (e instanceof Error && e.message !== text) throw e;
      throw new Error(text || `Request failed (${res.status})`);
    }
  }
  return res.json() as Promise<T>;
}

export function fetchCases() {
  return request<CaseSummary[]>("/api/cases");
}

export function generateFromCase(slug: string) {
  return request<GenerateResponse>("/api/reports/from-case", {
    method: "POST",
    body: JSON.stringify({ slug }),
  });
}

export function generateFromBrief(body: {
  company: string;
  industry: string;
  target_market: string;
  objective: string;
  key_question?: string;
}) {
  return request<GenerateResponse>("/api/reports/from-brief", {
    method: "POST",
    body: JSON.stringify(body),
  });
}

export function recomputeScenarios(body: {
  slug: string;
  expected_share_pct: number;
  entry_investment: number;
  annual_growth_pct: number;
  price_index: number;
}) {
  return request<GenerateResponse>("/api/reports/scenarios", {
    method: "POST",
    body: JSON.stringify(body),
  });
}

export async function exportReportPdf(report: MarketIntelligenceReport): Promise<void> {
  const res = await fetch(`${BASE}/api/reports/export-pdf`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ report }),
  });
  if (!res.ok) {
    const text = await res.text();
    try {
      const parsed = JSON.parse(text) as { detail?: string };
      throw new Error(parsed.detail || text || `PDF export failed (${res.status})`);
    } catch (e) {
      if (e instanceof Error && !e.message.startsWith("{") && e.message !== text) throw e;
      throw new Error(text || `PDF export failed (${res.status})`);
    }
  }
  const blob = await res.blob();
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  const company = report.brief.company.toLowerCase().replace(/\s+/g, "-");
  a.href = url;
  a.download = `marketlens-${company}-report.pdf`;
  document.body.appendChild(a);
  a.click();
  a.remove();
  URL.revokeObjectURL(url);
}

export function polishNarrative(report: MarketIntelligenceReport) {
  return request<{ report: MarketIntelligenceReport; note: string }>(
    "/api/reports/polish-narrative",
    {
      method: "POST",
      body: JSON.stringify({ report }),
    },
  );
}
