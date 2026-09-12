import React from 'react';
import { AlertTriangle, RefreshCw } from 'lucide-react';

export class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }


  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error('ErrorBoundary caught error:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen bg-slate-900 text-white flex flex-col items-center justify-center p-6 text-center">
          <div className="w-16 h-16 bg-amber-500/20 border border-amber-500/50 rounded-2xl flex items-center justify-center mb-4 text-amber-400">
            <AlertTriangle className="w-8 h-8" />
          </div>
          <h1 className="text-2xl font-bold mb-2">Application Interface Notice</h1>
          <p className="text-slate-400 max-w-md mb-6 text-sm">
            {this.state.error?.message || 'An unexpected error occurred while rendering the page.'}
          </p>
          <div className="flex gap-3">
            <button
              onClick={() => {
                this.setState({ hasError: false, error: null });
                window.location.reload();
              }}
              className="px-5 py-2.5 bg-blue-600 hover:bg-blue-500 text-white rounded-xl font-bold text-sm flex items-center gap-2 transition-all shadow-md"
            >
              <RefreshCw className="w-4 h-4" />
              Reload Page
            </button>
            <button
              onClick={() => {
                this.setState({ hasError: false, error: null });
                window.location.href = '/';
              }}
              className="px-5 py-2.5 bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 rounded-xl font-bold text-sm transition-all"
            >
              Return Home
            </button>
          </div>
        </div>
      );
    }
    return this.props.children;
  }
}
