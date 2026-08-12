import { NavLink, Outlet, useLocation } from "react-router-dom";
import { useReport } from "./state/ReportContext";

const REPORT_SECTIONS = [
  { id: "summary", label: "Overview" },
  { id: "market", label: "Market Attractiveness" },
  { id: "competition", label: "Competitive Landscape" },
  { id: "customers", label: "Audience Segments" },
  { id: "geography", label: "Geography" },
  { id: "scenarios", label: "Scenario Model" },
] as const;

export default function App() {
  const { data } = useReport();
  const location = useLocation();
  const onReport = location.pathname.startsWith("/report");
  const report = data?.report;
  const section = new URLSearchParams(location.search).get("section") || "summary";

  return (
    <div className="app-shell">
      <aside className="icon-rail" aria-label="Primary">
        <NavLink to="/" end className={({ isActive }) => `rail-btn ${isActive ? "active" : ""}`} title="New analysis">
          ML
        </NavLink>
        <NavLink
          to="/report"
          className={({ isActive }) => `rail-btn ${isActive ? "active" : ""}`}
          title="Report"
        >
          RP
        </NavLink>
      </aside>

      <aside className="side-nav" aria-label="Secondary">
        <div className="side-brand">MarketLens</div>

        <div className="side-section">
          <div className="side-label">Workspace</div>
          <NavLink to="/" end className={({ isActive }) => `side-link ${isActive ? "active" : ""}`}>
            New analysis
          </NavLink>
          <NavLink
            to="/report"
            className={({ isActive }) => `side-link ${isActive && section === "summary" ? "active" : ""}`}
          >
            Intelligence report
          </NavLink>
        </div>

        {onReport && report && (
          <div className="side-section">
            <div className="side-label">Report modules</div>
            {REPORT_SECTIONS.map((s) => (
              <NavLink
                key={s.id}
                to={`/report?section=${s.id}`}
                className={() => `side-link ${section === s.id ? "active" : ""}`}
              >
                {s.label}
              </NavLink>
            ))}
          </div>
        )}

        {report && (
          <div className="side-section">
            <div className="side-label">Active engagement</div>
            <div className="muted" style={{ padding: "0 0.35rem", lineHeight: 1.45 }}>
              <div style={{ color: "var(--ink)", fontWeight: 650 }}>{report.brief.company}</div>
              <div>
                {report.brief.target_market} · {report.brief.industry}
              </div>
              <div style={{ marginTop: "0.35rem" }}>
                Rec: <b>{report.recommendation.action}</b> ·{" "}
                {report.recommendation.overall_confidence.toFixed(0)}/100
              </div>
            </div>
          </div>
        )}
      </aside>

      <header className="topbar">
        <div className="top-left">
          <div>
            <div className="top-title">
              {onReport && report
                ? `${report.brief.company} · Market intelligence`
                : "Market intelligence platform"}
            </div>
            <div className="top-sub">
              {onReport && report
                ? report.brief.key_question ||
                  `${report.brief.objective} · ${report.brief.target_market}`
                : "Structure a market problem into scored analysis and a recommendation"}
            </div>
          </div>
        </div>
        <div className="filters">
          {report ? (
            <>
              <span className="chip">{report.brief.company}</span>
              <span className="chip">{report.brief.target_market}</span>
              <span className="chip">{report.brief.industry}</span>
              <span className="chip">{report.brief.objective}</span>
            </>
          ) : (
            <span className="chip">No engagement loaded</span>
          )}
        </div>
      </header>

      <div className="main">
        <Outlet />
      </div>
    </div>
  );
}
