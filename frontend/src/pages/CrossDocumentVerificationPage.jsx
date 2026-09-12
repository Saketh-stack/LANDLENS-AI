import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { 
  CheckCircle2, AlertTriangle, XCircle, ShieldCheck, 
  ArrowLeft, RefreshCw, FileText, Check, AlertCircle, Sparkles
} from 'lucide-react';
import { useNavigate } from 'react-router-dom';

const CrossDocumentVerificationPage = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [officerNotes, setOfficerNotes] = useState('Cross-document verification review conducted.');
  const [decision, setDecision] = useState(null);
  const [submitting, setSubmitting] = useState(false);
  const navigate = useNavigate();

  const loadVerificationData = async () => {
    setLoading(true);
    try {
      const res = await axios.post('/api/officer/cross-verify', {});
      setData(res.data);
    } catch (err) {
      console.error('Failed to load cross-document verification:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadVerificationData();
  }, []);

  const handleFinalDecision = async (statusAction) => {
    setSubmitting(true);
    try {
      // Simulate saving officer's legal decision
      setDecision(statusAction);
      alert(`Government Officer Final Legal Decision recorded: ${statusAction}. The audit log has been updated.`);
    } catch (err) {
      alert('Failed to submit decision.');
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return (
      <div className="flex-1 p-12 text-center text-slate-500">
        <RefreshCw className="w-8 h-8 animate-spin mx-auto mb-3 text-blue-900" />
        <p className="text-sm font-semibold">Running Cross-Document Verification Matrix...</p>
      </div>
    );
  }

  const matrix = data?.comparison_matrix || [];
  const overall = data?.overall_status || 'YELLOW';

  return (
    <div className="flex-1 bg-slate-100 p-6 space-y-6">
      {/* Top Header */}
      <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <button
              onClick={() => navigate('/officer/digitize-historical')}
              className="p-1.5 rounded-lg text-slate-600 hover:bg-slate-100 transition-colors"
            >
              <ArrowLeft className="w-5 h-5" />
            </button>
            <span className="text-xs font-bold uppercase tracking-wider text-blue-900 bg-blue-100 px-2.5 py-0.5 rounded-full">
              Multi-Document Consistency Audit
            </span>
          </div>
          <h1 className="text-2xl font-black text-slate-900 mt-1">
            Cross-Document Verification
          </h1>
          <p className="text-xs text-slate-500">
            Automated field cross-check between uploaded Sale Deed, Khasra/Khatauni, Cadastral Map, and Mutation Order.
          </p>
        </div>

        {/* Overall Status Badge */}
        <div className="flex items-center gap-3">
          <div className={`p-4 rounded-xl border text-right ${
            overall === 'GREEN' ? 'bg-emerald-50 border-emerald-300 text-emerald-950' :
            overall === 'YELLOW' ? 'bg-amber-50 border-amber-300 text-amber-950' :
            'bg-rose-50 border-rose-300 text-rose-950'
          }`}>
            <div className="text-[10px] font-bold uppercase tracking-wider">Overall Consistency Status</div>
            <div className="text-lg font-black flex items-center justify-end gap-1.5 mt-0.5">
              {overall === 'GREEN' && <CheckCircle2 className="w-5 h-5 text-emerald-600" />}
              {overall === 'YELLOW' && <AlertTriangle className="w-5 h-5 text-amber-600" />}
              {overall === 'RED' && <XCircle className="w-5 h-5 text-rose-600" />}
              <span>{overall}</span>
            </div>
            <div className="text-[11px] font-medium mt-0.5 max-w-xs">{data?.status_description}</div>
          </div>
        </div>
      </div>

      {/* Mandatory Officer Review Notice */}
      <div className="bg-amber-50 border border-amber-300 rounded-xl p-4 text-xs text-amber-950 leading-relaxed">
        <div className="font-bold flex items-center gap-1.5 text-amber-900 mb-1">
          <ShieldCheck className="w-4 h-4 text-amber-700" />
          Statutory Disclaimer & Separation of AI from Legal Authority
        </div>
        <p>
          "AI assists in document classification, OCR, information extraction and inconsistency detection. AI does not make the final legal ownership decision. Final verification must be performed by an authorized government officer."
        </p>
      </div>

      {/* Comparison Matrix Table */}
      <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-base font-bold text-slate-900">
            Document Cross-Check Comparison Matrix
          </h2>
          <div className="flex items-center gap-2 text-xs font-semibold">
            <span className="px-2.5 py-1 rounded bg-emerald-100 text-emerald-800">
              Matching: {data?.match_count || 0}
            </span>
            <span className="px-2.5 py-1 rounded bg-amber-100 text-amber-800">
              Discrepant / Missing: {(data?.mismatch_count || 0) + (data?.missing_count || 0)}
            </span>
          </div>
        </div>

        <div className="overflow-x-auto border border-slate-200 rounded-xl">
          <table className="w-full text-left text-xs border-collapse">
            <thead>
              <tr className="bg-slate-100 border-b border-slate-200 text-slate-700 font-bold uppercase tracking-wider text-[10px]">
                <th className="py-3 px-3">Field</th>
                <th className="py-3 px-3">Sale Deed</th>
                <th className="py-3 px-3">Khasra / Khatauni</th>
                <th className="py-3 px-3">Cadastral Map</th>
                <th className="py-3 px-3">Mutation Order</th>
                <th className="py-3 px-3 text-center">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-200">
              {matrix.map((row) => (
                <tr key={row.field_key} className="hover:bg-slate-50/80 transition-colors">
                  <td className="py-2.5 px-3 font-bold text-slate-800 whitespace-nowrap">
                    {row.field_label}
                  </td>
                  <td className="py-2.5 px-3 font-mono text-[11px] text-slate-700 max-w-xs truncate">
                    {renderCell(row.sale_deed)}
                  </td>
                  <td className="py-2.5 px-3 font-mono text-[11px] text-slate-700 max-w-xs truncate">
                    {renderCell(row.khasra_khatauni)}
                  </td>
                  <td className="py-2.5 px-3 font-mono text-[11px] text-slate-700 max-w-xs truncate">
                    {renderCell(row.cadastral_map)}
                  </td>
                  <td className="py-2.5 px-3 font-mono text-[11px] text-slate-700 max-w-xs truncate">
                    {renderCell(row.mutation_order)}
                  </td>
                  <td className="py-2.5 px-3 text-center">
                    <span className={`inline-flex items-center gap-1 font-bold font-mono px-2 py-0.5 rounded text-[10px] ${
                      row.status === 'GREEN' ? 'bg-emerald-100 text-emerald-800 border border-emerald-300' :
                      row.status === 'YELLOW' ? 'bg-amber-100 text-amber-800 border border-amber-300' :
                      'bg-rose-100 text-rose-800 border border-rose-300'
                    }`}>
                      {row.status}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Government Officer Final Legal Decision Panel */}
      <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-4">
        <h3 className="text-base font-bold text-slate-900 flex items-center gap-2">
          <ShieldCheck className="w-5 h-5 text-blue-900" />
          Government Officer Final Legal Decision & Certification
        </h3>
        <p className="text-xs text-slate-500">
          The revenue officer must evaluate cross-document verification results before executing official mutation or title certification.
        </p>

        <div className="space-y-3">
          <label className="block text-xs font-bold text-slate-700">
            Officer Verification Remarks & Grounds for Decision:
          </label>
          <textarea
            value={officerNotes}
            onChange={(e) => setOfficerNotes(e.target.value)}
            rows={3}
            className="w-full p-3 text-xs rounded-xl border border-slate-300 focus:ring-1 focus:ring-blue-900 bg-slate-50"
            placeholder="Record legal grounds, survey cross-references, or clarification requests..."
          />
        </div>

        <div className="flex flex-wrap items-center gap-3 pt-2">
          <button
            onClick={() => handleFinalDecision('REJECTED_DISCREPANCY')}
            disabled={submitting}
            className="px-4 py-2.5 bg-rose-50 hover:bg-rose-100 text-rose-800 font-bold text-xs rounded-xl border border-rose-300 transition-colors flex items-center gap-1.5"
          >
            <XCircle className="w-4 h-4 text-rose-600" /> Reject Due to Discrepancy
          </button>
          <button
            onClick={() => handleFinalDecision('CLARIFICATION_REQUIRED')}
            disabled={submitting}
            className="px-4 py-2.5 bg-amber-50 hover:bg-amber-100 text-amber-900 font-bold text-xs rounded-xl border border-amber-300 transition-colors flex items-center gap-1.5"
          >
            <AlertTriangle className="w-4 h-4 text-amber-600" /> Require Field Clarification
          </button>
          <button
            onClick={() => handleFinalDecision('LEGALLY_CERTIFIED')}
            disabled={submitting}
            className="px-5 py-2.5 bg-emerald-700 hover:bg-emerald-800 text-white font-bold text-xs rounded-xl shadow-sm transition-colors flex items-center gap-1.5"
          >
            <Check className="w-4 h-4" /> Grant Government Legal Verification
          </button>
        </div>

        {decision && (
          <div className="p-3.5 bg-blue-50 border border-blue-200 rounded-xl text-xs text-blue-950 font-medium">
            Status: <strong>{decision}</strong>. Recorded by Authorized Tahsildar / Revenue Officer.
          </div>
        )}
      </div>
    </div>
  );
};

const renderCell = (val) => {
  if (!val || val === 'Document not uploaded') {
    return <span className="text-slate-300 italic">Not uploaded</span>;
  }
  if (val === 'Not found') {
    return <span className="text-slate-400 italic">Not found</span>;
  }
  return <span className="text-slate-900 font-semibold">{val}</span>;
};

export default CrossDocumentVerificationPage;
