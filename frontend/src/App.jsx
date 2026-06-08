import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import AppShell from "./components/layout/AppShell";
import ProtectedRoute from "./components/layout/ProtectedRoute";
import CandidateListPage from "./pages/CandidateListPage";
import LoginPage from "./pages/LoginPage";

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route element={<ProtectedRoute />}>
          <Route element={<AppShell />}>
            <Route path="/candidates" element={<CandidateListPage />} />
          </Route>
        </Route>
        <Route path="*" element={<Navigate to="/candidates" replace />} />
      </Routes>
    </BrowserRouter>
  );
}
