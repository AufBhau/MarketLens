import {
  createContext,
  useContext,
  useMemo,
  useState,
  type ReactNode,
} from "react";
import type { GenerateResponse } from "../types";

type ReportState = {
  data: GenerateResponse | null;
  setData: (data: GenerateResponse | null) => void;
  activeSlug: string | null;
  setActiveSlug: (slug: string | null) => void;
};

const Ctx = createContext<ReportState | null>(null);

export function ReportProvider({ children }: { children: ReactNode }) {
  const [data, setData] = useState<GenerateResponse | null>(null);
  const [activeSlug, setActiveSlug] = useState<string | null>(null);
  const value = useMemo(
    () => ({ data, setData, activeSlug, setActiveSlug }),
    [data, activeSlug],
  );
  return <Ctx.Provider value={value}>{children}</Ctx.Provider>;
}

export function useReport() {
  const ctx = useContext(Ctx);
  if (!ctx) throw new Error("useReport must be used within ReportProvider");
  return ctx;
}
