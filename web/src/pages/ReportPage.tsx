import { useEffect, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Scatter,
  ScatterChart,
  Tooltip,
  XAxis,
  YAxis,
  ZAxis,
} from "recharts";
import { recomputeScenarios, exportReportPdf } from "../api";
import { useReport } from "../state/ReportContext";

type Tab = "summary" | "market" | "competition" | "customers" | "geography" | "scenarios";

const TAB_GUIDE: Record<Tab, string> = {
  summary: "Executive overview — recommendation, KPIs, reasons, and priority actions.",
  market:
    "Market attractiveness scorecard. Competition is inverted: higher bar = more attractive competitive setting.",
  competition:
    "Competitive set map: X = innovation, Y = premium, bubble = share. Empty space ≈ whitespace.",
  customers: "Audience segments ranked by attractiveness. Recommended target is highest fit.",
  geography: "Geographic Market Attractiveness Score (MAS). Prioritize top-ranked regions.",
  scenarios: "Stress-test base-case assumptions. Recommendation can change after recompute.",
};

export default function ReportPage() {
  const { data, setData, activeSlug } = useReport();
  const [params, setParams] = useSearchParams();
  const tab = (params.get("section") as Tab) || "summary";
  const [busy, setBusy] = useState(false);
  const [pdfBusy, setPdfBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const report = data?.report;
  const base = report?.scenarios.base;
  const [share, setShare] = useState(2.5);
  const [invest, setInvest] = useState(0.25);
  const [growth, setGrowth] = useState(12);
  const [price, setPrice] = useState(1);

  useEffect(() => {
    if (!base) return;
    setShare(base.expected_share_pct);
    setInvest(base.entry_investment);
    setGrowth(base.annual_growth_pct);
    setPrice(base.price_index);
  }, [base]);

  function setTab(next: Tab) {
    setParams({ section: next });
  }

  if (!report || !data) {
    return (
      <>
        <div className="page-head">
          <h1>No report loaded</h1>
          <p>Create an engagement from New analysis to open the intelligence workspace.</p>
        </div>
        <Link className="btn" to="/">
          New analysis
        </Link>
      </>
    );
  }

  const ex = report.executive_summary;
  const action = report.recommendation.action;
  const marketData = report.market.dimensions.map((d) => ({
    name: d.name,
    score: d.score,
  }));
  const geoData = [...report.geography.opportunities]
    .sort((a, b) => a.mas - b.mas)
    .map((g) => ({ region: g.region, mas: g.mas }));
  const compData = report.competition.competitors.map((c) => ({
    name: c.name,
    x: c.x_innovation,
    y: c.y_premium,
    z: c.market_share_pct ?? 5,
  }));

  async function onExportPdf() {
    if (!report) return;
    setPdfBusy(true);
    setError(null);
    try {
      await exportReportPdf(report);
    } catch (e) {
      setError(e instanceof Error ? e.message : "PDF export failed");
    } finally {
      setPdfBusy(false);
    }
  }

  async function onRecompute() {
    if (!activeSlug) return;
    setBusy(true);
    setError(null);
    try {
      const res = await recomputeScenarios({
        slug: activeSlug,
        expected_share_pct: share,
        entry_investment: invest,
        annual_growth_pct: growth,
        price_index: price,
      });
      setData(res);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Recompute failed");
    } finally {
      setBusy(false);
    }
  }

  const assumptions = report.assumptions ?? {};
  const growthDim = report.market.dimensions.find((d) => d.name === "Growth");

  return (
    <>
      <div className="page-head" style={{ display: "flex", justifyContent: "space-between", gap: "1rem", alignItems: "flex-start" }}>
        <div>
          <h1>
            {report.brief.company} competitive & market set
          </h1>
          <p>
            {report.brief.industry} in {report.brief.target_market} · {report.brief.objective}
          </p>
        </div>
        <div style={{ display: "flex", gap: "0.5rem", flexWrap: "wrap", justifyContent: "flex-end" }}>
          <button
            className="btn secondary"
            type="button"
            disabled={pdfBusy}
            onClick={onExportPdf}
            style={{ whiteSpace: "nowrap" }}
          >
            {pdfBusy ? "Preparing PDF…" : "Export PDF"}
          </button>
        </div>
      </div>

      <div className="compare-bar">
        <span className="domain-pill">
          <span className="dot" />
          {report.brief.company}
        </span>
        {report.competition.competitors.slice(0, 3).map((c, i) => (
          <span className="domain-pill" key={c.name}>
            <span
              className="dot"
              style={{
                background: ["#0d9488", "#ea580c", "#1d4ed8"][i % 3],
              }}
            />
            {c.name}
          </span>
        ))}
        <span className="chip">{report.brief.target_market}</span>
        <span className="chip">{report.brief.industry}</span>
      </div>

      {data.note && <div className="guide warn">{data.note}</div>}
      {error && <div className="error">{error}</div>}

      <div className="decision">
        <div>
          <div className="label">Strategic recommendation</div>
          <div className="action">{action}</div>
          <div style={{ opacity: 0.9, maxWidth: "40rem", lineHeight: 1.5 }}>{ex.narrative}</div>
        </div>
        <div className="score">
          <span style={{ opacity: 0.7, fontSize: "0.78rem" }}>Entry score</span>
          <b>{report.recommendation.overall_confidence.toFixed(0)}/100</b>
        </div>
      </div>

      <div className="grid-5" style={{ marginBottom: "0.9rem" }}>
        <button type="button" className={`metric ${tab === "summary" ? "active" : ""}`} onClick={() => setTab("summary")} style={{ cursor: "pointer", textAlign: "left" }}>
          <div className="label">Decision</div>
          <div className="value">{action}</div>
          <div className="hint">Model recommendation</div>
        </button>
        <button type="button" className={`metric ${tab === "market" ? "active" : ""}`} onClick={() => setTab("market")} style={{ cursor: "pointer", textAlign: "left" }}>
          <div className="label">Market score</div>
          <div className="value">{report.market.overall.toFixed(0)}</div>
          <div className="delta up">Attractiveness /100</div>
        </button>
        <button type="button" className={`metric ${tab === "competition" ? "active" : ""}`} onClick={() => setTab("competition")} style={{ cursor: "pointer", textAlign: "left" }}>
          <div className="label">Competitive intensity</div>
          <div className="value">{report.competition.intensity_score.toFixed(0)}</div>
          <div className="hint">{ex.competitive_intensity}</div>
        </button>
        <button type="button" className={`metric ${tab === "customers" ? "active" : ""}`} onClick={() => setTab("customers")} style={{ cursor: "pointer", textAlign: "left" }}>
          <div className="label">Target segment</div>
          <div className="value" style={{ fontSize: "1.05rem" }}>{report.customers.recommended_segment}</div>
          <div className="hint">{ex.customer_opportunity} opportunity</div>
        </button>
        <button type="button" className={`metric ${tab === "scenarios" ? "active" : ""}`} onClick={() => setTab("scenarios")} style={{ cursor: "pointer", textAlign: "left" }}>
          <div className="label">Base scenario</div>
          <div className="value">{report.scenarios.base.score.toFixed(0)}</div>
          <div className={report.scenarios.base.roi_pct >= 0 ? "delta up" : "delta down"}>
            ROI {report.scenarios.base.roi_pct.toFixed(0)}%
          </div>
        </button>
      </div>

      <div className="guide">{TAB_GUIDE[tab]}</div>

      {tab === "summary" && (
        <section className="section-block">
          <div className="grid-2">
            <div className="card">
              <h3>Priority actions</h3>
              <ul style={{ margin: 0, paddingLeft: "1.1rem", lineHeight: 1.6 }}>
                {ex.priority_actions.map((a) => (
                  <li key={a}>{a}</li>
                ))}
              </ul>
            </div>
            <div className="card">
              <h3>Snapshot</h3>
              <div className="score-row">
                <div>Market</div>
                <div className="track"><div className="fill" style={{ width: `${report.market.overall}%` }} /></div>
                <div style={{ textAlign: "right", fontWeight: 700 }}>{report.market.overall.toFixed(0)}</div>
              </div>
              <div className="score-row">
                <div>Growth</div>
                <div className="track"><div className="fill" style={{ width: `${growthDim?.score ?? 0}%` }} /></div>
                <div style={{ textAlign: "right", fontWeight: 700 }}>{(growthDim?.score ?? 0).toFixed(0)}</div>
              </div>
              <div className="score-row">
                <div>Risk</div>
                <div className="track"><div className="fill" style={{ width: `${report.scenarios.base.risk_score}%`, background: "var(--orange)" }} /></div>
                <div style={{ textAlign: "right", fontWeight: 700 }}>{report.scenarios.base.risk_score.toFixed(0)}</div>
              </div>
            </div>
          </div>

          <h2 style={{ marginTop: "1rem" }}>Insights</h2>
          <div className="insight-row">
            {report.recommendation.why.slice(0, 4).map((w, i) => (
              <div className="insight-tile" key={w}>
                <b>Signal {i + 1}</b>
                {w}
              </div>
            ))}
          </div>

          <div className="card">
            <h3>Recommended strategy</h3>
            <p style={{ margin: 0, lineHeight: 1.55 }}>{report.recommendation.recommended_strategy}</p>
          </div>
        </section>
      )}

      {tab === "market" && (
        <section className="section-block">
          <div className="grid-2">
            <div className="card">
              <h3>Attractiveness scorecard</h3>
              {report.market.dimensions.map((d) => (
                <div key={d.name} style={{ marginBottom: "0.65rem" }}>
                  <div className="score-row">
                    <div>{d.name}</div>
                    <div className="track"><div className="fill" style={{ width: `${d.score}%` }} /></div>
                    <div style={{ textAlign: "right", fontWeight: 700 }}>{d.score.toFixed(0)}</div>
                  </div>
                  {d.rationale && <div className="muted" style={{ marginLeft: 0 }}>{d.rationale}</div>}
                </div>
              ))}
            </div>
            <div className="card">
              <h3>Dimension chart</h3>
              <div className="chart-wrap" style={{ border: "none", height: 280, padding: 0 }}>
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={marketData} layout="vertical" margin={{ left: 8, right: 8 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#eef2f6" />
                    <XAxis type="number" domain={[0, 100]} />
                    <YAxis type="category" dataKey="name" width={90} />
                    <Tooltip />
                    <Bar dataKey="score" fill="#2563eb" name="Score" radius={[0, 4, 4, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>
          {report.market.high_growth_underpenetrated.length > 0 && (
            <div className="insight">
              <b>High-growth + underpenetrated</b>
              <ul>
                {report.market.high_growth_underpenetrated.map((x) => (
                  <li key={x}>{x}</li>
                ))}
              </ul>
            </div>
          )}
        </section>
      )}

      {tab === "competition" && (
        <section className="section-block">
          <div className="insight">{report.competition.whitespace_insight}</div>
          <div className="grid-2">
            <div className="card">
              <h3>Positioning map</h3>
              <div className="chart-wrap" style={{ height: 360, border: "none", padding: 0 }}>
                <ResponsiveContainer width="100%" height="100%">
                  <ScatterChart margin={{ top: 12, right: 12, bottom: 12, left: 12 }}>
                    <CartesianGrid stroke="#eef2f6" />
                    <XAxis type="number" dataKey="x" name="Innovation" domain={[0, 100]} />
                    <YAxis type="number" dataKey="y" name="Premium" domain={[0, 100]} />
                    <ZAxis type="number" dataKey="z" range={[60, 260]} />
                    <Tooltip cursor={{ strokeDasharray: "3 3" }} />
                    <Scatter data={compData} fill="#2563eb" name="Competitors" />
                  </ScatterChart>
                </ResponsiveContainer>
              </div>
            </div>
            <div className="card">
              <h3>Positioning call</h3>
              <p style={{ marginTop: 0, lineHeight: 1.5 }}>{report.competition.recommended_positioning}</p>
              <div className="metric flat" style={{ boxShadow: "none" }}>
                <div className="label">Intensity</div>
                <div className="value">{report.competition.intensity_score.toFixed(0)}</div>
                <div className="hint">{ex.competitive_intensity}</div>
              </div>
            </div>
          </div>
          <div className="card" style={{ marginTop: "0.75rem" }}>
            <h3>Competitive set table</h3>
            <table className="table">
              <thead>
                <tr>
                  <th>Competitor</th>
                  <th>Share %</th>
                  <th>Pricing</th>
                  <th>Segment</th>
                  <th>Value prop</th>
                </tr>
              </thead>
              <tbody>
                {report.competition.competitors.map((c) => (
                  <tr key={c.name}>
                    <td>{c.name}</td>
                    <td>{c.market_share_pct ?? "—"}</td>
                    <td>{c.pricing_position}</td>
                    <td>{c.customer_segment}</td>
                    <td>{c.value_proposition}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      )}

      {tab === "customers" && (
        <section className="section-block">
          <div className="insight">
            <b>Recommended target: {report.customers.recommended_segment}</b>
            <div>{report.customers.rationale}</div>
          </div>
          <div className="card">
            <h3>Audience segments</h3>
            <table className="table">
              <thead>
                <tr>
                  <th>Segment</th>
                  <th>Who they are</th>
                  <th>Demand %</th>
                  <th>Attractiveness</th>
                </tr>
              </thead>
              <tbody>
                {[...report.customers.segments]
                  .sort((a, b) => b.attractiveness - a.attractiveness)
                  .map((s) => (
                    <tr key={s.name}>
                      <td>{s.name}</td>
                      <td>{s.description}</td>
                      <td>{s.share_of_demand_pct}</td>
                      <td>{s.attractiveness.toFixed(0)}</td>
                    </tr>
                  ))}
              </tbody>
            </table>
          </div>
        </section>
      )}

      {tab === "geography" && (
        <section className="section-block">
          <p className="muted">{report.geography.methodology_note}</p>
          <div className="insight">
            <b>Prioritize:</b> {report.geography.top_markets.join(", ")}
          </div>
          <div className="card">
            <h3>Geographic MAS</h3>
            <div className="chart-wrap" style={{ border: "none", padding: 0 }}>
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={geoData} layout="vertical" margin={{ left: 8, right: 8 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#eef2f6" />
                  <XAxis type="number" domain={[0, 100]} />
                  <YAxis type="category" dataKey="region" width={110} />
                  <Tooltip />
                  <Bar dataKey="mas" fill="#2563eb" name="MAS" radius={[0, 4, 4, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        </section>
      )}

      {tab === "scenarios" && (
        <section className="section-block">
          <div className="grid-3" style={{ marginBottom: "0.75rem" }}>
            <div className="metric">
              <div className="label">Conservative</div>
              <div className="value">{report.scenarios.conservative.score.toFixed(0)}</div>
              <div className="hint">ROI {report.scenarios.conservative.roi_pct.toFixed(0)}%</div>
            </div>
            <div className="metric active">
              <div className="label">Base case</div>
              <div className="value">{report.scenarios.base.score.toFixed(0)}</div>
              <div className="delta up">ROI {report.scenarios.base.roi_pct.toFixed(0)}%</div>
            </div>
            <div className="metric">
              <div className="label">Aggressive</div>
              <div className="value">{report.scenarios.aggressive.score.toFixed(0)}</div>
              <div className="hint">ROI {report.scenarios.aggressive.roi_pct.toFixed(0)}%</div>
            </div>
          </div>
          <div className="grid-2">
            <div className="card">
              <h3>Base-case levers</h3>
              <div className="field">
                <label>Expected share % ({share.toFixed(1)})</label>
                <input type="range" min={0.5} max={8} step={0.1} value={share} onChange={(e) => setShare(Number(e.target.value))} />
              </div>
              <div className="field">
                <label>Entry investment ({invest.toFixed(2)})</label>
                <input type="range" min={0.05} max={3} step={0.05} value={invest} onChange={(e) => setInvest(Number(e.target.value))} />
              </div>
              <div className="field">
                <label>Annual growth % ({growth.toFixed(1)})</label>
                <input type="range" min={1} max={35} step={0.5} value={growth} onChange={(e) => setGrowth(Number(e.target.value))} />
              </div>
              <div className="field">
                <label>Price index ({price.toFixed(2)})</label>
                <input type="range" min={0.7} max={1.3} step={0.01} value={price} onChange={(e) => setPrice(Number(e.target.value))} />
              </div>
              <button className="btn" type="button" disabled={busy} onClick={onRecompute}>
                {busy ? "Recomputing…" : "Recompute scenarios"}
              </button>
            </div>
            <div className="card">
              <h3>Base economics</h3>
              <p>Revenue potential: <b>{report.scenarios.base.revenue_potential.toFixed(2)}</b></p>
              <p>Profit potential: <b>{report.scenarios.base.profit_potential.toFixed(2)}</b></p>
              <p>Break-even years: <b>{report.scenarios.base.break_even_years ?? "—"}</b></p>
              <p>Risk score: <b>{report.scenarios.base.risk_score.toFixed(0)}/100</b></p>
            </div>
          </div>
        </section>
      )}

      <div className="footnote">
        <b>Assumptions:</b>{" "}
        {typeof assumptions.data_vintage === "string"
          ? assumptions.data_vintage
          : "Illustrative estimates"}
        {typeof assumptions.note === "string" ? ` · ${assumptions.note}` : ""}
        {" · "}
        Figures are directional for decision support and should be validated with primary research.
      </div>
    </>
  );
}
