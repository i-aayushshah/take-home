import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import AppShell from "./components/layout/AppShell";
import ProtectedRoute from "./components/layout/ProtectedRoute";
import ApplyPage from "./pages/ApplyPage";
import CandidateDetailPage from "./pages/CandidateDetailPage";
import CandidateListPage from "./pages/CandidateListPage";
import InterviewsPage from "./pages/InterviewsPage";
import LoginPage from "./pages/LoginPage";
import ToastContainer from "./components/ui/ToastContainer";

export default function App() {
  return (
    <BrowserRouter>
      <ToastContainer />
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/apply" element={<ApplyPage />} />
        <Route element={<ProtectedRoute />}>
          <Route element={<AppShell />}>
            <Route path="/candidates" element={<CandidateListPage />} />
            <Route path="/candidates/:id" element={<CandidateDetailPage />} />
            <Route path="/interviews" element={<InterviewsPage />} />
          </Route>
        </Route>
        <Route path="*" element={<Navigate to="/candidates" replace />} />
      </Routes>
    </BrowserRouter>
  );
}
