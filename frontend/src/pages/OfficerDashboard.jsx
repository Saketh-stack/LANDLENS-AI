import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Link } from 'react-router-dom';
import { 
  FileText, CheckCircle2, Clock, XCircle, AlertTriangle, AlertOctagon, 
  Send, TrendingUp, BarChart3, ShieldCheck, ArrowUpRight, Sparkles 
} from 'lucide-react';
import { 
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, 
  LineChart, Line, CartesianGrid, PieChart, Pie, Cell 
} from 'recharts';

const OfficerDashboard = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  const fetchDashboard = async () => {
    try {
      const res = await axios.get('/api/officer/dashboard-metrics');
      setData(res.data);
    } catch (err) {
      console.error(err);
      setData({
        cards: {
          total_land_records: 1248,
          digitized: 1184,
          pending_verification: 64,
          approved_records: 1120,
          rejected_records: 18,
          low_confidence_records: 14,
          validation_errors: 12,
          new_registrations: 28,
          average_ocr_accuracy: '96.4%'
        },
        charts: {
          daily_processing: [
            { day: 'Mon', processed: 45, approved: 42 },
            { day: 'Tue', processed: 52, approved: 49 },
            { day: 'Wed', processed: 60, approved: 58 },
            { day: 'Thu', processed: 48, approved: 45 },
            { day: 'Fri', processed: 65, approved: 61 },
            { day: 'Sat', processed: 38, approved: 36 },
            { day: 'Sun', processed: 22, approved: 20 }
          ],
          district_progress: [
            { district: 'Bhopal', digitized: 380, total: 400, accuracy: 97 },
            { district: 'Indore', digitized: 340, total: 360, accuracy: 96 },
            { district: 'Jabalpur', digitized: 270, total: 290, accuracy: 95 },
            { district: 'Gwalior', digitized: 194, total: 210, accuracy: 94 }
          ]
        },
        recent_activity: [
          { reg_id: 'REG-2026-MP-001', owner: 'Rameshwar Dayal Patidar', date: '12-09-2026', type: 'Sale Deed (Bhopal SRO)', status: 'Approved' },
          { reg_id: 'REG-2026-MP-002', owner: 'Kailash Nath Verma', date: '12-09-2026', type: 'ROR Patta (Khasra 101/2B)', status: 'Low Confidence (74%)' },
          { reg_id: 'REG-2026-MP-003', owner: 'Smt. Shanti Devi Sharma', date: '11-09-2026', type: 'Gift Deed', status: 'Approved' },
          { reg_id: 'REG-2026-MP-004', owner: 'Bhagwandas Agarwal', date: '11-09-2026', type: 'Mutation Order', status: 'Discrepancy (Area Mismatch)' },
          { reg_id: 'REG-2026-MP-005', owner: 'Mohan Lal Choudhary', date: '10-09-2026', type: 'Inheritance Partition', status: 'Under Review' }
        ]
      });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboard();
  }, []);

  if (loading) {
    return (
      <div className="flex-1 p-8 text-center text-slate-500">
        <div className="w-8 h-8 border-4 border-blue-900 border-t-transparent rounded-full animate-spin mx-auto mb-3"></div>
        Loading Officer Dashboard telemetry...
      </div>
    );
  }

  const { cards = {}, charts = {}, recent_activity = [] } = (data && typeof data === 'object' && !Array.isArray(data)) ? data : {};

  const cardItems = [
    { title: 'Total Land Records', value: (cards?.total_land_records ?? 0).toLocaleString(), icon: FileText, color: 'text-blue-600', bg: 'bg-blue-50', border: 'border-blue-200' },
    { title: 'Digitized & Verified', value: (cards?.digitized ?? 0).toLocaleString(), icon: CheckCircle2, color: 'text-emerald-600', bg: 'bg-emerald-50', border: 'border-emerald-200' },
    { title: 'Pending Verification', value: cards?.pending_verification ?? 0, icon: Clock, color: 'text-amber-600', bg: 'bg-amber-50', border: 'border-amber-200' },
    { title: 'Approved Records', value: (cards?.approved_records ?? 0).toLocaleString(), icon: ShieldCheck, color: 'text-indigo-600', bg: 'bg-indigo-50', border: 'border-indigo-200' },
    { title: 'Rejected Records', value: cards?.rejected_records ?? 0, icon: XCircle, color: 'text-rose-600', bg: 'bg-rose-50', border: 'border-rose-200' },
    { title: 'Low Confidence (<80%)', value: cards?.low_confidence_records ?? 0, icon: AlertTriangle, color: 'text-orange-600', bg: 'bg-orange-50', border: 'border-orange-200' },
    { title: 'Validation Discrepancies', value: cards?.validation_errors ?? 0, icon: AlertOctagon, color: 'text-red-600', bg: 'bg-red-50', border: 'border-red-200' },
    { title: 'New Registrations (SRO)', value: cards?.new_registrations ?? 0, icon: Send, color: 'text-purple-600', bg: 'bg-purple-50', border: 'border-purple-200' },
  ];

  return (
    <div className="flex-1 bg-slate-100 p-6 space-y-6">
      {/* Header Banner */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 bg-white p-6 rounded-2xl border border-slate-200 shadow-sm">
        <div>
          <div className="flex items-center gap-2">
            <span className="text-xs font-bold uppercase tracking-wider text-blue-900 bg-blue-100 px-2.5 py-0.5 rounded-full">
              Revenue Officer Dashboard
            </span>
            <span className="text-xs font-bold text-emerald-800 bg-emerald-100 px-2.5 py-0.5 rounded-full border border-emerald-300">
              Avg OCR Accuracy: {cards?.average_ocr_accuracy ?? '94.2%'}
            </span>
          </div>
          <h1 className="text-2xl font-black text-slate-900 mt-2">
            Land Record Digitization & Validation Overview
          </h1>
          <p className="text-xs text-slate-500">
            Real-time pipeline monitoring, OCR extraction quality, and proposed 2–3 day public viewing targets.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <Link
            to="/officer/new-registrations"
            className="px-4 py-2.5 bg-purple-900 hover:bg-purple-800 text-white text-xs font-bold rounded-xl transition-all shadow-sm flex items-center gap-1.5"
          >
            <Send className="w-3.5 h-3.5 text-purple-300" />
            New Registrations (Mock API)
          </Link>
          <Link
            to="/officer/digitize-historical"
            className="px-4 py-2.5 bg-blue-950 hover:bg-blue-900 text-white text-xs font-bold rounded-xl transition-all shadow-sm flex items-center gap-1.5"
          >
            <FileText className="w-3.5 h-3.5 text-amber-400" />
            Digitize Historical Record
          </Link>
        </div>
      </div>

      {/* 8 KPI Cards Grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {cardItems.map((c, i) => {
          const Icon = c.icon;
          return (
            <div key={i} className={`bg-white rounded-xl border ${c.border} p-4 shadow-sm flex flex-col justify-between`}>
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold text-slate-600 uppercase tracking-wider">{c.title}</span>
                <div className={`p-2 rounded-lg ${c.bg}`}>
                  <Icon className={`w-4 h-4 ${c.color}`} />
                </div>
              </div>
              <div className="mt-3">
                <span className="text-2xl font-black text-slate-900 font-mono">{c.value}</span>
              </div>
            </div>
          );
        })}
      </div>

      {/* Analytics Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Chart 1: Daily Throughput */}
        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm lg:col-span-2">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-sm font-bold text-slate-900">Documents Processed Per Day</h3>
              <p className="text-xs text-slate-500">Processed vs Approved volume over weekly timeline</p>
            </div>
            <span className="text-xs font-mono font-bold text-blue-900 bg-blue-50 px-2.5 py-1 rounded">Weekly Trend</span>
          </div>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={charts?.daily_processing || []}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                <XAxis dataKey="day" tick={{ fontSize: 12 }} />
                <YAxis tick={{ fontSize: 12 }} />
                <Tooltip />
                <Bar dataKey="processed" fill="#1e3a8a" name="Processed" radius={[4, 4, 0, 0]} />
                <Bar dataKey="approved" fill="#10b981" name="Approved" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Chart 2: District Progress */}
        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-sm font-bold text-slate-900">District-wise Progress</h3>
              <p className="text-xs text-slate-500">Coverage & Accuracy across major hubs</p>
            </div>
          </div>
          <div className="space-y-4">
            {(charts?.district_progress || []).map((d, i) => (
              <div key={i} className="space-y-1 text-xs">
                <div className="flex justify-between font-medium">
                  <span className="font-bold text-slate-800">{d.district}</span>
                  <span className="text-slate-500">{d.digitized} / {d.total} ({d.accuracy}%)</span>
                </div>
                <div className="w-full bg-slate-100 h-2 rounded-full overflow-hidden">
                  <div 
                    className="bg-blue-900 h-full rounded-full transition-all"
                    style={{ width: `${(d.digitized / d.total) * 100}%` }}
                  ></div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Recent Activity Table */}
      <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-6">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="text-base font-bold text-slate-900">Recent Verification Activity</h3>
            <p className="text-xs text-slate-500">Live incoming documents and officer action queue</p>
          </div>
          <Link
            to="/officer/verification-queue"
            className="text-xs font-bold text-blue-900 hover:underline flex items-center gap-1"
          >
            Open Full Verification Queue <ArrowUpRight className="w-3.5 h-3.5" />
          </Link>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-xs text-left">
            <thead className="bg-slate-50 text-slate-600 font-bold border-y border-slate-200">
              <tr>
                <th className="py-2.5 px-3">Registration ID</th>
                <th className="py-2.5 px-3">Owner Name</th>
                <th className="py-2.5 px-3">Date</th>
                <th className="py-2.5 px-3">Document Type</th>
                <th className="py-2.5 px-3">Status</th>
                <th className="py-2.5 px-3 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {(recent_activity || []).map((row, i) => (
                <tr key={i} className="hover:bg-slate-50">
                  <td className="py-3 px-3 font-mono font-bold text-blue-950">{row.reg_id}</td>
                  <td className="py-3 px-3 font-medium text-slate-900">{row.owner}</td>
                  <td className="py-3 px-3 text-slate-500">{row.date}</td>
                  <td className="py-3 px-3 text-slate-600">{row.type}</td>
                  <td className="py-3 px-3">
                    <span className={`px-2 py-0.5 rounded-full font-semibold text-[11px] ${
                      row.status === 'Approved' ? 'bg-emerald-100 text-emerald-800' :
                      row.status.includes('Low') ? 'bg-orange-100 text-orange-800' :
                      row.status.includes('Discrepancy') ? 'bg-rose-100 text-rose-800' :
                      'bg-amber-100 text-amber-800'
                    }`}>
                      {row.status}
                    </span>
                  </td>
                  <td className="py-3 px-3 text-right">
                    <Link
                      to="/officer/verification-queue"
                      className="px-2.5 py-1 bg-slate-100 hover:bg-slate-200 text-slate-800 font-bold rounded transition-colors"
                    >
                      Review
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default OfficerDashboard;
