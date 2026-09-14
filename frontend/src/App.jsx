import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import { LanguageProvider } from './context/LanguageContext';

import Navbar from './components/Navbar';
import PublicHomePage from './pages/PublicHomePage';
import LoginPage from './pages/LoginPage';
import OfficerDashboard from './pages/OfficerDashboard';
import NewRegistrationsPage from './pages/NewRegistrationsPage';
import DigitizeHistoricalPage from './pages/DigitizeHistoricalPage';
import SplitScreenVerificationPage from './pages/SplitScreenVerificationPage';
import VerificationQueuePage from './pages/VerificationQueuePage';
import AILearningPage from './pages/AILearningPage';
import AuditLogsPage from './pages/AuditLogsPage';
import GISMapPage from './pages/GISMapPage';
import RegistrationStatusPage from './pages/RegistrationStatusPage';
import CrossDocumentVerificationPage from './pages/CrossDocumentVerificationPage';




// Protected Route wrapper for Government Officer roles
const ProtectedOfficerRoute = ({ children }) => {
  const { isOfficer } = useAuth();
  if (!isOfficer) {
    return <Navigate to="/login" replace />;
  }
  return children;
};

function App() {
  return (
    <AuthProvider>
      <LanguageProvider>
        <BrowserRouter>
          <div className="min-h-screen flex flex-col bg-slate-50 font-sans text-slate-900">
            {/* Official Government Navbar */}
            <Navbar />

          {/* Main Application Routes */}
          <main className="flex-1 flex flex-col">
            <Routes>
              {/* Public Portal Routes */}
              <Route path="/" element={<PublicHomePage />} />
              <Route path="/status-tracker" element={<RegistrationStatusPage />} />
              <Route path="/gis-map" element={<GISMapPage />} />
              <Route path="/login" element={<LoginPage />} />

              {/* Government Officer Routes */}
              <Route
                path="/officer/dashboard"
                element={
                  <ProtectedOfficerRoute>
                    <OfficerDashboard />
                  </ProtectedOfficerRoute>
                }
              />
              <Route
                path="/officer/new-registrations"
                element={
                  <ProtectedOfficerRoute>
                    <NewRegistrationsPage />
                  </ProtectedOfficerRoute>
                }
              />
              <Route
                path="/officer/digitize-historical"
                element={
                  <ProtectedOfficerRoute>
                    <DigitizeHistoricalPage />
                  </ProtectedOfficerRoute>
                }
              />
              <Route
                path="/officer/verification-queue"
                element={
                  <ProtectedOfficerRoute>
                    <VerificationQueuePage />
                  </ProtectedOfficerRoute>
                }
              />
              <Route
                path="/officer/verification/:id"
                element={
                  <ProtectedOfficerRoute>
                    <SplitScreenVerificationPage />
                  </ProtectedOfficerRoute>
                }
              />
              <Route
                path="/officer/ai-learning"
                element={
                  <ProtectedOfficerRoute>
                    <AILearningPage />
                  </ProtectedOfficerRoute>
                }
              />
              <Route
                path="/officer/audit-logs"
                element={
                  <ProtectedOfficerRoute>
                    <AuditLogsPage />
                  </ProtectedOfficerRoute>
                }
              />
              <Route
                path="/officer/cross-verification"
                element={
                  <ProtectedOfficerRoute>
                    <CrossDocumentVerificationPage />
                  </ProtectedOfficerRoute>
                }
              />
              <Route
                path="/officer/cross-verify"
                element={
                  <ProtectedOfficerRoute>
                    <CrossDocumentVerificationPage />
                  </ProtectedOfficerRoute>
                }
              />


              {/* Fallback */}
              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
          </main>

          {/* Government Portal Footer */}
          <footer className="bg-slate-900 text-slate-400 text-xs py-6 px-4 border-t border-slate-800">
            <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-4">
              <div>
                <div className="font-bold text-slate-200">
                  Digital Land Records Portal • SIH26018 Hackathon Prototype
                </div>
                <div>Department of Land Resources (DoLR), Ministry of Rural Development, Government of India</div>
              </div>
              <div className="text-center sm:text-right">
                <span className="text-amber-400 font-medium">Proposed Prototype Target:</span> Public viewing within 2–3 days subject to officer verification.
              </div>
            </div>
          </footer>
        </div>
      </BrowserRouter>
      </LanguageProvider>
    </AuthProvider>
  );
}

export default App;
