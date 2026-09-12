import React, { useState } from 'react';
import axios from 'axios';
import { Play, Sparkles, CheckCircle2, AlertTriangle, RefreshCw, Layers } from 'lucide-react';

const DemoToolbar = ({ onScenarioTriggered }) => {
  const [activeScenario, setActiveScenario] = useState('');
  const [loading, setLoading] = useState(false);
  const [fastMode, setFastMode] = useState(true);

  const scenarios = [
    { id: 'scenario_1', name: '1. Successful Reg', desc: 'Auto-processing & 2-3 day publication' },
    { id: 'scenario_2', name: '2. Low Confidence', desc: 'Highlights <80% fields for officer' },
    { id: 'scenario_3', name: '3. Duplicate Survey', desc: 'Detects collision on Survey 101/2B' },
    { id: 'scenario_5', name: '4. Area Mismatch', desc: '2.45 vs 2.40 Cadastral DB Delta' },
    { id: 'scenario_7', name: '5. AI Learning', desc: 'Feedback loop accuracy boost' }
  ];

  const triggerScenario = async (scId) => {
    setLoading(true);
    setActiveScenario(scId);
    try {
      const res = await axios.post(`/api/demo/trigger/${scId}`);
      if (onScenarioTriggered) {
        onScenarioTriggered(res.data);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-slate-900 text-slate-100 border-b border-amber-500/30 px-4 py-2 text-xs">
      <div className="max-w-7xl mx-auto flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-2">
          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded bg-amber-500/20 text-amber-300 font-semibold border border-amber-500/40">
            <Sparkles className="w-3.5 h-3.5 text-amber-400" />
            SIH26018 HACKATHON JUDGE DEMO MODE
          </span>
          <span className="hidden md:inline text-slate-400">
            One-click demonstration presets:
          </span>
        </div>

        <div className="flex items-center flex-wrap gap-1.5">
          {scenarios.map((sc) => (
            <button
              key={sc.id}
              onClick={() => triggerScenario(sc.id)}
              disabled={loading}
              title={sc.desc}
              className={`px-2.5 py-1 rounded transition-all font-medium flex items-center gap-1.5 ${
                activeScenario === sc.id
                  ? 'bg-amber-500 text-slate-950 font-bold shadow-md shadow-amber-500/30'
                  : 'bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700'
              }`}
            >
              <Play className="w-3 h-3 text-amber-400" />
              {sc.name}
            </button>
          ))}
        </div>

        <div className="flex items-center gap-3">
          <label className="flex items-center gap-1.5 cursor-pointer text-slate-300 select-none">
            <input
              type="checkbox"
              checked={fastMode}
              onChange={(e) => setFastMode(e.target.checked)}
              className="accent-amber-500 rounded cursor-pointer"
            />
            <span className="text-amber-400 font-medium">Fast Demo Mode</span>
            <span className="text-slate-400 hidden lg:inline">(Accelerated 2-3 Day Target)</span>
          </label>
        </div>
      </div>
    </div>
  );
};

export default DemoToolbar;
