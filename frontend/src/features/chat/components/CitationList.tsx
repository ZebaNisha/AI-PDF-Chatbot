'use client';

import React from 'react';
import { FileText, ChevronRight } from 'lucide-react';
import { Citation } from '@/types';

interface Props {
  citations: Citation[];
  onCitationClick?: (citation: Citation) => void;
}

/**
 * Intelligent citation grouping and rendering.
 * Groups multiple page references from the same document.
 */
const CitationList: React.FC<Props> = ({ citations }) => {
  // Group by document_id
  const grouped = citations.reduce((acc, curr) => {
    if (!acc[curr.document_id]) {
      acc[curr.document_id] = {
        title: curr.document_title || 'Untitled Document',
        pages: new Set<number>(),
      };
    }
    acc[curr.document_id].pages.add(curr.start_page);
    return acc;
  }, {} as Record<string, { title: string; pages: Set<number> }>);

  return (
    <div className="space-y-2 mt-4 border-t border-gray-800/50 pt-4">
      <div className="flex items-center gap-2 mb-3">
        <span className="text-[10px] font-bold uppercase tracking-widest text-gray-500">Sources</span>
      </div>
      <div className="flex flex-wrap gap-2">
        {Object.entries(grouped).map(([id, info]) => (
          <button
            key={id}
            onClick={() => onCitationClick?.(citations.find(c => c.document_id === id)!)}
            className="group flex items-center gap-2 px-3 py-1.5 bg-gray-800/50 hover:bg-gray-800 border border-gray-700/50 rounded-lg transition-all active:scale-95"
            title={`View ${info.title}`}
          >
            <FileText className="h-3.5 w-3.5 text-blue-400" />
            <div className="flex items-center gap-1.5 overflow-hidden">
              <span className="text-xs font-medium text-gray-300 truncate max-w-[150px]">
                {info.title}
              </span>
              <span className="text-[10px] text-gray-500 font-mono">
                p.{Array.from(info.pages).sort((a, b) => a - b).join(', ')}
              </span>
            </div>
            <ChevronRight className="h-3 w-3 text-gray-600 group-hover:text-blue-400 transition-colors" />
          </button>
        ))}
      </div>
    </div>
  );
};

export default CitationList;
