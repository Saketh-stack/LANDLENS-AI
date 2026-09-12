import React from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { ShieldCheck, Search, FileText, Map, Clock, LogIn, LogOut, UserCheck, Activity, Database, CheckCircle2 } from 'lucide-react';

const Navbar = () => {
  const { user, logout, isOfficer } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const isActive = (path) => location.pathname === path;

  return (
    <header className="w-full bg-white border-b border-slate-200 shadow-sm sticky top-0 z-40">
      {/* Top Tricolor Brand Bar */}
      <div className="h-1.5 w-full bg-gradient-to-r from-amber-500 via-white to-emerald-600"></div>

      {/* Main Government Header */}
      <div className="max-w-7xl mx-auto px-4 py-3 flex flex-wrap items-center justify-between gap-4">
        {/* Emblem & Portal Title */}
        <Link to="/" className="flex items-center gap-3 group">
          <div className="w-11 h-11 rounded-full bg-slate-900 flex items-center justify-center text-white font-bold text-lg border-2 border-amber-500 shadow-sm">
            <span className="text-amber-400">DoLR</span>
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="text-xs uppercase tracking-widest text-slate-500 font-semibold">
                Ministry of Rural Development • Gov of India
              </span>
              <span className="bg-emerald-100 text-emerald-800 text-[10px] font-bold px-1.5 py-0.5 rounded border border-emerald-300">
                SIH26018
              </span>
            </div>
            <h1 className="text-xl font-black text-slate-900 tracking-tight leading-tight group-hover:text-blue-900 transition-colors">
              Digital Land Records Portal
            </h1>
            <p className="text-xs text-slate-500 hidden sm:block">
              Intelligent AI/OCR Land Record Digitization and Validation Platform
            </p>
          </div>
        </Link>

        {/* Navigation Links */}
        <nav className="flex items-center flex-wrap gap-1 md:gap-2 text-sm font-medium">
          <Link
            to="/"
            className={`px-3 py-1.5 rounded-lg transition-colors flex items-center gap-1.5 ${
              isActive('/') ? 'bg-blue-50 text-blue-900 font-bold border border-blue-200' : 'text-slate-600 hover:text-blue-900 hover:bg-slate-50'
            }`}
          >
            <Search className="w-4 h-4 text-blue-600" />
            Search Records
          </Link>

          <Link
            to="/status-tracker"
            className={`px-3 py-1.5 rounded-lg transition-colors flex items-center gap-1.5 ${
              isActive('/status-tracker') ? 'bg-blue-50 text-blue-900 font-bold border border-blue-200' : 'text-slate-600 hover:text-blue-900 hover:bg-slate-50'
            }`}
          >
            <Clock className="w-4 h-4 text-emerald-600" />
            Registration Status
          </Link>

          <Link
            to="/gis-map"
            className={`px-3 py-1.5 rounded-lg transition-colors flex items-center gap-1.5 ${
              isActive('/gis-map') ? 'bg-blue-50 text-blue-900 font-bold border border-blue-200' : 'text-slate-600 hover:text-blue-900 hover:bg-slate-50'
            }`}
          >
            <Map className="w-4 h-4 text-amber-600" />
            Cadastral GIS Map
          </Link>

          {/* Officer Workspace Switcher */}
          {isOfficer ? (
            <div className="flex items-center gap-2 pl-2 border-l border-slate-200">
              <Link
                to="/officer/dashboard"
                className={`px-3 py-1.5 rounded-lg transition-colors flex items-center gap-1.5 ${
                  location.pathname.startsWith('/officer') ? 'bg-amber-100 text-amber-900 font-bold border border-amber-300' : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
                }`}
              >
                <ShieldCheck className="w-4 h-4 text-amber-700" />
                Officer Workspace
              </Link>
              <button
                onClick={() => { logout(); navigate('/'); }}
                title="Sign out of Officer Portal"
                className="p-1.5 rounded-lg text-rose-600 hover:bg-rose-50 transition-colors"
              >
                <LogOut className="w-4 h-4" />
              </button>
            </div>
          ) : (
            <Link
              to="/login"
              className="ml-2 px-3.5 py-1.5 rounded-lg bg-blue-900 hover:bg-blue-800 text-white font-semibold transition-all shadow-sm flex items-center gap-1.5"
            >
              <LogIn className="w-4 h-4 text-amber-400" />
              Officer Login
            </Link>
          )}
        </nav>
      </div>

      {/* Officer Internal Subnavigation Bar */}
      {isOfficer && location.pathname.startsWith('/officer') && (
        <div className="bg-slate-800 text-slate-200 px-4 py-2 border-t border-slate-700 text-xs">
          <div className="max-w-7xl mx-auto flex items-center justify-between flex-wrap gap-2">
            <div className="flex items-center gap-4">
              <span className="font-bold text-amber-400 uppercase tracking-wide flex items-center gap-1">
                <UserCheck className="w-3.5 h-3.5" />
                {user?.designation || 'Tahsildar'} : {user?.full_name}
              </span>
              <div className="h-3 w-px bg-slate-600"></div>
              <Link to="/officer/dashboard" className={`hover:text-amber-400 ${isActive('/officer/dashboard') ? 'text-amber-400 font-bold' : ''}`}>
                Dashboard
              </Link>
              <Link to="/officer/new-registrations" className={`hover:text-amber-400 ${isActive('/officer/new-registrations') ? 'text-amber-400 font-bold' : ''}`}>
                New Registrations (Mock API)
              </Link>
              <Link to="/officer/digitize-historical" className={`hover:text-amber-400 ${isActive('/officer/digitize-historical') ? 'text-amber-400 font-bold' : ''}`}>
                Digitize Historical Record
              </Link>
              <Link to="/officer/verification-queue" className={`hover:text-amber-400 ${isActive('/officer/verification-queue') ? 'text-amber-400 font-bold' : ''}`}>
                Verification Queue
              </Link>
              <Link to="/officer/ai-learning" className={`hover:text-amber-400 ${isActive('/officer/ai-learning') ? 'text-amber-400 font-bold' : ''}`}>
                AI Learning Metrics
              </Link>
              <Link to="/officer/audit-logs" className={`hover:text-amber-400 ${isActive('/officer/audit-logs') ? 'text-amber-400 font-bold' : ''}`}>
                Audit Trail
              </Link>
            </div>
            <div className="text-slate-400 italic">
              Proposed Prototype Target: Public Viewing in 2-3 Days
            </div>
          </div>
        </div>
      )}
    </header>
  );
};

export default Navbar;
