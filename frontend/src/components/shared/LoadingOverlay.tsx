'use client';

import React from 'react';
import { Loader2 } from 'lucide-react';

interface Props {
  message?: string;
  fullScreen?: boolean;
}

/**
 * Modern loading overlay with glassmorphism.
 */
const LoadingOverlay: React.FC<Props> = ({ message = 'Loading...', fullScreen = false }) => {
  const content = (
    <div className="flex flex-col items-center justify-center gap-4 animate-in fade-in zoom-in duration-300">
      <div className="relative">
        <div className="absolute inset-0 bg-blue-500/20 blur-xl rounded-full" />
        <Loader2 className="h-10 w-10 text-blue-500 animate-spin relative" />
      </div>
      <p className="text-sm font-medium text-gray-400 tracking-wide">{message}</p>
    </div>
  );

  if (fullScreen) {
    return (
      <div className="fixed inset-0 z-[9999] flex items-center justify-center bg-gray-950/80 backdrop-blur-md">
        {content}
      </div>
    );
  }

  return (
    <div className="flex h-full w-full items-center justify-center p-8">
      {content}
    </div>
  );
};

export default LoadingOverlay;
