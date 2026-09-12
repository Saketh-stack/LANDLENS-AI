import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useParams, useNavigate } from 'react-router-dom';
import { 
  CheckCircle2, XCircle, AlertTriangle, ArrowLeft, Edit3, 
  Save, Check, ShieldAlert, Sparkles, Database, FileText 
} from 'lucide-react';

const SplitScreenVerificationPage = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [editableFields, setEditableFields] = useState({});
  const [editingKey, setEditingKey] = useState(null);
  const [remarks, setRemarks] = useState('Officer verification verified against Cadastral Register');
  const [submitting, setSubmitting] = useState(false);

  const fetchRecord = async () => {
    try {
      const res = await axios.get(`/api/officer/record-detail/${id}`);
      setData(res.data);
      // Initialize editable fields map
      const map = {};
      res.data.fields.forEach(f => {
        map[f.field_name] = f.value;
      });
      setEditableFields(map);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRecord();
  }, [id]);

  const handleFieldValueChange = (fieldName, val) => {
    setEditableFields(prev => ({ ...prev, [fieldName]: val }));
  };

  const handleAction = async (action) => {
    setSubmitting(true);
    try {
      // Build corrections array for AI feedback loop
      const corrections = [];
      data.fields.forEach(f => {
        if (editableFields[f.field_name] !== f.value) {
          corrections.push({
            field_name: f.field_name,
            corrected_value: editableFields[f.field_name]
          });
        }
      });

      await axios.post(`/api/officer/record/${id}/verify`, {
        action,
        remarks,
        corrections
      });

      alert(`Record status updated to: ${action}! Corrections have been logged to the AI Feedback Model.`);
      navigate('/officer/verification-queue');
    } catch (err) {
      console.error(err);
      alert('Action submission failed');
    } finally {
      setSubmitting(false);
    }
  };

  if (loading || !data) {
    return (
      <div className="flex-1 p-8 text-center text-slate-500">
        <div className="w-8 h-8 border-4 border-blue-900 border-t-transparent rounded-full animate-spin mx-auto mb-3"></div>
        Loading split-screen verification interface...
      </div>
    );
  }

  const { record, fields, cadastral_crosscheck, validation_report } = data;

  return (
    <div className="flex-1 bg-slate-100 flex flex-col h-[calc(100vh-112px)] overflow-hidden">
      {/* Top Officer Action Toolbar */}
      <div className="bg-white border-b border-slate-200 px-6 py-3 flex items-center justify-between gap-4 shrink-0 shadow-sm">
        <div className="flex items-center gap-3">
          <button
            onClick={() => navigate('/officer/verification-queue')}
            className="p-1.5 rounded-lg text-slate-600 hover:bg-slate-100 transition-colors"
          >
            <ArrowLeft className="w-5 h-5" />
          </button>
          <div>
            <div className="flex items-center gap-2">
              <span className="text-xs font-bold font-mono text-blue-950 bg-blue-50 px-2 py-0.5 rounded border border-blue-200">
                {record.registration_number}
              </span>
              <span className="text-xs font-bold text-slate-700">
                Landowner: {record.owner_name}
              </span>
            </div>
            <span className="text-[11px] text-slate-500">
              Survey: {record.survey_number} • {record.village}, {record.district}
            </span>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex items-center gap-2">
          <input
            type="text"
            placeholder="Officer Remarks / Notes..."
            value={remarks}
            onChange={(e) => setRemarks(e.target.value)}
            className="px-3 py-1.5 text-xs rounded-lg border border-slate-300 w-64 focus:ring-1 focus:ring-blue-900"
          />

          <button
            onClick={() => handleAction('REJECTED')}
            disabled={submitting}
            className="px-3 py-1.5 bg-rose-50 hover:bg-rose-100 text-rose-700 text-xs font-bold rounded-lg border border-rose-200 transition-colors flex items-center gap-1"
          >
            <XCircle className="w-3.5 h-3.5" /> Reject
          </button>

          <button
            onClick={() => handleAction('SENT_BACK')}
            disabled={submitting}
            className="px-3 py-1.5 bg-amber-50 hover:bg-amber-100 text-amber-800 text-xs font-bold rounded-lg border border-amber-300 transition-colors flex items-center gap-1"
          >
            <AlertTriangle className="w-3.5 h-3.5" /> Send Back for Clarification
          </button>

          <button
            onClick={() => handleAction('APPROVED')}
            disabled={submitting}
            className="px-4 py-1.5 bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-bold rounded-lg shadow-sm transition-colors flex items-center gap-1.5"
          >
            <CheckCircle2 className="w-4 h-4" /> Approve & Publish to Public Portal
          </button>
        </div>
      </div>

      {/* Cross-Database Cadastral Alert Bar if mismatch */}
      {cadastral_crosscheck.mismatch_detected && (
        <div className="bg-amber-50 border-b border-amber-200 px-6 py-2 flex items-center justify-between text-xs text-amber-900 shrink-0">
          <div className="flex items-center gap-2">
            <ShieldAlert className="w-4 h-4 text-amber-600 shrink-0" />
            <span>
              <strong>Cross-Database Discrepancy:</strong> Deed Land Area = <strong>{record.land_area} Acres</strong>, whereas Official Cadastral Survey Baseline = <strong>{cadastral_crosscheck.cadastral_area} Acres</strong> (Delta: {cadastral_crosscheck.delta_acres} Acres).
            </span>
          </div>
          <button
            onClick={() => {
              handleFieldValueChange('land_area', String(cadastral_crosscheck.cadastral_area));
              alert(`Area updated to match Cadastral Baseline: ${cadastral_crosscheck.cadastral_area} Acres. This correction will feed AI Model Learning upon approval.`);
            }}
            className="px-2.5 py-1 bg-amber-200 hover:bg-amber-300 text-amber-950 font-bold rounded text-[11px] transition-colors"
          >
            Sync with Cadastral DB ({cadastral_crosscheck.cadastral_area} Ac)
          </button>
        </div>
      )}

      {/* SPLIT SCREEN MAIN CONTAINER */}
      <div className="flex-1 grid grid-cols-1 lg:grid-cols-2 divide-y lg:divide-y-0 lg:divide-x divide-slate-200 overflow-hidden">
        
        {/* LEFT PANE: Original Document Preview */}
        <div className="bg-slate-800 p-6 flex flex-col overflow-y-auto">
          <div className="flex items-center justify-between text-white text-xs mb-3">
            <div className="flex items-center gap-2">
              <FileText className="w-4 h-4 text-amber-400" />
              <span className="font-bold uppercase tracking-wider">Original Registered Document</span>
            </div>
            <span className="text-slate-400">Resolution: 300 DPI • Scanned Deed</span>
          </div>

          {/* Realistic High-Fidelity Simulated Deed Canvas */}
          <div className="flex-1 bg-[#fcf9ee] text-[#1a1714] p-8 rounded-xl shadow-2xl border-4 border-[#e3dac9] font-serif relative select-none overflow-y-auto space-y-6">
            {/* Deed Header / Seal */}
            <div className="text-center border-b-2 border-slate-900/40 pb-4">
              <div className="w-16 h-16 rounded-full border-2 border-slate-800 mx-auto flex items-center justify-center font-bold text-xs mb-1">
                GOV SEAL
              </div>
              <div className="text-xs uppercase tracking-widest font-bold text-slate-800">
                Department of Registration and Stamps
              </div>
              <div className="text-sm font-bold uppercase tracking-wide">
                Certified Extract of Registered Sale Deed / RoR
              </div>
              <div className="text-[11px] text-slate-600 font-mono mt-1">
                Deed No: {record.registration_number} | Book 1, Vol 412, Page 89
              </div>
            </div>

            {/* Visual Bounding Box Highlights */}
            <div className="text-xs leading-relaxed space-y-3 font-sans">
              <p>
                This indenture is executed on this <strong>{record.registration_date}</strong> at Tehsil <strong>{record.tehsil}</strong>, District <strong>{record.district}</strong>, State of <strong>Madhya Pradesh</strong>.
              </p>

              <div className="p-3 bg-amber-500/10 border-2 border-amber-500 rounded relative">
                <span className="absolute -top-2.5 left-2 bg-amber-500 text-slate-950 font-bold px-1.5 py-0.2 text-[9px] rounded uppercase">
                  AI OCR Zone: Landowner
                </span>
                <div>Transferee / Landowner: <strong>{record.owner_name}</strong></div>
                <div>Father / Husband: <strong>{editableFields.father_husband_name || 'Anand Kumar'}</strong></div>
              </div>

              <div className="p-3 bg-blue-500/10 border-2 border-blue-500 rounded relative">
                <span className="absolute -top-2.5 left-2 bg-blue-500 text-white font-bold px-1.5 py-0.2 text-[9px] rounded uppercase">
                  AI OCR Zone: Survey Parcel
                </span>
                <div>Survey Number: <strong>{record.survey_number}</strong></div>
                <div>Khasra No: <strong>{record.khasra_number}</strong> | Khata No: <strong>{record.khata_number}</strong></div>
                <div>Village: <strong>{record.village}</strong></div>
              </div>

              <div className={`p-3 rounded relative border-2 ${
                cadastral_crosscheck.mismatch_detected 
                  ? 'bg-rose-500/10 border-rose-500' 
                  : 'bg-emerald-500/10 border-emerald-500'
              }`}>
                <span className={`absolute -top-2.5 left-2 font-bold px-1.5 py-0.2 text-[9px] rounded uppercase ${
                  cadastral_crosscheck.mismatch_detected ? 'bg-rose-500 text-white' : 'bg-emerald-500 text-white'
                }`}>
                  AI OCR Zone: Land Area (Acres)
                </span>
                <div className="text-sm font-bold">
                  Total Land Extent: {record.land_area} Acres
                </div>
                <div className="text-[11px] text-slate-600">
                  Land Classification: {record.document_status || 'Agricultural Irrigated'}
                </div>
              </div>

              <div className="pt-4 border-t border-slate-300 flex justify-between text-[11px] text-slate-600 italic">
                <span>Sub-Registrar Signature & Thumb Impression</span>
                <span>Revenue Verification Official</span>
              </div>
            </div>
          </div>
        </div>

        {/* RIGHT PANE: Extracted Fields & Officer Corrections Form */}
        <div className="bg-white p-6 flex flex-col overflow-y-auto">
          <div className="flex items-center justify-between mb-4">
            <div>
              <div className="flex items-center gap-1.5 text-xs font-bold text-blue-900 uppercase tracking-wider">
                <Sparkles className="w-3.5 h-3.5 text-amber-500" />
                <span>AI Extracted Fields & Confidence Scores</span>
              </div>
              <p className="text-xs text-slate-500">
                Fields with &lt;80% confidence or cadastral mismatch require officer review
              </p>
            </div>
            <span className="text-xs font-bold text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200">
              Confidence: {record.confidence_score}%
            </span>
          </div>

          {/* Fields List */}
          <div className="space-y-3 flex-1 overflow-y-auto pr-1">
            {fields.map((f) => {
              const currentValue = editableFields[f.field_name] || '';
              const isEdited = currentValue !== f.value;
              const isLowConf = f.confidence < 80;
              const isEditing = editingKey === f.field_name;

              return (
                <div
                  key={f.field_name}
                  className={`p-3 rounded-xl border transition-all ${
                    isLowConf ? 'bg-amber-50/60 border-amber-300' :
                    isEdited ? 'bg-blue-50/60 border-blue-300' :
                    'bg-slate-50 border-slate-200'
                  }`}
                >
                  <div className="flex items-center justify-between text-xs mb-1">
                    <span className="font-bold text-slate-700">{f.label}</span>
                    <div className="flex items-center gap-2">
                      <span className={`px-2 py-0.5 rounded font-bold text-[10px] ${
                        f.confidence >= 80 ? 'bg-emerald-100 text-emerald-800' :
                        f.confidence >= 60 ? 'bg-amber-100 text-amber-800' : 'bg-rose-100 text-rose-800'
                      }`}>
                        {f.confidence}% Confidence
                      </span>
                      {isEdited && (
                        <span className="text-[10px] font-bold text-blue-900 bg-blue-100 px-1.5 py-0.5 rounded">
                          Modified
                        </span>
                      )}
                    </div>
                  </div>

                  {/* Field Input or Display */}
                  <div className="flex items-center gap-2 mt-1.5">
                    {isEditing ? (
                      <div className="flex items-center gap-2 flex-1">
                        <input
                          type="text"
                          value={currentValue}
                          onChange={(e) => handleFieldValueChange(f.field_name, e.target.value)}
                          className="flex-1 px-3 py-1.5 text-xs font-medium rounded border border-blue-600 focus:outline-none focus:ring-1 focus:ring-blue-600 bg-white"
                          autoFocus
                        />
                        <button
                          type="button"
                          onClick={() => setEditingKey(null)}
                          className="px-2.5 py-1.5 bg-blue-900 text-white text-xs font-bold rounded flex items-center gap-1"
                        >
                          <Check className="w-3.5 h-3.5" /> Save
                        </button>
                      </div>
                    ) : (
                      <div className="flex items-center justify-between flex-1">
                        <span className="font-bold text-sm text-slate-900 font-mono">
                          {currentValue}
                        </span>
                        <div className="flex items-center gap-1">
                          <button
                            type="button"
                            onClick={() => setEditingKey(f.field_name)}
                            className="p-1 rounded text-slate-500 hover:text-blue-900 hover:bg-slate-200 transition-colors"
                            title="Edit this extracted field"
                          >
                            <Edit3 className="w-3.5 h-3.5" />
                          </button>
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              );
            })}
          </div>

          {/* Validation Engine Findings Summary */}
          <div className="mt-4 pt-3 border-t border-slate-200 text-xs">
            <h4 className="font-bold text-slate-800 mb-2">Automated Business-Rule Check Results:</h4>
            <div className="space-y-1.5 max-h-32 overflow-y-auto pr-1">
              {validation_report.results.map((r, i) => (
                <div key={i} className="flex items-start gap-2 text-[11px]">
                  {r.status === 'PASS' && <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600 shrink-0 mt-0.5" />}
                  {r.status === 'WARNING' && <AlertTriangle className="w-3.5 h-3.5 text-amber-600 shrink-0 mt-0.5" />}
                  {r.status === 'ERROR' && <XCircle className="w-3.5 h-3.5 text-rose-600 shrink-0 mt-0.5" />}
                  <span className={r.status === 'PASS' ? 'text-slate-600' : 'text-slate-900 font-semibold'}>
                    {r.message}
                  </span>
                </div>
              ))}
            </div>
          </div>

        </div>

      </div>
    </div>
  );
};

export default SplitScreenVerificationPage;
