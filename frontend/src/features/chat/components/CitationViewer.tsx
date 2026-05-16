'use client';

import React, { useState } from 'react';
import { Document, Page, pdfjs } from 'react-pdf';
import { X, ChevronLeft, ChevronRight, Download, Loader2, Maximize2 } from 'lucide-react';
import { clsx } from 'clsx';

// Configure PDF.js worker
pdfjs.GlobalWorkerOptions.workerSrc = `//unpkg.com/pdfjs-dist@${pdfjs.version}/build/pdf.worker.min.mjs`;

interface Props {
  url: string;
  initialPage?: number;
  isOpen: boolean;
  onClose: () => void;
  title: string;
}

/**
 * Premium PDF Viewer for citations.
 * Supports jumping to pages and clean navigation.
 */
const CitationViewer: React.FC<Props> = ({ url, initialPage = 1, isOpen, onClose, title }) => {
  const [numPages, setNumPages] = useState<number | null>(null);
  const [pageNumber, setPageNumber] = useState(initialPage);
  const [scale, setScale] = useState(1.0);

  // Sync page number if initialPage changes while open
  React.useEffect(() => {
    setPageNumber(initialPage);
  }, [initialPage]);

  function onDocumentLoadSuccess({ numPages }: { numPages: number }) {
    setNumPages(numPages);
  }

  if (!isOpen) return null;

  return (
    <div className="fixed inset-y-0 right-0 z-[100] w-full max-w-2xl bg-gray-950 border-l border-gray-800 shadow-2xl animate-in slide-in-from-right duration-500 flex flex-col">
      {/* Header */}
      <header className="h-16 flex items-center justify-between px-6 border-b border-gray-800 bg-gray-900/50 backdrop-blur-md">
        <div className="flex items-center gap-3 overflow-hidden">
          <div className="p-2 bg-blue-600/10 rounded-lg">
            <Maximize2 className="h-4 w-4 text-blue-500" />
          </div>
          <h2 className="text-sm font-bold text-white truncate">{title}</h2>
        </div>
        
        <div className="flex items-center gap-2">
           <button 
             onClick={() => window.open(url, '_blank')}
             className="p-2 text-gray-500 hover:text-white transition-colors"
             title="Download PDF"
           >
             <Download className="h-4 w-4" />
           </button>
           <button 
             onClick={onClose}
             className="p-2 text-gray-500 hover:text-white bg-gray-800/50 rounded-lg hover:bg-gray-800 transition-all"
           >
             <X className="h-4 w-4" />
           </button>
        </div>
      </header>

      {/* Viewer Area */}
      <div className="flex-1 overflow-auto bg-gray-900/20 p-8 scrollbar-thin scrollbar-thumb-gray-800 scrollbar-track-transparent">
        <div className="flex justify-center min-h-full">
          <Document
            file={url}
            onLoadSuccess={onDocumentLoadSuccess}
            loading={
              <div className="flex flex-col items-center justify-center p-20 text-gray-500">
                <Loader2 className="h-8 w-8 animate-spin mb-4" />
                <p className="text-xs font-mono uppercase tracking-widest">Rendering PDF...</p>
              </div>
            }
            error={
              <div className="p-12 text-center text-red-400 bg-red-400/5 border border-red-400/20 rounded-2xl">
                 Failed to load document. The link might be expired or the file is corrupted.
              </div>
            }
          >
            <Page 
              pageNumber={pageNumber} 
              scale={scale}
              renderAnnotationLayer={false}
              renderTextLayer={true}
              className="shadow-2xl rounded-sm overflow-hidden"
            />
          </Document>
        </div>
      </div>

      {/* Footer / Controls */}
      <footer className="h-16 border-t border-gray-800 bg-gray-950 flex items-center justify-between px-8">
        <div className="flex items-center gap-4">
          <button
            onClick={() => setPageNumber(prev => Math.max(prev - 1, 1))}
            disabled={pageNumber <= 1}
            className="p-2 text-gray-400 hover:text-white disabled:opacity-30 disabled:cursor-not-allowed transition-all"
          >
            <ChevronLeft className="h-5 w-5" />
          </button>
          
          <div className="flex items-center gap-2">
             <span className="text-xs font-bold text-blue-500">{pageNumber}</span>
             <span className="text-[10px] text-gray-600 uppercase font-bold tracking-tighter">of</span>
             <span className="text-xs font-bold text-gray-400">{numPages || '--'}</span>
          </div>

          <button
            onClick={() => setPageNumber(prev => Math.min(prev + 1, numPages || prev))}
            disabled={pageNumber >= (numPages || 0)}
            className="p-2 text-gray-400 hover:text-white disabled:opacity-30 disabled:cursor-not-allowed transition-all"
          >
            <ChevronRight className="h-5 w-5" />
          </button>
        </div>

        <div className="flex items-center gap-2 bg-gray-900 rounded-lg p-1">
          {[0.75, 1.0, 1.5].map((s) => (
            <button
              key={s}
              onClick={() => setScale(s)}
              className={clsx(
                "px-3 py-1 rounded-md text-[10px] font-bold transition-all",
                scale === s ? "bg-blue-600 text-white" : "text-gray-500 hover:text-gray-300"
              )}
            >
              {s * 100}%
            </button>
          ))}
        </div>
      </footer>
    </div>
  );
};

export default CitationViewer;
