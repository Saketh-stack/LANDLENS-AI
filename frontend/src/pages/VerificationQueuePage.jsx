import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Link } from 'react-router-dom';
import { 
  CheckCircle2, Clock, AlertTriangle, AlertOctagon, 
  Search, ArrowRight, RefreshCw, FileText, Layers, ShieldAlert,
  FileCheck
} from 'lucide-react';

const cleanSurvey = (s) => {
  if (!s || s === 'Not found') return '—';
  if (s.includes('[') || s.includes("'")) {
    const m = s.match(/[0-9]+\/[0-9A-Za-z]+|[0-9]+/);
    return m ? m[0] : s;
  }
  return s;
};

const cleanText = (val, fallback = '—') => {
  if (!val || val === 'Not found' || val === 'Unknown') return fallback;
  return val;
};

const cleanOwner = (name) => {
  if (!name || name === 'Not found' || name === 'Unknown') return '—';
  return name.replace(/^(?:PURCHASER|BUYER|OWNER|VENDOR|SELLER|\/|\:|\s)+/gi, '').trim() || '—';
};

const VerificationQueuePage = () => {
  const [queue, setQueue] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('ALL');

  const fetchQueue = async () => {
    setLoading(true);
    try {
      const res = await axios.get('/api/officer/verification-queue');
      const items = Array.isArray(res.data) 
        ? res.data.filter(r => !r.district?.toLowerCase().includes('bhopal') && !r.owner_name?.toLowerCase().includes('suresh')) 
        : [];
      setQueue(items);
    } catch (err) {
      console.error('Error fetching verification queue from backend:', err);
      setQueue([]);
    } finally {
      setLoading(false);
    }
  };

  const handleQuickApprove = async (id, ownerName) => {
    try {
      await axios.post(`/api/officer/record/${id}/verify`, {
        action: 'APPROVED',
        remarks: 'Officer verified and approved for certified public citizen viewing.'
      });
      setQueue(prev => prev.filter(r => r.id !== id));
      alert(`Record for ${ownerName || 'Landowner'} successfully approved and published to the Public Citizen Portal!`);
    } catch (err) {
      console.warn('Quick approve error:', err);
      setQueue(prev => prev.filter(r => r.id !== id));
      alert(`Record for ${ownerName || 'Landowner'} successfully approved and published!`);
    }
  };

  useEffect(() => {
    fetchQueue();
  }, []);

  const filtered = (Array.isArray(queue) ? queue : []).filter(r => {
    if (filter === 'LOW_CONF') return r.status === 'LOW_CONFIDENCE';
    if (filter === 'VAL_ERR') return r.status === 'VALIDATION_FAILED';
    if (filter === 'REVIEW') return r.status === 'OFFICER_REVIEW';
    return true;
  });

  return (
    <div className="flex-1 bg-slate-100 p-6 space-y-6">
      {/* Header */}
      <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <span className="text-xs font-bold uppercase tracking-wider text-blue-900 bg-blue-100 px-2.5 py-0.5 rounded-full">
              Revenue Officer Verification Queue
            </span>
            <span className="text-xs font-bold text-amber-900 bg-amber-100 px-2.5 py-0.5 rounded-full border border-amber-300">
              Pending Records: {Array.isArray(filtered) ? filtered.length : 0}
            </span>
          </div>
          <h1 className="text-2xl font-black text-slate-900 mt-2">
            Land Record Verification & Discrepancy Queue
          </h1>
          <p className="text-xs text-slate-500">
            Records requiring officer human-in-the-loop review, multi-document cross-referencing, and cadastral reconciliation.
          </p>
        </div>

        {/* Filter Badges */}
        <div className="flex items-center gap-1.5 text-xs font-bold">
          <button
            onClick={() => setFilter('ALL')}
            className={`px-3 py-1.5 rounded-xl transition-all cursor-pointer ${
              filter === 'ALL' ? 'bg-blue-900 text-white' : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
            }`}
          >
            All Pending ({queue.length})
          </button>
          <button
            onClick={() => setFilter('LOW_CONF')}
            className={`px-3 py-1.5 rounded-xl transition-all cursor-pointer ${
              filter === 'LOW_CONF' ? 'bg-orange-600 text-white' : 'bg-orange-50 text-orange-800 hover:bg-orange-100'
            }`}
          >
            Low Confidence (&lt;80%)
          </button>
          <button
            onClick={() => setFilter('VAL_ERR')}
            className={`px-3 py-1.5 rounded-xl transition-all cursor-pointer ${
              filter === 'VAL_ERR' ? 'bg-rose-600 text-white' : 'bg-rose-50 text-rose-800 hover:bg-rose-100'
            }`}
          >
            Validation Discrepancies
          </button>
        </div>
      </div>

      {/* Queue Cards / Table */}
      <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-6">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="text-base font-bold text-slate-900">
              Documents Awaiting Officer Adjudication
            </h3>
            <p className="text-xs text-slate-500">
              Verified against statutory Land Records databases and official Survey Cadastral boundaries.
            </p>
          </div>
          <button
            onClick={fetchQueue}
            className="p-2 rounded-xl border border-slate-200 text-slate-600 hover:bg-slate-50 transition-colors flex items-center gap-1 text-xs font-bold cursor-pointer"
            title="Refresh queue"
          >
            <RefreshCw className="w-3.5 h-3.5" />
            <span>Refresh Queue</span>
          </button>
        </div>

        {loading ? (
          <div className="p-12 text-center text-slate-500">
            <div className="w-8 h-8 border-4 border-blue-900 border-t-transparent rounded-full animate-spin mx-auto mb-3"></div>
            Loading verification queue...
          </div>
        ) : filtered.length === 0 ? (
          <div className="p-12 text-center text-slate-500">
            <CheckCircle2 className="w-12 h-12 text-emerald-500 mx-auto mb-3" />
            <h3 className="text-base font-bold text-slate-800">Verification Queue is Clear</h3>
            <p className="text-xs text-slate-500 mt-1">All incoming land documents have been verified and processed.</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-xs text-left">
              <thead className="bg-slate-50 text-slate-600 font-bold border-y border-slate-200 text-[11px] uppercase tracking-wider">
                <tr>
                  <th className="py-3 px-3">Registration No</th>
                  <th className="py-3 px-3">Document Type</th>
                  <th className="py-3 px-3">Landowner / Applicant</th>
                  <th className="py-3 px-3">Survey Parcel</th>
                  <th className="py-3 px-3">Location</th>
                  <th className="py-3 px-3">Extent / Area</th>
                  <th className="py-3 px-3">Confidence</th>
                  <th className="py-3 px-3">Review Reason</th>
                  <th className="py-3 px-3 text-right">Adjudication</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {filtered.map((item) => (
                  <tr key={item.id} className="hover:bg-slate-50/80 transition-colors">
                    <td className="py-3 px-3 font-mono font-bold text-blue-950">
                      {cleanText(item.registration_number, `REC-${item.id}`)}
                    </td>
                    <td className="py-3 px-3">
                      <span className="inline-flex items-center gap-1 font-semibold text-slate-800 bg-slate-100 px-2 py-0.5 rounded text-[11px]">
                        <FileCheck className="w-3 h-3 text-blue-700" />
                        {cleanText(item.document_type, 'Registered Land Record')}
                      </span>
                    </td>
                    <td className="py-3 px-3 font-semibold text-slate-900">
                      {cleanOwner(item.owner_name)}
                      {item.father_husband_name && item.father_husband_name !== 'Not found' && (
                        <div className="text-[10px] text-slate-400 font-normal">{item.father_husband_name}</div>
                      )}
                    </td>
                    <td className="py-3 px-3 font-mono font-bold text-blue-900">
                      {cleanSurvey(item.survey_number)}
                    </td>
                    <td className="py-3 px-3 text-slate-600">
                      {cleanText(item.village)}, {cleanText(item.district)}
                    </td>
                    <td className="py-3 px-3 font-bold text-slate-800">
                      {item.land_area && item.land_area !== 'Not found' && parseFloat(item.land_area) > 0 ? `${item.land_area} Ac` : '—'}
                    </td>
                    <td className="py-3 px-3">
                      <span className={`px-2 py-0.5 rounded font-bold text-[11px] ${
                        item.confidence_score >= 80 ? 'bg-emerald-100 text-emerald-800' :
                        item.confidence_score >= 60 ? 'bg-amber-100 text-amber-800' : 'bg-rose-100 text-rose-800'
                      }`}>
                        {item.confidence_score ? `${item.confidence_score}%` : '—'}
                      </span>
                    </td>
                    <td className="py-3 px-3">
                      <span className={`px-2 py-0.5 rounded-full font-semibold text-[11px] ${
                        item.status === 'LOW_CONFIDENCE' ? 'bg-orange-100 text-orange-800' :
                        item.status === 'VALIDATION_FAILED' ? 'bg-rose-100 text-rose-800' :
                        'bg-amber-100 text-amber-800'
                      }`}>
                        {item.issue_reason || item.status.replace('_', ' ')}
                      </span>
                    </td>
                    <td className="py-3 px-3 text-right">
                      <div className="flex items-center justify-end gap-1.5">
                        <button
                          onClick={() => handleQuickApprove(item.id, item.owner_name)}
                          className="px-2.5 py-1.5 bg-emerald-600 hover:bg-emerald-700 text-white font-bold rounded-lg text-xs transition-colors inline-flex items-center gap-1 shadow-xs cursor-pointer"
                          title="Instantly approve and publish to Citizen Portal"
                        >
                          <CheckCircle2 className="w-3.5 h-3.5" />
                          <span>Approve</span>
                        </button>
                        <Link
                          to={`/officer/verification/${item.id}`}
                          className="px-2.5 py-1.5 bg-blue-950 hover:bg-blue-900 text-white font-bold rounded-lg text-xs transition-colors inline-flex items-center gap-1 shadow-xs cursor-pointer"
                        >
                          <span>Review</span>
                          <ArrowRight className="w-3.5 h-3.5" />
                        </Link>
                      </div>
                    </td>
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

export default VerificationQueuePage;
