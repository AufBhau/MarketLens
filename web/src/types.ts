export type CaseSummary = {
  slug: string;
  company: string;
  industry: string;
  target_market: string;
  objective: string;
  key_question?: string | null;
  label: string;
};

export type ScoreDimension = {
  name: string;
  score: number;
  rationale: string;
};

export type MarketIntelligenceReport = {
  brief: {
    company: string;
    industry: string;
    target_market: string;
    objective: string;
    key_question?: string | null;
  };
  market: {
    dimensions: ScoreDimension[];
    overall: number;
    high_growth_underpenetrated: string[];
  };
  competition: {
    competitors: Array<{
      name: string;
      revenue_bn?: number | null;
      market_share_pct?: number | null;
      pricing_position: string;
      customer_segment: string;
      value_proposition: string;
      strengths: string[];
      weaknesses: string[];
      x_innovation: number;
      y_premium: number;
    }>;
    intensity_score: number;
    whitespace_insight: string;
    recommended_positioning: string;
  };
  customers: {
    segments: Array<{
      name: string;
      description: string;
      income_level: string;
      price_sensitivity: string;
      brand_sensitivity: string;
      share_of_demand_pct: number;
      attractiveness: number;
    }>;
    recommended_segment: string;
    rationale: string;
  };
  geography: {
    opportunities: Array<{
      region: string;
      mas: number;
      drivers: Record<string, number>;
    }>;
    top_markets: string[];
    methodology_note: string;
  };
  scenarios: {
    currency: string;
    conservative: ScenarioResult;
    base: ScenarioResult;
    aggressive: ScenarioResult;
  };
  recommendation: {
    action: "ENTER" | "HOLD" | "EXIT" | "EXPAND";
    why: string[];
    recommended_strategy: string;
    priority_actions: string[];
    overall_confidence: number;
  };
  executive_summary: {
    market_attractiveness: string;
    competitive_intensity: string;
    customer_opportunity: string;
    entry_risk: string;
    overall_recommendation: "ENTER" | "HOLD" | "EXIT" | "EXPAND";
    narrative: string;
    priority_actions: string[];
  };
  assumptions: Record<string, unknown>;
  case_id?: string | null;
};

export type ScenarioResult = {
  name: string;
  expected_share_pct: number;
  entry_investment: number;
  annual_growth_pct: number;
  price_index: number;
  revenue_potential: number;
  profit_potential: number;
  break_even_years: number | null;
  roi_pct: number;
  risk_score: number;
  score: number;
};

export type GenerateResponse = {
  report: MarketIntelligenceReport;
  pack_slug: string;
  note?: string | null;
};
