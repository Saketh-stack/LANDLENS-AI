import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { ShieldCheck, Lock, User, AlertCircle, Sparkles } from 'lucide-react';

const LoginPage = () => {
  const [username, setUsername] = useState('officer');
  const [password, setPassword] = useState('officer123');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      const user = await login(username, password);
      if (user.role === 'OFFICER' || user.role === 'ADMIN') {
        navigate('/officer/dashboard');
      } else {
        navigate('/');
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Authentication failed. Please check credentials.');
    } finally {
      setLoading(false);
    }
  };

  const setPreset = (u, p) => {
    setUsername(u);
    setPassword(p);
  };

  return (
    <div className="flex-1 flex items-center justify-center p-4 bg-slate-100 min-h-[calc(100vh-120px)]">
      <div className="w-full max-w-md bg-white rounded-2xl shadow-xl border border-slate-200 overflow-hidden">
        {/* Top Header */}
        <div className="bg-gradient-to-r from-blue-950 to-slate-900 text-white p-6 text-center">
          <div className="w-12 h-12 rounded-2xl bg-amber-500/20 border border-amber-500/40 text-amber-400 flex items-center justify-center mx-auto mb-3">
            <ShieldCheck className="w-6 h-6" />
          </div>
          <h2 className="text-xl font-bold">Government Officer Portal</h2>
          <p className="text-xs text-slate-300 mt-1">
            Department of Land Resources (DoLR) • Revenue Verification System
          </p>
        </div>

        {/* Demo Fast Login Switcher */}
        <div className="bg-amber-50 border-b border-amber-200 p-3 text-xs text-amber-950">
          <div className="flex items-center gap-1.5 font-bold mb-1.5">
            <Sparkles className="w-3.5 h-3.5 text-amber-600" />
            <span>Hackathon Quick-Login Presets:</span>
          </div>
          <div className="grid grid-cols-2 gap-2">
            <button
              type="button"
              onClick={() => setPreset('officer', 'officer123')}
              className="px-2 py-1 rounded bg-white hover:bg-amber-100 border border-amber-300 text-left transition-colors text-[11px]"
            >
              <div className="font-bold text-slate-800">Officer (Tahsildar)</div>
              <div className="text-slate-500 font-mono">officer / officer123</div>
            </button>
            <button
              type="button"
              onClick={() => setPreset('admin', 'admin123')}
              className="px-2 py-1 rounded bg-white hover:bg-amber-100 border border-amber-300 text-left transition-colors text-[11px]"
            >
              <div className="font-bold text-slate-800">Administrator</div>
              <div className="text-slate-500 font-mono">admin / admin123</div>
            </button>
          </div>
        </div>

        {/* Login Form */}
        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          {error && (
            <div className="p-3 bg-rose-50 border border-rose-200 text-rose-800 text-xs rounded-lg flex items-center gap-2">
              <AlertCircle className="w-4 h-4 shrink-0 text-rose-600" />
              <span>{error}</span>
            </div>
          )}

          <div>
            <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1.5">
              Username or Email
            </label>
            <div className="relative">
              <User className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
              <input
                type="text"
                required
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                placeholder="officer@dolr.gov.in"
                className="w-full pl-9 pr-3 py-2.5 text-sm rounded-lg border border-slate-300 focus:outline-none focus:ring-2 focus:ring-blue-900"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1.5">
              Password
            </label>
            <div className="relative">
              <Lock className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
              <input
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                className="w-full pl-9 pr-3 py-2.5 text-sm rounded-lg border border-slate-300 focus:outline-none focus:ring-2 focus:ring-blue-900"
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full py-2.5 bg-blue-950 hover:bg-blue-900 text-white font-bold rounded-lg transition-colors shadow-md text-sm flex items-center justify-center gap-2"
          >
            {loading ? 'Authenticating...' : 'Sign In to Officer Console'}
          </button>

          <p className="text-center text-xs text-slate-400 pt-2">
            Secured Government Gateway • Strictly Authorized Personnel Only
          </p>
        </form>
      </div>
    </div>
  );
};

export default LoginPage;
