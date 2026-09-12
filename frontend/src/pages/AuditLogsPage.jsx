import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { ShieldCheck, Clock, User, Filter, RefreshCw } from 'lucide-react';

const AuditLogsPage = () => {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchLogs = async () => {
    setLoading(true);
    try {
      const res = await axios.get('/api/officer/audit-logs');
      setLogs(res.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLogs();
  }, []);

  return (
    <div className="flex-1 bg-slate-100 p-6 space-y-6">
      {/* Header */}
      <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-700 bg-slate-100 px-2.5 py-0.5 rounded-full">
              Government Compliance Trail
            </span>
            <span className="text-xs font-bold text-emerald-800 bg-emerald-100 px-2.5 py-0.5 rounded-full border border-emerald-300">
              Tamper-Evident Chronological Ledger
            </span>
          </div>
          <h1 className="text-2xl font-black text-slate-900 mt-2">
            System Audit Trail & Access Logs
          </h1>
          <p className="text-xs text-slate-500">
            Every document upload, OCR run, validation error, officer edit, and approval action is permanently recorded.
          </p>
        </div>

        <button
          onClick={fetchLogs}
          className="px-3.5 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 font-bold rounded-xl text-xs transition-colors flex items-center gap-1.5 self-start"
        >
          <RefreshCw className="w-4 h-4" /> Refresh Trail
        </button>
      </div>

      {/* Logs Table */}
      <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-6">
        {loading ? (
          <div className="p-12 text-center text-slate-500">
            <div className="w-8 h-8 border-4 border-blue-900 border-t-transparent rounded-full animate-spin mx-auto mb-3"></div>
            Loading audit ledger...
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-xs text-left">
              <thead className="bg-slate-50 text-slate-600 font-bold border-y border-slate-200">
                <tr>
                  <th className="py-2.5 px-3">Timestamp</th>
                  <th className="py-2.5 px-3">Actor</th>
                  <th className="py-2.5 px-3">Role</th>
                  <th className="py-2.5 px-3">Action</th>
                  <th className="py-2.5 px-3">Entity ID</th>
                  <th className="py-2.5 px-3">Audit Details</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {logs.map((l) => (
                  <tr key={l.id} className="hover:bg-slate-50">
                    <td className="py-3 px-3 font-mono text-slate-500 whitespace-nowrap">{l.timestamp}</td>
                    <td className="py-3 px-3 font-bold text-slate-900">{l.actor}</td>
                    <td className="py-3 px-3">
                      <span className="px-2 py-0.5 rounded font-mono text-[10px] bg-slate-100 text-slate-700 font-bold">
                        {l.actor_role}
                      </span>
                    </td>
                    <td className="py-3 px-3 font-bold text-blue-950">{l.action}</td>
                    <td className="py-3 px-3 font-mono text-slate-600">{l.entity_id || '—'}</td>
                    <td className="py-3 px-3 text-slate-700 leading-relaxed">{l.details}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};

export default AuditLogsPage;
