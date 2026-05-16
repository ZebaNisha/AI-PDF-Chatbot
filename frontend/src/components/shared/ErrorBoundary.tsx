'use client';

import React, { Component, ErrorInfo, ReactNode } from 'react';
import { AlertTriangle, RefreshCcw } from 'lucide-react';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
  error?: Error;
}

/**
 * Global Error Boundary to catch UI crashes and show a premium fallback.
 */
class ErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false
  };

  public static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('Uncaught error:', error, errorInfo);
  }

  public render() {
    if (this.state.hasError) {
      return this.props.fallback || (
        <div className="flex min-h-[400px] flex-col items-center justify-center p-8 text-center bg-gray-900/50 rounded-2xl border border-gray-800 backdrop-blur-xl">
          <div className="mb-6 p-4 bg-red-500/10 rounded-full">
            <AlertTriangle className="h-12 w-12 text-red-500" />
          </div>
          <h2 className="mb-2 text-2xl font-bold text-white">Something went wrong</h2>
          <p className="mb-8 text-gray-400 max-w-md">
            Our team has been notified. Please try refreshing the page or contact support if the issue persists.
          </p>
          <button
            onClick={() => window.location.reload()}
            className="flex items-center gap-2 px-6 py-3 bg-blue-600 hover:bg-blue-500 text-white rounded-xl font-medium transition-all active:scale-95 shadow-lg shadow-blue-600/20"
          >
            <RefreshCcw className="h-4 w-4" />
            Refresh Page
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;
