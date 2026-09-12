import React, { useState, useEffect, useRef } from 'react';
import { Mic, MicOff, AlertCircle } from 'lucide-react';
import { useLanguage } from '../context/LanguageContext';

const VoiceSearchInput = ({ onVoiceInput, isSearching = false }) => {
  const { currentLang, getCurrentMeta, t } = useLanguage();
  const [isListening, setIsListening] = useState(false);
  const [speechSupported, setSpeechSupported] = useState(true);
  const [feedback, setFeedback] = useState('');
  const recognitionRef = useRef(null);

  useEffect(() => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
      setSpeechSupported(false);
      return;
    }

    try {
      const recognition = new SpeechRecognition();
      recognition.continuous = false;
      recognition.interimResults = false;
      const meta = getCurrentMeta();
      recognition.lang = meta.locale || 'en-IN';

      recognition.onstart = () => {
        setIsListening(true);
        setFeedback(`${t('listening')} ${meta.nativeName}...`);
      };

      recognition.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        if (transcript && onVoiceInput) {
          onVoiceInput(transcript);
        }
        setIsListening(false);
        setFeedback('');
      };

      recognition.onerror = (event) => {
        console.warn('Speech recognition error:', event.error);
        setIsListening(false);
        setFeedback('Voice recognition error. Please type your search.');
        setTimeout(() => setFeedback(''), 4000);
      };

      recognition.onend = () => {
        setIsListening(false);
      };

      recognitionRef.current = recognition;
    } catch (e) {
      console.warn('Speech API init error:', e);
      setSpeechSupported(false);
    }
  }, [currentLang]);

  const toggleListening = () => {
    if (!speechSupported) {
      alert('Speech recognition is not supported in this browser. Please use Chrome, Edge, or Safari.');
      return;
    }

    if (isListening) {
      recognitionRef.current?.stop();
      setIsListening(false);
      setFeedback('');
    } else {
      try {
        const meta = getCurrentMeta();
        if (recognitionRef.current) {
          recognitionRef.current.lang = meta.locale || 'en-IN';
          recognitionRef.current.start();
        }
      } catch (e) {
        console.warn('Start recognition error:', e);
      }
    }
  };

  if (!speechSupported) {
    return null;
  }

  return (
    <div className="relative inline-flex items-center">
      <button
        type="button"
        onClick={toggleListening}
        title={t('voice_search_tooltip')}
        className={`p-2.5 rounded-xl transition-all flex items-center justify-center ${
          isListening
            ? 'bg-rose-600 text-white animate-pulse shadow-lg ring-4 ring-rose-200'
            : 'text-slate-500 hover:text-blue-900 hover:bg-blue-50 bg-slate-100'
        }`}
      >
        {isListening ? (
          <MicOff className="w-5 h-5 text-white animate-bounce" />
        ) : (
          <Mic className="w-5 h-5 text-blue-700" />
        )}
      </button>

      {feedback && (
        <div className="absolute right-0 top-full mt-2 w-64 p-2 bg-slate-900 text-white text-xs rounded-lg shadow-xl z-50 flex items-center gap-1.5 animate-in fade-in">
          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping shrink-0"></span>
          <span>{feedback}</span>
        </div>
      )}
    </div>
  );
};

export default VoiceSearchInput;
