'use client';

import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { Layers, Check, FileText } from 'lucide-react';
import { clsx } from 'clsx';
import apiClient from '@/lib/api-client';
import { Document, DocumentStatus } from '@/types';
import LoadingOverlay from '@/components/shared/LoadingOverlay';

interface Props {
  selectedIds: string[];
  onChange: (ids: string[]) => void;
}

const DocumentSelector: React.FC<Props> = ({ selectedIds, onChange }) => {
  const { data: documents, isLoading } = useQuery<Document[]>({
    queryKey: ['documents'],
    queryFn: async () => {
      const res = await apiClient.get('/documents');
      return res.data;
    },
  });

  const toggleDoc = (id: string) => {
    if (selectedIds.includes(id)) {
      onChange(selectedIds.filter((i) => i !== id));
    } else {
      onChange([...selectedIds, id]);
    }
  };

  const isAllSelected = selectedIds.length === 0;

  if (isLoading) return <div className="p-4"><LoadingOverlay message="Loading documents..." /></div>;

  return (
    <div className="w-64 bg-gray-900/30 border-r border-gray-800 flex flex-col h-full overflow-hidden">
      <div className="p-6 border-b border-gray-800">
        <h3 className="flex items-center gap-2 text-sm font-semibold text-white">
          <Layers className="h-4 w-4 text-blue-500" />
          Context Selection
        </h3>
        <p className="mt-1 text-[10px] text-gray-500 uppercase tracking-widest font-medium">
          Targeted Search
        </p>
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-1">
        <button
          onClick={() => onChange([])}
          className={clsx(
            "w-full flex items-center justify-between px-3 py-2 rounded-lg text-xs transition-all",
            isAllSelected ? "bg-blue-600/10 text-blue-400 border border-blue-500/20" : "text-gray-400 hover:bg-gray-800/50"
          )}
        >
          <span>All Documents</span>
          {isAllSelected && <Check className="h-3 w-3" />}
        </button>

        <div className="my-4 border-t border-gray-800" />

        {documents?.filter(d => d.status === DocumentStatus.COMPLETED).map((doc) => (
          <button
            key={doc.id}
            onClick={() => toggleDoc(doc.id)}
            className={clsx(
              "w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-left transition-all group relative",
              selectedIds.includes(doc.id) 
                ? "bg-gray-800 text-blue-400 border border-gray-700 shadow-lg" 
                : "text-gray-500 hover:text-gray-300"
            )}
          >
            <FileText className={clsx(
              "h-4 w-4 flex-shrink-0",
              selectedIds.includes(doc.id) ? "text-blue-500" : "text-gray-600 group-hover:text-gray-400"
            )} />
            <span className="text-[13px] truncate font-medium">{doc.original_filename}</span>
            {selectedIds.includes(doc.id) && (
              <div className="absolute right-2 top-1/2 -translate-y-1/2 h-1.5 w-1.5 bg-blue-500 rounded-full shadow-[0_0_8px_rgba(59,130,246,0.5)]" />
            )}
          </button>
        ))}
        
        {documents?.length === 0 && (
          <p className="text-center text-xs text-gray-600 py-8">No processed documents found.</p>
        )}
      </div>
    </div>
  );
};

export default DocumentSelector;
