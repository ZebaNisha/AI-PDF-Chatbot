'use client';

import React, { useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { FileText, Trash2, Clock, CheckCircle, AlertCircle, Loader2, MoreVertical } from 'lucide-react';
import { Document, DocumentStatus } from '@/types';
import { DocumentService } from '../services/document.service';
import { notify } from '@/lib/notifications';
import { clsx } from 'clsx';

/**
 * Status badge with stage-specific styling.
 */
const StatusBadge: React.FC<{ status: DocumentStatus }> = ({ status }) => {
  const config = {
    [DocumentStatus.PENDING]: { icon: Clock, color: 'text-gray-400 bg-gray-400/10 border-gray-400/20', label: 'Queued' },
    [DocumentStatus.UPLOADED]: { icon: Loader2, color: 'text-blue-400 bg-blue-400/10 border-blue-400/20', label: 'Uploaded' },
    [DocumentStatus.EXTRACTING]: { icon: Loader2, color: 'text-purple-400 bg-purple-400/10 border-purple-400/20', label: 'Extracting' },
    [DocumentStatus.CHUNKING]: { icon: Loader2, color: 'text-indigo-400 bg-indigo-400/10 border-indigo-400/20', label: 'Chunking' },
    [DocumentStatus.EMBEDDING]: { icon: Loader2, color: 'text-cyan-400 bg-cyan-400/10 border-cyan-400/20', label: 'Embedding' },
    [DocumentStatus.STORING]: { icon: Loader2, color: 'text-sky-400 bg-sky-400/10 border-sky-400/20', label: 'Storing' },
    [DocumentStatus.COMPLETED]: { icon: CheckCircle, color: 'text-green-400 bg-green-400/10 border-green-400/20', label: 'Processed' },
    [DocumentStatus.FAILED]: { icon: AlertCircle, color: 'text-red-400 bg-red-400/10 border-red-400/20', label: 'Failed' },
  }[status];

  const Icon = config.icon;

  return (
    <div className={clsx("flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[10px] font-bold uppercase tracking-wider border", config.color)}>
      <Icon className={clsx("h-3 w-3", status !== DocumentStatus.COMPLETED && status !== DocumentStatus.FAILED && status !== DocumentStatus.PENDING && "animate-spin")} />
      {config.label}
    </div>
  );
};

const DocumentList: React.FC = () => {
  const queryClient = useQueryClient();
  
  const { data: documents, isLoading } = useQuery<Document[]>({
    queryKey: ['documents'],
    queryFn: () => DocumentService.list(),
    // Poll every 3 seconds if there are documents being processed
    refetchInterval: (query) => {
      const docs = query.state.data as Document[] | undefined;
      const isProcessing = docs?.some(d => 
        ![DocumentStatus.COMPLETED, DocumentStatus.FAILED].includes(d.status)
      );
      return isProcessing ? 3000 : false;
    }
  });

  const deleteMutation = useMutation({
    mutationFn: (id: string) => DocumentService.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['documents'] });
      notify.success('Document deleted');
    },
    onError: (error: any) => notify.error(error.message || 'Delete failed'),
  });

  if (isLoading) return (
    <div className="flex flex-col items-center justify-center p-20 opacity-50">
      <Loader2 className="h-8 w-8 animate-spin mb-4" />
      <p className="text-sm font-mono text-gray-500 uppercase tracking-widest">Fetching Library...</p>
    </div>
  );

  if (!documents?.length) return (
    <div className="flex flex-col items-center justify-center p-20 text-center bg-gray-900/10 border border-dashed border-gray-800 rounded-[2rem]">
       <div className="h-16 w-16 bg-gray-800/50 rounded-2xl flex items-center justify-center mb-6">
          <FileText className="h-8 w-8 text-gray-700" />
       </div>
       <h3 className="text-white font-bold mb-2">No Documents Found</h3>
       <p className="text-sm text-gray-500 max-w-xs mx-auto">
         Your knowledge base is empty. Upload a PDF to start chatting with your data.
       </p>
    </div>
  );

  return (
    <div className="w-full max-w-4xl mx-auto space-y-3">
      {documents.map((doc) => (
        <div 
          key={doc.id}
          className="group flex items-center justify-between p-4 bg-gray-900/30 hover:bg-gray-900/50 border border-gray-800 hover:border-gray-700 rounded-2xl transition-all duration-300"
        >
          <div className="flex items-center gap-4">
            <div className="h-10 w-10 bg-gray-800/50 rounded-xl flex items-center justify-center text-gray-400 group-hover:text-blue-400 transition-colors">
              <FileText className="h-5 w-5" />
            </div>
            <div>
              <h4 className="text-sm font-semibold text-gray-200 group-hover:text-white transition-colors">{doc.original_filename}</h4>
              <div className="flex items-center gap-3 mt-1">
                <span className="text-[10px] text-gray-500 font-mono">{(doc.file_size / (1024 * 1024)).toFixed(2)} MB</span>
                <span className="text-gray-700">•</span>
                <span className="text-[10px] text-gray-500 font-mono">Added {new Date(doc.created_at).toLocaleDateString()}</span>
              </div>
            </div>
          </div>

          <div className="flex items-center gap-6">
            <StatusBadge status={doc.status} />
            
            <button
              onClick={() => {
                if (window.confirm('Delete this document and all associated data?')) {
                  deleteMutation.mutate(doc.id);
                }
              }}
              className="p-2 text-gray-600 hover:text-red-500 hover:bg-red-500/10 rounded-lg transition-all"
              disabled={deleteMutation.isPending}
            >
              <Trash2 className="h-4 w-4" />
            </button>
          </div>
        </div>
      ))}
    </div>
  );
};

export default DocumentList;
