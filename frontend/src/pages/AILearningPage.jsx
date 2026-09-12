import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { 
  Sparkles, TrendingUp, RefreshCw, CheckCircle2, 
  Brain, Award, ShieldCheck, ArrowRight 
} from 'lucide-react';

const AILearningPage = () => {
  const [metrics, setMetrics] = useState(null);
  const [loading, setLoading] = useState(true);

  const fetchMetrics = async () => {
    try {
      const res = await axios.get('/api/officer/ai-learning-metrics');
      setMetrics(res.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchMetrics();
  }, []);

  if (loading || !metrics || typeof metrics !== 'object' || Array.isArray(metrics)) {
    return (
      <div className="flex-1 p-8 text-center text-slate-500">
        <div className="w-8 h-8 border-4 border-blue-900 border-t-transparent rounded-full animate-spin mx-auto mb-3"></div>
        Loading AI Continuous Learning analytics...
      </div>
    );
  }

  return (
    <div className="flex-1 bg-slate-100 p-6 space-y-6">
      {/* Header */}
      <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm">
        <div className="flex items-center gap-2">
          <span className="text-xs font-bold uppercase tracking-wider text-purple-900 bg-purple-100 px-2.5 py-0.5 rounded-full">
            Self-Improving NLP Architecture
          </span>
          <span className="text-xs font-bold text-emerald-800 bg-emerald-100 px-2.5 py-0.5 rounded-full border border-emerald-300">
            Active Feedback Pipeline
          </span>
        </div>
        <h1 className="text-2xl font-black text-slate-900 mt-2">
          AI Learning & Human-in-the-Loop Feedback Loop
        </h1>
        <p className="text-xs text-slate-500">
          When officers accept or edit extracted fields (e.g. Land Area: 2.45 → 2.40 Acres), the system logs corrective deltas and continuously tunes the OCR extraction model.
        </p>
      </div>

      {/* Accuracy KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-6">
        <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm flex flex-col justify-between">
          <span className="text-xs font-bold text-slate-500 uppercase tracking-wider">Documents Corrected by Officers</span>
          <div className="text-3xl font-black text-slate-900 font-mono mt-2">
            {metrics.documents_corrected}
          </div>
          <span className="text-xs text-slate-400 mt-2">Human supervision feedback samples</span>
        </div>

        <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm flex flex-col justify-between">
          <span className="text-xs font-bold text-slate-500 uppercase tracking-wider">Baseline Model Accuracy</span>
          <div className="text-3xl font-black text-slate-400 font-mono mt-2">
            {metrics.baseline_accuracy}
          </div>
          <span className="text-xs text-slate-400 mt-2">Initial out-of-box OCR/NLP model</span>
        </div>

        <div className="bg-gradient-to-br from-purple-900 to-indigo-950 text-white p-6 rounded-2xl shadow-lg flex flex-col justify-between">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-purple-300 uppercase tracking-wider">Current Post-Learning Accuracy</span>
            <Sparkles className="w-5 h-5 text-amber-400" />
          </div>
          <div className="text-4xl font-black text-white font-mono mt-2">
            {metrics.current_accuracy}
          </div>
          <span className="text-xs text-emerald-300 font-bold mt-2 flex items-center gap-1">
            <TrendingUp className="w-3.5 h-3.5" /> +3.0% improvement from officer feedback
          </span>
        </div>
      </div>

      {/* Top Corrected Fields & Learning Dynamics */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-4">
          <h3 className="text-base font-bold text-slate-900">
            Top Fields Corrected by Verification Officers
          </h3>
          <p className="text-xs text-slate-500">
            High-friction historical calligraphy zones with the largest model gains
          </p>

          <div className="space-y-3 pt-2">
            {metrics.top_corrected_fields.map((f, i) => (
              <div key={i} className="p-4 bg-slate-50 rounded-xl border border-slate-200 flex items-center justify-between">
                <div>
                  <div className="font-bold text-sm text-slate-900">{f.field}</div>
                  <div className="text-xs text-slate-500">{f.corrections} officer verified updates</div>
                </div>
                <span className="px-2.5 py-1 bg-emerald-100 text-emerald-800 font-bold text-xs rounded-full border border-emerald-300">
                  {f.improvement} Accuracy
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* AI Learning Pipeline Architecture */}
        <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-4">
          <h3 className="text-base font-bold text-slate-900">
            How Continuous AI Learning Works
          </h3>
          <p className="text-xs text-slate-500">
            Active human-in-the-loop retraining architecture
          </p>

          <div className="space-y-3 text-xs pt-1">
            <div className="p-3 rounded-xl bg-blue-50 border border-blue-200">
              <span className="font-bold text-blue-950 block mb-0.5">1. Officer Manual Correction</span>
              <p className="text-blue-900">Officer edits a field (e.g. adjusting Land Area to match Cadastral survey).</p>
            </div>

            <div className="p-3 rounded-xl bg-purple-50 border border-purple-200">
              <span className="font-bold text-purple-950 block mb-0.5">2. Immutable Delta Logging</span>
              <p className="text-purple-900">Original OCR string and corrected value stored in the <code>ai_corrections</code> telemetry table.</p>
            </div>

            <div className="p-3 rounded-xl bg-emerald-50 border border-emerald-200">
              <span className="font-bold text-emerald-950 block mb-0.5">3. Synthetic Preprocessing Retraining</span>
              <p className="text-emerald-900">Adaptive thresholding weights dynamically adjust bounding box character segmentation for that handwriting style.</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AILearningPage;
