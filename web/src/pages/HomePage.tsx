import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import { fetchCases, generateFromBrief, generateFromCase } from "../api";
import { useReport } from "../state/ReportContext";
import type { CaseSummary } from "../types";

const OBJECTIVES = [
  "Market Entry",
  "Market Expansion",
  "Competitive Analysis",
  "New Product Opportunity",
  "Pricing Analysis",
];

const INDUSTRIES = [
  "Coffee & Retail",
  "Electric Vehicles",
  "Healthcare",
  "Consumer Electronics",
  "Technology",
];

const PACK_HINT: Record<string, string> = {
  "Coffee & Retail": "Starbucks / India retail pack",
  "Electric Vehicles": "Tesla / Germany EV pack",
  Healthcare: "Apex Pharma / India healthcare pack",
  "Consumer Electronics": "Starbucks / India retail pack (nearest)",
  Technology: "Tesla / Germany EV pack (nearest)",
};

export default function HomePage() {
  const navigate = useNavigate();
  const { setData, setActiveSlug } = useReport();
  const [cases, setCases] = useState<CaseSummary[]>([]);
  const [slug, setSlug] = useState("");
  const [mode, setMode] = useState<"demo" | "custom">("demo");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [company, setCompany] = useState("");
  const [industry, setIndustry] = useState(INDUSTRIES[0]);
  const [market, setMarket] = useState("");
  const [objective, setObjective] = useState(OBJECTIVES[0]);
  const [question, setQuestion] = useState("");

  useEffect(() => {
    fetchCases()
      .then((rows) => {
        setCases(rows);
        if (rows[0]) setSlug(rows[0].slug);
      })
      .catch((e: Error) => setError(e.message));
  }, []);

  const selected = useMemo(
    () => cases.find((c) => c.slug === slug),
    [cases, slug],
  );

  async function onGenerate() {
    setLoading(true);
    setError(null);
    try {
      const res =
        mode === "demo"
          ? await generateFromCase(slug)
          : await generateFromBrief({
              company,
              industry,
              target_market: market,
              objective,
              key_question: question || undefined,
            });
      setData(res);
      setActiveSlug(mode === "demo" ? slug : res.pack_slug);
      navigate("/report?section=summary");
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to generate report");
    } finally {
      setLoading(false);
    }
  }

  return (
    <>
      <div className="page-head">
        <h1>New market intelligence analysis</h1>
        <p>
          Define the engagement, then generate a scored market, competition, audience,
          geography, and scenario report with a clear strategic recommendation.
        </p>
      </div>

      <div className="grid-4" style={{ marginBottom: "0.9rem" }}>
        <div className="metric">
          <div className="label">Modules</div>
          <div className="value">6</div>
          <div className="hint">Market to recommendation</div>
        </div>
        <div className="metric">
          <div className="label">Demo packs</div>
          <div className="value">{cases.length || 3}</div>
          <div className="hint">Retail · EV · Healthcare</div>
        </div>
        <div className="metric">
          <div className="label">Outputs</div>
          <div className="value">ENTER+</div>
          <div className="hint">HOLD / EXIT / EXPAND</div>
        </div>
        <div className="metric">
          <div className="label">Scoring</div>
          <div className="value">Model</div>
          <div className="hint">Deterministic analytics</div>
        </div>
      </div>

      <div className="guide">
        <b>Best path:</b> use a demo case for the full research pack. Custom briefs reuse the
        nearest industry pack to explore the workflow — not live diligence on the named company.
      </div>

      {error && <div className="error">{error}</div>}

      <div className="grid-2">
        <section className="card">
          <div className="card-title-row">
            <h3>Engagement setup</h3>
          </div>

          <div className="mode-toggle">
            <button
              type="button"
              className={mode === "demo" ? "active" : ""}
              onClick={() => setMode("demo")}
            >
              Demo case
            </button>
            <button
              type="button"
              className={mode === "custom" ? "active" : ""}
              onClick={() => setMode("custom")}
            >
              Custom brief
            </button>
          </div>

          {mode === "demo" ? (
            <>
              <div className="case-grid">
                {cases.map((c) => (
                  <button
                    key={c.slug}
                    type="button"
                    className={`case-chip ${slug === c.slug ? "active" : ""}`}
                    onClick={() => setSlug(c.slug)}
                  >
                    <div className="title">
                      {c.company} → {c.target_market}
                    </div>
                    <div className="meta">
                      {c.industry} · {c.objective}
                    </div>
                  </button>
                ))}
              </div>
              {selected && (
                <div className="guide" style={{ marginBottom: 0 }}>
                  <b>Key question:</b> {selected.key_question || "—"}
                </div>
              )}
            </>
          ) : (
            <>
              <div className="guide warn">
                <b>You can still generate.</b> Custom names do not run new research —
                MarketLens will analyze using the <b>{PACK_HINT[industry]}</b> and label
                the report with your company name.
              </div>
              <div className="field">
                <label>Company</label>
                <input
                  value={company}
                  onChange={(e) => setCompany(e.target.value)}
                  placeholder="Example Corp"
                />
              </div>
              <div className="field">
                <label>Industry</label>
                <select value={industry} onChange={(e) => setIndustry(e.target.value)}>
                  {INDUSTRIES.map((i) => (
                    <option key={i}>{i}</option>
                  ))}
                </select>
              </div>
              <div className="field">
                <label>Target market</label>
                <input
                  value={market}
                  onChange={(e) => setMarket(e.target.value)}
                  placeholder="India"
                />
              </div>
              <div className="field">
                <label>Objective</label>
                <select value={objective} onChange={(e) => setObjective(e.target.value)}>
                  {OBJECTIVES.map((o) => (
                    <option key={o}>{o}</option>
                  ))}
                </select>
              </div>
              <div className="field">
                <label>Key question</label>
                <textarea
                  rows={2}
                  value={question}
                  onChange={(e) => setQuestion(e.target.value)}
                  placeholder="Should Example Corp enter this market?"
                />
              </div>
            </>
          )}

          <button
            className="btn"
            type="button"
            disabled={
              loading ||
              (mode === "demo" ? !slug : !company.trim() || !market.trim())
            }
            onClick={onGenerate}
            style={{ width: "100%", marginTop: "0.5rem" }}
          >
            {loading ? "Generating & polishing report…" : "Generate intelligence report"}
          </button>
        </section>

        <aside className="card">
          <h3>Analysis pipeline</h3>
          <ol className="flow-list">
            <li>Load structured research pack</li>
            <li>Score market attractiveness</li>
            <li>Map competitors and whitespace</li>
            <li>Recommend audience segment</li>
            <li>Rank geographic opportunity</li>
            <li>Run financial scenarios</li>
            <li>Publish strategic recommendation</li>
          </ol>
        </aside>
      </div>

      <div className="footnote">
        Demo figures are illustrative and directional — validate with primary research before
        real decisions.
      </div>
    </>
  );
}
