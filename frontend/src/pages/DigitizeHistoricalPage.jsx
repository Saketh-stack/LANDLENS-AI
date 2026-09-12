import React, { useState } from 'react';
import axios from 'axios';
import { 
  UploadCloud, FileText, CheckCircle2, AlertCircle, RefreshCw, 
  ArrowRight, Sparkles, Layers, Eye, ShieldCheck 
} from 'lucide-react';
import { useNavigate } from 'react-router-dom';

const DigitizeHistoricalPage = () => {
  const [file, setFile] = useState(null);
  const [language, setLanguage] = useState('English');
  const [documentType, setDocumentType] = useState('Sale Deed');
  const [scenario, setScenario] = useState('standard');
  const [uploading, setUploading] = useState(false);
  const [result, setResult] = useState(null);
  const navigate = useNavigate();

  const handleFileDrop = (e) => {
    e.preventDefault();
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      setFile(e.dataTransfer.files[0]);
    }
  };

  const handleProcessUpload = async (e) => {
    e.preventDefault();
    setUploading(true);
    setResult(null);

    const formData = new FormData();
    if (file) {
      formData.append('file', file);
    } else {
      // Mock dummy file for instant click-through demo
      const dummyBlob = new Blob(["Mock archival deed binary stream"], { type: "application/pdf" });
      formData.append('file', dummyBlob, `historical_record_${language.toLowerCase()}.pdf`);
    }
    formData.append('language', language);
    formData.append('document_type', documentType);
    formData.append('scenario', scenario);

    try {
      const res = await axios.post('/api/officer/historical-upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      setResult(res.data);
    } catch (err) {
      console.error('Upload processing error:', err);
      const msg = err.response?.data?.detail || err.message || 'Upload processing encountered an issue';
      alert(`Upload error: ${msg}`);
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="flex-1 bg-slate-100 p-6 space-y-6">
      {/* Header */}
      <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm">
        <div className="flex items-center gap-2">
          <span className="text-xs font-bold uppercase tracking-wider text-blue-900 bg-blue-100 px-2.5 py-0.5 rounded-full">
            Archival Land Registry Digitization
          </span>
          <span className="text-xs font-bold text-slate-600 bg-slate-100 px-2.5 py-0.5 rounded-full">
            8-Stage End-to-End Pipeline
          </span>
        </div>
        <h1 className="text-2xl font-black text-slate-900 mt-2">
          Digitize Historical Record
        </h1>
        <p className="text-xs text-slate-500">
          Upload handwritten land registers, scanned deeds, or historical PDFs in English and Indian languages (Hindi, Telugu, Tamil, Marathi).
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Upload Form (Left Column) */}
        <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-4">
          <h2 className="text-base font-bold text-slate-900">Upload & Extraction Settings</h2>

          <form onSubmit={handleProcessUpload} className="space-y-4">
            {/* Drag and drop zone */}
            <div
              onDragOver={(e) => e.preventDefault()}
              onDrop={handleFileDrop}
              className={`border-2 border-dashed rounded-xl p-6 text-center cursor-pointer transition-colors ${
                file ? 'border-emerald-500 bg-emerald-50/40' : 'border-slate-300 hover:border-blue-600 bg-slate-50'
              }`}
            >
              {file ? (
                <div className="space-y-1.5">
                  <div className="flex items-center justify-center gap-1.5 text-emerald-700 font-bold text-xs">
                    <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                    Original Document Attached
                  </div>
                  <p className="text-xs font-bold text-slate-800 break-all">{file.name}</p>
                  <p className="text-[11px] text-slate-500 font-medium">
                    {(file.size / 1024).toFixed(1)} KB • Genuine data will be extracted
                  </p>
                </div>
              ) : (
                <>
                  <UploadCloud className="w-10 h-10 text-slate-400 mx-auto mb-2" />
                  <p className="text-xs font-bold text-slate-700">
                    Drag and drop your original PDF, JPG, PNG
                  </p>
                  <p className="text-[11px] text-slate-400 mt-1">
                    Supports registered deeds, 7/12, Patta, mutation certificates
                  </p>
                </>
              )}
              <input
                type="file"
                accept=".pdf,.jpg,.jpeg,.png"
                onChange={(e) => setFile(e.target.files[0])}
                className="hidden"
                id="file-upload"
              />
              <label
                htmlFor="file-upload"
                className="mt-3 inline-block px-3 py-1.5 bg-slate-200 hover:bg-slate-300 text-slate-700 text-xs font-bold rounded-lg cursor-pointer"
              >
                {file ? "Choose Another Document" : "Browse Files"}
              </label>
            </div>

            {/* Language Selection */}
            <div>
              <label className="block text-xs font-bold text-slate-700 mb-1">
                Script / OCR Language Support
              </label>
              <select
                value={language}
                onChange={(e) => setLanguage(e.target.value)}
                className="w-full px-3 py-2 text-xs rounded-lg border border-slate-300 bg-white"
              >
                <option value="English">English (Standard Certified Deed)</option>
                <option value="Hindi">Hindi (मध्य प्रदेश खतौनी / अधिकार अभिलेख)</option>
                <option value="Telugu">Telugu (తెలంగాణ పట్టాదారు పాస్‌బుక్ / RoR-1B)</option>
                <option value="Tamil">Tamil (பட்டா / சிட்டா ஆவணம்)</option>
                <option value="Marathi">Marathi (७/१२ उतारा / भूमी अभिलेख)</option>
              </select>
            </div>

            {/* Document Type */}
            <div>
              <label className="block text-xs font-bold text-slate-700 mb-1">
                Document Classification
              </label>
              <select
                value={documentType}
                onChange={(e) => setDocumentType(e.target.value)}
                className="w-full px-3 py-2 text-xs rounded-lg border border-slate-300 bg-white"
              >
                <option value="Sale Deed">Registered Sale Deed</option>
                <option value="Khasra Khatauni">Khasra / Khatauni Register</option>
                <option value="Cadastral Map">Cadastral Boundary Map</option>
                <option value="Mutation Sanction">Mutation Sanction Order</option>
              </select>
            </div>

            {/* Demo Preset Scenario */}
            <div>
              <label className="block text-xs font-bold text-slate-700 mb-1">
                Validation Demonstration Condition
              </label>
              <select
                value={scenario}
                onChange={(e) => setScenario(e.target.value)}
                className="w-full px-3 py-2 text-xs rounded-lg border border-slate-300 bg-white"
              >
                <option value="standard">Standard High Confidence Extraction</option>
                <option value="low_confidence">Low Confidence Alert on Land Area (68%)</option>
                <option value="duplicate_survey">Duplicate Survey Collision (101/2B)</option>
                <option value="area_mismatch">Cadastral Area Mismatch (2.45 vs 2.40 Ac)</option>
              </select>
            </div>

            <button
              type="submit"
              disabled={uploading}
              className="w-full py-2.5 bg-blue-950 hover:bg-blue-900 text-white font-bold rounded-xl transition-all shadow-md text-xs flex items-center justify-center gap-2 disabled:opacity-50"
            >
              {uploading ? (
                <>
                  <RefreshCw className="w-4 h-4 animate-spin text-amber-400" />
                  Executing 8-Stage OCR Pipeline...
                </>
              ) : (
                <>
                  <Sparkles className="w-4 h-4 text-amber-400" />
                  Run AI/OCR Preprocessing & Extraction
                </>
              )}
            </button>
          </form>
        </div>

        {/* Pipeline & Results (Right 2 Columns) */}
        <div className="lg:col-span-2 space-y-6">
          {result ? (
            <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-6">
              <div className="flex items-center justify-between pb-4 border-b border-slate-200">
                <div>
                  <div className="flex items-center gap-2 flex-wrap">
                    <span className="text-xs font-bold uppercase tracking-wider text-emerald-800 bg-emerald-100 px-2.5 py-0.5 rounded-full border border-emerald-300">
                      Digitization Completed
                    </span>
                    {result.original_filename && (
                      <span className="text-[11px] font-bold text-blue-900 bg-blue-50 px-2.5 py-0.5 rounded-full border border-blue-200 truncate max-w-xs">
                        📄 {result.original_filename}
                      </span>
                    )}
                  </div>
                  <h3 className="text-lg font-bold text-slate-900 mt-1">
                    Record Digitize Result #{result.record_id}
                  </h3>
                  {result.ocr_engine && (
                    <p className="text-[11px] text-slate-500 mt-0.5">
                      Extracted via: <span className="font-semibold text-slate-700">{result.ocr_engine}</span>
                    </p>
                  )}
                </div>
                <button
                  onClick={() => navigate(`/officer/verification/${result.record_id}`)}
                  className="px-4 py-2 bg-blue-900 hover:bg-blue-800 text-white font-bold text-xs rounded-xl transition-all shadow-sm flex items-center gap-1.5"
                >
                  Open Officer Split-Screen Verification <ArrowRight className="w-4 h-4" />
                </button>
              </div>

              {/* 8-Stage Visual Stepper */}
              <div>
                <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-3">
                  8-Stage Pipeline Execution Progress
                </h4>
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
                  {(result.pipeline_stages || []).map((st) => (
                    <div
                      key={st.step}
                      className={`p-3 rounded-xl border text-xs flex flex-col justify-between ${
                        st.status === 'COMPLETED' ? 'bg-emerald-50 border-emerald-200 text-emerald-900' :
                        st.status === 'PENDING_OFFICER_REVIEW' ? 'bg-amber-50 border-amber-300 text-amber-950 font-bold animate-pulse' :
                        'bg-slate-50 border-slate-200 text-slate-500'
                      }`}
                    >
                      <div className="flex items-center justify-between mb-1">
                        <span className="font-mono text-[10px] text-slate-400">Step 0{st.step}</span>
                        {st.status === 'COMPLETED' && <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />}
                      </div>
                      <div className="font-semibold text-[11px] leading-tight">{st.name}</div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Live Extracted Text Stream Preview */}
              {result.ocr_raw_text_preview && (
                <div className="bg-slate-900 text-emerald-400 p-3.5 rounded-xl text-xs font-mono border border-slate-800 space-y-1.5 shadow-inner">
                  <div className="text-[10px] uppercase font-bold text-slate-400 flex items-center justify-between border-b border-slate-800 pb-1">
                    <span>Live Document Text Stream (OCR Ingested)</span>
                    <span className="text-emerald-400 font-semibold bg-emerald-950 px-2 py-0.5 rounded border border-emerald-800">
                      Genuine File Content
                    </span>
                  </div>
                  <div className="whitespace-pre-wrap line-clamp-4 text-[11px] text-emerald-300/90 leading-relaxed font-mono">
                    {result.ocr_raw_text_preview}
                  </div>
                </div>
              )}

              {/* OCR Preprocessing Applied */}
              {result.ocr?.preprocessing_applied && (
                <div className="bg-slate-50 rounded-xl p-4 border border-slate-200 text-xs space-y-2">
                  <div className="font-bold text-slate-800 flex items-center gap-2">
                    <Layers className="w-4 h-4 text-blue-900" />
                    Image Preprocessing & Noise Reduction Filters Applied:
                  </div>
                  <div className="flex flex-wrap gap-2 pt-1">
                    {result.ocr.preprocessing_applied.map((p, i) => (
                      <span key={i} className="px-2.5 py-1 bg-white border border-slate-300 rounded text-slate-700 font-medium text-[11px]">
                        {p}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {/* Extracted Fields Summary */}
              <div>
                <div className="flex items-center justify-between mb-3">
                  <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider">
                    Structured Land Record Extractions ({result.extraction?.extracted_fields?.length || 0} Fields)
                  </h4>
                  <span className="text-xs font-bold text-blue-900 bg-blue-50 px-2 py-0.5 rounded border border-blue-200">
                    Average Confidence: {result.extraction?.average_confidence || result.confidence_score || 0}%
                  </span>
                </div>

                <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 text-xs">
                  {(result.extraction?.extracted_fields || []).slice(0, 9).map((f) => (
                    <div key={f.field_name} className="p-3 bg-slate-50 rounded-xl border border-slate-200">
                      <div className="flex items-center justify-between text-slate-500 text-[10px]">
                        <span>{f.field_label}</span>
                        <span className={`font-bold ${
                          f.confidence >= 80 ? 'text-emerald-600' :
                          f.confidence >= 60 ? 'text-amber-600' : 'text-rose-600'
                        }`}>
                          {f.confidence}%
                        </span>
                      </div>
                      <div className="font-bold text-slate-900 text-xs mt-1 truncate">
                        {f.extracted_value}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          ) : (
            <div className="bg-white p-12 rounded-2xl border border-slate-200 shadow-sm text-center">
              <FileText className="w-12 h-12 text-slate-300 mx-auto mb-3" />
              <h3 className="text-base font-bold text-slate-800">No Document Processing in Progress</h3>
              <p className="text-xs text-slate-500 max-w-sm mx-auto mt-1">
                Select your parameters and click "Run AI/OCR Preprocessing & Extraction" on the left to start the 8-stage automated digitization pipeline.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default DigitizeHistoricalPage;
