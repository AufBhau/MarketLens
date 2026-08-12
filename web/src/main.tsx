import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import App from "./App";
import HomePage from "./pages/HomePage";
import ReportPage from "./pages/ReportPage";
import { ReportProvider } from "./state/ReportContext";
import "./index.css";

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <ReportProvider>
      <BrowserRouter>
        <Routes>
          <Route element={<App />}>
            <Route path="/" element={<HomePage />} />
            <Route path="/report" element={<ReportPage />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </ReportProvider>
  </StrictMode>,
);
