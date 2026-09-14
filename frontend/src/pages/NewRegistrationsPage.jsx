import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { 
  Send, Sparkles, Clock, CheckCircle2, AlertTriangle, ArrowRight, 
  ExternalLink, Eye, RefreshCw, ShieldAlert, FileText 
} from 'lucide-react';
import { useNavigate } from 'react-router-dom';

const NewRegistrationsPage = () => {
  const [registrations, setRegistrations] = useState([]);
  const [loading, setLoading] = useState(false);
  const [selectedScenario, setSelectedScenario] = useState('standard');
  const [simulating, setSimulating] = useState(false);
  const [latestProcessed, setLatestProcessed] = useState(null);
  const navigate = useNavigate();

  const fetchRegistrations = async () => {
    setLoading(true);
    try {
      const res = await axios.get('/api/mock-registration/list');
      setRegistrations(res.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRegistrations();
  }, []);

  const handleSimulate = async () => {
    setSimulating(true);
    try {
      // 1. Trigger Mock Registration from Sub-Registrar API
      const res = await axios.post('/api/mock-registration/simulate', {
        scenario: selectedScenario
      });
      const reg = res.data.registration;

      // 2. Automatically trigger pipeline simulation (OCR -> AI Extraction -> Validation -> Queue)
      const pipelineRes = await axios.post(`/api/mock-registration/${reg.id}/process-pipeline`);
      setLatestProcessed(pipelineRes.data);
      
      // Refresh list
      fetchRegistrations();
    } catch (err) {
      console.error(err);
    } finally {
      setSimulating(false);
    }
  };

  const handleApprove = async (regId) => {
    try {
      await axios.post(`/api/mock-registration/${regId}/approve`);
      fetchRegistrations();
      alert('Registration verified and published! Now searchable on the Citizen Portal.');
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="flex-1 bg-slate-100 p-6 space-y-6">
      {/* Header Banner */}
      <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <span className="text-xs font-bold uppercase tracking-wider text-purple-900 bg-purple-100 px-2.5 py-0.5 rounded-full">
              Sub-Registrar Integration (SRO API)
            </span>
            <span className="text-xs font-bold text-amber-900 bg-amber-100 px-2.5 py-0.5 rounded-full border border-amber-300">
              Target: Public Viewing in 2–3 Days
            </span>
          </div>
          <h1 className="text-2xl font-black text-slate-900 mt-2">
            New Registration Monitoring & Automatic Processing
          </h1>
          <p className="text-xs text-slate-500">
            Simulates registered sale deeds pushed via external Registration Department APIs with real-time OCR and Cadastral validation.
          </p>
        </div>

        {/* Simulation Action Box */}
        <div className="flex items-center flex-wrap gap-2">
          <select
            value={selectedScenario}
            onChange={(e) => setSelectedScenario(e.target.value)}
            className="px-3 py-2 text-xs font-semibold bg-slate-50 border border-slate-300 rounded-xl text-slate-800 focus:outline-none focus:ring-2 focus:ring-purple-600"
          >
            <option value="standard">Scenario 1: Standard Sale Deed</option>
            <option value="area_mismatch">Scenario 5: Cadastral Area Mismatch (2.45 vs 2.40 Acres)</option>
            <option value="duplicate_survey">Scenario 3: Duplicate Survey Number (101/2B)</option>
            <option value="low_confidence">Scenario 2: Low OCR Confidence Alert</option>
          </select>

          <button
            onClick={handleSimulate}
            disabled={simulating}
            className="px-5 py-2.5 bg-purple-900 hover:bg-purple-800 text-white font-bold rounded-xl transition-all shadow-md text-xs flex items-center gap-2 shrink-0 disabled:opacity-50"
          >
            {simulating ? (
              <>
                <RefreshCw className="w-4 h-4 animate-spin text-purple-300" />
                Receiving from SRO...
              </>
            ) : (
              <>
                <Sparkles className="w-4 h-4 text-amber-400" />
                Simulate New Registration
              </>
            )}
          </button>
        </div>
      </div>

      {/* Real-time Pipeline Visualizer (Appears after simulation) */}
      {latestProcessed && (
        <div className="bg-slate-900 text-white p-6 rounded-2xl border border-purple-500/40 shadow-xl space-y-4 animate-in fade-in slide-in-from-top-4 duration-200">
          <div className="flex items-center justify-between flex-wrap gap-2">
            <div>
              <span className="text-[11px] uppercase font-bold tracking-widest text-purple-400">
                Automatic Pipeline Pipeline Execution Telemetry
              </span>
              <h3 className="text-lg font-bold">
                Registration Processing Stream: {latestProcessed.registration_id}
              </h3>
            </div>
            <div className="text-xs bg-purple-950 px-3 py-1 rounded-full border border-purple-500/50 text-purple-200 font-mono">
              Status: Awaiting Officer Verification
            </div>
          </div>

          {/* Stepper Pipeline */}
          <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-7 gap-2 pt-2">
            {latestProcessed.pipeline_events.map((ev, i) => (
              <div 
                key={i} 
                className={`p-3 rounded-xl border text-xs flex flex-col justify-between ${
                  ev.status === 'DONE' ? 'bg-emerald-950/40 border-emerald-500/40 text-emerald-300' :
                  ev.status === 'FLAGGED' ? 'bg-amber-950/50 border-amber-500/50 text-amber-300' :
                  'bg-blue-950/60 border-blue-500 text-white font-bold shadow-md shadow-blue-900/50 animate-pulse'
                }`}
              >
                <div className="flex items-center justify-between mb-2">
                  <span className="text-[10px] font-mono text-slate-400">0{i+1}</span>
                  {ev.status === 'DONE' && <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />}
                  {ev.status === 'FLAGGED' && <AlertTriangle className="w-3.5 h-3.5 text-amber-400" />}
                  {ev.status === 'ACTIVE' && <Clock className="w-3.5 h-3.5 text-blue-400" />}
                </div>
                <div className="font-semibold text-[11px] leading-tight">{ev.label}</div>
              </div>
            ))}
          </div>

          {/* Cadastral Mismatch Banner if present */}
          {latestProcessed.cadastral_mismatch?.has_mismatch && (
            <div className="bg-amber-950/60 border border-amber-500/50 p-4 rounded-xl flex items-start gap-3 text-xs text-amber-200">
              <ShieldAlert className="w-5 h-5 text-amber-400 shrink-0 mt-0.5" />
              <div className="space-y-1">
                <span className="font-bold text-amber-300 uppercase tracking-wide">
                  Cross-Database Cadastral Discrepancy Detected:
                </span>
                <p>{latestProcessed.cadastral_mismatch.message}</p>
                <p className="text-amber-400/80">
                  Officer action required: Verify whether the 0.05 Acre delta reflects road surrender, subdivision mutation, or clerical deed error.
                </p>
              </div>
            </div>
          )}

          <div className="pt-2 flex items-center justify-between text-xs text-slate-400 border-t border-slate-800">
            <span>{latestProcessed.target_service_notice}</span>
            <button
              onClick={() => navigate(`/officer/verification/${latestProcessed.land_record_id}`)}
              className="px-4 py-1.5 bg-blue-600 hover:bg-blue-500 text-white font-bold rounded-lg transition-colors flex items-center gap-1"
            >
              Open Split-Screen Officer Verification <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>
      )}

      {/* Registrations List */}
      <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-6">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="text-base font-bold text-slate-900">
              Incoming Registrations Queue ({registrations.length})
            </h3>
            <p className="text-xs text-slate-500">
              Received via Mock SRO Gateway awaiting verification & public publication
            </p>
          </div>
          <button
            onClick={fetchRegistrations}
            className="p-1.5 rounded-lg text-slate-500 hover:bg-slate-100 transition-colors"
          >
            <RefreshCw className="w-4 h-4" />
          </button>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-xs text-left">
            <thead className="bg-slate-50 text-slate-600 font-bold border-y border-slate-200">
              <tr>
                <th className="py-2.5 px-3">Reg ID</th>
                <th className="py-2.5 px-3">Owner</th>
                <th className="py-2.5 px-3">Survey No</th>
                <th className="py-2.5 px-3">Village / District</th>
                <th className="py-2.5 px-3">Area</th>
                <th className="py-2.5 px-3">Target Public Date</th>
                <th className="py-2.5 px-3">Status</th>
                <th className="py-2.5 px-3 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {registrations.map((r) => (
                <tr key={r.id} className="hover:bg-slate-50">
                  <td className="py-3 px-3 font-mono font-bold text-purple-950">{r.registration_number}</td>
                  <td className="py-3 px-3 font-medium text-slate-900">{r.owner_name}</td>
                  <td className="py-3 px-3 font-mono font-semibold text-blue-900">{r.survey_number}</td>
                  <td className="py-3 px-3 text-slate-600">{r.village}, {r.district}</td>
                  <td className="py-3 px-3 font-bold text-slate-800">{r.land_area} Ac</td>
                  <td className="py-3 px-3 font-medium text-amber-900 bg-amber-50/50">{r.expected_public_date}</td>
                  <td className="py-3 px-3">
                    <span className={`px-2 py-0.5 rounded-full font-semibold text-[11px] ${
                      r.status === 'PUBLISHED' ? 'bg-emerald-100 text-emerald-800' :
                      r.has_mismatch ? 'bg-amber-100 text-amber-800 border border-amber-300' :
                      'bg-purple-100 text-purple-800'
                    }`}>
                      {r.status === 'PUBLISHED' ? 'Publicly Available' : (r.has_mismatch ? 'Area Mismatch' : r.status)}
                    </span>
                  </td>
                  <td className="py-3 px-3 text-right space-x-2">
                    {r.status !== 'PUBLISHED' ? (
                      <button
                        onClick={() => handleApprove(r.id)}
                        className="px-2.5 py-1 bg-emerald-600 hover:bg-emerald-700 text-white font-bold rounded text-[11px] transition-colors shadow-sm"
                      >
                        Approve & Publish
                      </button>
                    ) : (
                      <span className="text-[11px] font-bold text-emerald-600 flex items-center justify-end gap-1">
                        <CheckCircle2 className="w-3.5 h-3.5" /> Published
                      </span>
                    )}
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

export default NewRegistrationsPage;
