import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Search, MapPin, FileCheck, Filter, AlertCircle, ChevronRight, Eye, Sparkles, Building2, CheckCircle, ShieldCheck } from 'lucide-react';
import RecordDetailsModal from '../components/RecordDetailsModal';
import VoiceSearchInput from '../components/VoiceSearchInput';
import { useLanguage } from '../context/LanguageContext';

const PublicHomePage = () => {
  const { t, currentLang } = useLanguage();
  const [records, setRecords] = useState([]);
  const [loading, setLoading] = useState(false);
  const [selectedRecord, setSelectedRecord] = useState(null);
  const [stats, setStats] = useState(null);

  // Search filter states
  const [searchTerm, setSearchTerm] = useState('');
  const [ownerName, setOwnerName] = useState('');
  const [surveyNumber, setSurveyNumber] = useState('');
  const [village, setVillage] = useState('');
  const [district, setDistrict] = useState('');
  const [showAdvanced, setShowAdvanced] = useState(false);

  const fetchRecords = async (overrideTerm = null) => {
    setLoading(true);
    try {
      const qVal = overrideTerm !== null ? overrideTerm : searchTerm;
      const params = {};
      if (qVal) params.q = qVal;
      if (ownerName) params.owner_name = ownerName;
      if (surveyNumber) params.survey_number = surveyNumber;
      if (village) params.village = village;
      if (district) params.district = district;

      const res = await axios.get('/api/public/records', { params });
      setRecords(Array.isArray(res.data) ? res.data : []);
    } catch (err) {
      console.error('Failed to search records', err);
      setRecords([]);
    } finally {
      setLoading(false);
    }
  };

  const fetchStats = async () => {
    try {
      const res = await axios.get('/api/public/stats');
      if (res.data && typeof res.data === 'object' && !Array.isArray(res.data)) {
        setStats(res.data);
      }
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    fetchRecords();
    fetchStats();
  }, []);

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    fetchRecords();
  };

  const handleVoiceInput = (text) => {
    setSearchTerm(text);
    fetchRecords(text);
  };

  return (
    <div className="flex-1 bg-slate-50 min-h-screen">
      {/* Hero Banner with Official Government Theme */}
      <div className="bg-gradient-to-b from-blue-950 via-slate-900 to-blue-900 text-white py-12 px-4 relative overflow-hidden">
        <div className="absolute inset-0 opacity-10 bg-[radial-gradient(#fff_1px,transparent_1px)] [background-size:16px_16px]"></div>
        <div className="max-w-7xl mx-auto relative z-10 text-center">
          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-blue-800/80 border border-blue-600/50 text-blue-200 text-xs font-semibold uppercase tracking-wider mb-4">
            <ShieldCheck className="w-4 h-4 text-emerald-400" />
            {t('ministry_sub')}
          </div>
          <h1 className="text-3xl sm:text-5xl font-extrabold tracking-tight mb-3">
            {t('hero_headline')}
          </h1>
          <p className="text-base sm:text-lg text-slate-300 max-w-2xl mx-auto mb-8 font-light">
            {t('hero_sub')}
          </p>

          {/* Search Box */}
          <div className="max-w-4xl mx-auto bg-white rounded-2xl shadow-2xl p-4 text-slate-900 border border-slate-200">
            <form onSubmit={handleSearchSubmit} className="space-y-4">
              <div className="flex flex-col sm:flex-row gap-2">
                <div className="relative flex-1 flex items-center">
                  <Search className="w-5 h-5 text-slate-400 absolute left-3.5" />
                  <input
                    type="text"
                    placeholder={t('search_placeholder')}
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="w-full pl-11 pr-12 py-3 rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-blue-600 font-medium text-sm"
                  />
                  <div className="absolute right-2">
                    <VoiceSearchInput onVoiceInput={handleVoiceInput} />
                  </div>
                </div>
                <button
                  type="submit"
                  className="px-8 py-3 bg-blue-900 hover:bg-blue-800 text-white font-bold rounded-xl transition-colors shadow-md flex items-center justify-center gap-2 shrink-0"
                >
                  <Search className="w-4 h-4" />
                  {t('search_btn')}
                </button>
              </div>

              {/* Toggle Advanced Filters */}
              <div className="flex items-center justify-between pt-1 border-t border-slate-100 text-xs text-slate-600">
                <button
                  type="button"
                  onClick={() => setShowAdvanced(!showAdvanced)}
                  className="font-semibold text-blue-900 hover:underline flex items-center gap-1"
                >
                  <Filter className="w-3.5 h-3.5" />
                  {showAdvanced ? 'Hide Detailed Parameters' : t('advanced_filters')}
                </button>
                <span className="text-slate-400 italic">
                  Showing only APPROVED & verified public records
                </span>
              </div>

              {showAdvanced && (
                <div className="grid grid-cols-1 sm:grid-cols-4 gap-3 pt-2 text-left">
                  <div>
                    <label className="block text-xs font-bold text-slate-700 mb-1">Owner Name</label>
                    <input
                      type="text"
                      placeholder="e.g. Ravi Kumar"
                      value={ownerName}
                      onChange={(e) => setOwnerName(e.target.value)}
                      className="w-full px-3 py-2 text-xs rounded-lg border border-slate-200 focus:ring-1 focus:ring-blue-600"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-bold text-slate-700 mb-1">Survey Number</label>
                    <input
                      type="text"
                      placeholder="e.g. 123/4A"
                      value={surveyNumber}
                      onChange={(e) => setSurveyNumber(e.target.value)}
                      className="w-full px-3 py-2 text-xs rounded-lg border border-slate-200 focus:ring-1 focus:ring-blue-600"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-bold text-slate-700 mb-1">Village</label>
                    <input
                      type="text"
                      placeholder="e.g. Rampur Kalan"
                      value={village}
                      onChange={(e) => setVillage(e.target.value)}
                      className="w-full px-3 py-2 text-xs rounded-lg border border-slate-200 focus:ring-1 focus:ring-blue-600"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-bold text-slate-700 mb-1">District</label>
                    <input
                      type="text"
                      placeholder="e.g. Bhopal"
                      value={district}
                      onChange={(e) => setDistrict(e.target.value)}
                      className="w-full px-3 py-2 text-xs rounded-lg border border-slate-200 focus:ring-1 focus:ring-blue-600"
                    />
                  </div>
                </div>
              )}
            </form>
          </div>
        </div>
      </div>

      {/* Target Service Notice Banner */}
      <div className="bg-amber-50 border-y border-amber-200 py-2.5 px-4 text-center text-xs text-amber-900 font-medium">
        <span className="font-bold uppercase tracking-wider text-amber-950 bg-amber-200 px-2 py-0.5 rounded mr-2">
          Proposed Service Target
        </span>
        Newly registered properties are validated and made available for certified public viewing within <strong>2–3 days</strong> after registration.
      </div>

      {/* Main Results Container */}
      <div className="max-w-7xl mx-auto px-4 py-8">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h2 className="text-xl font-bold text-slate-900">
              Approved Land Records ({records.length})
            </h2>
            <p className="text-xs text-slate-500">
              Official Land Registry certified records verified by Department Officers
            </p>
          </div>
          <button
            onClick={() => { setSearchTerm(''); setOwnerName(''); setSurveyNumber(''); setVillage(''); setDistrict(''); fetchRecords(); }}
            className="text-xs font-medium text-blue-900 hover:underline"
          >
            Reset All Filters
          </button>
        </div>

        {/* Records Table / Cards */}
        {loading ? (
          <div className="p-12 text-center text-slate-500">
            <div className="w-8 h-8 border-4 border-blue-900 border-t-transparent rounded-full animate-spin mx-auto mb-3"></div>
            Searching verified records...
          </div>
        ) : !Array.isArray(records) || records.length === 0 ? (
          <div className="bg-white rounded-xl border border-slate-200 p-12 text-center">
            <AlertCircle className="w-12 h-12 text-amber-500 mx-auto mb-3" />
            <h3 className="text-lg font-bold text-slate-800">No Approved Records Found</h3>
            <p className="text-sm text-slate-500 max-w-md mx-auto mt-1">
              No public records matched your search criteria. Note that pending or unapproved historical scans are strictly hidden from public view.
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
            {Array.isArray(records) && records.map((rec) => (
              <div
                key={rec.id}
                className="bg-white rounded-xl border border-slate-200 hover:border-blue-400 hover:shadow-lg transition-all p-5 flex flex-col justify-between"
              >
                <div>
                  <div className="flex items-start justify-between gap-2 mb-3">
                    <div>
                      <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-emerald-100 text-emerald-800 border border-emerald-300">
                        <CheckCircle className="w-3 h-3 text-emerald-600" />
                        Approved & Certified
                      </span>
                      <h3 className="text-lg font-bold text-slate-900 mt-2">
                        {rec.owner_name}
                      </h3>
                      <p className="text-xs text-slate-500">
                        S/o or W/o: {rec.father_husband_name || 'N/A'}
                      </p>
                    </div>
                    <div className="text-right">
                      <span className="text-xs font-bold text-slate-700 bg-slate-100 px-2 py-1 rounded">
                        {rec.land_classification}
                      </span>
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-2 text-xs py-3 my-2 border-y border-slate-100">
                    <div>
                      <span className="text-slate-500 block">Survey Number</span>
                      <span className="font-bold text-blue-900 font-mono text-sm">{rec.survey_number}</span>
                    </div>
                    <div>
                      <span className="text-slate-500 block">Land Area</span>
                      <span className="font-bold text-slate-800 font-mono text-sm">{rec.land_area} Acres</span>
                    </div>
                    <div>
                      <span className="text-slate-500 block">Khata Number</span>
                      <span className="font-medium text-slate-700">{rec.khata_number}</span>
                    </div>
                    <div>
                      <span className="text-slate-500 block">Khasra Number</span>
                      <span className="font-medium text-slate-700">{rec.khasra_number}</span>
                    </div>
                  </div>

                  <div className="flex items-center gap-1.5 text-xs text-slate-600 mb-4">
                    <MapPin className="w-3.5 h-3.5 text-slate-400 shrink-0" />
                    <span>{rec.village}, Tehsil {rec.tehsil}, {rec.district}</span>
                  </div>
                </div>

                <div className="pt-3 border-t border-slate-100 flex items-center justify-between gap-2">
                  <span className="text-[11px] font-mono text-slate-500 truncate">
                    {rec.registration_number}
                  </span>
                  <div className="flex items-center gap-1.5 shrink-0">
                    <button
                      onClick={() => setSelectedRecord(rec)}
                      className="px-3 py-1.5 bg-blue-50 hover:bg-blue-100 text-blue-900 text-xs font-bold rounded-lg transition-colors flex items-center gap-1"
                    >
                      <Eye className="w-3.5 h-3.5" />
                      View Details
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Record Details Modal */}
      {selectedRecord && (
        <RecordDetailsModal
          record={selectedRecord}
          onClose={() => setSelectedRecord(null)}
        />
      )}
    </div>
  );
};

export default PublicHomePage;
